import flet as ft
import datetime
import asyncio
from enum import Enum

# --- STEP 6: Pub/Sub Logging System ---
class EventType(Enum):
    LOG_EVENT = "log_event"
    DEVICE_UPDATE = "device_update"
    POWER_UPDATE = "power_update"

class DataStore:
    """
    Centralized data store with Pub/Sub capabilities.
    """
    
    # Subscribers: list of callback functions
    _subscribers = []
    
    # Internal counter for the X-axis of the chart
    _x_counter = 0

    # STEP 2: Device Dictionary
    devices = [
        {
            "id": "light_1",
            "name": "Living Room Light",
            "type": "light",
            "icon": ft.Icons.LIGHTBULB,
            "status": "OFF",
            "is_slider": False,
            "description": "Tap to switch the light."
        },
        {
            "id": "door_1",
            "name": "Front Door",
            "type": "door",
            "icon": ft.Icons.DOOR_FRONT_DOOR,
            "status": "LOCKED",
            "is_slider": False,
            "description": "Tap to lock / unlock the door."
        },
        {
            "id": "thermostat_1",
            "name": "Thermostat",
            "type": "temp",
            "icon": ft.Icons.THERMOSTAT,
            "value": 22.0,
            "is_slider": True,
            "unit": "°C",
            "description": "Use slider to change temperature."
        },
        {
            "id": "fan_1",
            "name": "Ceiling Fan",
            "type": "fan",
            "icon": ft.Icons.WIND_POWER,
            "value": 0,
            "is_slider": True,
            "unit": "",
            "description": "0 = OFF, 3 = MAX."
        }
    ]

    logs = []
    
    # For Real-Time Chart (Step 10)
    power_history = [] 

    @staticmethod
    def subscribe(callback):
        """Register a callback to receive updates."""
        DataStore._subscribers.append(callback)

    @staticmethod
    async def publish(event_type: EventType, payload: dict):
        """Notify all subscribers of an event."""
        for callback in DataStore._subscribers:
            # We assume callbacks might be async
            if asyncio.iscoroutinefunction(callback):
                await callback(event_type, payload)
            else:
                callback(event_type, payload)

    @staticmethod
    def get_device_by_id(device_id):
        for device in DataStore.devices:
            if device["id"] == device_id:
                return device
        return None

    @staticmethod
    def get_logs_for_device(device_id):
        return [log for log in DataStore.logs if log["device"] == device_id]

    @staticmethod
    async def add_log(device_id, action, user="User"):
        new_log = {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "device": device_id,
            "action": action,
            "user": user
        }
        DataStore.logs.insert(0, new_log)
        # Notify subscribers (Step 6)
        await DataStore.publish(EventType.LOG_EVENT, new_log)

    @staticmethod
    async def update_device_status(device_id, new_status, user="User"):
        device = DataStore.get_device_by_id(device_id)
        if device:
            device["status"] = new_status
            await DataStore.add_log(device_id, f"Status changed to {new_status}", user)
            # Notify UI to update (Step 6)
            await DataStore.publish(EventType.DEVICE_UPDATE, device)

    @staticmethod
    async def update_device_value(device_id, new_value, user="User"):
        device = DataStore.get_device_by_id(device_id)
        if device:
            if device["value"] != new_value:
                device["value"] = new_value
                
                # We create a descriptive message for the log
                action_msg = f"Set to {new_value}{device.get('unit', '')}"
                if device["type"] == "fan":
                    action_msg = f"Speed set to {new_value}" if new_value > 0 else "Turned OFF"
                
                # We add the entry to the log
                await DataStore.add_log(device_id, action_msg, user)
                
                # Notify UI to update
                await DataStore.publish(EventType.DEVICE_UPDATE, device)

    @staticmethod
    async def add_power_reading(value):
        """Adds a new power reading for the chart."""
        # We use a global counter for X
        timestamp = DataStore._x_counter * 2 
        DataStore._x_counter += 1
        
        reading = {"x": timestamp, "y": value}
        DataStore.power_history.append(reading)
        
        # Keep history manageable
        if len(DataStore.power_history) > 20:
            DataStore.power_history.pop(0)
        
        await DataStore.publish(EventType.POWER_UPDATE, reading)