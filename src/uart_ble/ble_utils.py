"""Sample doc string."""

import asyncio

from bleak import BleakClient, BleakError, BleakScanner
from loguru import logger

from uart_ble.definitions import BLE_TIMEOUT, TX_CHAR_UUID

BUFFER = b""


async def find_device(target_name: str):
    """Find the BLE device with the given name."""
    devices = await BleakScanner.discover(timeout=BLE_TIMEOUT)
    device = next((d for d in devices if d.name and target_name in d.name), None)
    return device


def list_devices(devices) -> None:
    """List the found BLE devices."""
    if not devices:
        logger.error("❌ No BLE devices found.")
        return

    for device in devices:
        logger.info(
            f"{device.name or 'Unnamed'} — {device.address} — RSSI: {device.rssi} dBm"
        )


class BLEHandler:
    """BLE handler class."""

    def __init__(self):
        self._buffer = b""

    def handle_rx(self, _, data):
        """Handle received data."""
        self._buffer += data

        # Process all full lines
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            logger.info(f"Received: {line.decode('utf-8').replace(',', ', ')}")


async def list_services(client) -> None:
    """List the services of the connected device."""
    services = await client.get_services()
    for service in services:
        logger.info(f"[Service] {service.uuid}")
        for char in service.characteristics:
            logger.info(f"└─ [Characteristic] {char.uuid} — {char.properties}")


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
                await asyncio.sleep(1.0)  # Give it time to receive stuff
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
                logger.info("Disconnected cleanly.")


async def stream_uart_ble(microcontroller_name: str):
    """Run the main function."""
    task = asyncio.create_task(read_device(device_name=microcontroller_name))
    try:
        await task
    except BleakError as bleak_err:
        logger.error(bleak_err)
    except KeyboardInterrupt:
        task.cancel()
        await task
