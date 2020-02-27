"""
Support for Sentiotec Pro Series Sauna controllers
"""

import logging
import time
from datetime import timedelta
import voluptuous as vol
import serial
from pysentio import SentioPro

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_FILENAME, CONF_NAME, STATE_UNKNOWN
from homeassistant.components.climate.const import HVAC_MODE_OFF
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.event import track_time_interval

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'sentio'
VERSION = '0.0.4'
SIGNAL_UPDATE_SENTIO = "sentio_update"

CONF_BAUDRATE = 'baudrate'
DEFAULT_CONF_BAUDRATE = '57600'
DEFAULT_CONF_NAME = 'Sauna'
SCAN_INTERVAL = timedelta(seconds=60)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_FILENAME, default='/dev/null'): cv.isdevice,
        vol.Optional(CONF_BAUDRATE, default=DEFAULT_CONF_BAUDRATE): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_CONF_NAME): cv.string,
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
  HEATER_TEMP: "get temp-heater val0\r",
  CONFIG: "get config\r",
  INFO: "get info\r",
  STATUS: "get status\r",
}

def setup(hass, config):
    """Setup component"""
    _LOGGER.info("Starting %s, %s", DOMAIN, VERSION)

    # Data that you want to share with your platforms
    hass.data[DOMAIN] = {
    }
    conf = config.get(DOMAIN)
    serial_port = conf.get(CONF_FILENAME)
    _LOGGER.debug("Config %s: filename = %s", DOMAIN, serial_port)
    serial_baudrate = conf.get(CONF_BAUDRATE)
    _LOGGER.debug("Config %s: baudrate = %s", DOMAIN, serial_baudrate)

    hass.data[DOMAIN]['sentio'] = SentioPro(serial_port, serial_baudrate)

    def poll_update(event_time):
      hass.data[DOMAIN]['sentio'].update()
      _LOGGER.debug("Calling dispatcher_send")
      dispatcher_send(hass, SIGNAL_UPDATE_SENTIO)

    poll_update(None)
    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('switch', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('climate', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('light', DOMAIN, {}, config)

    track_time_interval(hass, poll_update, SCAN_INTERVAL)
    dispatcher_send(hass, SIGNAL_UPDATE_SENTIO)

    
    return True