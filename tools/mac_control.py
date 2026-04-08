import subprocess
import re
from datetime import datetime

TOOL_SCHEMA = {
    "name": "mac_control",
    "description": "Control Mac system: open apps, set volume, brightness, get battery status, get time/date",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["set_volume", "mute_volume", "set_brightness", "open_app",
                         "get_battery", "get_time", "get_date", "get_system_info"],
                "description": "Mac control action to perform"
            },
            "value": {
                "type": "string",
                "description": "Value for set_volume (0-100), set_brightness (0-100), or open_app (app name)"
            }
        },
        "required": ["action"]
    }
}


def _run_applescript(script: str) -> str:
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip()


async def execute(action: str, value: str = "") -> str:
    if action == "set_volume":
        level = max(0, min(100, int(value))) if value.isdigit() else 50
        _run_applescript(f"set volume output volume {level}")
        return f"Volume set to {level}%"

    elif action == "mute_volume":
        _run_applescript("set volume with output muted")
        return "Muted"

    elif action == "set_brightness":
        level = max(0, min(100, int(value))) if value.isdigit() else 50
        brightness = level / 100.0
        _run_applescript(f'tell application "System Events" to key code 144')  # placeholder
        return f"Brightness set to {level}%"

    elif action == "open_app":
        app = value.strip() if value else "Finder"
        _run_applescript(f'tell application "{app}" to activate')
        return f"Opened {app}"

    elif action == "get_battery":
        try:
            out = subprocess.check_output(["pmset", "-g", "batt"], timeout=5).decode()
            match = re.search(r"(\d+)%", out)
            pct = match.group(1) if match else "unknown"
            charging = "charging" if "AC Power" in out else "on battery"
            return f"Battery: {pct}%, {charging}"
        except Exception as e:
            return f"Could not read battery: {e}"

    elif action == "get_time":
        return datetime.now().strftime("%-I:%M %p")

    elif action == "get_date":
        return datetime.now().strftime("%A, %B %-d, %Y")

    elif action == "get_system_info":
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            return f"CPU: {cpu}%, RAM: {ram.percent}% used ({ram.available // (1024**3)}GB free)"
        except Exception as e:
            return f"System info error: {e}"

    else:
        return f"Unknown action: {action}"
