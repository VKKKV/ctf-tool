import sys

import angr
import claripy
from pwn import *
from pwn import process

binary_path = "/home/kita/Downloads/Vital Signs/Vital_Signs/vault"

project = angr.Project(binary_path, auto_load_libs=False)

# 2. 构造符号化输入 (Symbolic Argument)
# 假设 passphrase 的长度最大为 37 字节 (37 * 8 bits)。如果不够，可以往上加。
arg_len = 37
# BVS = BitVector Symbolic (创建一个符号化的比特向量)
sym_arg = claripy.BVS("passphrase", arg_len * 8)

# 3. 初始化程序状态 (Initialize entry state)
# argv[0] 是程序名, argv[1] 是我们的符号化参数
initial_state = project.factory.entry_state(args=[binary_path, sym_arg])

for i in range(arg_len):
    initial_state.solver.add(sym_arg.get_byte(i) >= 0x20)
    initial_state.solver.add(sym_arg.get_byte(i) <= 0x7e)

simulation = project.factory.simulation_manager(initial_state)

def is_successful(state):
    stdout_output = state.posix.dumps(1)
    return b"Correct!" in stdout_output


def should_abort(state):
    stdout_output = state.posix.dumps(1)
    return b"Wrong." in stdout_output


simulation.explore(find=is_successful, avoid=should_abort)

if simulation.found:
    solution_state = simulation.found[0]
    res = solution_state.solver.eval(sym_arg, cast_to=bytes)
    print(res)
    print(len(res))
else:
    raise Exception("Could not find the solution")
