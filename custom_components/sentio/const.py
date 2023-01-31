"""Constants for the sentio sauna integration."""

DOMAIN = "sentio"
VERSION = "0.0.17"
SIGNAL_UPDATE_SENTIO = "update_sentio"
MANUFACTURER = "Sentiotec"
DEVICE_NAME = "Sentio Pro Sauna Controller"

SERIAL_PORT = "serial_port"
DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 57600

MIN_SET_TEMP = 30
MAX_SET_TEMP = 110

HUMIDITY_MODELS = ("C3", "C3I", "D3", "D3I")
