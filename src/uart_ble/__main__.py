"""Sample doc string."""

import argparse
import asyncio

from uart_ble import stream_uart_ble

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read sensor data over BLE.")
    parser.add_argument(
        "--microcontroller",
        "-m",
        required=True,
        choices=["ARDUINO", "CIRCUITPY"],
        help="Microcontroller to read data from",
    )

    args = parser.parse_args()
    asyncio.run(stream_uart_ble(microcontroller_name=args.microcontroller))
