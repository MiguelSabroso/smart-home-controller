import flet as ft
from data_store import DataStore, EventType

def OverviewView(page: ft.Page):
    """
    Generates the content for the Overview/Main Dashboard page.
    """

    def navigate_to_details(e):
        device_id = e.control.data
        page.go(f"/details/{device_id}")

    # Dictionary to keep track of UI controls by device ID for real-time updates
    device_status_texts = {}
    device_buttons = {}

    # --- Event Handler for Pub/Sub Updates ---
    async def on_store_update(event_type, payload):
        if event_type == EventType.DEVICE_UPDATE:
            device_id = payload["id"]
            
            # Update Status Text
            if device_id in device_status_texts:
                control = device_status_texts[device_id]
                if control.page:
                    device = payload
                    new_text = f"Status: {device.get('status')}"
                    if device["is_slider"]:
                        new_text = f"Status: {device.get('value')}{device.get('unit', '')}"
                    control.value = new_text
                    control.update()

            # Update Button Text (if applicable)
            if device_id in device_buttons and not payload["is_slider"]:
                btn = device_buttons[device_id]
                if btn.page:
                    if payload["type"] == "door":
                        btn.text = "Lock" if payload["status"] == "UNLOCKED" else "Unlock"
                    else:
                        btn.text = "Turn OFF" if payload["status"] == "ON" else "Turn ON"
                    btn.update()

    # Subscribe to DataStore events
    DataStore.subscribe(on_store_update)

    # --- UI Creation Helper ---
    def create_device_card(device):
        # 1. Initial State
        initial_status_text = f"Status: {device.get('status')}"
        if device["is_slider"]:
            initial_status_text = f"Set point: {device.get('value')}{device.get('unit', '')}"
        
        # 2. Create Controls
        status_txt = ft.Text(initial_status_text, color=ft.Colors.GREY_700)
        
        # Register control for updates
        device_status_texts[device["id"]] = status_txt

        # 3. Event Handlers
        async def on_toggle_click(e):
            current_status = device.get("status")
            new_status = ""
            if device["type"] == "door":
                new_status = "UNLOCKED" if current_status == "LOCKED" else "LOCKED"
            else:
                new_status = "ON" if current_status == "OFF" else "OFF"
            
            await DataStore.update_device_status(device["id"], new_status)

        async def on_slider_change(e):
            new_val = int(e.control.value)
            await DataStore.update_device_value(device["id"], new_val)
            status_txt.value = f"Set point: {new_val}{device.get('unit', '')}"
            if status_txt.page:
                status_txt.update()

        # 4. Interactive Element
        interactive_control = None
        if device["is_slider"]:
            interactive_control = ft.Slider(
                min=0, max=30 if device["unit"] == "°C" else 3, 
                divisions=30 if device["unit"] == "°C" else 3,
                value=device["value"],
                thumb_color=ft.Colors.BLUE_500,
                active_color=ft.Colors.BLUE_200,
                on_change=on_slider_change
            )
        else:
            btn_text = "Turn ON"
            if device["status"] == "ON": btn_text = "Turn OFF"
            if device["status"] == "LOCKED": btn_text = "Unlock"
            if device["status"] == "UNLOCKED": btn_text = "Lock"
            
            interactive_control = ft.ElevatedButton(
                text=btn_text,
                bgcolor=ft.Colors.WHITE,
                color=ft.Colors.BLUE_700,
                elevation=0,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=18), # Bordes redondeados
                ),
                on_click=on_toggle_click
            )
            device_buttons[device["id"]] = interactive_control

        # 5. Card Layout & Colors
        bg_color = ft.Colors.BLUE_50
        icon_color = ft.Colors.BLUE_GREY_800

        if device["type"] == "light":
            bg_color = ft.Colors.YELLOW_50
            icon_color = ft.Colors.AMBER_700
        elif device["type"] == "door":
            bg_color = ft.Colors.BLUE_GREY_50
            icon_color = ft.Colors.BLUE_GREY_700
        elif device["type"] == "temp":
            bg_color = ft.Colors.RED_50
            icon_color = ft.Colors.RED_700
            if device["is_slider"]:
                status_txt.value = f"Set point: {device.get('value')}{device.get('unit', '')}"
        elif device["type"] == "fan":
            bg_color = ft.Colors.CYAN_50
            icon_color = ft.Colors.CYAN_700
            if device["is_slider"]:
                status_txt.value = f"Fan speed: {device.get('value')}"
                if device["value"] == 0:
                     status_txt.value = "Fan speed: OFF"
        
        # Construction of the list of controls for the card
        card_controls = [
            ft.Row(controls=[
                ft.Icon(device["icon"], size=30, color=icon_color),
                ft.Text(device["name"], size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900)
            ]),
            status_txt,
            ft.Text(device["description"], size=12, italic=True, color=ft.Colors.GREY_600),
            ft.Container(height=10),
        ]

        # Differentiated Layout Logic
        details_btn = ft.TextButton(
            "Details", 
            data=device["id"], 
            on_click=navigate_to_details,
            style=ft.ButtonStyle(color=ft.Colors.BLUE_GREY_700)
        )

        if device["is_slider"]:
            card_controls.append(interactive_control)
            card_controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[details_btn]
                )
            )
        else:
            card_controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        details_btn,
                        interactive_control
                    ]
                )
            )

        return ft.Container(
            padding=20,
            bgcolor=bg_color,
            border_radius=15,
            content=ft.Column(controls=card_controls)
        )

    # --- Assembly ---
    on_off_controls = []
    slider_controls = []

    for device in DataStore.devices:
        card = create_device_card(device)
        if device["is_slider"]:
            slider_controls.append(ft.Column([card], expand=1))
        else:
            on_off_controls.append(ft.Column([card], expand=1))

    return ft.View(
        route="/",
        controls=[
            ft.AppBar(
                title=ft.Text("Smart Home Controller", color=ft.Colors.BLUE_GREY_900, weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.WHITE
            ),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text("On/Off devices", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row(controls=on_off_controls),
                        ft.Divider(height=30),
                        ft.Text("Slider controlled devices", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row(controls=slider_controls),
                    ]
                )
            )
        ],
        navigation_bar=ft.NavigationBar(
            selected_index=0,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label="Overview"),
                ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS, label="Statistics"),
            ],
            on_change=lambda e: page.go("/statistics") if e.control.selected_index == 1 else page.go("/")
        )
    )