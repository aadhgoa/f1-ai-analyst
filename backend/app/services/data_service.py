"""Service for fetching and analyzing F1 telemetry data using FastF1."""

# pylint: disable=line-too-long, broad-exception-caught, too-many-locals, too-many-branches, too-many-statements, bare-except

import os
import logging
import fastf1
import polars as pl
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

CACHE_DIR = "./cache"

os.makedirs(CACHE_DIR, exist_ok=True)

fastf1.Cache.enable_cache(CACHE_DIR)

SESSION_CACHE = {}


# app/services/data_service.py
class F1RaceAnalyzer:
    """Class to load and analyze F1 race sessions."""

    def __init__(self, year: int, gp: str):
        """Initialize the analyzer with a specific year and Grand Prix."""
        self.year = year
        self.gp = gp

    def _get_session(self):
        """Load and cache the FastF1 session for the race."""
        key = f"{self.year}_{self.gp}"
        if key not in SESSION_CACHE:
            logger.info("Loading session for %s %s...", self.year, self.gp)
            session = fastf1.get_session(self.year, self.gp, "R")
            session.load()
            logger.info("Session loaded successfully.")
            SESSION_CACHE[key] = session
        return SESSION_CACHE[key]

    def get_race_data(self) -> pl.DataFrame:
        """Get the lap data as a Polars DataFrame."""
        session = self._get_session()
        return pl.from_pandas(session.laps)

    def extract_track_status(self) -> str:
        """Extract a timeline of major track incidents (Safety Cars, VSCs, Red Flags)."""
        session = self._get_session()
        events = []
        laps_pd = session.laps
        if "TrackStatus" not in laps_pd.columns:
            return "Track status data unavailable."

        sc_laps = (
            laps_pd[laps_pd["TrackStatus"].astype(str).str.contains("4", na=False)][
                "LapNumber"
            ]
            .dropna()
            .unique()
            .tolist()
        )
        vsc_laps = (
            laps_pd[laps_pd["TrackStatus"].astype(str).str.contains("6", na=False)][
                "LapNumber"
            ]
            .dropna()
            .unique()
            .tolist()
        )
        red_laps = (
            laps_pd[laps_pd["TrackStatus"].astype(str).str.contains("5", na=False)][
                "LapNumber"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        if sc_laps:
            events.append(f"Safety Car (SC): laps {sorted([int(x) for x in sc_laps])}")
        if vsc_laps:
            events.append(
                f"Virtual Safety Car (VSC): laps {sorted([int(x) for x in vsc_laps])}"
            )
        if red_laps:
            events.append(f"Red Flag: laps {sorted([int(x) for x in red_laps])}")

        if not events:
            return "Clean race. No Safety Cars, VSCs, or Red Flags."
        return "\n".join(events)

    def extract_driver_stints(self, driver: str) -> str:
        """Extract a breakdown of a driver's tire strategy and stints."""
        session = self._get_session()
        try:
            dlaps = session.laps.pick_drivers(driver)
            if dlaps.empty:
                return f"No data found for driver {driver}"

            results = []
            if "Stint" not in dlaps.columns:
                return "Stint data unavailable."

            stints = dlaps["Stint"].dropna().unique()
            for stint in stints:
                stint_laps = dlaps[dlaps["Stint"] == stint]
                compound = (
                    stint_laps["Compound"].iloc[0]
                    if not stint_laps["Compound"].isna().all()
                    else "Unknown"
                )
                start_lap = int(stint_laps["LapNumber"].min())
                end_lap = int(stint_laps["LapNumber"].max())
                laps_in_stint = end_lap - start_lap + 1

                valid_times = stint_laps["LapTime"].dropna()
                if not valid_times.empty:
                    avg_time = valid_times.mean().total_seconds()
                    avg_str = f"{avg_time:.3f}s"
                else:
                    avg_str = "N/A"

                results.append(
                    f"Stint {int(stint)}: {compound} | Laps {start_lap}-{end_lap} ({laps_in_stint} laps) | Avg Pace: {avg_str}"
                )

            return "\n".join(results)
        except Exception as e:
            logger.error(
                "Error extracting driver stints for %s: %s", driver, e, exc_info=True
            )
            return f"Could not extract driver stints for {driver}: {str(e)}"

    def extract_telemetry_summary(self, driver: str, lap_num: int) -> str:
        """Extract a summary of engineering telemetry for a specific driver and lap."""
        session = self._get_session()
        try:
            dlaps = session.laps.pick_drivers(driver)
            if dlaps.empty:
                return f"No driver data for {driver}"

            lap_rows = dlaps[dlaps["LapNumber"] == lap_num]
            if lap_rows.empty:
                return f"No lap data for Lap {lap_num}"

            lap = lap_rows.iloc[0]
            telemetry = lap.get_telemetry()

            logger.info(
                "Extracted telemetry for %s Lap %s. Rows: %s",
                driver,
                lap_num,
                len(telemetry),
            )

            if telemetry.empty:
                return "Empty telemetry data."

            top_speed = telemetry["Speed"].max()
            min_speed = telemetry["Speed"].min()
            avg_speed = telemetry["Speed"].mean()
            max_rpm = telemetry["RPM"].max()

            full_throttle_pct = (telemetry["Throttle"] >= 95).mean() * 100
            brake_pct = (telemetry["Brake"] > 0).mean() * 100

            gear_changes = (telemetry["nGear"].diff().fillna(0) != 0).sum()
            drs_active_pct = (telemetry["DRS"] >= 10).mean() * 100

            summary = (
                f"Telemetry Summary for {driver} on Lap {lap_num}:\n"
                f"- Top Speed: {top_speed} km/h\n"
                f"- Min Speed (Apex): {min_speed} km/h\n"
                f"- Avg Speed: {avg_speed:.1f} km/h\n"
                f"- Max RPM: {max_rpm}\n"
                f"- Full Throttle: {full_throttle_pct:.1f}% of the lap\n"
                f"- Braking: {brake_pct:.1f}% of the lap\n"
                f"- Gear Changes: {gear_changes}\n"
                f"- DRS Active: {drs_active_pct:.1f}% of the lap"
            )

            logger.info("Telemetry summary generated:\n%s", summary)
            return summary
        except Exception as e:
            logger.error(
                "Error extracting telemetry for %s Lap %s: %s",
                driver,
                lap_num,
                e,
                exc_info=True,
            )
            return (
                f"Could not extract telemetry for {driver} on lap {lap_num}: {str(e)}"
            )

    def get_dashboard_data(self) -> dict:
        """Get summarized race data for the frontend dashboard."""
        session = self._get_session()

        # 1. Podium
        podium_df = session.results.head(3)
        podium = []
        for _, row in podium_df.iterrows():
            time_val = row.get("Time", None)
            time_str = "N/A"
            if not pd.isna(time_val):
                if isinstance(time_val, pd.Timedelta):
                    h = time_val.components.hours
                    m = time_val.components.minutes
                    s = time_val.components.seconds
                    ms = time_val.components.milliseconds
                    if h > 0:
                        time_str = f"{h}:{m:02d}:{s:02d}.{ms:03d}"
                    else:
                        time_str = f"{m}:{s:02d}.{ms:03d}"
                        if row["ClassifiedPosition"] != "1":
                            time_str = f"+{time_str}"
                else:
                    time_str = str(time_val)
            else:
                time_str = str(row.get("Status", "N/A"))

            # fastf1 returns 'nan' string for missing colors sometimes
            color = str(row.get("TeamColor", "ffffff"))
            if color == "nan" or not color:
                color = "ffffff"

            podium.append(
                {
                    "position": str(
                        row.get("ClassifiedPosition", row.get("Position", ""))
                    ),
                    "name": str(row.get("BroadcastName", "")),
                    "abbr": str(row.get("Abbreviation", "")),
                    "team": str(row.get("TeamName", "")),
                    "color": f"#{color}",
                    "time": time_str,
                }
            )

        # 2. Fastest Lap
        try:
            fastest_lap = session.laps.pick_fastest()
            fastest_time = fastest_lap.get("LapTime")
            fl_time_str = "N/A"
            if not pd.isna(fastest_time) and isinstance(fastest_time, pd.Timedelta):
                m = fastest_time.components.minutes
                s = fastest_time.components.seconds
                ms = fastest_time.components.milliseconds
                fl_time_str = f"{m}:{s:02d}.{ms:03d}"

            fl_data = {
                "driver": str(fastest_lap.get("Driver", "N/A")),
                "lap_time": fl_time_str,
                "lap_number": (
                    int(fastest_lap.get("LapNumber", 0))
                    if not pd.isna(fastest_lap.get("LapNumber"))
                    else 0
                ),
            }
        except Exception:
            fl_data = {"driver": "N/A", "lap_time": "N/A", "lap_number": 0}

        # 3. Lap by Lap standings
        try:
            laps_df = session.laps[["LapNumber", "Driver", "Position"]].dropna()
            laps_df = laps_df[laps_df["LapNumber"] > 0]
            lap_numbers = sorted(laps_df["LapNumber"].unique())
            chart_data = []
            for lap_num in lap_numbers:
                lap_data = {"lap": int(lap_num)}
                lap_rows = laps_df[laps_df["LapNumber"] == lap_num]
                for _, r in lap_rows.iterrows():
                    lap_data[str(r["Driver"])] = int(r["Position"])
                chart_data.append(lap_data)
        except Exception:
            chart_data = []

        # Drivers metadata for chart colors
        driver_colors = {}
        for _, row in session.results.iterrows():
            abbr = str(row.get("Abbreviation", ""))
            if abbr and abbr != "nan":
                c = str(row.get("TeamColor", ""))
                clr = f"#{c}" if c and c != "nan" else "#ffffff"
                driver_colors[abbr] = {
                    "color": clr,
                    "name": str(row.get("BroadcastName", "")),
                }

        return {
            "podium": podium,
            "fastest_lap": fl_data,
            "chart_data": chart_data,
            "drivers": driver_colors,
        }
