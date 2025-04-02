# Binary Code Compression and Decompression
## Overview
This project implements a binary code compression and decompression system in Python, designed to efficiently compress 32-bit binary patterns into variable-length encoded formats and decompress them back to their original form. Developed as part of a university assignment, it demonstrates proficiency in algorithmic design, bit manipulation, and file I/O in Python.

The compression algorithm uses a dictionary-based approach with multiple encoding formats (direct matching, bitmask, mismatches, and run-length encoding) to achieve space efficiency, while the decompression logic accurately reconstructs the original binaries from the compressed data.

## Features
Compression Formats:
-- Direct Matching (111): 7 bits, references dictionary entries.
-- Bitmask (010): 17 bits, applies a 4-bit mask to a dictionary entry.
-- 1-bit Mismatch (011): 14 bits, flips one bit.
-- 2-bit Consecutive Mismatch (100): 14 bits, flips two consecutive bits.
- 4-bit Consecutive Mismatch (101): 14 bits, flips four consecutive bits.
-- 2-bit Separated Mismatch (110): 19 bits, flips two non-consecutive bits.
-- Uncompressed (000): 35 bits, stores the original binary.
-- Run-Length Encoding (RLE, 001): 6 bits, repeats the previous pattern up to 8 times.
- Dictionary Creation: Builds a 16-entry dictionary based on pattern frequency and first occurrence.
- File I/O: Reads from and writes to text files (original.txt, cout.txt, compressed.txt, dout.txt).
- Error Handling: Robust parsing of compressed bit strings with boundary checks.
