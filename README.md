# Frank Energie Slim integratie

Deze integratie biedt een eenvoudige koppeling met Frank Energie om de gegevens van 'Slim Handelen' uit te lezen.
Op de langere termijn worden deze functies hopelijk opgenomen in de algemene Frank Energie-integratie, zodat alle gegevens van Frank Energie in één keer ingeladen kunnen worden.

## Installatie

[![Add to HACS](https://img.shields.io/badge/HACS-Add%20this%20repository-blue?style=for-the-badge&logo=home-assistant)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yholkamp&repository=frank-energie-slim&category=integration)

Gebruik bovenstaande knop of voeg in HACS deze repository toe als 'custom repository'. 

Of download een release en voeg de map uit 'custom_components' toe aan je eigen 'custom_components' folder.


Herstart vervolgens Home Assistant en voeg de integratie toe via Instellingen - Apparaten en Diensten - Toevoegen - Frank Energie Slim Handelen.

## Setup

Stel de koppeling in via de Home Assistant UI via Apparaten & Diensten.

## Entities

Dit component voegt meerdere entiteiten toe, als eerst worden de volgende per gekoppelde batterij toegevoegd: 

* sensor.frank_slim_{batteryId}_brutoresultaat
* sensor.frank_slim_{batteryId}_epex
* sensor.frank_slim_{batteryId}_frankslim
* sensor.frank_slim_{batteryId}_handelsresultaat
* sensor.frank_slim_{batteryId}_nettoresultaat
* sensor.frank_slim_{batteryId}_soc
* sensor.frank_slim_{batteryId}_trading_result
* sensor.frank_slim_{batteryId}_mode

Daarnaast worden deze sensoren toegevoegd voor een gemiddelde (voor state of charge) of de som van de batterijresultaten:

* sensor.frank_slim_average_soc
* sensor.frank_slim_epex_total
* sensor.frank_slim_frankslim_total
* sensor.frank_slim_handelsresultaat_total
* sensor.frank_slim_brutoresultaat_total
* sensor.frank_slim_nettoresultaat_total
* sensor.frank_slim_total_last_mode
* sensor.frank_slim_trading_result_total

## Testing

To execute the tests:

    python3 -m unittest discover tests


## License

MIT License