# Rotograph Camera

## Installing

- Head to [releases](https://github.com/LucasLis/rotograph-camera/releases) and download the latest zip file for your device.
- Extract the folder.
- Run the installer: `bash install.sh`
- Follow the instructions.

## FAQ

- **The application freezes when I disconnect the camera, what should I do?**

  In most cases, the application will unfreeze when the camera is plugged back in, however if it does not you should restart the program. This is an issue with how PyGame handles uninitialised cameras, and cannot be solved easily.

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

- Look into camera time out
