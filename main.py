"""
Overflow Detective: Computer Organization and Architecture (COA) Project
Topic: Signed Number Representation and Arithmetic Overflow Analysis
Author: Easala Jagadeesh (GitHub: @jagadeesh177)

This module implements:
1. Positional number system conversions (Base 10 to Base 2, 8, 16)
2. Fixed-width signed representations (Sign-Magnitude, 1's Complement, 2's Complement)
3. Bit-level ALU full adder simulation and hardware overflow detection (V = Cin XOR Cout)
4. Historical software and hardware case studies involving integer overflow
5. Interactive CLI interface and automated verification suite
"""

import sys
import argparse


# ---------------------------------------------------------------------------
# Section 1: Number Base Conversions
# ---------------------------------------------------------------------------

def to_base(n, base):
    """
    Convert a non-negative integer n to a string in the specified base (2, 8, or 16)
    using the repeated division method.
    """
    if n < 0:
        raise ValueError("to_base requires a non-negative integer.")
    if n == 0:
        return "0"

    digits = "0123456789ABCDEF"
    result = []
    current = n
    while current > 0:
        remainder = current % base
        result.append(digits[remainder])
        current //= base
    return "".join(reversed(result))


def from_binary(bit_string):
    """
    Convert an unsigned binary string to its non-negative decimal value
    using Horner's method / positional powers of two.
    """
    value = 0
    for bit in bit_string:
        if bit not in ("0", "1"):
            raise ValueError(f"Invalid binary digit '{bit}'.")
        value = (value << 1) | int(bit)
    return value


# ---------------------------------------------------------------------------
# Section 2: Fixed-Width Signed Integer Representations
# ---------------------------------------------------------------------------

def signed_range(bits):
    """
    Calculate the representable range for an n-bit two's complement integer.
    Formula: [-2^(bits-1), 2^(bits-1) - 1]
    """
    lower = -(1 << (bits - 1))
    upper = (1 << (bits - 1)) - 1
    return lower, upper


def sign_magnitude(n, bits):
    """
    Generate the sign-magnitude representation of an integer n in 'bits' width.
    - Most Significant Bit (MSB): Sign bit (0 for positive, 1 for negative).
    - Remaining bits: Absolute magnitude padded to (bits - 1) digits.
    Valid range: [-(2^(bits-1) - 1), +(2^(bits-1) - 1)]
    """
    max_mag = (1 << (bits - 1)) - 1
    if abs(n) > max_mag:
        return None  # Out of range for sign-magnitude

    sign_bit = "1" if n < 0 else "0"
    mag_bits = to_base(abs(n), 2).zfill(bits - 1)
    return sign_bit + mag_bits


def ones_complement(n, bits):
    """
    Generate the 1's complement representation of an integer n in 'bits' width.
    - Positive numbers: standard binary representation padded to 'bits'.
    - Negative numbers: bitwise NOT (inversion) of the positive magnitude.
    Valid range: [-(2^(bits-1) - 1), +(2^(bits-1) - 1)]
    """
    max_mag = (1 << (bits - 1)) - 1
    if abs(n) > max_mag:
        return None  # Out of range for 1's complement

    positive_binary = to_base(abs(n), 2).zfill(bits)
    if n >= 0:
        return positive_binary

    return "".join("1" if b == "0" else "0" for b in positive_binary)


def twos_complement(n, bits):
    """
    Generate the 2's complement representation of an integer n in 'bits' width.
    - Positive numbers: standard binary representation padded to 'bits'.
    - Negative numbers: invert all bits of positive magnitude and add 1 (modulo 2^bits).
    Valid range: [-2^(bits-1), 2^(bits-1) - 1]
    """
    low, high = signed_range(bits)
    if not (low <= n <= high):
        return None  # Out of representable range

    if n >= 0:
        return to_base(n, 2).zfill(bits)

    # Invert positive magnitude and add 1
    pos_bits = to_base(-n, 2).zfill(bits)
    inverted = "".join("1" if b == "0" else "0" for b in pos_bits)
    numeric_sum = from_binary(inverted) + 1
    # Truncate to exact bit width
    return to_base(numeric_sum, 2).zfill(bits)[-bits:]


def read_twos_complement(bit_string):
    """
    Decode an n-bit two's complement binary string to its signed decimal value.
    If MSB is 1, value is negative: value = unsigned_value - 2^bits.
    """
    bits = len(bit_string)
    unsigned_val = from_binary(bit_string)
    if bit_string[0] == "1":
        return unsigned_val - (1 << bits)
    return unsigned_val


