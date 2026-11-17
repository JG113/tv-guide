import json
import time
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("America/New_York")

CHANNEL_MAP = {
    "NBC": "Ch. 12-6 (WCSH NBC)",
    "ABC": "Ch. 11-1 (WMTW ABC)",
    "PBS": "Ch. 13-6 (MPBN)",
    "CBS": "Ch. 11-6 (WGME CBS)",
    "FOX": "Ch. 12-1 (WPFO FOX)",
    "ION": "Ch. 23-1 / 35 (ION)",
    "ION Television": "Ch. 17 / 35 (ION)",
    "MeTV": "Ch. 23-2 (MeTV)",
    "NESN": "Ch. 28-1 / 773 (NESN)",
    "NESN+": "Ch. 326 (NESN+)",
    "ESPN": "Ch. 47-2 / 730 (ESPN)",
    "ESPN2": "Ch. 25 / 731 (ESPN2)",
    "ESPNU": "Ch. 370 (ESPNU)",
    "FS1": "Ch. 400 (FS1)",
    "CBS Sports Network": "Ch. 315 (CBSSN)",
    "ACCN": "Ch. 388 (ACC Network)",
    "ACC Network": "Ch. 388 (ACC Network)",
    "SNY": "Ch. 320 (SNY)",
    "Peacock": "Peacock App",
    "ESPN+": "ESPN+ App",
    "USA Network": "Ch. 21 / 718 (USA)",
    "TNT": "Ch. 27 / 719 (TNT)",
    "TBS": "Ch. 15 / 717 (TBS)",
    "A&E": "Ch. 32 / 722 (A&E)",
    "Paramount Network": "Ch. 23 (Paramount)",
    "TV Land": "Ch. 54 (TV Land)",
    "WE tv": "Ch. 68 (WE tv)",
    "Oxygen": "Ch. 90 (Oxygen)",
    "BBC America": "Ch. 110 (BBC America)",
    "Investigation Discovery": "Ch. 138 (ID)",
    "Start TV": "Ch. 155 (Start TV)",
    "Pop": "Ch. 175 (Pop TV)",
    "SundanceTV": "Ch. 628 (Sundance)",
    "UPtv": "Ch. 124 (UPtv)"
}

FAVORITE_SHOWS = {
    "blue bloods": "BLUE BLOODS",
    "chicago fire": "CHICAGO FIRE",
    "law & order": "DETECTIVE",
    "ncis": "DETECTIVE",
    "fbi": "DETECTIVE",
    "csi": "DETECTIVE",
    "criminal minds": "DETECTIVE",
    "the equalizer": "DETECTIVE",
    "matlock": "DETECTIVE",
    "elsbeth": "DETECTIVE",
    "tracker": "DETECTIVE",
    "will trent": "DETECTIVE",
    "perry mason": "DETECTIVE",
    "columbo": "DETECTIVE",
    "monk": "DETECTIVE",
    "murder, she wrote": "DETECTIVE",
    "cold case": "DETECTIVE",
    "bones": "DETECTIVE",
    "major crimes": "DETECTIVE",
    "the closer": "DETECTIVE",
    "rizzoli & isles": "DETECTIVE"
}

TEAM_IDS = {
    "41": "UConn Huskies",
    "311": "UMaine Black Bears",
    "150": "Duke Blue Devils"
}

SYNDICATION_BLOCKS = (
    {"days": (0, 1, 2, 3, 4), "hour": 13, "minute": 0, "hours": 3, "channel": "Ch. 21 / 718 (USA)", "title": "Chicago Fire (Afternoon Reruns)", "subtitle": "Syndicated Episodes on USA Network", "category": "CHICAGO FIRE"},
    {"days": (0, 1, 2, 3, 4), "hour": 16, "minute": 0, "hours": 3, "channel": "Ch. 68 (WE tv)", "title": "Blue Bloods (Afternoon Reruns)", "subtitle": "Syndicated Episodes on WE tv", "category": "BLUE BLOODS"},
    {"days": (0, 1, 2, 3, 4), "hour": 19, "minute": 0, "hours": 4, "channel": "Ch. 17 / 35 (ION)", "title": "Blue Bloods / NCIS / FBI Marathon", "subtitle": "Prime Time Syndication on ION TV", "category": "BLUE BLOODS"},
    {"days": (0, 1, 2, 3, 4), "hour": 12, "minute": 0, "hours": 4, "channel": "Ch. 27 / 719 (TNT)", "title": "Law & Order / Detective Reruns", "subtitle": "Afternoon Crime Drama Block on TNT", "category": "DETECTIVE"},
    {"days": (5, 6), "hour": 13, "minute": 0, "hours": 5, "channel": "Ch. 17 / 35 (ION)", "title": "Law & Order: SVU / Detective Marathon", "subtitle": "Weekend Marathon on ION TV", "category": "DETECTIVE"},
    {"days": (5, 6), "hour": 18, "minute": 0, "hours": 5, "channel": "Ch. 68 (WE tv)", "title": "Blue Bloods Evening Marathon", "subtitle": "Weekend Episodes on WE tv", "category": "BLUE BLOODS"},
    {"days": (5, 6), "hour": 14, "minute": 0, "hours": 4, "channel": "Ch. 21 / 718 (USA)", "title": "Chicago Fire Weekend Block", "subtitle": "Back-to-Back Episodes on USA Network", "category": "CHICAGO FIRE"}
)

