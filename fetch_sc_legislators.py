#!/usr/bin/env python3
import json
import requests
import os
from bs4 import BeautifulSoup

BASE = "https://www.scstatehouse.gov/member.php?chamber={}"
OUTPUT = "data/legislators.json"

def fetch_chamber(chamber: str):
    url = BASE.format(chamber)
    print(f"→ Fetching {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    members = []
    # For each district heading
    for heading in soup.find_all(lambda tag: tag.name in ("h1","h2","h3") and "District" in tag.get_text()):
        district = heading.get_text(strip=True)
        # Next paragraph contains the member info
        p = heading.find_next_sibling("p")
        if not p:
            continue
        # Find the legislator name link (member.php?member=)
        name_link = p.find("a", href=lambda href: href and "member.php?member=" in href)
        if not name_link:
            continue
        name = name_link.get_text(strip=True)
        # Extract party text within parentheses
        party = ""
        text = p.get_text()
        if "(" in text and ")" in text:
            party = text.split("(", 1)[1].split(")", 1)[0].strip()
        members.append({
            "name":     name,
            "district": district,
            "party":    party
        })
    print(f"  • Found {len(members)} in chamber {chamber}")
    return members

if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

    senators        = fetch_chamber("S")
    representatives = fetch_chamber("H")
    all_reps = senators + representatives

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(all_reps, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(all_reps)} total legislators to {OUTPUT}")
