"""Sample doc string."""

from bleak import BleakScanner
from loguru import logger

from uart_ble.definitions import BLE_TIMEOUT

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
