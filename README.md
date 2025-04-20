# Frank Energie Slim integratie

Deze integratie biedt een eenvoudige koppeling met Frank Energie om de gegevens van 'Slim Handelen' uit te lezen.
Op de langere termijn worden deze functies hopelijk opgenomen in de algemene Frank Energie-integratie, zodat alle gegevens van Frank Energie in één keer ingeladen kunnen worden.

## Installatie

[![Add to HACS](https://img.shields.io/badge/HACS-Add%20this%20repository-blue?style=for-the-badge&logo=home-assistant)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yholkamp&repository=frank-energie-slim&category=integration)

Gebruik bovenstaande knop of voeg in HACS deze repository toe als 'custom repository'. 

Of download een release en voeg de map uit 'custom_components' toe aan je eigen 'custom_components' folder.


Herstart vervolgens Home Assistant en voeg de integratie toe via Instellingen - Apparaten en Diensten - Toevoegen - Frank Energie Slim Handelen.


## Setup

Configuration is done via the Home Assistant UI (Integrations page). No YAML configuration is required.

## Testing

To execute the tests:

    python3 -m unittest discover tests


## License

MIT License