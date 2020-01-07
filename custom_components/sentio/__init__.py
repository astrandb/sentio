"""
Support for Sentiotec Pro Series Sauna controllers
"""

import logging
import time
import voluptuous as vol
import serial

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_FILENAME, STATE_UNKNOWN
from homeassistant.components.climate.const import HVAC_MODE_OFF

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'sentiotec_pro'
VERSION = '0.0.1'

CONF_BAUDRATE = 'baudrate'
DEFAULT_CONF_BAUDRATE = '57600'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_FILENAME, default='/dev/null'): cv.isdevice,
        vol.Optional(CONF_BAUDRATE, default=DEFAULT_CONF_BAUDRATE): cv.positive_int,
    })
}, extra=vol.ALLOW_EXTRA)

SAUNA = 'Sauna'
TARGET_TEMP = 'Target temp'
LIGHT = 'Light'
FAN = 'Fan'
AUX = 'Aux'
BENCH_TEMP = 'Bench Temp'
HEATER_TEMP = 'Heater Temp'
CONFIG = 'Config'
INFO = 'Info'
STATUS = 'Status'

CMD_DICT = {
    SAUNA: "get sauna\r",
    TARGET_TEMP: "get sauna val\r",
    LIGHT: "get light\r",
    FAN: "get fan\r",
    AUX: "get i-switch\r",
    BENCH_TEMP: "get temp-bench val\r",
    HEATER_TEMP: "get temp-heater val0",
    CONFIG: "get config\r",
    INFO: "get info\r",
    STATUS: "get status",
}

def setup(hass, config):
    """Setup component"""
    _LOGGER.info("Starting %s, %s", DOMAIN, VERSION)

    # Data that you want to share with your platforms
    hass.data[DOMAIN] = {
        'bench_temperature': 23,
        'heater_temperature': 60,
        'target_temperature': 90,
        'hvac_mode': HVAC_MODE_OFF,
        'sauna_on' : False,
        'sauna_light_on' : False
    }
    conf = config.get(DOMAIN)
    serial_port = conf.get(CONF_FILENAME)
    _LOGGER.debug("Config %s: filename = %s", DOMAIN, serial_port)
    serial_baudrate = conf.get(CONF_BAUDRATE)
    _LOGGER.debug("Config %s: baudrate = %s", DOMAIN, serial_baudrate)

    _ser = serial.Serial(port=serial_port, baudrate=serial_baudrate, timeout=2)
    _attributes = {
      SAUNA: STATE_UNKNOWN,
      LIGHT: STATE_UNKNOWN,
      FAN: STATE_UNKNOWN,
      BENCH_TEMP: STATE_UNKNOWN,
    }
    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('switch', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('climate', DOMAIN, {}, config)

    return True