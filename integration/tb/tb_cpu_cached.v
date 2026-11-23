`timescale 1ns/1ps
// Independent architectural interpreter checks EVERY retired instruction and all
// registers, PC, HALT, output and address-error behavior, not only final values.
module tb_cpu_cached;
    parameter CACHE_KIND=1, PROG_NUM=1, MEM_LATENCY=3;
    localparam PROG_FILE = PROG_NUM==1 ? "programs/prog1.hex" :
                          PROG_NUM==2 ? "programs/prog2.hex" :
                          PROG_NUM==3 ? "programs/prog3.hex" :
                          PROG_NUM==4 ? "programs/prog4.hex" :
                          PROG_NUM==5 ? "programs/prog5.hex" : "programs/prog6.hex";
    localparam DATA_FILE = PROG_NUM==1 ? "programs/prog1_data.hex" :
                          PROG_NUM==2 ? "programs/prog2_data.hex" :
                          PROG_NUM==3 ? "programs/prog3_data.hex" :
                          PROG_NUM==4 ? "programs/prog4_data.hex" :
                          PROG_NUM==5 ? "programs/prog5_data.hex" : "programs/prog6_data.hex";
    reg clk=0, rst=1;
    always #5 clk=~clk;
    wire halted, addr_err, retire, request, done;
    wire [15:0] io_out, instruction;
    wire [5:0] pc;
    cpu_cached_top #(.CACHE_KIND(CACHE_KIND),.MEM_LATENCY(MEM_LATENCY),
        .PROG_FILE(PROG_FILE),.DATA_FILE(DATA_FILE)) dut (
        .clk(clk),.rst(rst),.halted(halted),.io_out(io_out),.addr_err(addr_err),
        .retired_pc(pc),.retired_instr(instruction),.retire(retire),
        .cache_request(request),.cache_done(done));
    reg [15:0] golden_mem [0:63];
    reg [15:0] golden_regs [0:7];
    reg [5:0] golden_pc;
    reg [15:0] golden_io;
    reg golden_halt;
    reg [15:0] ins, value;
    reg [5:0] address;
    integer i, op, rd, rs1, rs2, imm;
    integer cycles=0, retired=0, requests=0, responses=0;
    integer expected_retired;
    always @(posedge clk) if (!rst && !halted) begin
        cycles=cycles+1;
        if (request) requests=requests+1;
        if (done) responses=responses+1;
        if (retire) begin
            ins=golden_mem[golden_pc];
            if (pc !== golden_pc || instruction !== ins)
                $fatal(1,"Fetch mismatch pc=%h expected=%h instruction=%h expected=%h",pc,golden_pc,instruction,ins);
            op=ins[15:12];rd=ins[11:9];rs1=ins[8:6];rs2=ins[5:3];imm=ins[5:0];
            address=(golden_regs[rs1]+imm)&63;
            if (addr_err !== ((op==2 || op==3) && address>=48 && address<63))
                $fatal(1,"Address error flag mismatch");
            golden_pc=(golden_pc+1)&63;
            case(op)
                1: if(rd!=0) golden_regs[rd]=golden_regs[rs1]+golden_regs[rs2];
                2: if(rd!=0) golden_regs[rd]= address<48 ? golden_mem[address] : address==63 ? golden_io : 0;
                3: begin
                    if(address<48) golden_mem[address]=golden_regs[rd];
                    if(address==63) golden_io=golden_regs[rd];
                end
                4: if(rd!=0) golden_regs[rd]=golden_regs[rs1]-golden_regs[rs2];
                5: if(rd!=0) golden_regs[rd]=golden_regs[rs1]+imm;
                6: if(golden_regs[rs1]==golden_regs[rd]) golden_pc=imm;
                7: golden_pc=imm;
                default: begin golden_halt=1;golden_pc=pc;end
            endcase
            retired=retired+1;
            #1;
            for(i=0;i<8;i=i+1)
                if(dut.u_cpu.u_rf.regs[i] !== golden_regs[i])
                    $fatal(1,"Register mismatch R%0d got=%h expected=%h",i,dut.u_cpu.u_rf.regs[i],golden_regs[i]);
            if(pc !== golden_pc || io_out !== golden_io || halted !== golden_halt)
                $fatal(1,"Architectural PC/IO/HALT mismatch");
        end
    end
    initial begin
        golden_pc=0;golden_io=0;golden_halt=0;
        for(i=0;i<64;i=i+1) golden_mem[i]=0;
        for(i=0;i<8;i=i+1) golden_regs[i]=0;
        $readmemh(PROG_FILE,golden_mem);$readmemh(DATA_FILE,golden_mem);
        repeat(3) @(negedge clk);
        rst=0;
        while(!halted && cycles<10000) @(negedge clk);
        if(!halted) $fatal(1,"Cached CPU timed out");
        case(PROG_NUM)
            1: expected_retired=5;
            2,3,6: expected_retired=4;
            4: expected_retired=23;
            5: expected_retired=12;
        endcase
        if(retired!=expected_retired || requests!=responses)
            $fatal(1,"Retirement or request/response count mismatch retired=%0d expected=%0d req=%0d ack=%0d",retired,expected_retired,requests,responses);
        $display("RESULT integrated %0d prog%0d latency=%0d cycles=%0d retired=%0d requests=%0d PASS",CACHE_KIND,PROG_NUM,MEM_LATENCY,cycles,retired,requests);
        repeat(4) @(negedge clk);
        if(request || retire || !halted) $fatal(1,"HALT did not quiesce CPU bridge");
        $finish;
    end
endmodule
