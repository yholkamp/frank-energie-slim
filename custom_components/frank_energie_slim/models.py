from datetime import datetime

class Battery:
    def __init__(self, brand, capacity, created_at, external_reference, id, max_charge_power, max_discharge_power, provider, updated_at):
        self.brand = brand
        self.capacity = capacity
        self.created_at = datetime.fromisoformat(created_at)
        self.external_reference = external_reference
        self.id = id
        self.max_charge_power = max_charge_power
        self.max_discharge_power = max_discharge_power
        self.provider = provider
        self.updated_at = datetime.fromisoformat(updated_at)

class BatterySession:
    def __init__(self, device_id, period_start_date, period_end_date, period_epex_result, period_frank_slim, period_imbalance_result, period_total_result, period_trade_index, period_trading_result, sessions, total_trading_result):
        self.device_id = device_id
        self.period_start_date = datetime.fromisoformat(period_start_date)
        self.period_end_date = datetime.fromisoformat(period_end_date)
        self.period_epex_result = period_epex_result
        self.period_frank_slim = period_frank_slim
        self.period_imbalance_result = period_imbalance_result
        self.period_total_result = period_total_result
        self.period_trade_index = period_trade_index
        self.period_trading_result = period_trading_result
        self.sessions = sessions
        self.total_trading_result = total_trading_result