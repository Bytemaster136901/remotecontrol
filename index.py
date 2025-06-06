"""
Bluetooth-to-Chromecast Python bridge.
- Discovers all Chromecasts on the network.
- If multiple, allows navigation with arrow keys sent from Bluetooth.
- Uses Enter/OK to select.
- Forwards subsequent commands to the selected Chromecast.
Requires: pychromecast, bleak (for BLE), and Python 3.7+
"""

import asyncio
from bleak import BleakServer, BleakGATTCharacteristic
import pychromecast

# UUIDs must match the ones in remote.js
SERVICE_UUID = '0000abcd-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC_UUID = '0000dcba-0000-1000-8000-00805f9b34fb'

COMMANDS = [
    "UP", "DOWN", "LEFT", "RIGHT", "OK", "HOME", "BACK", "MENU",
    "VOL_UP", "VOL_DOWN", "MUTE", "POWER_OFF"
]

class ChromecastRemote:
    def __init__(self):
        self.chromecasts = []
        self.selected_idx = 0
        self.selected = None
        self.state = "SELECT_DEVICE"  # or "CONTROL"

    def discover_devices(self):
        print("Discovering Chromecasts...")
        self.chromecasts, browser = pychromecast.get_chromecasts()
        if not self.chromecasts:
            print("No Chromecasts found.")
            return False
        # Pick first not currently casting as default, else first
        self.selected_idx = 0
        self.selected = None
        self.state = "SELECT_DEVICE"
        self._print_device_menu()
        return True

    def _print_device_menu(self):
        print("\nSelect Chromecast:")
        for i, cc in enumerate(self.chromecasts):
            prefix = "-> " if i == self.selected_idx else "   "
            status = " (CASTING)" if cc.status.status_text == "Casting" else ""
            print(f"{prefix}{cc.device.friendly_name}{status}")
        print("Use UP/DOWN arrows, OK/Enter to select.")

    def handle_command(self, cmd):
        if self.state == "SELECT_DEVICE":
            if cmd == "UP":
                self.selected_idx = (self.selected_idx - 1) % len(self.chromecasts)
                self._print_device_menu()
            elif cmd == "DOWN":
                self.selected_idx = (self.selected_idx + 1) % len(self.chromecasts)
                self._print_device_menu()
            elif cmd == "OK":
                self.selected = self.chromecasts[self.selected_idx]
                self.selected.wait()
                print(f"Selected {self.selected.device.friendly_name}!")
                self.state = "CONTROL"
        elif self.state == "CONTROL":
            self._send_chromecast_command(cmd)

    def _send_chromecast_command(self, cmd):
        cast = self.selected
        mc = cast.media_controller
        # Basic example: extend as needed for real Chromecast control
        if cmd == "HOME":
            cast.quit_app()
        elif cmd == "BACK" or cmd == "MENU":
            cast.quit_app()
        elif cmd == "VOL_UP":
            cast.volume_up()
        elif cmd == "VOL_DOWN":
            cast.volume_down()
        elif cmd == "MUTE":
            cast.set_volume_muted(True)
        elif cmd == "POWER_OFF":
            cast.quit_app()
        elif cmd == "OK":
            # Play/Pause toggle for demo
            if mc.status.player_state == "PLAYING":
                mc.pause()
            else:
                mc.play()
        # Arrow keys might be used to navigate in apps, but Chromecast by default doesn't support this
        print(f"Sent {cmd} to {cast.device.friendly_name}")

# ---- Bluetooth GATT Server ----
class BluetoothGATTServer:
    def __init__(self, remote):
        self.remote = remote
        self.server = None

    async def start(self):
        # NOTE: Bleak currently supports peripheral/server mode only on Linux with BlueZ 5.54+
        # You'll need to implement GATT server using appropriate platform tools if not available.
        print("Starting Bluetooth GATT server (simulated, see docs for full implementation)...")
        # For demo: simulate command input loop
        self.remote.discover_devices()
        while True:
            cmd = input("Simulate input command (e.g. UP, DOWN, OK): ").strip().upper()
            if cmd in COMMANDS:
                self.remote.handle_command(cmd)
            else:
                print("Unknown command.")

if __name__ == "__main__":
    remote = ChromecastRemote()
    # For actual BLE, use asyncio.run(BluetoothGATTServer(remote).start())
    # For demo, just run input loop:
    BluetoothGATTServer(remote).start()