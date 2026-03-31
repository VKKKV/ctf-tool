from pwn import *

context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"

p = gdb.debug(
    "/challenge/can-it-fizz",
    env={"SHELL": "/bin/bash"},
    gdbscript="""
b * challenge+360
continue
ni
""",
)

p.sendline(b"1")

p.send(cyclic(74))

p.interactive()
