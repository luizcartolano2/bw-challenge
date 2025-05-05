"""Unit tests for the `last_lines` file reading functionality.

This module contains comprehensive tests for reading files in reverse order,
verifying correct behavior with different file formats, encodings, and edge cases.
"""

import os
import tempfile
import unittest
from itertools import islice

from exceptions import BufferTooSmallException
from fileread import last_lines


class TestLastLines(unittest.TestCase):
    """Test suite for reverse file line reading functionality.

    This class tests the `last_lines` function's ability to:
    - Read files in reverse order efficiently
    - Handle various file sizes and line lengths
    - Process different newline formats and encodings
    - Manage buffer sizes appropriately
    - Handle error conditions gracefully
    """

    def setUp(self):
        """Set up test environment before each test case.

        Creates a temporary directory for test files that will be automatically
        cleaned up after tests complete.
        """
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_files = []

    def tearDown(self):
        """Clean up test environment after each test case.

        Removes the temporary directory and all test files created during testing.
        """
        self.test_dir.cleanup()

    def _create_test_file(self, content, name=None, encoding='utf-8'):
        """Helper method to create test files with specified content.

        Args:
            content (str): Text content to write to the file
            name (str, optional): Specific filename to use. Generates temp name if None.
            encoding (str): Character encoding to use (default: 'utf-8')

        Returns:
            str: Path to the created test file
        """
        if name is None:
            fd, path = tempfile.mkstemp(dir=self.test_dir.name)
        else:
            path = os.path.join(self.test_dir.name, name)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT)

        with os.fdopen(fd, 'wb') as f:
            f.write(content.encode(encoding))
        self.test_files.append(path)
        return path

    def test_empty_file(self):
        """Test reading an empty file returns empty list."""
        path = self._create_test_file("")
        lines = list(last_lines(path))
        self.assertEqual(lines, [])

    def test_single_line_variations(self):
        """Test various single line formatting cases.

        Verifies correct handling of:
        - No trailing newline
        - With trailing newline
        - Newline-only content
        - Empty content
        """
        cases = [
            ("No newline", ["No newline\n"]),
            ("With newline\n", ["With newline\n"]),
            ("\n", ["\n"]),  # Single newline only
            ("", []),  # Empty content
        ]
        for content, expected in cases:
            with self.subTest(content=content):
                path = self._create_test_file(content)
                self.assertEqual(list(last_lines(path)), expected)

    def test_multiple_line_variations(self):
        """Test multiple line cases with different newline patterns.

        Verifies correct handling of:
        - Unix-style newlines
        - Windows-style newlines
        - Mixed newline formats
        - Files with/without trailing newline
        """
        cases = [
            ("L1\nL2\nL3\n", ["L3\n", "L2\n", "L1\n"]),
            ("L1\nL2\nL3", ["L3\n", "L2\n", "L1\n"]),
            ("L1\r\nL2\r\nL3\r\n", ["L3\r\n", "L2\r\n", "L1\r\n"]),  # Windows style
            ("L1\nL2\r\nL3\n", ["L3\n", "L2\r\n", "L1\n"]),  # Mixed newlines
        ]
        for content, expected in cases:
            with self.subTest(content=content):
                path = self._create_test_file(content)
                self.assertEqual(list(last_lines(path)), expected)

    def test_buffer_boundary_conditions(self):
        """Test buffer size edge cases.

        Verifies correct behavior with:
        - Buffer exactly matching file size
        - Buffer larger than file
        - Minimum allowed buffer size
        """
        content = "A" * 500 + "\n" + "B" * 500 + "\n" + "C" * 500
        path = self._create_test_file(content)

        # Test with buffer size exactly matching file size
        self.assertEqual(len(list(last_lines(path, buf_size=1502))), 3)

        # Test with buffer size 1 byte larger than file
        self.assertEqual(len(list(last_lines(path, buf_size=1503))), 3)

        # Test with very small buffer (minimum size)
        self.assertEqual(len(list(last_lines(path, buf_size=4))), 3)

    def test_large_file_with_varied_lines(self):
        """Test with large file containing varied line lengths.

        Verifies:
        - Correct number of lines returned
        - All lines properly terminated
        - Handling of varying line lengths
        """
        content = "\n".join(
            f"{'A' * (i % 50)} Line {i} {'Z' * (i % 20)}"
            for i in range(1000)
        )
        path = self._create_test_file(content)
        lines = list(last_lines(path))
        self.assertEqual(len(lines), 1000)
        self.assertTrue(all(line.endswith('\n') for line in lines))

    def test_unicode_edge_cases(self):
        """Test various Unicode handling cases.

        Verifies correct processing of:
        - Accented characters
        - 4-byte Unicode symbols
        - Emoji characters
        - Long lines with Unicode
        """
        cases = [
            ("Normal é character", ["Normal é character\n"]),
            ("𝄞 Musical symbol", ["𝄞 Musical symbol\n"]),  # 4-byte char
            ("😊 Emoji", ["😊 Emoji\n"]),
            ("A" * 500 + "é" + "B" * 500, ["A" * 500 + "é" + "B" * 500 + "\n"]),
        ]
        for content, expected in cases:
            with self.subTest(content=content):
                path = self._create_test_file(content)
                self.assertEqual(list(last_lines(path)), expected)

    def test_huge_lines(self):
        """Test files with lines larger than buffer size.

        Verifies correct handling of lines that exceed the read buffer size.
        """
        huge_line = "X" * 10000  # Line much larger than default buffer
        path = self._create_test_file(huge_line)
        lines = list(last_lines(path, buf_size=512))
        self.assertEqual(lines, [huge_line + "\n"])

    def test_binary_file_handling(self):
        """Test behavior with non-UTF-8 binary data.

        Verifies proper exception is raised when attempting to read binary files.
        """
        binary_data = b'\x80\x81\x82\xff'  # Invalid UTF-8
        path = os.path.join(self.test_dir.name, "binary")
        with open(path, 'wb') as f:
            f.write(binary_data)

        with self.assertRaises(BufferTooSmallException):
            list(last_lines(path))

    def test_partial_iteration(self):
        """Test partial file iteration capability.

        Verifies that:
        - Partial iteration works correctly
        - Correct lines are returned (most recent first)
        - Only requested number of lines are returned
        """
        content = "\n".join(f"Line {i}" for i in range(100))
        path = self._create_test_file(content)

        # Only read first 5 lines
        lines = list(islice(last_lines(path), 5))
        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[0], "Line 99\n")

    def test_buffer_size_validation(self):
        """Test buffer size parameter validation.

        Verifies that invalid buffer sizes raise ValueError.
        """
        path = self._create_test_file("test")
        with self.assertRaises(ValueError):
            list(last_lines(path, buf_size=3))  # less than minimum 4

    def test_nonexistent_file(self):
        """Test handling of non-existent file paths.

        Verifies proper exception is raised when file doesn't exist.
        """
        with self.assertRaises(FileNotFoundError):
            list(last_lines("/nonexistent/file/path"))


if __name__ == '__main__':
    unittest.main()
