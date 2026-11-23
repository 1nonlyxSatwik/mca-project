`timescale 1ns / 1ps
// Program counter: holds the address of the current instruction.
// Moves to branch_target when branch_taken is 1, otherwise advances +1 on each
// rising clock edge when `en` is 1. The CPU sets en = 0 during a stall or after HALT.
module program_counter (
    input            clk,
    input            rst,           // synchronous, active high: PC -> 0
    input            en,            // 1 = update PC
    input            branch_taken,  // 1 = branch/jump taken
    input      [5:0] branch_target, // destination address
    output reg [5:0] pc
);
    always @(posedge clk) begin
        if (rst)
            pc <= 6'd0;
        else if (en) begin
            if (branch_taken)
                pc <= branch_target;
            else
                pc <= pc + 6'd1;
        end
    end
endmodule
