module test_06 (N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N19, N20, N21, N22, N23, N24, N25, N26, N27, N28, N29, N30, N31, N32, N33);

input N1; 
input N2; 
input N3; 
input N4; 
input N5; 
input N6; 
input N7; 
input N8; 
input N9; 
input N10; 

output N19; 
output N20; 
output N21; 
output N22; 
output N23; 
output N24; 
output N25; 
output N26; 
output N27; 
output N28; 
output N29; 
output N30; 
output N31; 
output N32; 
output N33; 

wire N11; 
wire N12; 
wire N13; 
wire N14; 
wire N15; 
wire N16; 
wire N17; 
wire N18; 

assign N11 = ~(N3); 
assign N12 = N8 & N10 & N4; 
assign N13 = ~(N8); 
assign N14 = ~(N10); 
assign N15 = N6 & N2; 
assign N16 = N5 & N9; 
assign N17 = N4 & N5; 
assign N18 = ~(N1); 
assign N19 = N3 | N16 | N11 | N2 | N5 | N14 | N18 | N17 | N9; 
assign N20 = N13 & N6 & N16 & N5 & N15 & N3 & N14 & N11 & N7; 
assign N21 = ~(N18); 
assign N22 = N11 & N14; 
assign N23 = ~(N1); 
assign N24 = ~(N17); 
assign N25 = ~(N13); 
assign N26 = N18 & N2 & N4 & N3 & N7 & N13 & N14 & N12 & N5; 
assign N27 = N5 & N16 & N10 & N15 & N14 & N12 & N18 & N6 & N7; 
assign N28 = ~(N16); 
assign N29 = N2 | N3 | N12; 
assign N30 = ~(N15); 
assign N31 = N8 | N16 | N18 | N2 | N1 | N12 | N3 | N4 | N9; 
assign N32 = N12 & N10 & N16 & N11 & N2 & N6 & N4 & N1 & N13; 
assign N33 = ~(N7); 
endmodule
