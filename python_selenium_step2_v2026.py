import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time as t
import random
import collections
from collections import defaultdict

with open("strava_cookies.json", "r") as f:
    cookies = json.load(f)

s = requests.Session()
for cookie in cookies:
    s.cookies.set(cookie["name"], cookie["value"])

# Segments grouped by team
north_segments = [
    28905618,
    31546864,
    41697108,
    41684542,
    4749905,
    41701816,
    41696115,
    29231020,
    8378497,
    39523117,
]
south_segments = [
    11895728,
    18779432,
    39663350,
    1332276,
    39499332,
    26938538,
    22659315,
    30471058,
    10768454,
    4821298,
]
stp_segments = [
    41697105,
    15898012,
    41701953,
    41703161,
    17268802,
    26285065,
    24530544,
    1078817,
    23218709,
    3815236,
]
# monday_dd = [24202567]
tuesday_dd = [12498700]
wednesday_dd = [37433791]

# All Segments
segments = north_segments + south_segments + stp_segments
test_segment = [11895728]
# validating fake profile
segments = segments
club_id = 2201363
base_url = f"https://www.strava.com/segments/{segments}?date_range=this_week&filter=club&club_id={club_id}"
urls = [
    f"https://www.strava.com/segments/{segments}?date_range=this_week&filter=club&club_id={club_id}"
    for segment_id in segments
]
test_url = [
    f"https://www.strava.com/segments/{segments}?date_range=this_week&filter=club&club_id={club_id}"
    for segment_id in test_segment
]
score_limit = 100
page_size = 25  # Strava uses pages of 25 entries

segment_name_lists = {}
tie_summary_per_segment = {}
raw_name_time_pairs = []

for seggie in segments:
    print(f"📊 Processing segment: {seggie}")
    entries = []  # list of (name, team_emoji, time)
    t.sleep(random.randint(2, 7))
    for page in range(1, (score_limit // page_size) + 1):
        url = f"https://www.strava.com/frontend/segments/{seggie}/leaderboard"
        params = {
            "filter_type": "club",
            "filter_value": club_id,
            "date_range": "this_week",
            "gender": "overall",
            "page": page,
        }
        res = s.get(url, params=params)
        if res.status_code != 200:
            break
        try:
            data = res.json()
        except ValueError:
            break

        rows = data.get("leaderboard", [])
        if not rows:
            break

        for row in rows:
            name_raw = (row.get("displayName") or "").strip()
            date_val = row.get("startDateLocal", "")
            time_val = row.get("elapsedTime")

            emoji = ""
            for symbol in ["📁", "🧿", "🗿"]:
                if symbol in name_raw:
                    emoji = symbol
                    break

            raw_name_time_pairs.append(
                {
                    "Segment": seggie,
                    "Name": name_raw,
                    "Date": date_val,
                    "Time": time_val,
                }
            )
            entries.append((name_raw, emoji, time_val))

        if len(rows) < page_size:
            break
        t.sleep(random.randint(2, 7))

    # Save name order
    segment_name_lists[seggie] = [name for (name, _, _) in entries]
    # ---- TIE SCORING ----
    time_groups = defaultdict(list)
    for idx, (name, emoji, time) in enumerate(entries):
        time_groups[time].append((idx, name, emoji))  # preserve order
    team_points = defaultdict(int)
    for time, group in time_groups.items():
        if len(group) > 1:
            group.sort()  # by original order
            for rank_offset, (_, _, emoji) in enumerate(group[1:], start=1):
                team_points[emoji] += rank_offset
    # Build header string like "🎩-2\n🧢-1"
    if team_points:
        sorted_summary = sorted(
            team_points.items(), key=lambda x: -x[1]
        )  # sort by points
        header_str = "\n".join(f"{emoji}-{pts}" for emoji, pts in sorted_summary)
    else:
        header_str = ""
    tie_summary_per_segment[seggie] = header_str
# Normalize lengths
max_len = max(len(v) for v in segment_name_lists.values())
for seg_id in segment_name_lists:
    segment_name_lists[seg_id] += [None] * (max_len - len(segment_name_lists[seg_id]))
# Create main DF
df = pd.DataFrame(segment_name_lists)
# Add tie header row
tie_row = pd.DataFrame([tie_summary_per_segment])
final_df = pd.concat([tie_row, df], ignore_index=True)
# Leaderboard export
final_df.to_csv("leaderboard_ties_scored.csv", index=False, encoding="utf-8-sig")
print("✅ Exported with tie-based team scoring")

# Individual Times export
raw_df = pd.DataFrame(raw_name_time_pairs)
raw_df.to_csv("raw_name_time_log.csv", index=False, encoding="utf-8-sig")
print("📄 Exported raw name-time log to raw_name_time_log.csv")
