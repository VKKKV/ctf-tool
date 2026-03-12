#!/usr/bin/env python3
"""
Angr CTF Solving Template & Cheat Sheet
Author: Kita (Optimized)
"""

import logging
import sys

import angr
import claripy

# Disable overly verbose logging
logging.getLogger("angr").setLevel(logging.CRITICAL)


def setup_project(bin_path):
    """Initializes the angr project and basic objects."""
    proj = angr.Project(bin_path, auto_load_libs=False)

    # Useful project attributes
    # arch = proj.arch
    # entry = proj.entry
    # obj = proj.loader.main_object
    # functions = proj.kb.functions

    return proj


def basic_solve(bin_path, find_addr, avoid_addr=None):
    """
    A standard template for basic find/avoid exploration.
    """
    proj = setup_project(bin_path)

    # Create the initial state (often entry_state or blank_state)
    state = proj.factory.entry_state()

    # Create the simulation manager
    simgr = proj.factory.simulation_manager(state)

    # Explore the binary for the find/avoid addresses
    simgr.explore(find=find_addr, avoid=avoid_addr)

    if simgr.found:
        solution_state = simgr.found[0]
        # Example: if flag is read from stdin
        # print(solution_state.posix.dumps(0))
        return solution_state
    else:
        print("[-] No solution found.")
        return None


def snippets_cheat_sheet():
    """
    Collection of useful angr/claripy snippets for reference.
    This function is not intended to be run as-is.
    """
    # --- Loading & Objects ---
    # proj.loader.find_symbol("strcmp")
    # proj.loader.shared_objects
    # hex(proj.loader.min_addr), hex(proj.loader.max_addr)

    # --- Factory & Blocks ---
    # block = proj.factory.block(proj.entry)
    # block.pp()  # Pretty print disassembly
    # print(block.instructions, block.instruction_addrs)
    # print(block.capstone)  # Capstone disassembly
    # print(block.vex)      # VEX IRSB

    # --- State Management ---
    # state = proj.factory.entry_state()
    # state.regs.rax, state.regs.rip, state.regs.rsp
    # state.mem[addr].long = value
    # value = state.mem[addr].int.resolved  # bitvector
    # value = state.mem[addr].int.concrete  # python int

    # --- Claripy (Bitvectors) ---
    # bvv = claripy.BVV(0xDEADBEEF, 32)  # Concrete bitvector value
    # bvs = claripy.BVS("flag", 8 * 32)  # Symbolic bitvector (32 bytes)
    # bvv_extended = bvv.zero_extend(32) # Extend 32-bit to 64-bit

    # --- Constraints & Solver ---
    # state.add_constraints(state.regs.rax == 0x1337)
    # if state.satisfiable():
    #     val = state.solver.eval(bvs, cast_to=bytes)

    pass


# tcp://0c4c28058a1f7a2f.247ctf.com:50230
# nc 0c4c28058a1f7a2f.247ctf.com 50230
def mysolve(bin_path):
    path_to_binary = bin_path  # :string
    project = angr.Project(path_to_binary)
    initial_state = project.factory.entry_state(
        add_options={
            angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
            angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS,
        }
    )
    simulation = project.factory.simgr(initial_state)

    simulation.explore(find=0x08048596, avoid=0x8048609)
    if simulation.found:
        solution_state = simulation.found[0]
        print(solution_state.posix.dumps(sys.stdin.fileno()).decode())
    else:
        raise Exception("Could not find the solution")


def main():
    # Default path from original script
    bin_path = "/home/kita/Downloads/angr-y_binary"
    print(f"[*] Angr template loaded. Target: {bin_path}")
    mysolve(bin_path)

    # To use:
    # find_addr = 0x400000
    # solve_state = basic_solve(bin_path, find_addr)
    # if solve_state:
    #     print(solve_state.posix.dumps(0))


if __name__ == "__main__":
    main()
