# Sentio - Documentation
## Configuration options
| Parameter          | Description                                          | Default       |
|--------------------|------------------------------------------------------|-----------    |
| filename           | filename of the serial port  (required)              | /dev/ttyUSB0  |
| baudrate           | baudrate for the serial port                         | 57600         |
| name               | base name for entities                               | sentio        |

## Example
```yaml
sentio:
  filename: /dev/ttyUSB0
  baudrate: 57600
```