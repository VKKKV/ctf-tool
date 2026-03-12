#!/usr/bin/env python3

import logging
import sys

import angr
import claripy

logging.getLogger("angr").setLevel(logging.CRITICAL)
logging.getLogger("cle").setLevel(logging.CRITICAL)


def mysolve(bin_path):
    path_to_binary = bin_path
    project = angr.Project(path_to_binary, auto_load_libs=False)

    initial_state = project.factory.entry_state(
        add_options={
            angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
            angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS,
        }
    )

    simulation = project.factory.simgr(initial_state)
    simulation.explore(find=0x410270, avoid=0x403129)

    if simulation.found:
        solution_state = simulation.found[0]
        print(solution_state.posix.dumps(sys.stdin.fileno()).decode())
    else:
        raise Exception("Could not find the solution")


def main():
    # Default path from original script
    bin_path = "/home/kita/Downloads/flag_errata.exe"
    print(f"[*] Target: {bin_path}")
    mysolve(bin_path)


if __name__ == "__main__":
    main()
