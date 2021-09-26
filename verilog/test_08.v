module test_08 (N1, N2, N3, N4, N5, N23, N24);

input N1; 
input N2; 
input N3; 
input N4; 
input N5; 

output N23; 
output N24; 

wire N6; 
wire N7; 
wire N8; 
wire N9; 
wire N10; 
wire N11; 
wire N12; 
wire N13; 
wire N14; 
wire N15; 
wire N16; 
wire N17; 
wire N18; 
wire N19; 
wire N20; 
wire N21; 
wire N22; 

assign N6 = ~(N1); 
assign N7 = ~(N2); 
assign N8 = N3 & N2; 
assign N9 = ~(N3); 
assign N10 = ~(N8); 
assign N11 = ~(N3); 
assign N12 = ~(N7); 
assign N13 = ~(N11); 
assign N14 = ~(N1); 
assign N15 = N2 | N1; 
assign N16 = ~(N12); 
assign N17 = ~(N8); 
assign N18 = ~(N6); 
assign N19 = N6 & N2; 
assign N20 = N13 & N15 & N17 & N18; 
assign N21 = N12 & N13; 
assign N22 = N4 | N5 | N7 | N10 | N11 | N13; 
assign N23 = N14 & N16 & N18 & N19 & N20; 
assign N24 = N9 | N21 | N22; 
endmodule
