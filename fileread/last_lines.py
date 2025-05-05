"""File utilities for reverse line reading.

This module provides functionality for efficiently reading files in reverse order,
line by line. It's particularly useful for processing large files like logs where
the most recent entries appear at the end.

The main functionality is provided by the `last_lines()` generator function which
yields lines from the end of the file moving upwards.
"""

import io
import os

from exceptions.buffer_too_small import BufferTooSmallException


def last_lines(filename, buf_size=io.DEFAULT_BUFFER_SIZE, encoding='utf-8'):
    """
    A generator that yields lines from a file in reverse order (last line first).

    Args:
        filename (str): Path to the file to be read.
        buf_size (int): Size of the buffer used for reading chunks (in bytes).
            Must be at least 4 for UTF-8. Defaults to io.DEFAULT_BUFFER_SIZE.
        encoding (str): File encoding to use. Defaults to 'utf-8'.

    Yields:
        str: Lines from the file in reverse order, with newline included.

    Raises:
        ValueError: If buf_size is too small for the encoding.
        FileNotFoundError: If the file doesn't exist.
        BufferTooSmallException: If buffer can't decode a multi-byte character.
        UnicodeDecodeError: For invalid encoding sequences within a buffer.
    """
    # Minimum buffer size depends on encoding (4 for UTF-8)
    min_buf_size = 4 if encoding.lower().replace('-', '') in ('utf8', 'utf') else 1
    if buf_size < min_buf_size:
        raise ValueError(f"buf_size must be at least {min_buf_size} for {encoding}")

    try:
        with open(filename, 'rb') as fh:
            file_size = fh.seek(0, os.SEEK_END)
            if file_size == 0:
                return  # empty file

            segment = None
            offset = 0
            remaining_size = file_size

            while remaining_size > 0:
                offset = min(file_size, offset + buf_size)
                fh.seek(max(0, file_size - offset))
                chunk_size = min(remaining_size, buf_size)
                buffer = fh.read(chunk_size)

                # Remove last newline only if it's the end of file
                if remaining_size == file_size and buffer.endswith(b'\n'):
                    buffer = buffer[:-1]

                remaining_size -= chunk_size
                lines = buffer.split(b'\n')

                if segment is not None:
                    # Prepend pending segment to last line of current chunk
                    lines[-1] += segment

                # The first line becomes the pending segment
                segment = lines[0]

                # Yield all complete lines in reverse order
                for line in reversed(lines[1:]):
                    try:
                        yield line.decode(encoding) + '\n'
                    except UnicodeDecodeError as e:
                        if remaining_size > 0:  # Still more data to read
                            raise BufferTooSmallException(
                                f"Decoding failed. Try increasing buf_size (current: {buf_size})"
                            ) from e
                        raise  # Re-raise for actual decode errors

            # Yield the remaining segment if any
            if segment is not None:
                try:
                    yield segment.decode(encoding) + '\n'
                except UnicodeDecodeError as e:
                    raise BufferTooSmallException(
                        f"Final segment decoding failed. Try increasing buf_size (current: {buf_size})"
                    ) from e

    except OSError as e:
        if isinstance(e, FileNotFoundError):
            raise
        raise OSError(f"Error reading file {filename}") from e
