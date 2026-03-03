# 🛠️ File Magic Numbers Reference

A quick reference guide for common file signatures (Magic Numbers) often encountered in CTFs, forensics, and daily Arch Linux life.

---

### 💻 核心系统与可执行文件 (Executables & Scripts)

| Format | Magic Number (Hex) | ASCII / Note |
| :--- | :--- | :--- |
| **ELF** | `7F 45 4C 46` | `.ELF` (Linux Executable) |
| **PE (EXE/DLL)** | `4D 5A` | `MZ` (Windows Portable Executable) |
| **Mach-O (32-bit)**| `CF FA ED FE` | macOS Executable |
| **Mach-O (64-bit)**| `FE ED FA CF` | macOS Executable |
| **Mach-O (Fat)** | `CA FE BA BE` | macOS Multi-architecture binary |
| **Java Class** | `CA FE BA BE` | Compiled Java bytecode |
| **Shebang** | `23 21` | `#!` (Script interpreter directive) |

---

### 📦 归档与压缩 (Archives & Compression)

| Format | Magic Number (Hex) | ASCII / Note |
| :--- | :--- | :--- |
| **Zstandard (.zst)**| `28 B5 2F FD` | Modern Arch Linux `pacman` default |
| **XZ (.xz)** | `FD 37 7A 58 5A 00` | `.7zXZ.` |
| **Gzip (.gz)** | `1F 8B` | Classic Unix compression |
| **Bzip2 (.bz2)** | `42 5A 68` | `BZh` |
| **ZIP (.zip)** | `50 4B 03 04` | `PK..` (Phil Katz) |
| **7z (.7z)** | `37 7A BC AF 27 1C` | `7z..'` |
| **RAR (v4.x)** | `52 61 72 21 1A 07 00` | `Rar!...` |
| **RAR (v5.0)** | `52 61 72 21 1A 07 01 00` | `Rar!....` |
| **Tar (.tar)** | `75 73 74 61 72` | `ustar` (at offset `0x101`) |

---

### 🎨 常见数据与多媒体 (Data & Media)

| Format | Magic Number (Hex) | ASCII / Note |
| :--- | :--- | :--- |
| **PDF** | `25 50 44 46 2D` | `%PDF-` |
| **PNG** | `89 50 4E 47 0D 0A 1A 0A`| `.PNG....` (Built-in corruption check) |
| **JPEG** | `FF D8 FF` | Start of Image (SOI) |
| **GIF** | `47 49 46 38 39 61` | `GIF89a` (or `37 61` for `GIF87a`) |
| **BMP** | `42 4D` | `BM` (Windows Bitmap) |
| **WebP** | `52 49 46 46` | `RIFF` (Header starts with WebP at `0x08`) |

---

### 📄 数据库与文档 (Data & Documents)

| Format | Magic Number (Hex) | ASCII / Note |
| :--- | :--- | :--- |
| **SQLite 3** | `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00` | `SQLite format 3.` |
| **RTF** | `7B 5C 72 74 66 31` | `{\rtf1` |
| **MS Office** | `D0 CF 11 E0 A1 B1 1A E1` | Legacy Doc/Xls/Ppt (Compound File) |
| **OOXML** | `50 4B 03 04` | Docx/Xlsx/Pptx (Same as ZIP) |

---
*Note: This list is optimized for quick lookups during CTF competitions.*

git clone https://github.com/file/file.git

magic/Magdir
