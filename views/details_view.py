import flet as ft
from data_store import DataStore

def DetailsView(page: ft.Page, device_id: str):
    """
    Generates the content for the Details page for a specific device.
    """
    
    device = DataStore.get_device_by_id(device_id)
    device_logs = DataStore.get_logs_for_device(device_id)
    
    if not device:
        return ft.View(route="/404", controls=[ft.Text("Device not found")])

    actions_list = ft.Column(spacing=10)
    for log in device_logs:
        actions_list.controls.append(
            ft.Text(f"{log['time']} - {log['action']} ({log['user']})", size=16, color=ft.Colors.BLUE_GREY_700)
        )
    
    if not device_logs:
        actions_list.controls.append(ft.Text("No recent actions.", italic=True))

    return ft.View(
        route=f"/details/{device_id}",
        controls=[
            ft.AppBar(
                title=ft.Text(f"Smart Home Controller", color=ft.Colors.BLUE_GREY_900, weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.WHITE
            ),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            padding=20,
                            bgcolor=ft.Colors.BLUE_GREY_50,
                            border_radius=10,
                            width=float('inf'),
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.Text(f"{device['name']} details", size=28, weight=ft.FontWeight.BOLD),
                                    ft.Divider(),
                                    ft.Text(f"ID: {device['id']}", size=16),
                                    ft.Text(f"Type: {device['type']}", size=16),
                                    ft.Text(f"Current State: {device.get('status') or device.get('value')}", size=16, weight=ft.FontWeight.BOLD),
                                ]
                            )
                        ),
                        ft.Divider(height=30),
                        ft.Text("Recent actions", size=22, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Container(
                            padding=15,
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=10,
                            content=actions_list
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Back to overview",
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda _: page.go("/")
                        )
                    ]
                )
            )
        ]
    )