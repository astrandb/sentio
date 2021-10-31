# Sentio - Work in progress
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![stability-wip](https://img.shields.io/badge/stability-work_in_progress-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![Downloads for latest release](https://img.shields.io/github/downloads-pre/astrandb/sentio/latest/total.svg?style=for-the-badge)](https://github.com/astrandb/sentio/releases/latest)

Custom component for Sentiotec sauna controller for integration in  Home Assistant

## Preparation
In order to connect the Sentio Pro sauna controller you need a serial port with RS-485 interface on the server running Home Assistant. On Linux based machines the serial port is typically called /dev/ttyUSB0.

The user running Homeassistant should be added to group dialout.
## Installation
### Install with HACS (Recommended)
Add this repository as a custom repo in HACS settings.

Search for Sentio integration and install it directly from HACS. HACS will keep track of updates and you can easily upgrade to latest version.

HACS can be found [here](https://hacs.xyz/)
### Install manually
If you want to install manually, you probably already know how to proceed.
## Configuration
Goto Configuration->Integrations and press (+)
Enter the port to use. On Linux typically /dev/ttyUSB0 .
Relevant entities will be created in HA depending on what the connected controller model supports
## Links
[Documentation](https://github.com/astrandb/sentio/wiki)
