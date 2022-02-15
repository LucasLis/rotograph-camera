# Rotograph Camera

## Installing

- Head to [releases](https://github.com/LucasLis/rotograph-camera/releases) and download the latest zip file for your device.
- Extract the folder.
- On Debian based systems:
  - Install the following package using apt:
  - `python3-opengl` (`sudo apt install python3-opengl`)
- Run the installer: `bash install.sh`
- Follow the instructions.

## Development

### Installing Dependencies

```sh
poetry install
```

### Running

```sh
poetry run python camera.py
```

## Todo

- Fix camera colour adjustments
- Look into camera time out
