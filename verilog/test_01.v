module test_01 (N1, N2, N3, N4, N13, N14, N15, N16, N17);

input N1; 
input N2; 
input N3; 
input N4; 

output N13; 
output N14; 
output N15; 
output N16; 
output N17; 

wire N5; 
wire N6; 
wire N7; 
wire N8; 
wire N9; 
wire N10; 
wire N11; 
wire N12; 

assign N5 = ~(N1); 
assign N6 = ~(N4); 
assign N7 = N4 & N3; 
assign N8 = ~(N1); 
assign N9 = ~(N2); 
assign N10 = ~(N7); 
assign N11 = ~(N4); 
assign N12 = N5 & N6; 
assign N13 = ~(N12); 
assign N14 = N7 & N8; 
assign N15 = N1 | N3; 
assign N16 = ~(N9); 
assign N17 = N10 & N11; 
endmodule
