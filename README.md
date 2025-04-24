# UART-Bluetooth Low Energy
Stream UART BLE data from a microcontroller

## Install
To install the library run: `pip install uart-ble`

## Development
0. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
1. `make init` to create the virtual environment and install dependencies
2. `make format` to format the code and check for errors
3. `make test` to run the test suite
4. `make clean` to delete the temporary files and directories
5. `poetry publish --build` to build and publish to https://pypi.org/project/uart-ble


## Usage
```
import asyncio

from uart_ble import stream_uart_ble

if __name__ == "__main__":
    asyncio.run(stream_uart_ble(microcontroller_name="CIRCUITPY"))

```
