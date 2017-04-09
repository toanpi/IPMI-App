#!/usr/bin/expect

set timeout 20
set cmd0 [lindex $argv 0]
set cmd1 [lindex $argv 1]
set cmd2 [lindex $argv 2]
exp_spawn scp $cmd0 $cmd1
expect "password:"
send "$cmd2\r";
interact
