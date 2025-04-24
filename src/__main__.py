"""Sample doc string."""

import argparse
import asyncio

from uart_ble import stream_from_ble_device

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read sensor data over BLE.")
    parser.add_argument(
        "--microcontroller",
        "-m",
        choices=["ARDUINO", "CIRCUITPY"],
        default="CIRCUITPY",
        help="Microcontroller to read data from",
    )

    args = parser.parse_args()

    """Stream data from the BLE device."""
    asyncio.run(stream_from_ble_device(device_name=args.microcontroller))
