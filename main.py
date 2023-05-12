""" rw_speed_test/main.py
Test the read & write speed of a connected storage device.

Prints to console the write and read speeds in megabytes per second.
Allows for testing of USB flash drives, external hard drives, etc.
Optional iterations parameter allows for multiple tests to be run and averaged.

Compatible with Windows, Python 3.6+.

Author: Aareon Sullivan
Date: 2023-05-12
License: MIT
"""
import os
import sys
import time
from pathlib import Path

import psutil

ROOT_FP = Path(__file__).parent.resolve()  # Root file path of this script


def sizeof_fmt(num: float, suffix: str = "B") -> str:
    """
    Convert the given file size into a human-readable string representation.
    Source: https://stackoverflow.com/a/1094933

    Parameters:
        num (float): The size in bytes to be converted.
        suffix (str, optional): The unit suffix to append to the converted size. Default is 'B' for bytes.

    Returns:
        str: The human-readable string representation of the file size with the appropriate unit suffix.

    Examples:
        >>> sizeof_fmt(1024)
        '1.0KiB'
        >>> sizeof_fmt(2048, suffix='B')
        '2.0KB'
        >>> sizeof_fmt(1000000, suffix='B')
        '976.6KB'
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def test_storage_speed(
    file_size: int = 1024, iterations: int = 1, drive: str = "c"
) -> None:
    """
    Tests the read/write speed of a storage device.

    Args:
        file_size (int, optional): Size of the file to be used for testing, in megabytes.
            Defaults to 100.
        iterations (int, optional): Number of times to run the test.
            Defaults to 1.
        drive (str, optional): Letter of drive to test.
            Defaults to "c"

    Returns:
        None

    This function generates a random data string and writes it to a temporary file on the chosen storage device
    until the file size reaches the desired size. It measures the time taken for the write operation and calculates
    the write speed in megabytes per second.

    Then, it reads the entire file from the storage device to measure the read speed in megabytes per second.
    Finally, it deletes the temporary file and prints the write and read speeds.

    Example usage:
        test_usb_speed()  # Runs the test with a default file size of 100MB.
        test_usb_speed(500)  # Runs the test with a file size of 500MB.
    """

    # Check if chosen drive is mounted
    drive: str = drive.lower()
    disks: list = [
        d.mountpoint.replace(":\\", "").lower() for d in psutil.disk_partitions()
    ]  # list of mounted drives

    print(f"Mounted drives: {disks}")

    if drive not in disks:  # check if chosen drive is mounted
        print(f"Error: the drive `{drive}` is not mounted. Aborting...")
        sys.exit(1)

    # Check if this script is on `drive`
    print(f"Script located on drive '{ROOT_FP.drive.strip(':')}'")
    this_drive: str = ROOT_FP.drive.strip(
        ":"
    ).lower()  # get the drive letter of this script

    # Get a file path for desired disk to test
    if this_drive == drive:
        fp: Path = ROOT_FP.resolve()
    else:
        fp: Path = Path(f"{drive}:\\").resolve()

    print(
        f"Test file path {str(fp)[:-1].upper() if fp != ROOT_FP else fp}, is_dir: {fp.is_dir()}"
    )

    # Define the file size in MB (default: 100MB)
    file_size_mb: int = file_size

    # Convert file size to bytes
    file_size_bytes: int = int(file_size_mb * 1024 * 1024)  # convert megabytes to bytes

    # Define how many times to run the test
    iterations: int = iterations if iterations > 0 else 1

    print(
        f"Testing r/w speed for drive '{drive.upper()}:' with file size {sizeof_fmt(file_size_bytes)} for {iterations}",
        "iterations. Please wait...",
    )

    # Define a filename for test file
    test_fn = "test_file.bin"

    # Generate a random data string to write to the file
    data: bytes = os.urandom(file_size_bytes)

    read_speed: float = 0
    write_speed: float = 0

    # Time all iterations
    overall_start: float = time.perf_counter()

    # Combine all speeds to get an average for all iterations
    average_write_speed: float = 0
    average_read_speed: float = 0

    for i in range(iterations):
        iteration_start: float = time.perf_counter()
        # Create a temporary file for testing
        with open(fp / test_fn, "wb") as f:
            # Write the random data to the file until it reaches the desired file size
            start_time: float = time.perf_counter()
            while f.tell() < file_size_bytes:
                f.write(data)
            end_time: float = time.perf_counter()

        # Calculate the write speed
        write_speed: float = file_size_bytes / (end_time - start_time) / (1024 * 1024)
        average_write_speed += write_speed

        # Read the file to test the read speed
        with open(fp / test_fn, "rb") as f:
            start_time: float = time.perf_counter()
            f.read()
            end_time: float = time.perf_counter()

        iteration_end: float = time.perf_counter()

        # Calculate the read speed
        read_speed: float = (
            file_size_bytes / (end_time - start_time) / (1024 * 1024)
        )  # MB/s
        average_read_speed += read_speed

        # Delete the temporary file
        Path(fp / test_fn).unlink()

        # Print the results
        print(f"{'-' * 18}")
        print(f"Iteration: {i+1}")
        print(f"Write Speed: {write_speed:.2f} MB/s")
        print(f"Read Speed: {read_speed:.2f} MB/s")
        print(f"Iteration time elapsed: {(iteration_end - iteration_start):.2f} seconds")

    # Get end time for all iterations
    overall_end: float = time.perf_counter()

    # Give average speeds if running more than 1 iteration
    if iterations > 1:
        print(f"{'-' * 18}")
        print(f"Average write speed: {(average_write_speed / iterations):.2f} MB/s")
        print(f"Average read speed: {(average_read_speed / iterations):.2f} MB/s")
        print(f"{'-' * 18}")

    print(f"Total time elapsed: {(overall_end - overall_start):.2f} seconds")


# Example usage
test_storage_speed(file_size=128, iterations=1, drive="c")
