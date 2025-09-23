import requests
from datetime import datetime
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)

class FrankEnergie:
    def __init__(self, auth_token=None, refresh_token=None):
        self.DATA_URL = "https://frank-graphql-prod.graphcdn.app/"
        self.auth = {"auth_token": auth_token, "refresh_token": refresh_token} if auth_token or refresh_token else None

    def query(self, query_data):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Python/FrankV1',
        }
        if self.auth:
            headers['Authorization'] = f"Bearer {self.auth['authToken']}"

        response = requests.post(self.DATA_URL, json=query_data, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Log GraphQL request when API responds with errors to aid debugging
        errors = data.get('errors') if isinstance(data, dict) else None
        if isinstance(errors, list) and errors:
            # Build a redacted copy of the request to avoid leaking secrets
            safe_query = query_data
            try:
                if isinstance(query_data, dict):
                    safe_query = dict(query_data)
                    vars_in = safe_query.get('variables') if isinstance(safe_query.get('variables'), dict) else None
                    if isinstance(vars_in, dict):
                        vars_copy = dict(vars_in)
                        for k in ['password', 'email', 'authToken', 'refreshToken', 'token', 'authorization', 'Authorization']:
                            if k in vars_copy and vars_copy[k] is not None:
                                vars_copy[k] = '***REDACTED***'
                        safe_query['variables'] = vars_copy
            except Exception:
                # Best-effort redaction; ignore redaction failures
                pass
            _LOGGER.error("GraphQL returned errors: %s; Request payload: %s", errors, safe_query)

            # Preserve explicit handling of authentication errors
            for error in errors:
                if isinstance(error, dict) and error.get('message') == "user-error:auth-not-authorised":
                    raise Exception("Authentication required")

        return data

    def login(self, username, password):
        query = {
            "query": """
                mutation Login($email: String!, $password: String!) {
                    login(email: $email, password: $password) {
                        authToken
                        refreshToken
                    }
                }
            """,
            "operationName": "Login",
            "variables": {"email": username, "password": password}
        }

        response = self.query(query)
        # If errors are present, raise the first error message
        if response and 'errors' in response and response['errors']:
            raise Exception(response['errors'][0].get('message', 'Onbekende fout'))
        # Defensive: check for expected structure
        if not response or 'data' not in response:
            raise Exception("Inloggen mislukt: controleer gebruikersnaam en wachtwoord.")
        self.auth = response['data']['login']
        return self.auth

    def get_smart_batteries(self):
        if not self.auth:
            raise Exception("Authentication required")

        query = {
            "query": """
                query SmartBatteries {
                    smartBatteries {
                        id
                   }
              }
            """,
            "operationName": "SmartBatteries"
        }

        return self.query(query)

    def get_smart_battery_details(self, device_id):
        if not self.auth:
            raise Exception("Authentication required")

        query = {
            "query": """
                query SmartBattery($deviceId: String!) {
                    smartBattery(deviceId: $deviceId) {
                        brand
                        capacity
                        id
                        settings {
                            batteryMode
                            imbalanceTradingStrategy
                            selfConsumptionTradingAllowed
                        }
                    }
                    smartBatterySummary(deviceId: $deviceId) {
                        lastKnownStateOfCharge
                        lastKnownStatus
                        lastUpdate
                        totalResult
                    }
                }
            """,
            "operationName": "SmartBattery",
            "variables": {"deviceId": device_id}
        }
        return self.query(query)

    def get_smart_battery_sessions(self, device_id, start_date, end_date):
        if not self.auth:
            raise Exception("Authentication required")

        query = {
            "query": """
                query SmartBatterySessions($startDate: String!, $endDate: String!, $deviceId: String!) {
                    smartBatterySessions(
                        startDate: $startDate
                        endDate: $endDate
                        deviceId: $deviceId
                    ) {
                        deviceId
                        periodStartDate
                        periodEndDate
                        periodEpexResult
                        periodFrankSlim
                        periodImbalanceResult
                        periodTotalResult
                        periodTradeIndex
                        periodTradingResult
                        sessions {
                            cumulativeResult
                            date
                            result
                        }
                    }
                }
            """,
            "operationName": "SmartBatterySessions",
            "variables": {
                "deviceId": device_id,
                "startDate": start_date.strftime('%Y-%m-%d'),
                "endDate": end_date.strftime('%Y-%m-%d')
            }
        }

        return self.query(query)

    def is_authenticated(self):
        return self.auth is not None