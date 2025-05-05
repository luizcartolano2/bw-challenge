"""Module containing custom exceptions for buffer-related operations.

This module provides exceptions that can be raised when working with buffers,
particularly in the context of UTF-8 decoding operations.
"""


class BufferTooSmallException(Exception):
    """Exception raised when a buffer may be too small for UTF-8 decoding.

    This exception indicates that the provided buffer size might be insufficient
    to properly decode UTF-8 encoded data, which could lead to decoding errors
    or corrupted output.

    Attributes:
        message (str): Explanation of the error. Defaults to a general message
            about buffer size potentially being too small for UTF-8 decoding.
    """

    def __init__(self, message="Buffer size may be too small to decode UTF-8 properly"):
        """Initialize the BufferTooSmallException with an optional custom message.

        Args:
            message (str, optional): Custom error message. If not provided, a default
                message about buffer size and UTF-8 decoding will be used.
        """
        super().__init__(message)
