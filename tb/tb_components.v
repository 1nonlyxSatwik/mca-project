`timescale 1ns/1ps
module tb_components;
 reg clk=0,rst=1,en=0,branch=0,we=0,access=0;
 always #5 clk=~clk;
 reg [5:0] target=0,addr=0;
 wire [5:0] pc;
 reg [2:0] wa=0,ra=0,rb=0;
 reg [15:0] wd=0;
 wire [15:0] da,db;
 wire mem,io,err;
 integer i;
 program_counter p(.clk(clk),.rst(rst),.en(en),.branch_taken(branch),.branch_target(target),.pc(pc));
 register_file r(.clk(clk),.rst(rst),.we(we),.waddr(wa),.wdata(wd),.raddr1(ra),.raddr2(rb),.rdata1(da),.rdata2(db));
 address_decoder d(.addr(addr),.access(access),.sel_mem(mem),.sel_io(io),.addr_err(err));
 task tick;begin @(posedge clk);#1;end endtask
 initial begin
  tick;if(pc!==0 || da!==0 || db!==0)$fatal(1,"Reset failed");
  @(negedge clk);rst=0;en=1;tick;if(pc!==1)$fatal(1,"PC increment failed");
  @(negedge clk);en=0;tick;if(pc!==1)$fatal(1,"PC stall hold failed");
  @(negedge clk);en=1;branch=1;target=63;tick;if(pc!==63)$fatal(1,"Branch failed");
  @(negedge clk);branch=0;tick;if(pc!==0)$fatal(1,"PC wraparound failed");
  @(negedge clk);en=0;we=1;wa=0;wd=16'hffff;tick;if(da!==0)$fatal(1,"R0 writable");
  for(i=1;i<8;i=i+1)begin
   @(negedge clk);wa=i;wd=16'h1234+i;ra=i;rb=0;tick;
   if(da!==16'h1234+i || db!==0)$fatal(1,"Register ports failed");
  end
  for(i=0;i<64;i=i+1)begin
   addr=i;access=1;#1;
   if(mem!==(i<48) || io!==(i==63) || err!==((i>=48)&&(i<63)))$fatal(1,"Decoder failed address=%0d",i);
   access=0;#1;if(err!==0)$fatal(1,"Spurious error without access");
  end
  @(negedge clk);rst=1;tick;if(pc!==0 || da!==0)$fatal(1,"Repeated reset failed");
  $display("PASS components: PC increment/hold/branch/wrap/reset, R0-R7, all 64 decoder addresses");
  $finish;
 end
endmodule
