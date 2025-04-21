import board
import time
import digitalio
import busio

from adafruit_ble import BLERadio
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL

DECIMALS = 3
LOOP_DELAY = 0.01
ENCODING = "utf-8"

def get_sensor_str(sensor: tuple) -> str:
    msg = f"{sensor[0]:2.{DECIMALS}f},{sensor[1]:2.{DECIMALS}f},{sensor[2]:2.{DECIMALS}f},"
    return msg

# initialize the i2c bus
i2c = board.I2C2()
while not i2c.try_lock():
    pass
print("I2C addresses found:", [hex(x) for x in i2c.scan()])
i2c.unlock()

# initialize the sensors
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)

# initialize the BLE radio
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)
print("Advertising UART...")
ble.start_advertising(advertisement)

start_time = time.monotonic()

# advertise the sensor data
while True:
    while ble.connected:
        accel = accel_gyro.acceleration
        gyro = accel_gyro.gyro
        magnetic = mag.magnetic

        time_msg = f"{time.monotonic() - start_time:.3f},"
        acc_msg = get_sensor_str(accel)
        gyr_msg = get_sensor_str(gyro)
        mag_msg = get_sensor_str(magnetic)
        msg = time_msg + acc_msg + gyr_msg + mag_msg + "\n"

        uart.write(msg.encode(ENCODING))
        time.sleep(LOOP_DELAY)
    if not ble.advertising:
        print("Restarting advertising")
        ble.start_advertising(advertisement)
        time.sleep(1.0)
    time.sleep(0.1)