def bits_needed(n):
    """
    Determine the minimum standard word size (8, 16, 32, or 64 bits)
    required to represent integer n in two's complement.
    """
    for bits in (8, 16, 32, 64):
        low, high = signed_range(bits)
        if low <= n <= high:
            return bits
    return None


# ---------------------------------------------------------------------------
# Section 3: Bit-Level ALU Binary Addition & Overflow Detection
# ---------------------------------------------------------------------------

def add_and_check(a, b, bits):
    """
    Simulate ALU bit-by-bit addition using a ripple full-adder model
    and evaluate arithmetic overflow.

    Overflow Conditions in Two's Complement:
    1. Sign-Consistency Rule:
       Overflow occurs if and only if two operands of the SAME sign yield
       a sum with the OPPOSITE sign.
    2. Hardware Carry-Bit Condition:
       Overflow V = Carry_in_to_MSB XOR Carry_out_from_MSB (V = C_in XOR C_out).
    """
    x = twos_complement(a, bits)
    y = twos_complement(b, bits)

    low, high = signed_range(bits)
    if x is None or y is None:
        raise ValueError(
            f"Operands must fit within {bits}-bit range [{low:,} to {high:,}]."
        )

    result_bits = ["0"] * bits
    carries = ["0"] * bits
    carry = 0

    # Ripple full adder from LSB (index bits - 1) to MSB (index 0)
    for i in range(bits - 1, -1, -1):
        carries[i] = str(carry)
        bit_a = int(x[i])
        bit_b = int(y[i])
        total = bit_a + bit_b + carry
        result_bits[i] = str(total % 2)
        carry = total // 2

    carry_in_msb = int(carries[0])
    carry_out_msb = carry
    result_str = "".join(result_bits)
    carries_str = "".join(carries)

    # Hardware overflow flag: V = Cin_msb XOR Cout_msb
    hardware_overflow = bool(carry_in_msb ^ carry_out_msb)
    # Sign rule: operands have same sign, but result sign differs
    sign_overflow = (x[0] == y[0]) and (result_str[0] != x[0])

    # Both conditions are mathematically identical in 2's complement
    assert hardware_overflow == sign_overflow

    cpu_answer = read_twos_complement(result_str)
    true_answer = a + b

    overflow_reason = ""
    if sign_overflow:
        if x[0] == "0":
            overflow_reason = (
                f"Positive overflow: operands {a} and {b} are positive, but result wrapped to negative {cpu_answer}."
            )
        else:
            overflow_reason = (
                f"Negative underflow/overflow: operands {a} and {b} are negative, but result wrapped to positive {cpu_answer}."
            )
    else:
        overflow_reason = f"Valid operation: mathematical sum {true_answer} fits within {bits}-bit range."

    return {
        "a_bits": x,
        "b_bits": y,
        "carries": carries_str,
        "carry_in_msb": carry_in_msb,
        "carry_out_msb": carry_out_msb,
        "result_bits": result_str,
        "cpu_answer": cpu_answer,
        "true_answer": true_answer,
        "overflow": sign_overflow,
        "overflow_reason": overflow_reason,
    }


# ---------------------------------------------------------------------------
# Section 4: Real-World Case Studies
# ---------------------------------------------------------------------------

REAL_BUGS = [
    {
        "name": "YouTube View Counter (2014)",
        "story": "The viral video 'Gangnam Style' exceeded 2,147,483,647 views (maximum 32-bit signed integer), causing the view count to wrap around to -2,147,483,648. YouTube subsequently migrated counters to 64-bit integers.",
        "a": 2_147_483_647,
        "b": 1,
        "bits": 32,
    },
    {
        "name": "Boeing 787 Generator Control Unit (2015)",
        "story": "FAA Airworthiness Directive 2015-09-07 identified that continuous operation for 248.55 days caused a 32-bit signed centisecond counter (ticks of 10 ms) to overflow, causing the Generator Control Units (GCUs) to fail into fail-safe shutdown.",
        "a": 2_147_483_647,
        "b": 1,
        "bits": 32,
    },
    {
        "name": "Ariane 5 Flight 501 Disaster (1996)",
        "story": "An unprotected floating-point to 16-bit signed integer conversion of horizontal velocity exceeded 32,767. The resulting operand error caused the inertial guidance computer to halt, triggering catastrophic rocket self-destruction.",
        "a": 32_767,
        "b": 1,
        "bits": 16,
    },
    {
        "name": "Classic Arcade / 8-Bit Score Counter",
        "story": "Many legacy 8-bit arcade machines and embedded microcontrollers use 8-bit signed registers. When a player's score increases past 127, the value rolls over into -128, corrupting high-score tables and gameplay progression.",
        "a": 127,
        "b": 1,
        "bits": 8,
    },
]


