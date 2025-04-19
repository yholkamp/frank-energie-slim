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

- `frank_energie.battery_<id>_trading_result` (Handelsresultaat totaal)
- `frank_energie.battery_<id>_mode` (Thuisbatterij modus)
- `frank_energie.battery_<id>_soc` (Thuisbatterij SoC)
- `frank_energie.battery_<id>_epex` (EPEX-correctie vandaag)
- `frank_energie.battery_<id>_frankslim` (Frank Slim vandaag)
- `frank_energie.battery_<id>_handelsresultaat` (Handelsresultaat vandaag)
- `frank_energie.battery_<id>_brutoresultaat` (Brutoresultaat vandaag)
- `frank_energie.battery_<id>_nettoresultaat` (Totaalresultaat vandaag)

And the following totals entities:

- `frank_energie.periodEpexResult_total` (EPEX-correctie vandaag Totaal)
- `frank_energie.periodFrankSlim_total` (Frank Slim vandaag Totaal)
- `frank_energie.periodImbalanceResult_total` (Handelsresultaat vandaag Totaal)
- `frank_energie.periodTradingResult_total` (Brutoresultaat vandaag Totaal)
- `frank_energie.periodTotalResult_total` (Totaalresultaat vandaag Totaal)
- `frank_energie_total_avg_soc` (Gemiddelde SoC batterijen)
- `frank_energie_total_last_mode` (Laatste batterijmodus)

## Setup

Configuration is done via the Home Assistant UI (Integrations page). No YAML configuration is required.

## Testing

To execute the tests:

    python3 -m unittest discover tests


## License

MIT License