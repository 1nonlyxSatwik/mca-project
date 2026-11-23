`timescale 1ns/1ps
// 64 CPU words, packed into 16 cache lines; configurable response latency.
// RAM is initialized once. Reset aborts a pending transaction, not RAM contents.
module cpu_line_memory #(
    parameter LATENCY=3,
    parameter PROG_FILE="programs/prog1.hex",
    parameter DATA_FILE="programs/prog1_data.hex"
) (
    input clk, input rst, input [31:0] addr, input re, input we,
    input [127:0] wdata, output reg [127:0] rdata, output reg ready
);
    reg [15:0] boot [0:63];
    reg [127:0] lines [0:15];
    reg busy, write_pending;
    reg [3:0] line_addr;
    reg [127:0] saved_write;
    integer remaining, i, j;
    initial begin
        for (i=0;i<64;i=i+1) boot[i]=0;
        $readmemh(PROG_FILE,boot);
        $readmemh(DATA_FILE,boot);
        for (i=0;i<16;i=i+1)
            for (j=0;j<4;j=j+1) lines[i][j*32 +: 32]={16'd0,boot[i*4+j]};
    end
    always @(posedge clk) begin
        if (rst) begin
            busy<=0; ready<=0; rdata<=0; remaining<=0;
            line_addr<=0; saved_write<=0; write_pending<=0;
        end else begin
            ready<=0;
            if (busy) begin
                if (remaining==1) begin
                    if (write_pending) lines[line_addr]<=saved_write;
                    else rdata<=lines[line_addr];
                    ready<=1; busy<=0;
                end else remaining<=remaining-1;
            end else if (!ready && (re || we)) begin
                busy<=1; line_addr<=addr[7:4]; saved_write<=wdata;
                write_pending<=we; remaining<=LATENCY;
            end
        end
    end
endmodule
