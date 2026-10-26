# Overflow Detective

**Course:** Computer Organization and Architecture (COA)  
**Topic:** Signed Number Representation (Sign-Magnitude, 1's Complement, 2's Complement) and Arithmetic Overflow Detection  
**Author:** Easala Jagadeesh ([@jagadeesh177](https://github.com/jagadeesh177))  
**Live Deployed Application (Vercel):** [https://overflow-detective.vercel.app](https://overflow-detective.vercel.app)  
**GitHub Repository:** [https://github.com/jagadeesh177/overflow-detective](https://github.com/jagadeesh177/overflow-detective)  

---

## 1. Project Overview

Computers represent signed integer values within fixed-width registers ($4$, $8$, $16$, $32$, or $64$ bits) using two's complement arithmetic. When the result of an arithmetic operation exceeds the maximum representable value of a word size, the hardware does not inherently halt program execution; rather, it silently rolls over or wraps around, often producing an unexpected opposite-sign value.

This project, **Overflow Detective**, is an educational simulation system built to explore:
1. Positional number system conversions (decimal to binary, octal, hexadecimal via repeated division).
2. Fixed-width signed representations (sign-magnitude, 1's complement, and 2's complement).
3. Bit-by-bit ALU full-adder addition and arithmetic overflow detection using both the sign-bit rule and hardware carry-flag logic ($V = C_{\text{in}} \oplus C_{\text{out}}$ at the MSB).
4. Historical engineering software and hardware failures caused by unhandled integer overflows.

---

## 2. Theoretical Foundations

### 2.1 Representable Range for $n$-Bit Two's Complement
For an $n$-bit register in two's complement, the range of representable integers is:

$$\left[-2^{n-1},\ 2^{n-1} - 1\right]$$

| Word Size | Minimum Value ($-2^{n-1}$) | Maximum Value ($2^{n-1} - 1$) |
|---|---|---|
| 4-bit | $-8$ | $+7$ |
| 8-bit | $-128$ | $+127$ |
| 16-bit | $-32,768$ | $+32,767$ |
| 32-bit | $-2,147,483,648$ | $+2,147,483,647$ |
| 64-bit | $-9,223,372,036,854,775,808$ | $+9,223,372,036,854,775,807$ |

### 2.2 ALU Addition & Overflow Detection
In two's complement addition, overflow occurs under two mathematically equivalent conditions:

1. **Sign Consistency Rule:**
   - Adding two positive operands yields a negative sum ($A_{msb} = 0, B_{msb} = 0, Sum_{msb} = 1$).
   - Adding two negative operands yields a positive sum ($A_{msb} = 1, B_{msb} = 1, Sum_{msb} = 0$).
   - Adding two numbers of opposite signs **can never cause overflow**.

2. **ALU Carry-Bit Condition:**
   - Overflow flag $V$ is computed as the exclusive-OR of the carry into the sign bit ($C_{in}$) and the carry out of the sign bit ($C_{out}$):
   
   $$V = C_{in\_msb} \oplus C_{out\_msb}$$

---

## 3. Historical Engineering Failures

| Incident | Year | Root Cause and Impact |
|---|---|---|
| **YouTube Gangnam Style** | 2014 | View counter reached the 32-bit signed ceiling ($2,147,483,647$). Adding $1$ wrapped the counter to $-2,147,483,648$, forcing YouTube to upgrade counter architecture to 64-bit integers. |
| **Boeing 787 GCU Shutdown** | 2015 | FAA Airworthiness Directive 2015-09-07 documented that Generator Control Units (GCUs) kept continuously powered for $\approx 248.55$ days overflowed a 32-bit centisecond tick counter, causing a fail-safe generator shutdown. |
| **Ariane 5 Flight 501** | 1996 | A 64-bit floating-point horizontal velocity value exceeded the capacity of an unshielded 16-bit signed integer register ($> 32,767$), causing an operand error that aborted guidance and led to rocket destruction. |
| **Retro 8-Bit Game Rollover** | — | Arcade score counters stored in signed 8-bit registers overflow at $127 + 1 = -128$, corrupting score tables. |

---

## 4. Project Structure

```
overflow-detective/
├── 4_COA_Report_Easala_Jagadeesh.pdf  # Comprehensive academic project report
├── api/
│   └── index.py                      # Vercel serverless function entrypoint
├── app.py                            # Local HTTP server using standard library
├── index.html                        # Interactive, responsive web dashboard
├── main.py                           # Core computational engine, CLI runner, and test suite
├── requirements.txt                  # Python dependencies (standard library)
├── vercel.json                       # Vercel deployment and routing configuration
├── README.md                         # Project documentation and execution guide
└── .gitignore                        # Standard Python development ignores
```

---

## 5. Execution and Testing

The project requires only **Python 3.8+** with **zero external package dependencies**.

### 5.1 Live Web Dashboard (Vercel Production)

Access the live cloud deployment directly at:
**[https://overflow-detective.vercel.app](https://overflow-detective.vercel.app)**

### 5.2 Local Web Dashboard Mode

1. **Start the local HTTP server:**
   ```bash
   python app.py
   ```
   *(Optional port parameter: `python app.py --port 8080`)*

2. **Open the browser at:**
   ```
   http://localhost:8001
   ```

The dashboard includes:
- **Module 1:** Base converter & bit representation viewer (Binary, Octal, Hexadecimal, Sign-Magnitude, 1's Complement, 2's Complement).
- **Module 2:** ALU Full Adder Simulator displaying carry chains, operands, sum bits, and status badges.
- **Module 3:** Interactive historical bug replay buttons that automatically load parameters into the simulation engine.

### 5.3 Terminal Mode (CLI)

1. **Run Full Academic Demonstration:**
   ```bash
   python main.py
   ```
   *Executes structured demonstrations for radix conversions, 8-bit complement encodings, ALU addition with overflow analysis, and case studies.*

2. **Interactive CLI Shell:**
   ```bash
   python main.py --interactive
   ```
   *Provides an interactive menu to test custom integers, arbitrary word sizes (4, 8, 16, 32), and step-by-step full adder traces.*

3. **Run Automated Test Suite:**
   ```bash
   python main.py --test
   ```
   *Exhaustively tests all 256 combinations of 4-bit additions ($-8$ to $+7$) and key 8-bit boundary conditions against mathematical truth.*

---

## 6. Verification and Validation

The arithmetic logic was verified by:
- An exhaustive combinatorial test of all $16 \times 16 = 256$ four-bit signed additions.
- Boundary testing at extremal values (e.g., $127 + 1$, $-128 + (-1)$, $-64 + (-64)$ in 8-bit; $32,767 + 1$ in 16-bit; $2,147,483,647 + 1$ in 32-bit).
- Cross-verification that the Sign-Consistency condition ($A_{sign} = B_{sign} \land Sum_{sign} \ne A_{sign}$) and the hardware carry condition ($V = C_{in} \oplus C_{out}$) yield identical results across all test vectors.

---

## 7. License and Attribution

Developed as an academic mini-project for Computer Organization and Architecture.  
Author: Easala Jagadeesh ([@jagadeesh177](https://github.com/jagadeesh177))  
Report: [4_COA_Report_Easala_Jagadeesh.pdf](4_COA_Report_Easala_Jagadeesh.pdf)
