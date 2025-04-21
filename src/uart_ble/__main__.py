"""Sample doc string."""

import argparse
import asyncio

from bleak import BleakClient, BleakError, BleakScanner
from loguru import logger

from uart_ble.ble_utils import (
    BLEHandler,
    find_device,
    list_devices,
    list_services,
)
from uart_ble.definitions import BLE_TIMEOUT, TX_CHAR_UUID


async def read_device(device_name: str):
    """Stream data from the BLE device."""
    device = await find_device(target_name=device_name)
    if not device:
        list_devices(await BleakScanner.discover(timeout=BLE_TIMEOUT))
        logger.error(f"Could not find device named '{device_name}'")
        return
    async with BleakClient(device.address) as client:
        logger.info("Connected!")
        try:
            handler = BLEHandler()
            await client.start_notify(TX_CHAR_UUID, handler.handle_rx)
            while True:
                await asyncio.sleep(10)  # Give it time to receive stuff
        except asyncio.CancelledError:
            logger.warning("Cancelled — cleaning up...")
        except Exception as e:
            logger.error(e)
            await list_services(client)

        finally:
            if client.is_connected:
                logger.warning("Stopping notifications and disconnecting...")
                await client.stop_notify(TX_CHAR_UUID)
                await client.disconnect()
                logger.info("Disconnected cleanly ✅")


async def main(microcontroller_name: str):
    """Run the main function."""
    task = asyncio.create_task(read_device(device_name=microcontroller_name))
    try:
        await task
    except BleakError as bleak_err:
        logger.error(bleak_err)
    except KeyboardInterrupt:
        task.cancel()
        await task


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
    asyncio.run(main(microcontroller_name=args.microcontroller))
