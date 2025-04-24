"""Sample doc string."""

import asyncio

from bleak import BleakClient, BleakScanner
from loguru import logger

from uart_ble.definitions import BLE_TIMEOUT, TX_CHAR_UUID


class BLEHandler:
    """BLE handler that stores only the most recent line."""

    def __init__(self):
        self._buffer = b""
        self.latest_line = None
        self._new_data_event = asyncio.Event()

    def handle_rx(self, _, data):
        """Handle received data."""
        self._buffer += data
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            self.latest_line = line.decode("utf-8").strip()
            self._new_data_event.set()  # Signal that new data is available

    async def get_latest(self) -> str:
        """Wait for and return the latest line of data."""
        await self._new_data_event.wait()
        self._new_data_event.clear()
        return self.latest_line


class BLEDevice:
    """BLE device class."""

    def __init__(self, target_name: str):
        self.target_name: str = target_name
        self.name: str | None = None
        self.address: str | None = None
        self.client: BleakClient | None = None
        self.handler: BLEHandler | None = None

    async def find_device(self) -> bool:
        """Find the BLE device with the given name."""
        devices = await BleakScanner.discover(timeout=BLE_TIMEOUT)
        device = next(
            (d for d in devices if d.name and self.target_name in d.name), None
        )

        if not device:
            self._list_devices(devices)
            logger.error(f"Could not find device with name '{self.target_name}'.")
            return False

        self.address = device.address
        self.name = device.name
        logger.info(f"Found device: {self.name} — {self.address}")
        return True

    @staticmethod
    def _list_devices(devices) -> None:
        """List the found BLE devices."""
        for device in devices:
            logger.info(
                f"{device.name or 'Unnamed'} — {device.address} — RSSI: {device.rssi} dBm"
            )

    async def connect_and_subscribe(self) -> BLEHandler:
        """Connect to the BLE device and start notifications.

        :return: BLEHandler instance for receiving data.
        """
        if not self.address:
            raise ValueError("Device address not set. Call find_device() first.")

        self.client = BleakClient(self.address)
        await self.client.connect()
        logger.info("Connected!")

        self.handler = BLEHandler()
        await self.client.start_notify(TX_CHAR_UUID, self.handler.handle_rx)

        return self.handler

    async def disconnect(self) -> None:
        """Stop notifications and disconnect from the BLE device."""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(TX_CHAR_UUID)
            await self.client.disconnect()
            logger.info("Disconnected.")


async def stream_from_ble_device(device_name: str):
    """Stream data from the BLE device."""
    device = BLEDevice(device_name)
    found = await device.find_device()
    if not found:
        return

    try:
        handler = await device.connect_and_subscribe()
        while True:
            input("Press Enter to get the latest IMU reading...")
            latest = await handler.get_latest()
            logger.info(f"📥 Latest: {latest}")
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Disconnecting...")
    except asyncio.CancelledError:
        # Handle task cancellation gracefully without traceback
        logger.info("Task was canceled. Exiting gracefully.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        await device.disconnect()
        logger.info("Disconnected gracefully.")


if __name__ == "__main__":
    microcontroller_name = "YourDeviceName"
    asyncio.run(stream_from_ble_device(microcontroller_name))