def fetch_json(url, retries=3):
    clean_url = url.strip()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(clean_url, headers={"User-Agent": "TVGuideApp/2.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {clean_url}: {e}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return None

def format_channel(raw_name):
    if not raw_name:
        return "Check Spectrum Guide"
    return CHANNEL_MAP.get(raw_name, raw_name)
def get_live_tv_shows_for_week():
    programs = []
    today = datetime.now(LOCAL_TZ).date()
    for offset in range(7):
        target_date = today + timedelta(days=offset)
        date_str = target_date.strftime("%Y-%m-%d")
        urls = (
            f"https://tvmaze.com{date_str}",
            f"https://tvmaze.com{date_str}"
        )
        for url in urls:
            airings = fetch_json(url)
            if not airings:
                continue
            for item in airings:
                show = item.get("show") or item.get("_embedded", {}).get("show", {})
                title = show.get("name", "")
                title_lower = title.lower()
                genres = tuple(g.lower() for g in show.get("genres", ()))
                summary = (show.get("summary") or "").lower()
                matched_category = None
                for keyword, cat in FAVORITE_SHOWS.items():
                    if keyword in title_lower:
                        matched_category = cat
                        break
                if not matched_category and ("crime" in genres or "mystery" in genres) and "detective" in summary:
                    matched_category = "DETECTIVE"
                if not matched_category:
                    continue
                airstamp = item.get("airstamp")
                runtime = item.get("runtime") or 60
                if not airstamp:
                    continue
                start_dt = datetime.fromisoformat(airstamp).astimezone(LOCAL_TZ)
                end_dt = start_dt + timedelta(minutes=runtime)
                network = (show.get("network") or show.get("webChannel") or {}).get("name", "")
                ep_name = item.get("name", "")
                programs.append({
                    "date": start_dt.strftime("%Y-%m-%d"),
                    "date_label": start_dt.strftime("%A, %B %d"),
                    "start_iso": start_dt.isoformat(),
                    "end_iso": end_dt.isoformat(),
                    "time_display": start_dt.strftime("%I:%M %p").lstrip("0"),
                    "channel": format_channel(network),
                    "title": title,
                    "subtitle": f"Episode: {ep_name}" if ep_name else "First-Run / Featured Airing",
                    "category": matched_category
                })
    return programs

def get_syndicated_reruns_for_week():
    programs = []
    today = datetime.now(LOCAL_TZ).date()
    for offset in range(7):
        target_date = today + timedelta(days=offset)
        weekday = target_date.weekday()
        for block in SYNDICATION_BLOCKS:
            if weekday in block["days"]:
                start_dt = datetime(target_date.year, target_date.month, target_date.day, block["hour"], block["minute"], tzinfo=LOCAL_TZ)
                end_dt = start_dt + timedelta(hours=block["hours"])
                start_str = start_dt.strftime("%I:%M %p").lstrip("0")
                end_str = end_dt.strftime("%I:%M %p").lstrip("0")
                programs.append({
                    "date": target_date.strftime("%Y-%m-%d"),
                    "date_label": target_date.strftime("%A, %B %d"),
                    "start_iso": start_dt.isoformat(),
                    "end_iso": end_dt.isoformat(),
                    "time_display": f"{start_str} - {end_str}",
                    "channel": block["channel"],
                    "title": block["title"],
                    "subtitle": block["subtitle"],
                    "category": block["category"]
                })
    return programs

def get_full_team_schedules_for_week():
    games = []
    seen_event_ids = set()
    now = datetime.now(LOCAL_TZ)
    window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(days=7)
    for team_id, team_label in TEAM_IDS.items():
        url = f"https://espn.com{team_id}/schedule"
        data = fetch_json(url)
        if not data:
            continue
        for event in data.get("events", ()):
            event_id = event.get("id")
            if event_id in seen_event_ids:
                continue
            event_date_iso = event.get("date", "")
            try:
                start_dt = datetime.fromisoformat(event_date_iso.replace("Z", "+00:00")).astimezone(LOCAL_TZ)
            except Exception:
                continue
            if not (window_start <= start_dt <= window_end):
                continue
            seen_event_ids.add(event_id)
            end_dt = start_dt + timedelta(hours=2)
            name = event.get("name", f"{team_label} Basketball")
            broadcasts = []
            for comp in event.get("competitions", ()):
                for b in comp.get("broadcasts", ()):
                    if isinstance(b.get("names"), list):
                        broadcasts.extend(b.get("names"))
                    elif b.get("media", {}).get("shortName"):
                        broadcasts.append(b["media"]["shortName"])
            raw_channel = broadcasts[0] if broadcasts else "ESPN+ / SNY / NESN"
            games.append({
                "date": start_dt.strftime("%Y-%m-%d"),
                "date_label": start_dt.strftime("%A, %B %d"),
                "start_iso": start_dt.isoformat(),
                "end_iso": end_dt.isoformat(),
                "time_display": start_dt.strftime("%I:%M %p").lstrip("0"),
                "channel": format_channel(raw_channel),
                "title": f"Women's Basketball: {name}",
                "subtitle": f"NCAA Division I - {team_label}",
                "category": "BASKETBALL"
            })
    return games

def main():
    all_items = get_full_team_schedules_for_week() + get_live_tv_shows_for_week() + get_syndicated_reruns_for_week()
    unique_items = []
    seen_keys = set()
    for item in all_items:
        key = (item["date"], item["start_iso"], item["title"])
        if key not in seen_keys:
            seen_keys.add(key)
            unique_items.append(item)
    unique_items.sort(key=lambda x: x["start_iso"])
    output = {"updated_at": datetime.now(LOCAL_TZ).isoformat(), "programs": unique_items}
    with open("guide_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Saved {len(unique_items)} total programs to guide_data.json")

if __name__ == "__main__":
    main()
