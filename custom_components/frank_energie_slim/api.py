import requests
from datetime import datetime
import logging

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

        if 'errors' in data:
            for error in data['errors']:
                if error['message'] == "user-error:auth-not-authorised":
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
        logging.getLogger(__name__).info(f"Frank Energie login response: {response}")
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
                            cumulativeTradingResult
                            date
                            tradingResult
                        }
                        totalTradingResult
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