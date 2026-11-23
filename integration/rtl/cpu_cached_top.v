`timescale 1ns/1ps
// Blocking unified cache bridge. CPU architectural state changes only in COMMIT.
// Each 16-bit CPU word occupies the low half of one 32-bit cache word:
// cache byte address = CPU word address * 4. I/O and invalid accesses bypass cache.
module cpu_cached_top #(
    parameter CACHE_KIND = 1, // 0: direct mapped; 1: two-way LRU
    parameter MEM_LATENCY = 3,
    parameter PROG_FILE = "programs/prog1.hex",
    parameter DATA_FILE = "programs/prog1_data.hex"
) (
    input clk, input rst,
    output halted, output reg [15:0] io_out, output addr_err,
    output [5:0] retired_pc, output [15:0] retired_instr,
    output retire, output cache_request, output cache_done
);
    localparam FETCH_REQ=0, FETCH_WAIT=1, DATA_REQ=2, DATA_WAIT=3, COMMIT=4;
    reg [2:0] state;
    reg [15:0] instruction, load_data;
    wire [5:0] pc, data_addr;
    wire [15:0] data_write;
    wire cpu_read, cpu_write;
    wire is_load = instruction[15:12] == 4'd2;
    wire is_store = instruction[15:12] == 4'd3;
    wire normal_memory = data_addr <= 6'h2f;
    wire output_port = data_addr == 6'h3f;
    wire stall = state != COMMIT;
    wire [31:0] cache_addr = state == FETCH_REQ ? {24'd0,pc,2'b00} : {24'd0,data_addr,2'b00};
    wire cache_re = !rst && !halted && (state == FETCH_REQ || (state == DATA_REQ && is_load && normal_memory));
    wire cache_we = !rst && !halted && state == DATA_REQ && is_store && normal_memory;
    wire [31:0] cache_rdata;
    wire ready;
    wire [31:0] mem_addr;
    wire mem_re, mem_we, mem_ready;
    wire [127:0] mem_wdata, mem_rdata;

    assign retired_pc = pc;
    assign retired_instr = instruction;
    assign retire = !rst && !halted && state == COMMIT;
    assign addr_err = retire && (is_load || is_store) && !normal_memory && !output_port;
    assign cache_request = cache_re || cache_we;
    assign cache_done = ready && (state == FETCH_WAIT || state == DATA_WAIT);

    cpu u_cpu (.clk(clk),.rst(rst),.stall(stall),.i_addr(pc),.i_data(instruction),
        .d_addr(data_addr),.d_re(cpu_read),.d_we(cpu_write),.d_wdata(data_write),
        .d_rdata(load_data),.halted(halted));

    generate if (CACHE_KIND == 0) begin : dm
        direct_mapped_cache u_cache (.clk(clk),.rst_n(!rst),.cpu_addr(cache_addr),
            .cpu_wdata({16'd0,data_write}),.cpu_we(cache_we),.cpu_re(cache_re),
            .cpu_rdata(cache_rdata),.cpu_ready(ready),.mem_addr(mem_addr),
            .mem_re(mem_re),.mem_we(mem_we),.mem_wdata(mem_wdata),
            .mem_rdata(mem_rdata),.mem_ready(mem_ready));
    end else begin : sa
        cache_2way_top u_cache (.clk(clk),.rst_n(!rst),.cpu_addr(cache_addr),
            .cpu_wdata({16'd0,data_write}),.cpu_we(cache_we),.cpu_re(cache_re),
            .cpu_rdata(cache_rdata),.cpu_ready(ready),.mem_addr(mem_addr),
            .mem_re(mem_re),.mem_we(mem_we),.mem_wdata(mem_wdata),
            .mem_rdata(mem_rdata),.mem_ready(mem_ready));
    end endgenerate

    cpu_line_memory #(.LATENCY(MEM_LATENCY),.PROG_FILE(PROG_FILE),.DATA_FILE(DATA_FILE)) u_memory (
        .clk(clk),.rst(rst),.addr(mem_addr),.re(mem_re),.we(mem_we),
        .wdata(mem_wdata),.rdata(mem_rdata),.ready(mem_ready));

    always @(posedge clk) begin
        if (rst) begin
            state <= FETCH_REQ;
            instruction <= 0;
            load_data <= 0;
            io_out <= 0;
        end else if (!halted) begin
            case (state)
                FETCH_REQ: state <= FETCH_WAIT;
                FETCH_WAIT: if (ready) begin
                    instruction <= cache_rdata[15:0];
                    state <= DATA_REQ;
                end
                DATA_REQ: begin
                    if ((is_load || is_store) && normal_memory) state <= DATA_WAIT;
                    else begin
                        load_data <= output_port ? io_out : 16'd0;
                        state <= COMMIT;
                    end
                end
                DATA_WAIT: if (ready) begin
                    load_data <= cache_rdata[15:0];
                    state <= COMMIT;
                end
                COMMIT: begin
                    if (is_store && output_port) io_out <= data_write;
                    state <= FETCH_REQ;
                end
                default: state <= FETCH_REQ;
            endcase
        end
    end
endmodule
