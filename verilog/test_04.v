module test_04 (N1, N2, N3, N4, N5, N6, N7, N36, N37);

input N1; 
input N2; 
input N3; 
input N4; 
input N5; 
input N6; 
input N7; 

output N36; 
output N37; 

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
wire N23; 
wire N24; 
wire N25; 
wire N26; 
wire N27; 
wire N28; 
wire N29; 
wire N30; 
wire N31; 
wire N32; 
wire N33; 
wire N34; 
wire N35; 

assign N8 = N1 & N5; 
assign N9 = ~(N7); 
assign N10 = ~(N3); 
assign N11 = ~(N4); 
assign N12 = ~(N7); 
assign N13 = ~(N4); 
assign N14 = N8 | N3; 
assign N15 = N3 & N9; 
assign N16 = ~(N2); 
assign N17 = N5 | N6; 
assign N18 = N13 | N16 | N4; 
assign N19 = N9 & N3; 
assign N20 = ~(N13); 
assign N21 = ~(N10); 
assign N22 = N14 & N15; 
assign N23 = N2 | N6 | N19; 
assign N24 = N12 | N13; 
assign N25 = ~(N19); 
assign N26 = N19 & N23 & N17; 
assign N27 = ~(N20); 
assign N28 = N7 & N23; 
assign N29 = ~(N1); 
assign N30 = N26 & N17; 
assign N31 = ~(N25); 
assign N32 = N24 | N5; 
assign N33 = ~(N26); 
assign N34 = N11 & N20 & N13; 
assign N35 = N10 & N25 & N27 & N22; 
assign N36 = N4 | N17 | N18 | N29 | N30 | N31 | N32 | N34; 
assign N37 = N15 & N21 & N22 & N28 & N33 & N35; 
endmodule