`timescale 1ns / 1ps
// Single-cycle CPU with extended instructions. Each instruction is fetched, decoded
// and executed in one clock cycle (unless `stall` is 1).
//
//   opcode 0      HALT                  stop: halted = 1, PC stops
//   opcode 1      ADD   rd, rs1, rs2    rd = rs1 + rs2
//   opcode 2      LOAD  rd, [rs1+imm6]  rd = MEM[addr]
//   opcode 3      STORE rs2, [rs1+imm6] MEM[addr] = rs2
//   opcode 4      SUB   rd, rs1, rs2    rd = rs1 - rs2
//   opcode 5      ADDI  rd, rs1, imm6   rd = rs1 + imm6
//   opcode 6      BEQ   rs1, rs2, target if (rs1 == rs2) PC = target
//   opcode 7      JMP   target           PC = target
//   opcode 8..15  unused                treated as HALT
//
// Encoding: [15:12] opcode, [11:9] rd (or STORE value reg / BEQ rs2), [8:6] rs1,
//           [5:0] imm6 (LOAD/STORE/ADDI/BEQ/JMP) or [5:3] rs2 (ADD/SUB).
//
// The same CPU is used in both systems. `stall` = 1 means "the memory is busy
// this cycle": PC holds, no register write, no memory write. Harvard ties
// stall to 0; the shared-memory controller drives it.
module cpu (
    input         clk,
    input         rst,      // synchronous, active high
    input         stall,    // 1 = PC holds, no register write, no memory write
    output [5:0]  i_addr,   // = PC
    input  [15:0] i_data,   // instruction
    output [5:0]  d_addr,
    output        d_re,     // 1 for LOAD
    output        d_we,     // 1 for STORE (forced 0 when stall = 1)
    output [15:0] d_wdata,
    input  [15:0] d_rdata,
    output        halted
);
    // ---------------- Decode ----------------
    wire [3:0] opcode = i_data[15:12];
    wire [2:0] rd     = i_data[11:9];   // destination (ADD/LOAD/SUB/ADDI) or value reg (STORE/BEQ)
    wire [2:0] rs1    = i_data[8:6];    // first source / base address register
    wire [2:0] rs2    = i_data[5:3];    // second source (ADD/SUB only)
    wire [5:0] imm6   = i_data[5:0];    // address offset / target / immediate

    wire is_add   = (opcode == 4'd1);
    wire is_load  = (opcode == 4'd2);
    wire is_store = (opcode == 4'd3);
    wire is_sub   = (opcode == 4'd4);
    wire is_addi  = (opcode == 4'd5);
    wire is_beq   = (opcode == 4'd6);
    wire is_jmp   = (opcode == 4'd7);
    wire is_halt  = ~(is_add | is_load | is_store | is_sub | is_addi | is_beq | is_jmp);

    // ---------------- Control ----------------
    reg  halted_r;
    wire run = ~stall & ~halted_r;   // 1 = this instruction finishes this cycle

    // ---------------- Register file ----------------
    wire [15:0] rdata1, rdata2;
    wire [2:0]  raddr2 = (is_store | is_beq) ? rd : rs2;   // STORE/BEQ reads second value from [11:9]
    wire [15:0] alu_sum  = rdata1 + rdata2;                // ADD
    wire [15:0] alu_diff = rdata1 - rdata2;                // SUB
    wire [15:0] alu_addi = rdata1 + {10'd0, imm6};         // ADDI

    wire [15:0] alu_res  = is_sub  ? alu_diff :
                           is_addi ? alu_addi :
                                     alu_sum;

    wire [15:0] wdata    = is_load ? d_rdata : alu_res;
    wire is_rf_write     = is_add | is_load | is_sub | is_addi;

    register_file u_rf (
        .clk(clk), .rst(rst),
        .we(run & is_rf_write),
        .waddr(rd), .wdata(wdata),
        .raddr1(rs1), .raddr2(raddr2),
        .rdata1(rdata1), .rdata2(rdata2)
    );

    // ---------------- Program counter ----------------
    wire branch_taken        = (is_beq & (rdata1 == rdata2)) | is_jmp;
    wire [5:0] branch_target = imm6;

    wire [5:0] pc;
    program_counter u_pc (
        .clk(clk), .rst(rst),
        .en(run & ~is_halt),
        .branch_taken(branch_taken),
        .branch_target(branch_target),
        .pc(pc)
    );

    // HALT: set `halted` when the HALT instruction executes; it stays 1 until reset.
    always @(posedge clk) begin
        if (rst)
            halted_r <= 1'b0;
        else if (run & is_halt)
            halted_r <= 1'b1;
    end

    // ---------------- Outputs ----------------
    wire [15:0] addr_sum = rdata1 + {10'd0, imm6};   // data address = R[rs1] + imm6

    assign i_addr  = pc;
    assign d_addr  = addr_sum[5:0];
    assign d_re    = is_load & ~halted_r;
    assign d_we    = is_store & run;
    assign d_wdata = rdata2;
    assign halted  = halted_r;
endmodule
