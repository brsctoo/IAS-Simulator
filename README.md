# Instruction Cycle Simulator — IAS Architecture

A Python simulator of the fetch, decode, and execute cycle of a processor based on the **IAS** model, developed for the Computer Architecture and Organization course (UEM).

The simulator reproduces the behavior of a 256-position memory and a set of special-purpose and general-purpose registers, executing programs written in a symbolic machine language defined for this project.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-completed-brightgreen)
![License](https://img.shields.io/badge/license-educational-lightgrey)

---

## Table of Contents

- [Overview](#overview)
- [Simulated Architecture](#simulated-architecture)
- [Instruction Set](#instruction-set)
- [Input File Format](#input-file-format)
- [How to Run](#how-to-run)
- [Repository Structure](#repository-structure)
- [Example Programs](#example-programs)
- [Execution Example](#execution-example)
- [Design Decisions](#design-decisions)
- [Possible Future Improvements](#possible-future-improvements)
- [Authors](#authors)

---

## Overview

All instructions and data of a program are stored in a **simulated RAM memory of 256 positions** (addresses `0x00` to `0xFF`). At each step, the simulator executes the classic cycle:

```
MAR ← PC        (address of the next instruction)
MBR ← MEM[MAR]  (fetch the instruction)
IR  ← MBR       (load into the instruction register)
PC  ← PC + 1
execute the instruction
```

and prints the complete state of the registers after each instruction, allowing you to follow exactly what happens inside the processor at each step (pressing ENTER to advance).

## Simulated Architecture

| Register | Function |
|---|---|
| `A`, `B` | General-purpose registers |
| `PC` | *Program Counter* — address of the next instruction |
| `IR` | *Instruction Register* — instruction being executed |
| `MAR` | *Memory Address Register* — address currently in use in memory |
| `MBR` | *Memory Buffer Register* — data read from/written to memory |
| `AC` | Accumulator — default destination for arithmetic operations |
| `M` | High-order (16-bit) part of the `MULT` result |
| `R` | Remainder of the integer division of `DIV` |
| `C` | *Carry* — indicates overflow of `ADD`/`SUB` |
| `N` | Indicates whether the last manipulated value is negative |
| `Z` | Indicates whether the last manipulated value is zero |

Arithmetic results are treated as signed **16-bit words** (`-32768` to `32767`, two's complement). When an addition or subtraction exceeds this range, the value "wraps around" (like an odometer) and the `C` register is set.

## Instruction Set

Based on the IAS computer, with specific extensions to enable indexed array access.

| Instruction | Effect | Notes |
|---|---|---|
| `LOAD M(x)` / `LOAD #x` | `AC ← MEM[x]` or `AC ← x` | Direct or immediate; accepts an explicit register (`LOAD A, M(x)`) and `LOAD A` (`AC ← A`) |
| `LOADI M(x)` | `AC ← MEM[MEM[x]]` | Indirect addressing |
| `STORE` / `STOR` | `MEM[x] ← AC` (or the indicated register) | Has no immediate form — the destination is always an address |
| `STORI M(x)` | `MEM[MEM[x]] ← AC` | Indirect addressing for writing |
| `ADD` / `SUB` | `reg ← reg + value` / `reg ← reg − value` | Result truncated to 16 bits; `C = 1` on overflow |
| `MULT` | `M:reg ← reg × value` | 32-bit result split between `M` (high part) and `reg` (low part) |
| `DIV` | `reg ← reg ÷ value`, `R ← remainder` | Terminates the program on division by zero |
| `JUMP M(x)` | `PC ← x` | Unconditional branch |
| `JUMP+ M(x)` | If `AC ≥ 0`: `PC ← x` | Conditional branch — jumps when `AC` is greater **than or equal to** zero |
| `MOV destination, source` | `destination ← source` | Default source, if omitted, is `AC` |
| `HALT` | Ends execution | Extension added to explicitly mark the end of the program |

`LOAD`, `ADD`, `SUB`, `MULT`, and `DIV` accept both **direct addressing** (`M(x)`, fetch from memory) and **immediate addressing** (`#x`, value embedded in the instruction itself), and optionally an explicit destination register (`A,` — if omitted, the default is `AC`).

## Input File Format

Programs are written in `.txt` files divided into three mandatory sections, marked by explicit directives:

```
.DADOS
5
1
0x10

.INICIO
0x60

.CODIGO
LOAD M(0x01)
ADD M(0x00)
STOR M(0x02)
HALT
```

- **`.DADOS`** (DATA) — initial values (decimal or hexadecimal with the `0x` prefix), loaded sequentially starting at address `0x00`.
- **`.INICIO`** (START) — hexadecimal address where the first instruction will be stored.
- **`.CODIGO`** (CODE) — list of instructions, placed sequentially starting at the address defined in `.INICIO`.

Lines starting with `#` are comments and are ignored (whole-line comments only; inline comments are not supported).

Execution ends upon encountering `HALT`, an empty memory position (value `0`), or if the `PC` exceeds the memory bounds.

## How to Run

Requires only **Python 3.8+** — no external dependencies.

```bash
python3 main.py selection_sort.txt
python3 main.py fibonacci.txt
python3 main.py truncamento_teste.txt
```

The simulator prints the initial register state and, after each instruction, waits for `ENTER` to advance, showing the new state. At the end, the memory contents are displayed to verify the result.

## Repository Structure

```
.
├── memoria.py             # Global state: RAM memory and register dictionary
├── instrucoes.py          # Implementation of the instruction set (ISA)
├── main.py                # Input parser + instruction cycle (fetch/decode/execute)
├── selection_sort.txt     # Example program: selection sort
├── fibonacci.txt          # Example program: Fibonacci sequence
└── truncamento_teste.txt  # Example program: 16-bit arithmetic overflow/truncation
```

## Example Programs

### `selection_sort.txt`
Sorts the array `[10, 3, 7, 2, 8]` using the *Selection Sort* algorithm, adapted to fit within the 256-position memory using auxiliary pointers (with no dedicated index register). Expected result in `0x10`–`0x14`: `[2, 3, 7, 8, 10]`.

### `fibonacci.txt`
Iteratively calculates the first 10 terms of the Fibonacci sequence, using `ADD` in a loop controlled by `JUMP+`. Expected result in `0x20`–`0x29`: `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]`.

### `truncamento_teste.txt`
Validates 16-bit arithmetic overflow behavior: addition exceeding `32767`, subtraction exceeding `-32768`, normal use without overflow, and multiplication generating a 32-bit result split between `M` and the destination register.

## Execution Example

```
Initial State:
PC: 0x60 | MAR: 0x00
IR:  | MBR: 0x00
A: 0 | B: 0
AC: 0 | M: 0 | R: 0
C: 0 | N: 0 | Z: 0

Instruction to be executed: LOAD M(0x01)
PC: 0x61 | MAR: 0x01
IR: LOAD M(0x01) | MBR: 0x01
AC: 1 | M: 0 | R: 0
C: 0 | N: 0 | Z: 0

...

--- Result in Memory ---
MEM[0x10] = 2
MEM[0x11] = 3
MEM[0x12] = 7
MEM[0x13] = 8
MEM[0x14] = 10
```

## Design Decisions

- **Instructions stored as text** (not as binary opcodes), prioritizing readability and ease of debugging in an educational context.
- **Input format with explicit sections** (`.DADOS` / `.INICIO` / `.CODIGO`), more robust than relying on blank lines to separate blocks.
- **`STORE` does not alter the `Z`/`N` flags**, since the instruction writes an existing value to memory without modifying any register.
- **`JUMP+` jumps when `AC ≥ 0`** (not only when strictly positive), according to the convention defined for this project.
- **Indirect addressing (`LOADI`/`STORI`)** was added as an extension to the basic IAS instruction set, needed for `Selection Sort` to access array elements via dynamically calculated addresses.
- **Division by zero terminates execution** immediately, avoiding inconsistent states in the simulator.

## Possible Future Improvements

- Simple assembler with symbolic labels, eliminating manual calculation of branch addresses.
- Representation of instructions in binary/numeric opcode format.
- Support for procedure calls, with context saving and restoring.
- Debug mode with breakpoints and configurable step-by-step execution.
- Automated test suite covering each instruction and its edge cases.

## Authors

- Felipe Almeida Gomes
- Diego Pimenta Suárez
- Bruno Rafael Comin Scheffel
- José Luís Peres de Sousa

Academic project developed for the Computer Architecture and Organization course — State University of Maringá (UEM).
