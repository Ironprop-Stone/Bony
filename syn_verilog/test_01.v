/* Generated by Yosys 0.9+4272 (git sha1 10f8b75d, gcc 5.5.0-12ubuntu1~16.04 -fPIC -Os) */

(* top =  1  *)
(* src = "./verilog/test_01.v:1.1-36.10" *)
module test_01(N1, N2, N3, N4, N13, N14, N15, N16, N17);
  wire _00_;
  (* src = "./verilog/test_01.v:3.7-3.9" *)
  wire _01_;
  (* src = "./verilog/test_01.v:8.8-8.11" *)
  wire _02_;
  (* src = "./verilog/test_01.v:9.8-9.11" *)
  wire _03_;
  (* src = "./verilog/test_01.v:10.8-10.11" *)
  wire _04_;
  (* src = "./verilog/test_01.v:12.8-12.11" *)
  wire _05_;
  (* src = "./verilog/test_01.v:5.7-5.9" *)
  wire _06_;
  (* src = "./verilog/test_01.v:6.7-6.9" *)
  wire _07_;
  wire _08_;
  wire _09_;
  (* src = "./verilog/test_01.v:3.7-3.9" *)
  input N1;
  (* src = "./verilog/test_01.v:8.8-8.11" *)
  output N13;
  (* src = "./verilog/test_01.v:9.8-9.11" *)
  output N14;
  (* src = "./verilog/test_01.v:10.8-10.11" *)
  output N15;
  (* src = "./verilog/test_01.v:11.8-11.11" *)
  output N16;
  (* src = "./verilog/test_01.v:12.8-12.11" *)
  output N17;
  (* src = "./verilog/test_01.v:4.7-4.9" *)
  input N2;
  (* src = "./verilog/test_01.v:5.7-5.9" *)
  input N3;
  (* src = "./verilog/test_01.v:6.7-6.9" *)
  input N4;
  NOT _10_ (
    .A(_01_),
    .Y(_09_)
  );
  NOT _11_ (
    .A(_07_),
    .Y(_05_)
  );
  OR _12_ (
    .A(_01_),
    .B(_07_),
    .Y(_02_)
  );
  AND _13_ (
    .A(_07_),
    .B(_06_),
    .Y(_08_)
  );
  AND _14_ (
    .A(_09_),
    .B(_08_),
    .Y(_03_)
  );
  OR _15_ (
    .A(_01_),
    .B(_06_),
    .Y(_04_)
  );
  assign N16 = N2;
  assign _01_ = N1;
  assign _07_ = N4;
  assign N13 = _02_;
  assign _06_ = N3;
  assign N17 = _05_;
  assign N14 = _03_;
  assign N15 = _04_;
endmodule
