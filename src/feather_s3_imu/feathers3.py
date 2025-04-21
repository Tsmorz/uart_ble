"""Sample doc string."""

import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction

# Init Blink LED
led13 = DigitalInOut(board.LED)
led13.direction = Direction.OUTPUT

# Init LDO2 Pin
ldo2 = DigitalInOut(board.LDO2)
ldo2.direction = Direction.OUTPUT

# Setup the BATTERY voltage sense pin
vbat_voltage = AnalogIn(board.BATTERY)

# Setup the VBUS sense pin
vbus_sense = DigitalInOut(board.VBUS_SENSE)
vbus_sense.direction = Direction.INPUT


# Helper functions
def led_blink():
    """Set the internal LED IO13 to its inverse state."""
    led13.value = not led13.value


def led_set(state):
    """Set the internal LED IO13 to this state."""
    led13.value = state


def set_ldo2_power(state):
    """Enable or Disable power to the onboard NeoPixel to either show color, or to reduce power for deep sleep."""
    ldo2.value = state


def get_battery_voltage():
    """Get the approximate battery voltage."""
    # This formula should show the nominal 4.2V max capacity (approximately) when 5V is present and the
    # VBAT is in charge state for a 1S LiPo battery with a max capacity of 4.2V
    ADC_RESOLUTION = 2**16 - 1
    AREF_VOLTAGE = 3.3
    R1 = 442000
    R2 = 160000
    return vbat_voltage.value / ADC_RESOLUTION * AREF_VOLTAGE * (R1 + R2) / R2


def rgb_color_wheel(wheel_pos):
    """Color wheel to allow for cycling through the rainbow of RGB colors."""
    wheel_pos = wheel_pos % 255

    if wheel_pos < 85:
        return 255 - wheel_pos * 3, 0, wheel_pos * 3
    elif wheel_pos < 170:
        wheel_pos -= 85
        return 0, wheel_pos * 3, 255 - wheel_pos * 3
    else:
        wheel_pos -= 170
        return wheel_pos * 3, 255 - wheel_pos * 3, 0
