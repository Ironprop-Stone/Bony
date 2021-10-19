rm ./verilog/*
rm ./syn_verilog/*
rm ./syn_bench/*

~/opt/pypy3.7-v7.3.5-linux64/bin/pypy3 ./top.py
yosys run.tcl
~/opt/pypy3.7-v7.3.5-linux64/bin/pypy3 ./vabc2bench.py

