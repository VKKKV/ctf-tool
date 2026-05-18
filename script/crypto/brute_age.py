#!/usr/bin/env python3
"""Multi-process age passphrase brute-force against ~/en.txt using rockyou.txt"""
import subprocess
import sys
import os
from multiprocessing import Process, Queue, cpu_count
from pathlib import Path

ENC_FILE = os.path.expanduser("~/en.txt")
DICT_FILE = os.path.expanduser("~/ctf/tool/dict/rockyou.txt")
PROCS = max(cpu_count() - 1, 1)  # leave one core free
CHUNK_SIZE = 2000  # passwords per worker per batch

def try_passwords(passwords, worker_id, result_q):
    """Try a list of passwords against the age file."""
    for pwd in passwords:
        pwd = pwd.strip()
        if not pwd:
            continue
        try:
            r = subprocess.run(
                ["age", "-d", ENC_FILE],
                input=pwd + "\n",
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
            if r.returncode == 0:
                result_q.put(("FOUND", worker_id, pwd, r.stdout))
                return
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    result_q.put(("CHUNK_DONE", worker_id, None, None))


def main():
    print(f"Encrypted file: {ENC_FILE}", flush=True)
    print(f"Dictionary:     {DICT_FILE}", flush=True)
    print(f"Workers:        {PROCS}", flush=True)
    print(f"Chunk size:     {CHUNK_SIZE}", flush=True)
    print(flush=True)

    if not Path(ENC_FILE).exists():
        print(f"ERROR: {ENC_FILE} not found")
        sys.exit(1)
    if not Path(DICT_FILE).exists():
        print(f"ERROR: {DICT_FILE} not found")
        sys.exit(1)

    result_q = Queue()

    with open(DICT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        batch_num = 0
        tested = 0

        while True:
            chunk = []
            for _ in range(CHUNK_SIZE * PROCS):
                line = f.readline()
                if not line:
                    break
                chunk.append(line)
            if not chunk:
                break

            # Split chunk among workers
            per_worker = len(chunk) // PROCS + 1
            workers = []
            for i in range(PROCS):
                start = i * per_worker
                end = start + per_worker
                subchunk = chunk[start:end]
                if not subchunk:
                    continue
                p = Process(target=try_passwords, args=(subchunk, i, result_q))
                p.start()
                workers.append(p)

            # Wait for all workers in this batch
            for p in workers:
                p.join()

            batch_num += 1
            tested += len(chunk)

            # Check results
            while not result_q.empty():
                status, wid, pwd, output = result_q.get()
                if status == "FOUND":
                    print(f"\n✅ PASSWORD FOUND by worker {wid}: {pwd}")
                    print(f"Decrypted content:\n{output}")
                    # Kill remaining workers and exit
                    for p in workers:
                        p.terminate()
                    return

            print(f"  Batch {batch_num}: tested {tested:,} passwords...", end="\r", flush=True)

    print(f"\n❌ Password not found after testing {tested:,} entries.")


if __name__ == "__main__":
    main()
