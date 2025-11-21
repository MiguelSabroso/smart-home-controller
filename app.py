import flet as ft
import asyncio
import random
from data_store import DataStore
from views.overview_view import OverviewView
from views.statistics_view import StatisticsView
from views.details_view import DetailsView

# --- STEP 9: Async Device Simulator (Background Task) ---
async def async_device_simulator(page):
    """
    Simulates background activity:
    1. Changing device states randomly (Ghost touch).
    2. Generating power consumption data for the chart.
    """
    while True:
        await asyncio.sleep(2) # Wait 2 seconds between simulations
        
        # A. Simulate Power Consumption (Random float between 1.0 and 9.0 kW)
        power_val = round(random.uniform(1.0, 9.0), 2)
        await DataStore.add_power_reading(power_val)

        # B. Occasionally change a device state (10% chance)
        if random.random() < 0.1:
            device = random.choice(DataStore.devices)
            
            if device["type"] in ["light", "fan"]: # Only toggle lights/fans automatically
                if device["is_slider"]:
                    # Random speed for fan
                    new_val = random.randint(0, 3)
                    await DataStore.update_device_value(device["id"], new_val, user="Simulator")
                else:
                    # Toggle light
                    new_status = "ON" if device["status"] == "OFF" else "OFF"
                    await DataStore.update_device_status(device["id"], new_status, user="Simulator")
            
            # Update UI if we changed something (The Pub/Sub inside DataStore handles the logic, 
            # but we might want to force a page update if needed, though controls usually update themselves)

# --- STEP 11: Assemble & Run ---
async def main(page: ft.Page):
    """
    Async Main entry point.
    """
    page.title = "Smart Home Controller - Async"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    def route_change(route):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(OverviewView(page))
            
        elif page.route == "/statistics":
            page.views.append(StatisticsView(page))
            
        elif page.route.startswith("/details/"):
            try:
                device_id = page.route.split("/")[2]
                page.views.append(DetailsView(page, device_id))
            except IndexError:
                page.go("/")

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Start Routing
    page.go(page.route)

    # Start the background simulation task
    page.run_task(async_device_simulator, page)

if __name__ == "__main__":
    ft.app(target=main)