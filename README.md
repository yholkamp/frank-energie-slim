# Frank Energie Slim intergatie

Deze integratie biedt een eenvoudige koppeling met Frank Energie om de gegevens van 'Slim Handelen' uit te lezen.
Op de langere termijn worden deze functies hopelijk opgenomen in de algemene Frank Energie-integratie, zodat alle gegevens van Frank Energie in één keer ingeladen kunnen worden.

## Installatie

Gebruik deze knop:
[![Add to HACS](https://img.shields.io/badge/HACS-Add%20this%20repository-blue?style=for-the-badge&logo=home-assistant)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yholkamp&repository=frank-energie-slim&category=integration)

Of voeg in HACS deze repository toe als 'custom repository'. Herstart Home Assistant en voeg de installatie toe via Instellingen - Apparaten en Diensten - Toevoegen - Frank Energie Slim Handelen.

Tot slot kun je de repository ook clonen en de map uit 'custom_components' in je eigen 'components' zetten.

## Setup

Configuration is done via the Home Assistant UI (Integrations page). No YAML configuration is required.

## Testing

To execute the tests:

    python3 -m unittest discover tests


## License

MIT License