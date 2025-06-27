import csv
from datetime import datetime

def solar_to_lunar(solar_date):
    with open("data/lunar_table.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["solar"] == solar_date:
                return {
                    "lunar_date": row["lunar"],
                    "is_leap_month": row["is_leap"] == "True"
                }
    return None
