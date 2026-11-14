import json
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Force Eastern Time (Augusta, ME) even when running on cloud servers
LOCAL_TZ = ZoneInfo("America/New_York")

# SPECTRUM AUGUSTA, ME (04330) CHANNEL MAP
CHANNEL_MAP = {
    "NBC": "Ch. 12-6 (WCSH NBC)",
    "ABC": "Ch. 11-1 (WMTW ABC)",
    "PBS": "Ch. 13-6 (MPBN)",
    "CBS": "Ch. 11-6 (WGME CBS)",
    "FOX": "Ch. 12-1 (WPFO FOX)",
    "ION": "Ch. 23-1 (ION)",
    "MeTV": "Ch. 23-2 (MeTV)",

    # Women's Basketball (UConn, UMaine, Duke)
    "NESN": "Ch. 27 / 773 (NESN)",
    "NESN+": "Ch. 326 (NESN+)",
    "ESPN": "Ch. 24 / 730 (ESPN)",
    "ESPN2": "Ch. 25 / 731 (ESPN2)",
    "ESPNU": "Ch. 370 (ESPNU)",
    "FS1": "Ch. 400 (FS1)",
    "CBS Sports Network": "Ch. 315 (CBSSN)",
    "ACCN": "Ch. 388 (ACC Network)",
    "SNY": "Ch. 320 (SNY)",
    "Peacock": "Peacock App",
    "ESPN+": "ESPN+ App",

    # Cable Channels for Blue Bloods, Chicago Fire & Detective Shows
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

FAVORITE_TEAMS = [
    "uconn", "connecticut",
    "maine", "black bears",
    "duke", "blue devils"
]

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

def format_channel(raw_name):
    if not raw_name:
        return "Check Spectrum Guide"
    return CHANNEL_MAP.get(raw_name, raw_name)

def get_tv_shows_for_week():
    programs = []
    today = datetime.now(LOCAL_TZ).date()

    for offset in range(7):
        target_date = today + timedelta(days=offset)
        date_str = target_date.strftime("%Y-%m-%d")
        day_label = target_date.strftime("%A, %B %d")

        url = f"https://tvmaze.com{date_str}"
        try:
            airings = fetch_json(url)
        except Exception as e:
            print(f"Error fetching TVMaze for {date_str}: {e}")
            continue

        for item in airings:
            show = item.get("show", {})
            title = show.get("name", "")
            title_lower = title.lower()
            genres = [g.lower() for g in show.get("genres", [])]
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
                "subtitle": f"Episode: {ep_name}" if ep_name else "TV Series",
                "category": matched_category
            })

    return programs

def get_womens_basketball_for_week():
    games = []
    today = datetime.now(LOCAL_TZ).date()

    for offset in range(7):
        target_date = today + timedelta(days=offset)
        espn_date = target_date.strftime("%Y%m%d")

        url = f"https://espn.com{espn_date}&limit=200"
        try:
            data = fetch_json(url)
        except Exception as e:
            print(f"Error fetching ESPN for {espn_date}: {e}")
            continue

        for event in data.get("events", []):
            name = event.get("name", "")
            name_lower = name.lower()

            if not any(team in name_lower for team in FAVORITE_TEAMS):
                continue

            event_date_iso = event.get("date", "")
            try:
                start_dt = datetime.fromisoformat(event_date_iso.replace("Z", "+00:00")).astimezone(LOCAL_TZ)
            except Exception:
                continue

            end_dt = start_dt + timedelta(hours=2)

            broadcasts = []
            for comp in event.get("competitions", []):
                for b in comp.get("broadcasts", []):
                    broadcasts.extend(b.get("names", []))

            raw_channel = broadcasts if broadcasts else "ESPN+ / Streaming"

            games.append({
                "date": start_dt.strftime("%Y-%m-%d"),
                "date_label": start_dt.strftime("%A, %B %d"),
                "start_iso": start_dt.isoformat(),
                "end_iso": end_dt.isoformat(),
                "time_display": start_dt.strftime("%I:%M %p").lstrip("0"),
                "channel": format_channel(raw_channel),
                "title": f"Women's Basketball: {name}",
                "subtitle": "NCAA Division I Women's Basketball",
                "category": "BASKETBALL"
            })

    return games

def main():
    all_items = get_womens_basketball_for_week() + get_tv_shows_for_week()
    all_items.sort(key=lambda x: x["start_iso"])

    output = {
        "updated_at": datetime.now(LOCAL_TZ).isoformat(),
        "programs": all_items
    }

    with open("tv_guide.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Saved {len(all_items)} programs to tv_guide.json")

if __name__ == "__main__":
    main()

