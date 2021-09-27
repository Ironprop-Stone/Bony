rm ./verilog/*
rm ./syn_verilog/*
rm ./syn_bench/*

pypy3 ./top.py
yosys run.tcl
pypy3 ./v2bench.py

