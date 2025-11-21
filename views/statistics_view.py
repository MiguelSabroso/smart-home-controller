import flet as ft
from data_store import DataStore, EventType

def StatisticsView(page: ft.Page):
    """
    Generates the content for the Statistics page with Real-Time Chart.
    """
    
    # --- UI Components ---
    
    # 1. Log Table
    log_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Time")),
            ft.DataColumn(ft.Text("Device")),
            ft.DataColumn(ft.Text("Action")),
            ft.DataColumn(ft.Text("User")),
        ],
        rows=[],
        border=ft.border.all(1, ft.Colors.GREY_300),
    )

    def refresh_logs():
        """Rebuilds the DataRows from DataStore."""
        log_table.rows.clear()
        # Show last 10 logs
        for log in DataStore.logs[:10]:
            log_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(log["time"])),
                    ft.DataCell(ft.Text(log["device"])),
                    ft.DataCell(ft.Text(log["action"])),
                    ft.DataCell(ft.Text(log["user"])),
                ])
            )
        if log_table.page:
            log_table.update()

    # Initial load logs
    refresh_logs()

    # 2. Real-Time Line Chart
    
    # NEW: Load existing history from DataStore when initializing the view
    initial_data_points = [
        ft.LineChartDataPoint(p["x"], p["y"]) for p in DataStore.power_history
    ]
    
    chart_data_series = ft.LineChartData(
        data_points=initial_data_points, # We use the retrieved data
        stroke_width=3,
        color=ft.Colors.CYAN,
        curved=True,
        stroke_cap_round=True,
        below_line_bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.CYAN)
    )

    # If we already have data, we want the window to show the last ~40 seconds
    initial_min_x = 0
    initial_max_x = 40
    
    if initial_data_points:
        last_x = initial_data_points[-1].x
        # If time has advanced beyond the initial window (40), we move the window
        if last_x > 40:
            initial_max_x = last_x
            initial_min_x = last_x - 40

    chart = ft.LineChart(
        data_series=[chart_data_series],
        border=ft.Border(
            bottom=ft.BorderSide(2, ft.Colors.GREY_400),
            left=ft.BorderSide(2, ft.Colors.GREY_400)
        ),
        min_y=0,
        max_y=10, 
        min_x=initial_min_x, # Adjusted window
        max_x=initial_max_x, # Adjusted window
        expand=True
    )

    # --- Event Handler for Updates ---
    async def on_stats_update(event_type, payload):
        if event_type == EventType.LOG_EVENT:
            refresh_logs()
        
        elif event_type == EventType.POWER_UPDATE:
            new_point = ft.LineChartDataPoint(payload["x"], payload["y"])
            chart_data_series.data_points.append(new_point)
            
            if len(chart_data_series.data_points) > 20:
                chart_data_series.data_points.pop(0)
                # Adjust the window dynamically
                chart.min_x = chart_data_series.data_points[0].x
                chart.max_x = chart_data_series.data_points[-1].x

            if chart.page:
                chart.update()

    DataStore.subscribe(on_stats_update)

    return ft.View(
        route="/statistics",
        controls=[
            ft.AppBar(title=ft.Text("Smart Home Controller", color=ft.Colors.BLUE_GREY_900, weight=ft.FontWeight.BOLD),  bgcolor=ft.Colors.WHITE),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text("Live Power Consumption (kW-simulated)", size=20, weight=ft.FontWeight.BOLD),
                        
                        ft.Container(
                            height=250,
                            padding=20,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=10,
                            content=chart 
                        ),

                        ft.Divider(height=40),
                        
                        ft.Text("Live Action Log", size=20, weight=ft.FontWeight.BOLD),
                        
                        ft.Column([log_table], scroll=ft.ScrollMode.ADAPTIVE)
                    ]
                )
            )
        ],
        navigation_bar=ft.NavigationBar(
            selected_index=1,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label="Overview"),
                ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS, label="Statistics"),
            ],
            on_change=lambda e: page.go("/") if e.control.selected_index == 0 else page.go("/statistics")
        )
    )