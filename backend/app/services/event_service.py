"""Service for detecting and extracting notable events from F1 telemetry laps."""

# pylint: disable=line-too-long, too-many-locals, too-many-branches, too-many-statements

import polars as pl

DRIVER_MAP = {
    "VER": "Verstappen",
    "PER": "Pérez",
    "HAM": "Hamilton",
    "RUS": "Russell",
    "LEC": "Leclerc",
    "SAI": "Sainz",
    "NOR": "Norris",
    "PIA": "Piastri",
    "ALO": "Alonso",
    "STR": "Stroll",
    "GAS": "Gasly",
    "OCO": "Ocon",
    "ALB": "Albon",
    "SAR": "Sargeant",
    "TSU": "Tsunoda",
    "RIC": "Ricciardo",
    "BOT": "Bottas",
    "ZHO": "Zhou",
    "MAG": "Magnussen",
    "HUL": "Hülkenberg",
    "BEA": "Bearman",
    "COL": "Colapinto",
    "LAW": "Lawson",
    "DEV": "De Vries",
    "VET": "Vettel",
    "RAI": "Räikkönen",
    "GIO": "Giovinazzi",
    "MSC": "Schumacher",
    "LAT": "Latifi",
    "MAZ": "Mazepin",
    "KUB": "Kubica",
    "ANT": "Antonelli",
    "HAD": "Hadjar",
    "LIN": "Lindblad",
}


def detect_events(
    laps: pl.DataFrame, start_lap: int | None = None, end_lap: int | None = None
) -> list[str]:
    """Detect and return notable race events from telemetry data."""
    events = []

    def log_event(lap_num: int, message: str):
        """Helper to log an event if it falls within the requested lap range."""
        if start_lap is not None and lap_num < start_lap:
            return
        if end_lap is not None and lap_num > end_lap:
            return
        events.append(message)

    # Sort by Driver then LapNumber to appropriately compare consecutive laps for the SAME driver
    if "Driver" not in laps.columns or "LapNumber" not in laps.columns:
        return events

    laps_sorted = laps.sort(["Driver", "LapNumber"])

    fastest_driver = None
    fastest_lap_num = None
    if "LapTime" in laps.columns:
        valid_laps = laps.filter(pl.col("LapTime").is_not_null())
        if len(valid_laps) > 0:
            fl_row = valid_laps.sort("LapTime").to_dicts()[0]
            fastest_driver = fl_row.get("Driver")
            fastest_lap_num = fl_row.get("LapNumber")

    rows = laps_sorted.to_dicts()

    for i in range(1, len(rows)):
        prev = rows[i - 1]
        curr = rows[i]

        # Ensure we are only comparing consecutive laps for the same driver
        if prev.get("Driver") != curr.get("Driver"):
            continue

        raw_driver = curr.get("Driver")
        driver = DRIVER_MAP.get(raw_driver, raw_driver)
        lap = int(curr.get("LapNumber", 0))

        prev_pos = prev.get("Position")
        curr_pos = curr.get("Position")

        # Position Gain/Loss
        if curr_pos is not None and prev_pos is not None:
            diff = int(prev_pos - curr_pos)
            if diff > 0:
                log_event(
                    lap,
                    f"Lap {lap}: {driver} gained {diff} position(s) (P{int(prev_pos)} to P{int(curr_pos)})",
                )
            elif diff < 0:
                log_event(
                    lap,
                    f"Lap {lap}: {driver} lost {-diff} position(s) (P{int(prev_pos)} to P{int(curr_pos)})",
                )

        # Pit Stop Detection
        if curr.get("PitInTime") is not None:
            log_event(lap, f"Lap {lap}: {driver} made a pit stop")

        # Tire Change Detection
        prev_compound = prev.get("Compound")
        curr_compound = curr.get("Compound")
        if prev_compound and curr_compound and prev_compound != curr_compound:
            log_event(
                lap,
                f"Lap {lap}: {driver} changed tires from {prev_compound} to {curr_compound}",
            )

        # Fastest Lap Overall
        if curr.get("Driver") == fastest_driver and lap == fastest_lap_num:
            log_event(lap, f"Lap {lap}: {driver} set the fastest lap of the race")

        # Retirements
        if curr_pos is None and prev_pos is not None:
            log_event(lap, f"Lap {lap}: {driver} retired from the race")

        # Penalties
        penalty = curr.get("Penalty")
        if penalty is not None and str(penalty).strip() != "":
            log_event(lap, f"Lap {lap}: {driver} received a penalty")

    # Final Race Positions
    if "Position" in laps_sorted.columns:
        final_laps = (
            laps_sorted.filter(pl.col("Position").is_not_null())
            .group_by("Driver", maintain_order=True)
            .tail(1)
            .sort("Position")
            .to_dicts()
        )
        if final_laps:
            podium = [
                DRIVER_MAP.get(d.get("Driver"), d.get("Driver")) for d in final_laps[:3]
            ]

            # Use max lap to tag these summary events effectively so they aren't hidden by lap slicing,
            # but usually these are requested as an overview. We will log them with lap=999 to bypass lap limits, or simply not filter them.
            max_lap = (
                int(laps_sorted["LapNumber"].max())
                if not laps_sorted.is_empty()
                else 999
            )

            log_event(max_lap, "The podium finishers were: " + ", ".join(podium))

            standings = [
                f"{DRIVER_MAP.get(d.get('Driver'), d.get('Driver'))} (P{int(d.get('Position'))})"
                for d in final_laps
            ]
            log_event(
                max_lap, "The final standings looked like: " + ", ".join(standings)
            )

    return events
