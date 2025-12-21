from langchain_core.tools import tool
import datetime
import holidays

# Egypt national holidays using the holidays library
EG_HOLIDAYS = holidays.CountryHoliday("EG")

# Mock dashboard-blocked dates (to be replaced later by V0 calendar data)
MOCK_BUSY_DATES = [
    "2025-12-22",
    "2025-12-24",
]

@tool
def check_calendar_availability(start_date: str, end_date: str = None) -> dict:
    """
    Smart availability checker for a single date or a range.

    Usage:
    - Single-day:
         check_calendar_availability(start_date="2025-12-22")
    - Range:
         check_calendar_availability("2025-12-20", "2025-12-25")

    Inputs:
        start_date (str): Required. Format YYYY-MM-DD.
        end_date (str|None): Optional. Format YYYY-MM-DD. If omitted → single-day mode.

    Behavior:
    - Validates input.
    - Single-day if end_date missing.
    - Returns structured availability report.
    """

    # --- Step 1: Validate date formats ---
    try:
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end = (
            datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            if end_date
            else start  # Single-day mode
        )
    except ValueError:
        return {
            "status": "ERROR",
            "reason": "INVALID_FORMAT",
            "description": "Dates must follow YYYY-MM-DD."
        }

    # --- Step 2: Validate range order ---
    if end < start:
        return {
            "status": "ERROR",
            "reason": "INVALID_RANGE",
            "description": "end_date cannot be earlier than start_date."
        }

    # --- Step 3: Iterate and generate availability report ---
    results = []
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")

        # Default state
        status = "AVAILABLE"
        reason = None
        description = "Available for scheduling"

        # Egypt weekend (Fri/Sat)
        if current.weekday() in [4, 5]:
            status = "BUSY"
            reason = "WEEKEND"
            description = "Weekend (Friday/Saturday)"

        # Egypt national holidays
        elif current in EG_HOLIDAYS:
            status = "BUSY"
            reason = "HOLIDAY"
            description = EG_HOLIDAYS.get(current)

        # User-blocked days
        elif date_str in MOCK_BUSY_DATES:
            status = "BUSY"
            reason = "CALENDAR_BLOCK"
            description = "Marked as busy on dashboard"

        results.append({
            "date": date_str,
            "status": status,
            "reason": reason,
            "description": description
        })

        current += datetime.timedelta(days=1)

    # --- Step 4: Final response payload ---
    return {
        "status": "OK",
        "mode": "RANGE" if end_date else "SINGLE",
        "results": results
    }
