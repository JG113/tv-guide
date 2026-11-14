import urllib.request
import json
from datetime import datetime, timedelta

# Mapping of TVmaze network names to Maine Veterans' Homes Channel Numbers
CHANNEL_MAP = {
    "ABC": "11-1",
    "CBS": "11-6",
    "FOX": "12-1",
    "NBC": "12-6",
    "The CW": "13-1",
    "PBS": "13-6",
    "ION": "23-1",
    "ION Television": "23-1",
    "MeTV": "23-2",
    "NESN": "28-1",
    "ESPN": "47-2",
    "SEC Network": "48-3",
    "FS1": "49-1",
    "Pac-12 Network": "63-3",
    "Big Ten Network": "66-1",
    "ACC Network": "66-2",
    "CBS Sports Network": "70-1",
    "ESPNU": "74-2"
}

# Exact shows and keywords tailored to his preferences
FAVORITE_SHOWS = [
    "blue bloods", "chicago fire", "columbo", "matlock", "perry mason",
    "murder, she wrote", "ncis", "law & order", "csi", "criminal minds",
    "hawaii five-0", "magnum", "monk", "psych", "fbi", "the rookie",
    "walker", "in the heat of the night", "dragnet", "adam-12", "bones",
    "cold case", "without a trace", "major crimes", "the closer"
]

BASKETBALL_KEYWORDS = [
    "women's basketball", "womens basketball", "ncaa women", "college basketball"
]

def is_match(show_name, summary, genres):
    title_lower = (show_name or "").lower()
    summary_lower = (summary or "").lower()
    genres_lower = [g.lower() for g in (genres or [])]

    # 1. Check specific favorite shows
    for fav in FAVORITE_SHOWS:
        if fav in title_lower:
            return "Favorite Show"

    # 2. Check Women's College Basketball
    if "basketball" in title_lower or "basketball" in summary_lower:
        if any(kw in title_lower or kw in summary_lower for kw in BASKETBALL_KEYWORDS):
            # Exclude men's-only listings if clearly labeled men's
            if "men's" not in title_lower or "women's" in title_lower:
                return "Women's Basketball"

    # 3. Check general Detective / Crime dramas
    if "crime" in genres_lower or "mystery" in genres_lower:
        if any(word in summary_lower for word in ["detective", "investigat", "police", "murder", "precinct", "sheriff"]):
            return "Detective Show"

    return None

def format_time(airstamp):
    if not airstamp:
        return "Time TBD"
    dt = datetime.fromisoformat(airstamp)
    return dt.strftime("%I:%M %p").lstrip("0")

def fetch_weekly_guide():
    today = datetime.now()
    weekly_data = []

    for i in range(7):
        target_date = today + timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        day_label = "TODAY" if i == 0 else ("TOMORROW" if i == 1 else target_date.strftime("%A, %b %d"))
        
        url = f"https://tvmaze.com{date_str}"
        day_programs = []

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                episodes = json.loads(response.read().decode())

            for ep in episodes:
                show = ep.get("show", {})
                network = show.get("network")
                if not network:
                    continue

                net_name = network.get("name", "")
                if net_name not in CHANNEL_MAP:
                    continue

                show_name = show.get("name", "")
                summary = show.get("summary", "")
                genres = show.get("genres", [])
                category = is_match(show_name, summary, genres)

                if category:
                    airstamp = ep.get("airstamp", "")
                    # Filter out overnight hours (1 AM to 6 AM) to keep the list simple
                    if airstamp:
                        hour = datetime.fromisoformat(airstamp).hour
                        if 1 <= hour < 6:
                            continue

                    day_programs.append({
                        "time": format_time(airstamp),
                        "sort_key": airstamp,
                        "title": show_name,
                        "episode": ep.get("name", ""),
                        "network": net_name,
                        "channel": CHANNEL_MAP[net_name],
                        "category": category
                    })

            # Sort chronologically and remove duplicate back-to-back airings at same time
            day_programs.sort(key=lambda x: x["sort_key"])
            weekly_data.append({
                "date": date_str,
                "dayLabel": day_label,
                "isToday": (i == 0),
                "programs": day_programs
            })

        except Exception as e:
            print(f"Error fetching {date_str}: {e}")

    output = {
        "lastUpdated": today.strftime("%A, %B %d at %I:%M %p"),
        "days": weekly_data
    }

    # Save as a JS file so index.html works locally without needing a web server
    with open("guide_data.js", "w", encoding="utf-8") as f:
        f.write("window.TV_GUIDE_DATA = " + json.dumps(output, indent=2) + ";")
    print("Successfully updated guide_data.js!")

if __name__ == "__main__":
    fetch_weekly_guide()
