"""Tests for Overflow Detective. Run with:  python -m unittest discover tests"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from main import (add_and_check, bits_needed, ones_complement, read_twos_complement,   # noqa: E402
                  sign_magnitude, signed_range, to_base, twos_complement)


class TestRepresentations(unittest.TestCase):
    def test_base_conversion(self):
        self.assertEqual([to_base(13, b) for b in (2, 8, 16)], ["1101", "15", "D"])
        self.assertEqual([to_base(2026, b) for b in (2, 8, 16)], ["11111101010", "3752", "7EA"])
        for n in range(0, 2000, 7):
            self.assertEqual(int(to_base(n, 2), 2), n)

    def test_three_signed_forms_of_minus_five(self):
        self.assertEqual((sign_magnitude(-5, 8), ones_complement(-5, 8), twos_complement(-5, 8)),
                         ("10000101", "11111010", "11111011"))

    def test_minus_128_only_in_twos_complement(self):
        self.assertIsNone(sign_magnitude(-128, 8))
        self.assertIsNone(ones_complement(-128, 8))
        self.assertEqual(twos_complement(-128, 8), "10000000")

    def test_round_trip_every_8_bit_value(self):
        for n in range(-128, 128):
            self.assertEqual(read_twos_complement(twos_complement(n, 8)), n)

    def test_ranges_and_word_size(self):
        self.assertEqual([signed_range(b) for b in (4, 8, 16)], [(-8, 7), (-128, 127), (-32768, 32767)])
        self.assertEqual([bits_needed(n) for n in (127, 128, 2_147_483_648)], [8, 16, 64])


class TestAddition(unittest.TestCase):
    def test_examples(self):
        r = add_and_check(100, 50, 8)
        self.assertEqual((r["result_bits"], r["cpu_answer"], r["overflow"]), ("10010110", -106, True))
        r = add_and_check(-100, -50, 8)
        self.assertEqual((r["cpu_answer"], r["overflow"]), (106, True))
        r = add_and_check(50, 20, 8)
        self.assertEqual((r["cpu_answer"], r["overflow"]), (70, False))

    def test_overflow_flag_matches_the_range_for_every_8_bit_pair(self):
        for a in range(-128, 128):
            for b in range(-128, 128):
                r = add_and_check(a, b, 8)
                fits = -128 <= a + b <= 127
                self.assertEqual(r["overflow"], not fits)
                self.assertEqual(r["overflow"], bool(r["carry_in_msb"] ^ r["carry_out_msb"]))
                if fits:
                    self.assertEqual(r["cpu_answer"], a + b)
                else:
                    self.assertEqual(r["cpu_answer"], a + b - 256 if a + b > 127 else a + b + 256)

    def test_operands_out_of_range(self):
        with self.assertRaises(ValueError):
            add_and_check(200, 1, 8)


class TestCommandLine(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(ROOT, "main.py"), *args], capture_output=True, text=True)

    def test_add_and_convert(self):
        out = self.run_cli("--add", "100", "50").stdout
        self.assertIn("V = 1", out)
        self.assertIn("OVERFLOW DETECTED", out)
        self.assertIn("2's Complement:  11111011", self.run_cli("--convert", "-5").stdout)

    def test_bad_input(self):
        out = self.run_cli("--add", "200", "1")
        self.assertEqual(out.returncode, 1)
        self.assertIn("must fit within 8-bit range", out.stdout)
        self.assertEqual(self.run_cli("--add", "1", "1", "--bits", "12").returncode, 2)


if __name__ == "__main__":
    unittest.main()
