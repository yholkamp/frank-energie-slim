# Frank Energie Slim integratie

Deze integratie biedt een eenvoudige koppeling met Frank Energie om de gegevens van 'Slim Handelen' uit te lezen. Overige data, zoals de huidige energieprijzen, je maandkosten en dergelijke worden niet uitgelezen.
Op termijn komen hopelijk de functies van deze plugin ook terecht in een van de algemene Frank Energie-integraties, zodat alle gegevens van Frank Energie in één keer ingeladen kunnen worden.

Houd er rekening mee dat ook deze integratie werkt op basis van de API zoals die door de mobiele app van Frank Energie gebruikt wordt, updates van de app kunnen deze plugin verstoren.

## Installatie

[![Add to HACS](https://img.shields.io/badge/HACS-Add%20this%20repository-blue?style=for-the-badge&logo=home-assistant)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yholkamp&repository=frank-energie-slim&category=integration)

* Zorg voor een installatie van [Home Assistant](https://www.home-assistant.io/) met [HACS](https://hacs.xyz/).
* Toevoegen van de repository in HACS
  * Gebruik bovenstaande knop,
  * of voeg in HACS deze repository toe als 'custom repository',
  * of download een release en voeg de map uit 'custom_components' toe aan je eigen 'custom_components' folder.

* Herstart vervolgens Home Assistant
* Voeg de integratie toe zoals je gewend bent via Instellingen, Apparaten en Diensten, Toevoegen en zoek op "Frank Energie Slim Handelen".
* Vul hier je Frank Energie gebruikersnaam en wachtwoord in en sla op.

## Apparaten

Standaard voegt dit component minimaal 2 apparaten toe: één per batterij-set die je aan Frank Energie hebt gekoppeld en één 'totaal' apparaat met de totale waarden van alle batterijen. 
De meeste gebruikers zullen maar een batterij hebben maar wanneer je bijvoorbeeld 2 Sessy batterijen hebt dan kun je het totaal-apparaat gebruiken.

## Koppeling met Onbalansmarkt.com

Wil je jouw resultaten niet alleen zelf zien maar ook delen en vergelijken met andere systemen ? Volg dan de volgende stappen:

* Zorg eerst voor een afgeronde installatie van deze plugin en een account op [Onbalansmarkt.com](https://onbalansmarkt.com/).
* Voeg de volgende configuratie toe aan je Home Assistant `configuration.yaml` configuratiebestand: 


      rest_command:
        trigger_frank_energie_slim_onbalansmarkt:
          url: "https://onbalansmarkt.com/api/live"
          headers:
            Authorization: "Bearer VERVANG_DIT_DOOR_JOUW_APIKEY"
          method: POST
          payload: >
            {
                "timestamp": "{{ states('sensor.frank_slim_total_last_update') }}",
                "batteryResult": "{{ states('sensor.frank_slim_nettoresultaat_total') }}",
                "batteryResultTotal": "{{ states('sensor.frank_slim_trading_result_total') }}",
                "batteryCharge": "{{ states('sensor.frank_slim_average_soc') }}",
                "mode": "{{ states('sensor.frank_slim_total_last_mode') }}",
                "batteryResultEpex": "{{ states('sensor.frank_slim_epex_total') }}",
                "batteryResultImbalance": "{{ states('sensor.frank_slim_brutoresultaat_total') }}",
                "batteryResultCustom": "{{ states('sensor.frank_slim_frankslim_total') }}",
                "chargedToday": null,
                "dischargedToday": null,
                "chargerResult": null,
                "solarResult": null
            }
          content_type: "application/json"

* *Let op*: Frank Energie geeft de geladen of ontladen kWh van vandaag niet terug. Heb je deze waarden wel beschikbaar? Dan kun je ze toevoegen aan het script hierboven zodat ze op de site verschijnen.
* **Herstart Home Assistant of herlaad de configuratie.** Zonder deze actie kun je het RESTful command niet selecteren bij de volgende stappen.
* Maak een nieuwe 'Automation' aan via Instellingen - Automatiseringen en Scenes.
  * Kies als 'Wanneer' het type 'Entiteit', vervolgens 'Status' en kies de "Totaal batterijen laatste update" sensor.
  * Voeg een resultaat toe van type `RESTful Command: trigger_frank_energie_slim_onbalansmarkt` (als je begint met typen dan vult Home Assistant dit aan).
  * Sla de automation op.
* Ga ter controle naar 'Ontwikkelhulpmiddelen', 'Acties' en kies in de dropdown `RESTful Command: trigger_frank_energie_slim_onbalansmarkt`. Kies 'Actie uitvoeren' om je actuele data naar Onbalansmarkt.com te sturen.
  * Krijg je iets anders te zien dan `status: 200`? Mogelijk staat er een foutmelding met een toelichting in het antwoord van de server.

## Entiteiten

Daarnaast voegt de koppeling voegt meerdere entiteiten toe, als eerst worden de volgende per gekoppelde batterij toegevoegd: 

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
* sensor.frank_slim_total_last_update - datum en tijd van de laatste status update zoals getoond in de app.

## Testing

To execute the tests:

    python3 -m unittest discover tests


## License

MIT License
