#!/usr/bin/env python3
import json
import requests
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
    for heading in soup.find_all(lambda tag: tag.name in ("h1","h2","h3") 
                                              and "District" in tag.get_text()):
        district = heading.get_text(strip=True)
        a = heading.find_next("a", href=lambda href: href and "member.php" in href)
        if not a: continue
        name = a.get_text(strip=True)
        party_txt = a.next_sibling or ""
        party = party_txt.strip().strip("()")
        members.append({
            "name":     name,
            "district": district,
            "party":    party
        })
    print(f"  • Found {len(members)} in chamber {chamber}")
    return members

def main():
    senators       = fetch_chamber("S")
    representatives = fetch_chamber("H")
    all_reps = senators + representatives

    # ensure output dir exists
    import os
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(all_reps, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(all_reps)} total legislators to {OUTPUT}")

if __name__ == "__main__":
    main()
