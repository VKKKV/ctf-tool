#!/usr/bin/env python3
"""
x86 Emulation Script using Unicorn Engine
Used to extract flag characters pushed onto the stack during execution.
"""

import sys
from unicorn import *
from unicorn.x86_const import *

# Configuration
CODE_FILE = '../../../Downloads/message.txt'
BASE_ADDRESS = 0x1000000
STACK_ADDRESS = 0x2000000
MEM_SIZE = 2 * 1024 * 1024  # 2MB

# Global storage for the extracted flag
flag_chars = []

def hook_code(uc, address, size, user_data):
    """Optional: Trace instructions for debugging."""
    # eax = uc.reg_read(UC_X86_REG_EAX)
    # print(f">>> Tracing instruction at 0x{address:x}, EAX = 0x{eax:x}")
    pass

def hook_mem_write(uc, access, address, size, value, user_data):
    """
    Monitor memory writes to catch PUSH instructions.
    In many CTF challenges, characters are pushed onto the stack one by one.
    """
    if access == UC_MEM_WRITE:
        try:
            char = chr(value)
            if char.isprintable():
                flag_chars.append(char)
                print(f"[!] Stack Push: '{char}' (0x{value:02x})")
        except Exception:
            pass

def main():
    # Load the shellcode/binary
    try:
        with open(CODE_FILE, 'rb') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: {CODE_FILE} not found.")
        sys.exit(1)

    print(f"Emulating x86 code ({len(code)} bytes)...")

    try:
        # Initialize emulator in x86 32-bit mode
        mu = Uc(UC_ARCH_X86, UC_MODE_32)

        # Map memory for code and stack
        mu.mem_map(BASE_ADDRESS, MEM_SIZE)
        mu.mem_map(STACK_ADDRESS, MEM_SIZE)

        # Write code to memory
        mu.mem_write(BASE_ADDRESS, code)

        # Initialize registers
        mu.reg_write(UC_X86_REG_EAX, 0x0)
        # Set stack pointer to the middle of the mapped stack region
        mu.reg_write(UC_X86_REG_ESP, STACK_ADDRESS + (MEM_SIZE // 2))

        # Add hooks
        mu.hook_add(UC_HOOK_CODE, hook_code)
        mu.hook_add(UC_HOOK_MEM_WRITE, hook_mem_write)

        # Execute the code
        mu.emu_start(BASE_ADDRESS, BASE_ADDRESS + len(code))

    except UcError as e:
        # Emulation often ends with an error when shellcode runs off the end 
        # or lacks a proper exit syscall, which is expected.
        print(f"\nEmulation stopped: {e}")

    # Output the results
    if flag_chars:
        print("\n" + "="*20)
        print(f"Extracted Flag: {''.join(flag_chars)}")
        print("="*20)
    else:
        print("\nNo printable characters captured from stack writes.")

if __name__ == '__main__':
    main()