# ---------------------------------------------------------------------------
# Section 5: CLI Display and Formatting Utilities
# ---------------------------------------------------------------------------

def display_addition(a, b, bits):
    """Format and print a bit-level addition calculation to stdout."""
    res = add_and_check(a, b, bits)
    low, high = signed_range(bits)
    print(f"  Configuration: {bits}-bit Two's Complement (Range: {low:,} to {high:,})")
    print(f"  Carries:      {res['carries']}")
    print(f"  Operand A:    {res['a_bits']}  ({a:>11})")
    print(f"  Operand B:  + {res['b_bits']}  ({b:>11})")
    print("  " + "-" * (bits + 20))
    print(f"  ALU Result:   {res['result_bits']}  ({res['cpu_answer']:>11})")
    print(f"  Expected Sum: {res['true_answer']:>11}")
    print(f"  Hardware:     Cin(MSB) = {res['carry_in_msb']}, Cout(MSB) = {res['carry_out_msb']} -> V = {int(res['overflow'])}")
    if res["overflow"]:
        print(f"  STATUS:       [OVERFLOW DETECTED] - {res['overflow_reason']}")
    else:
        print(f"  STATUS:       [NORMAL - NO OVERFLOW] - {res['overflow_reason']}")
    return res


def run_demonstration():
    """Execute the full structured academic demonstration across all sections."""
    print("=" * 72)
    print("OVERFLOW DETECTIVE: COMPUTER ORGANIZATION & ARCHITECTURE DEMONSTRATION")
    print("=" * 72)

    # Section 1
    print("\n--- SECTION 1: POSITIONAL NUMBER BASE CONVERSIONS ---")
    test_values = [13, 200, 2026]
    for val in test_values:
        bin_str = to_base(val, 2)
        oct_str = to_base(val, 8)
        hex_str = to_base(val, 16)
        print(f"  Decimal: {val:>5}  |  Binary: {bin_str:>12}  |  Octal: {oct_str:>5}  |  Hex: {hex_str:>4}")

    # Section 2
    print("\n--- SECTION 2: SIGNED INTEGER ENCODING COMPARISON (8-BIT) ---")
    print(f"  {'Value':>7} | {'Sign-Magnitude':>14} | {'1s Complement':>14} | {'2s Complement':>14}")
    print("  " + "-" * 57)
    sample_ints = [5, -5, -1, -128]
    for val in sample_ints:
        sm = sign_magnitude(val, 8) or "Out of range"
        oc = ones_complement(val, 8) or "Out of range"
        tc = twos_complement(val, 8) or "Out of range"
        print(f"  {val:>7} | {sm:>14} | {oc:>14} | {tc:>14}")

    print("\n  Standard Word Size Ranges:")
    for width in (4, 8, 16, 32):
        low, high = signed_range(width)
        print(f"   {width:2d}-bit range: [{low:>12,} to {high:>11,}]")

    # Section 3
    print("\n--- SECTION 3: BIT-LEVEL ALU ADDITION & OVERFLOW DETECTION ---")
    print("\nCase 1: Positive Addition without Overflow (50 + 20 in 8-bit)")
    display_addition(50, 20, 8)

    print("\nCase 2: Positive Addition with Overflow (100 + 50 in 8-bit)")
    display_addition(100, 50, 8)

    print("\nCase 3: Negative Addition with Overflow (-100 + -50 in 8-bit)")
    display_addition(-100, -50, 8)

    # Section 4
    print("\n--- SECTION 4: HISTORICAL CASE STUDIES OF INTEGER OVERFLOW ---")
    for case in REAL_BUGS:
        print(f"\nCase: {case['name']}")
        print(f"  Description: {case['story']}")
        display_addition(case["a"], case["b"], case["bits"])
        recommended_width = bits_needed(case["a"] + case["b"])
        print(f"  Architectural Fix: Allocate minimum {recommended_width}-bit register width.")

    print("\n" + "=" * 72)
    print("DEMONSTRATION COMPLETE")
    print("=" * 72)


