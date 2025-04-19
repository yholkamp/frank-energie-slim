# Frank Energie Integration

[![Add to HACS](https://img.shields.io/badge/HACS-Add%20this%20repository-blue?style=for-the-badge&logo=home-assistant)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yholkamp&repository=frank-energie-slim&category=integration)

This is a Home Assistant integration for Frank Energie.

## Installation

1. Clone this repository into your Home Assistant `custom_components` folder.
2. Restart Home Assistant.

## Features

- Polls Frank Energie API every 5 minutes.
- Publishes data as Home Assistant entities.

## Example Entities

After setup, the following Home Assistant entities will be created (per battery):

- `frank_energie.battery_<id>_capacity` (Battery capacity)
- `frank_energie.battery_<id>_trading_result` (Total trading result)
- `frank_energie.battery_<id>_epex` (EPEX-correctie)
- `frank_energie.battery_<id>_frankslim` (Frank Slim)
- `frank_energie.battery_<id>_handelsresultaat` (Handelsresultaat)
- `frank_energie.battery_<id>_totaalresultaat` (Totaal Resultaat)

## Setup

Configuration is done via the Home Assistant UI (Integrations page). No YAML configuration is required.

## Testing

To execute the tests:

    python3 -m unittest discover tests


## License

MIT License