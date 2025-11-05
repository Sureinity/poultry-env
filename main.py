import random
import datetime
from time import time

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Static

from hardware_manager import get_environmental_data, get_co2_data, MotionSensor

class PoultryApp(App):
    """A Textual dashboard for Poultry Monitoring System."""

    CSS_PATH = "styles.css"
    
    # Declaring the widgets that will appear in App
    def compose(self) -> ComposeResult:
        yield Header(id="header", name="FlockEye Real-Time Monitoring Dashboard")
        
        with Vertical(id="main-container"):
            # System status banner
            yield Static("INITIALIZING...", id="status-panel")

            # Environmental Data Panel
            with Vertical(classes="panel"):
                yield Static("[bold]ENVIRONMENTAL DATA[/bold]", classes="panel-title")
                yield Static("Temperature: --", id="temperature-display")
                yield Static("Humidity:    --", id="humidity-display")
                yield Static("CO2 Level:   --", id="co2-display")

            # Flock Activity Panel
            with Vertical(classes="panel"):
                yield Static("[bold]FLOCK ACTIVITY[/bold]", classes="panel-title")
                yield Static("Motion Status: --", id="motion-status-display")
                yield Static("Last Motion:   --", id="last-motion-display")
        
        yield Footer(id="footer")
    def on_mount(self) -> None:
        """Called when the app is first mounted. We start our update timer here."""
        self.motion_tracker = MotionSensor(inactivity_threshold_sec=7200)

        # Set an interval to call the 'update_data' method every 3 seconds
        self.set_interval(3, self.update_data)

    def update_data(self) -> None:
        """This method will be called every 3 seconds to update the dashboard."""
        
        # CO2 data
        co2_data = get_co2_data()
        
        # DHT22 Sensor data
        env_data = get_environmental_data()
        temp = env_data['temperature']
        humidity = env_data['humidity']

        # PIR Motion Sensor data
        self.motion_tracker.update()
        motion_data = self.motion_tracker.get_status()

        # Update the environmental UI panel
        temp_widget = self.query_one("#temperature-display", Static)
        hum_widget = self.query_one("#humidity-display", Static)
        co2_widget = self.query_one("#co2-display", Static)

        current_temp = env_data['temperature']
        if current_temp is not None:
            temp_widget.update(f"Temperature: {current_temp:.1f} °C")
        else:
            temp_widget.update("Temperature: [bold red]ERROR[bold red]")

        if env_data['humidity'] is not None:
            hum_widget.update(f"Humidity:    {env_data['humidity']:.1f} %")
        else:
            hum_widget.update("Humidity:    [bold red]ERROR[bold red]")
        
        if co2_data is not None:
            co2_widget.update(f"CO2 Level:   {co2_data} PPM")
        else:
            co2_widget.update("CO2 Level:   [bold red]ERROR[bold red]")

        # Update the activity panel
        motion_status_widget = self.query_one("#motion-status-display", Static)
        last_motion_widget = self.query_one("#last-motion-display", Static)

        motion_status_text = "[bold green]ACTIVE[bold green]" if motion_data['motion_now'] else "[bold red]INACTIVE[red]"
        motion_status_widget.update(f"Motion Status: {motion_status_text}")
        last_motion_widget.update(f"Last Motion:   {motion_data['last_seen_str']}")
        
        # Overall System Status
        status_panel = self.query_one("#status-panel", Static)
        
        system_status = "NORMAL"

        # Prioritize alerts: Critical alerts override warnings
        if current_temp is not None and current_temp > 35.0:
            system_status = "CRITICAL"
        elif motion_data['inactivity_alert']:
            system_status = "CRITICAL"
        elif co2_data is not None and co2_data > 2000: # Using real CO2 data
            system_status = "WARNING"

        status_panel.update(system_status)
        status_panel.remove_class("normal", "warning", "critical")
        status_panel.add_class(system_status.lower())

        # Update the footer
        footer = self.query_one("#footer", Footer)
        footer.title = f"Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


if __name__ == "__main__":
    app = PoultryApp()
    app.run()