def run_unit_tests():
    """
    Exhaustively verify 4-bit addition (all 256 pairs) and 8-bit boundary cases
    against ground-truth mathematical addition and overflow definition.
    """
    print("Running verification test suite...")
    
    # 1. Test 4-bit exhaustive pairs: -8 to +7
    tested_pairs = 0
    for a in range(-8, 8):
        for b in range(-8, 8):
            res = add_and_check(a, b, 4)
            true_sum = a + b
            expected_overflow = not (-8 <= true_sum <= 7)
            assert res["overflow"] == expected_overflow, f"Mismatch on {a} + {b} in 4-bit"
            if not res["overflow"]:
                assert res["cpu_answer"] == true_sum
            tested_pairs += 1

    # 2. Test 8-bit boundary cases
    boundary_tests = [
        (127, 1, 8, True),
        (100, 27, 8, False),
        (-128, -1, 8, True),
        (-64, -64, 8, False),
        (-100, -28, 8, False),
        (-100, -29, 8, True),
        (0, 0, 8, False),
        (-1, 1, 8, False),
    ]
    for a, b, bits, expected_ovf in boundary_tests:
        res = add_and_check(a, b, bits)
        assert res["overflow"] == expected_ovf, f"Boundary test failed for {a} + {b}"

    print(f"Passed all {tested_pairs} 4-bit exhaustive combinations and {len(boundary_tests)} boundary cases.")
    print("Test status: SUCCESS. All hardware simulation models match ground truth.")


def interactive_mode():
    """Interactive command-line interface for exploratory arithmetic testing."""
    print("\n" + "=" * 60)
    print("OVERFLOW DETECTIVE - INTERACTIVE CLI MODE")
    print("=" * 60)
    print("Commands:")
    print("  1: Convert a single integer (Base, Sign-Mag, 1s, 2s Comp)")
    print("  2: Add two integers with bit-level ALU trace")
    print("  3: View historical overflow case studies")
    print("  4: Run automated test suite")
    print("  q: Exit")
    print("-" * 60)

    while True:
        try:
            choice = input("\nEnter choice [1-4, q]: ").strip().lower()
            if choice in ("q", "quit", "exit"):
                print("Exiting interactive mode.")
                break

            if choice == "1":
                num_str = input("Enter decimal integer: ").strip()
                if not num_str:
                    continue
                n = int(num_str)
                bits_str = input("Select bit width (4, 8, 16, 32) [default 8]: ").strip()
                bits = int(bits_str) if bits_str else 8
                if bits not in (4, 8, 16, 32):
                    print("Error: bit width must be 4, 8, 16, or 32.")
                    continue

                low, high = signed_range(bits)
                print(f"\n--- Conversion for {n} ({bits}-bit) ---")
                print(f"Absolute Binary: {to_base(abs(n), 2)}")
                print(f"Absolute Octal:  {to_base(abs(n), 8)}")
                print(f"Absolute Hex:    {to_base(abs(n), 16)}")
                print(f"Sign-Magnitude:  {sign_magnitude(n, bits) or 'Out of range'}")
                print(f"1's Complement:  {ones_complement(n, bits) or 'Out of range'}")
                print(f"2's Complement:  {twos_complement(n, bits) or 'Out of range'}")
                print(f"Word Range:      [{low:,} to {high:,}]")
                if low <= n <= high:
                    print(f"Status:          Value fits within {bits} bits.")
                else:
                    needed = bits_needed(n)
                    print(f"Status:          Value exceeds {bits} bits. Minimum required word size: {needed} bits.")

            elif choice == "2":
                a_str = input("Enter operand A: ").strip()
                b_str = input("Enter operand B: ").strip()
                if not a_str or not b_str:
                    continue
                a, b = int(a_str), int(b_str)
                bits_str = input("Select bit width (4, 8, 16, 32) [default 8]: ").strip()
                bits = int(bits_str) if bits_str else 8
                if bits not in (4, 8, 16, 32):
                    print("Error: bit width must be 4, 8, 16, or 32.")
                    continue

                print("\n--- ALU Addition Trace ---")
                display_addition(a, b, bits)

            elif choice == "3":
                print("\n--- Historical Overflow Case Studies ---")
                for idx, bug in enumerate(REAL_BUGS, 1):
                    print(f"\n[{idx}] {bug['name']}")
                    print(f"    {bug['story']}")
                    display_addition(bug["a"], bug["b"], bug["bits"])

            elif choice == "4":
                run_unit_tests()

            else:
                print("Invalid option. Please enter 1, 2, 3, 4, or q.")
        except ValueError as err:
            print(f"Input error: {err}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Overflow Detective: Signed Number Representations & Overflow Analysis."
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Launch interactive command-line interface."
    )
    parser.add_argument(
        "-t", "--test", action="store_true", help="Run internal validation test suite."
    )
    parser.add_argument(
        "-d", "--demo", action="store_true", help="Run academic demonstration."
    )

    args = parser.parse_args()

    if args.test:
        run_unit_tests()
    elif args.interactive:
        interactive_mode()
    else:
        run_demonstration()


if __name__ == "__main__":
    main()
