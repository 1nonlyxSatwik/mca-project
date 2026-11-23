`timescale 1ns/1ps
// New integration verification: all four words, dirty conflicts, read-after-write,
// and deterministic mixed workloads at multiple backing-memory latencies.
module tb_cache_word_stress;
 parameter LATENCY=3;
 reg clk=0,rst_n=0,re=0,we=0;
 always #5 clk=~clk;
 reg [31:0] addr=0,wdata=0;
 wire [31:0] dr,sr,dma,sma;
 wire dready,sready,dmre,dmwe,smre,smwe,dmready,smready;
 wire [127:0] dmwd,smwd,dmrd,smrd;
 direct_mapped_cache dm(.clk(clk),.rst_n(rst_n),.cpu_addr(addr),.cpu_wdata(wdata),.cpu_re(re),.cpu_we(we),.cpu_rdata(dr),.cpu_ready(dready),.mem_addr(dma),.mem_re(dmre),.mem_we(dmwe),.mem_wdata(dmwd),.mem_rdata(dmrd),.mem_ready(dmready));
 cache_2way_top sa(.clk(clk),.rst_n(rst_n),.cpu_addr(addr),.cpu_wdata(wdata),.cpu_re(re),.cpu_we(we),.cpu_rdata(sr),.cpu_ready(sready),.mem_addr(sma),.mem_re(smre),.mem_we(smwe),.mem_wdata(smwd),.mem_rdata(smrd),.mem_ready(smready));
 mem_model #(.LATENCY(LATENCY)) md(.clk(clk),.rst_n(rst_n),.mem_addr(dma),.mem_re(dmre),.mem_we(dmwe),.mem_wdata(dmwd),.mem_rdata(dmrd),.mem_ready(dmready));
 mem_model #(.LATENCY(LATENCY)) ms(.clk(clk),.rst_n(rst_n),.mem_addr(sma),.mem_re(smre),.mem_we(smwe),.mem_wdata(smwd),.mem_rdata(smrd),.mem_ready(smready));
 reg [31:0] golden[0:16383];
 integer i,j,ops=0;
 task access_word;
  input wr;
  input [31:0] a,d;
  reg dd,sd;
  integer timeout;
  begin
   dd=0;sd=0;timeout=0;
   @(negedge clk);addr=a;wdata=d;we=wr;re=!wr;
   @(negedge clk);we=0;re=0;
   while(!(dd&&sd) && timeout<1000) begin
    if(dready && !dd)begin
     dd=1;if(!wr && dr!==golden[a>>2])$fatal(1,"DM word mismatch addr=%h",a);
    end
    if(sready && !sd)begin
     sd=1;if(!wr && sr!==golden[a>>2])$fatal(1,"2WAY word mismatch addr=%h",a);
    end
    timeout=timeout+1;@(negedge clk);
   end
   if(!(dd&&sd))$fatal(1,"Cache stress timeout");
   if(wr)golden[a>>2]=d;
   ops=ops+1;
   repeat(2)@(negedge clk);
  end
 endtask
 initial begin
  for(i=0;i<16384;i=i+1)golden[i]={16'ha5a5,16'(i/4)};
  repeat(4)@(negedge clk);rst_n=1;
  for(i=0;i<4;i=i+1)access_word(1,i*4,32'hcafe0000+i);
  for(i=0;i<4;i=i+1)access_word(0,i*4,0);
  // Three tags in set zero force eviction even with two ways.
  for(i=1;i<4;i=i+1)access_word(1,i*2048,32'hfeed0000+i);
  for(i=0;i<4;i=i+1)access_word(0,i*4,0);
  for(i=1;i<4;i=i+1)access_word(0,i*2048,0);
  for(i=0;i<256;i=i+1)begin
   access_word(1,((i*337)%16384)*4,32'h12340000+i);
   access_word(0,((i*337)%16384)*4,0);
  end
  // Revisit written words after capacity pressure, checking backing writeback.
  for(i=0;i<256;i=i+1)access_word(0,((i*337)%16384)*4,0);
  $display("PASS cache_word_stress latency=%0d operations=%0d zero mismatches",LATENCY,ops);
  $finish;
 end
endmodule
