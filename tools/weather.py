import httpx

TOOL_SCHEMA = {
    "name": "get_weather",
    "description": "Get current weather for a city or the user's current location",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name (e.g. 'Chennai', 'London'). Leave empty for current location."
            }
        },
        "required": []
    }
}


async def execute(city: str = "") -> str:
    location = city.strip() if city.strip() else ""
    url = f"https://wttr.in/{location}?format=3"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(url, headers={"User-Agent": "jarwis/1.0"})
            response.raise_for_status()
            return response.text.strip()
    except Exception as e:
        return f"Couldn't fetch weather: {e}"
