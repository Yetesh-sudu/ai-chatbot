import datetime
import json
import threading
import tkinter as tk
from tkinter import ttk
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Heavy showers",
    82: "Violent showers",
    95: "Thunderstorm",
}


class WeatherApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("SkyCast Weather")
        self.root.geometry("880x620")
        self.root.minsize(760, 520)
        self.root.configure(bg="#0f2135")

        self.city_var = tk.StringVar(value="New Delhi")
        self.status_var = tk.StringVar(value="Search for a city to get the latest forecast.")
        self.location_var = tk.StringVar(value="New Delhi")
        self.condition_var = tk.StringVar(value="Loading sample forecast...")
        self.temp_var = tk.StringVar(value="-- deg C")
        self.meta_var = tk.StringVar(value="Humidity -- | Wind --")
        self.forecast_vars = []

        self._build_styles()
        self._build_ui()
        self.fetch_weather("New Delhi")

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("App.TFrame", background="#0f2135")
        style.configure("Card.TFrame", background="#17314d")
        style.configure("Panel.TFrame", background="#1d4267")

        style.configure(
            "Title.TLabel",
            background="#17314d",
            foreground="#f4fbff",
            font=("Segoe UI Semibold", 28),
        )
        style.configure(
            "Body.TLabel",
            background="#17314d",
            foreground="#c6ddf0",
            font=("Segoe UI", 11),
        )
        style.configure(
            "Muted.TLabel",
            background="#17314d",
            foreground="#9cc1db",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Heading.TLabel",
            background="#1d4267",
            foreground="#f4fbff",
            font=("Segoe UI Semibold", 22),
        )
        style.configure(
            "Temp.TLabel",
            background="#1d4267",
            foreground="#ffd166",
            font=("Segoe UI Semibold", 30),
        )
        style.configure(
            "ForecastTitle.TLabel",
            background="#244c74",
            foreground="#f4fbff",
            font=("Segoe UI Semibold", 12),
        )
        style.configure(
            "ForecastBody.TLabel",
            background="#244c74",
            foreground="#d7e8f5",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Search.TButton",
            background="#ffd166",
            foreground="#1c3048",
            font=("Segoe UI Semibold", 11),
            padding=(16, 10),
            borderwidth=0,
        )
        style.map(
            "Search.TButton",
            background=[("active", "#ffbf3c")],
            foreground=[("active", "#1c3048")],
        )

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, style="App.TFrame", padding=18)
        outer.pack(fill="both", expand=True)

        outer.columnconfigure(0, weight=3)
        outer.columnconfigure(1, weight=4)
        outer.rowconfigure(0, weight=1)

        left = ttk.Frame(outer, style="Card.TFrame", padding=24)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right = ttk.Frame(outer, style="Panel.TFrame", padding=24)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ttk.Label(left, text="Weather Prediction", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(left, text="Track the sky before your day begins.", style="Title.TLabel", wraplength=280).pack(
            anchor="w", pady=(12, 14)
        )
        ttk.Label(
            left,
            text="Search any city to see the current weather and the next 5-day outlook.",
            style="Body.TLabel",
            wraplength=300,
            justify="left",
        ).pack(anchor="w")

        search_row = ttk.Frame(left, style="Card.TFrame")
        search_row.pack(fill="x", pady=(24, 12))
        search_row.columnconfigure(0, weight=1)

        city_entry = tk.Entry(
            search_row,
            textvariable=self.city_var,
            font=("Segoe UI", 12),
            relief="flat",
            bg="#edf6fb",
            fg="#14324f",
            insertbackground="#14324f",
        )
        city_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=10)
        city_entry.bind("<Return>", lambda event: self.fetch_weather(self.city_var.get().strip()))

        ttk.Button(
            search_row,
            text="Check Forecast",
            style="Search.TButton",
            command=lambda: self.fetch_weather(self.city_var.get().strip()),
        ).grid(row=0, column=1, sticky="e")

        ttk.Label(left, textvariable=self.status_var, style="Body.TLabel", wraplength=300).pack(anchor="w", pady=(8, 0))

        ttk.Label(right, text="Current Forecast", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(right, textvariable=self.location_var, style="Heading.TLabel").pack(anchor="w", pady=(8, 4))
        ttk.Label(right, textvariable=self.condition_var, style="Body.TLabel").pack(anchor="w")
        ttk.Label(right, textvariable=self.temp_var, style="Temp.TLabel").pack(anchor="w", pady=(18, 4))
        ttk.Label(right, textvariable=self.meta_var, style="Body.TLabel").pack(anchor="w")

        ttk.Label(right, text="5-Day Prediction", style="Muted.TLabel").pack(anchor="w", pady=(28, 12))

        forecast_grid = ttk.Frame(right, style="Panel.TFrame")
        forecast_grid.pack(fill="both", expand=True)

        for index in range(5):
            forecast_grid.columnconfigure(index, weight=1)
            card = tk.Frame(
                forecast_grid,
                bg="#244c74",
                highlightthickness=1,
                highlightbackground="#335f8b",
                padx=12,
                pady=14,
            )
            card.grid(row=0, column=index, sticky="nsew", padx=6)

            day_var = tk.StringVar(value="Day")
            summary_var = tk.StringVar(value="Waiting")
            range_var = tk.StringVar(value="-- / --")

            tk.Label(
                card,
                textvariable=day_var,
                bg="#244c74",
                fg="#f4fbff",
                font=("Segoe UI Semibold", 11),
            ).pack(anchor="w")
            tk.Label(
                card,
                textvariable=summary_var,
                bg="#244c74",
                fg="#d7e8f5",
                font=("Segoe UI", 10),
                wraplength=110,
                justify="left",
            ).pack(anchor="w", pady=(12, 10))
            tk.Label(
                card,
                textvariable=range_var,
                bg="#244c74",
                fg="#ffd166",
                font=("Segoe UI Semibold", 10),
            ).pack(anchor="w")

            self.forecast_vars.append((day_var, summary_var, range_var))

    def fetch_weather(self, city: str) -> None:
        if not city:
            self.status_var.set("Please enter a city name.")
            return

        self.status_var.set("Fetching latest forecast...")
        threading.Thread(target=self._load_weather_data, args=(city,), daemon=True).start()

    def _load_weather_data(self, city: str) -> None:
        try:
            place = self._get_coordinates(city)
            forecast = self._get_forecast(place["latitude"], place["longitude"])
            self.root.after(0, lambda: self._update_ui(place, forecast))
        except Exception as exc:  # pylint: disable=broad-except
            self.root.after(0, lambda: self.status_var.set(str(exc)))

    def _get_coordinates(self, city: str) -> dict:
        geocode_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={quote(city)}&count=1&language=en&format=json"
        )
        data = self._fetch_json(geocode_url)
        results = data.get("results") or []
        if not results:
            raise ValueError("City not found. Try a different spelling.")
        return results[0]

    def _get_forecast(self, latitude: float, longitude: float) -> dict:
        forecast_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min"
            "&timezone=auto"
        )
        return self._fetch_json(forecast_url)

    def _fetch_json(self, url: str) -> dict:
        try:
            with urlopen(url, timeout=12) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Weather service error: {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("Unable to reach the weather service.") from exc

    def _update_ui(self, place: dict, forecast: dict) -> None:
        current = forecast["current"]
        daily = forecast["daily"]

        self.location_var.set(f"{place['name']}, {place.get('country', '')}".rstrip(", "))
        self.condition_var.set(WEATHER_CODES.get(current["weather_code"], "Mixed conditions"))
        self.temp_var.set(f"{round(current['temperature_2m'])} deg C")
        self.meta_var.set(
            f"Humidity {current['relative_humidity_2m']}% | "
            f"Wind {round(current['wind_speed_10m'])} km/h"
        )

        for index, vars_set in enumerate(self.forecast_vars):
            day_var, summary_var, range_var = vars_set
            day_var.set(self._format_day(daily["time"][index]))
            summary_var.set(WEATHER_CODES.get(daily["weather_code"][index], "Mixed conditions"))
            range_var.set(
                f"{round(daily['temperature_2m_max'][index])} deg / "
                f"{round(daily['temperature_2m_min'][index])} deg"
            )

        self.status_var.set(f"Forecast updated for {place['name']}.")

    @staticmethod
    def _format_day(date_text: str) -> str:
        year, month, day = [int(part) for part in date_text.split("-")]
        weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return weekday_names[datetime.date(year, month, day).weekday()]


def main() -> None:
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
