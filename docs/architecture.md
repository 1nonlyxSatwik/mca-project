# Architecture and implementation contract

## Primary: 2-way LRU cache

Cache data capacity is 2 KB: 64 sets x 2 ways x 128 bits. Tags are 22 bits. Both ways are looked up concurrently. Each set has two valid bits, two dirty bits and one LRU bit. `lru_bit=0` selects way zero as the next victim; touching way W stores `~W`.

The blocking FSM is IDLE -> TAG_CHECK -> HIT on a hit. A miss takes SELECT_VICTIM -> optional WRITE_BACK -> FETCH_BLOCK -> FILL_WAY -> TAG_CHECK -> HIT. Fill and hit both update LRU. Under the normal reset/fill protocol, the two initial fills use the empty ways. Clean victims need no writeback. Stores allocate on a miss and mark the selected line dirty.

The direct-mapped baseline has the same data capacity and block size, with 128 indexed lines and 21-bit tags. It has a different controller implementation, which matters when interpreting cycle measurements. The baseline resets storage arrays while the modular two-way design primarily invalidates metadata; synthesis comparisons therefore also reflect coding style, not associativity alone.

The cache-facing CPU address is 32-bit byte-addressed and word-aligned. The memory model serves whole 16-byte blocks and supports addresses 0..65535. The controller accepts one request at a time. There is no byte-store, flush instruction, write-through mode, DMA coherence or multicore coherence.

## New: CPU/cache bridge

`cpu_cached_top` instantiates the same original CPU, one selectable cache and `cpu_line_memory`. `CACHE_KIND=0` chooses direct mapped; 1 chooses two-way. Cache geometry stays at the validated default values; arbitrary cache parameter combinations are not claimed supported because some inherited submodules use fixed widths.

States:

1. FETCH_REQ pulses cache read at `PC*4`.
2. FETCH_WAIT waits for ready, then saves the instruction.
3. DATA_REQ decodes the saved instruction and starts an ordinary LOAD/STORE. I/O or invalid accesses go directly to commit.
4. DATA_WAIT waits for the requested word and saves read data.
5. COMMIT releases CPU stall for exactly one edge, then fetch restarts.

STORE requests use saved instruction opcode decoding, independent of CPU `d_we`, which is gated off during stall. This avoids circular stall/write-enable logic. Main memory data accesses cover CPU words 0x00..0x2F. Word 0x3F is output-register I/O; 0x30..0x3E reads zero, ignores writes and flags `addr_err` at commit.

A CPU word occupies the low 16 bits of a 32-bit cache slot. Thus byte address = word address * 4. Four CPU words occupy a 16-byte cache line. The initialized backing store has 16 lines for 64 CPU slots. Upper halves are zero. Code and data share this cache/backing store, so writes to future instructions are observed on later fetches.

Reset clears CPU/controller/output state and invalidates cache metadata. RAM boot contents are initialized once per simulation; reset is not a flush. Dirty cache contents can be lost on reset; the project does not promise persistent warm-reset behavior. HALT stops new requests but does not flush dirty lines.

## Supporting: original CPU systems

Harvard uses independent asynchronous instruction and data memory reads. Shared memory serializes a LOAD/STORE through fetch/data phases using one port. The same 16-bit, eight-register CPU is used; R0 always reads zero. Addresses wrap to six bits. ADDI is zero-extended unsigned; branch/jump targets are absolute six-bit addresses. Arithmetic wraps at 16 bits, without overflow traps.
