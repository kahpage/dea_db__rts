import sys
import json
from pathlib import Path
from typing import Any
import requests
from bs4 import BeautifulSoup
import lxml
import re
import unicodedata
from urllib.parse import urljoin, urlparse

# Add project root to sys.path (find the directory containing db_structs.py)
_root = Path(__file__).resolve().parent
while _root.parent != _root:
    if (_root / "db_structs.py").exists():
        if str(_root) not in sys.path:
            sys.path.append(str(_root))
        break
    _root = _root.parent

from db_structs import (
    Medium,
    Circle,
    Event,
    EventGroup,
    Source,
    ReliabilityTypes,
    OriginTypes,
    Location,
    is_to_add,
)

PATH_EVENT = Path(__file__).parent
PATH_CIRCLES_JSON = PATH_EVENT / "circles.json"
NAME = PATH_EVENT.name


import time


def retrieve_soup_fetch_if_needed(
    url: str,
    file_name: str = "raw.html",
    fallback_url: str | None = None,
    encoding: str | None = None,
) -> BeautifulSoup:
    """Retrieve a page, using a fallback URL when the primary source rejects the request."""
    html_path = PATH_EVENT / file_name
    if not html_path.exists():
        print(f"Raw HTML file not found, fetching from {url} ...")
        headers = {"User-Agent": "Mozilla/5.0"}
        response = None
        for attempt in range(5):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    break
                if fallback_url is not None:
                    print(
                        f"Primary source returned {response.status_code}; fetching from fallback ..."
                    )
                    response = requests.get(fallback_url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1 + attempt)

        if response is None or response.status_code != 200:
            status = response.status_code if response else "No response"
            raise Exception(
                f"Failed to retrieve data from {url}, status code: {status}"
            )
        html_path.write_bytes(response.content)
    with html_path.open("rb") as f:
        return BeautifulSoup(f, "lxml", from_encoding=encoding)


def sanitize_string(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[\s\n\t]+", " ", s)
    return s


FULLWIDTH = {
    "０": "0",
    "１": "1",
    "２": "2",
    "３": "3",
    "４": "4",
    "５": "5",
    "６": "6",
    "７": "7",
    "８": "8",
    "９": "9",
    "Ａ": "A",
    "Ｂ": "B",
    "Ｃ": "C",
    "Ｄ": "D",
    "Ｅ": "E",
    "Ｆ": "F",
    "Ｇ": "G",
    "Ｈ": "H",
    "Ｉ": "I",
    "Ｊ": "J",
    "Ｋ": "K",
    "Ｌ": "L",
    "Ｍ": "M",
    "Ｎ": "N",
    "Ｏ": "O",
    "Ｐ": "P",
    "Ｑ": "Q",
    "Ｒ": "R",
    "Ｓ": "S",
    "Ｔ": "T",
    "Ｕ": "U",
    "Ｖ": "V",
    "Ｗ": "W",
    "Ｘ": "X",
    "Ｙ": "Y",
    "Ｚ": "Z",
    "ａ": "a",
    "ｂ": "b",
    "ｃ": "c",
    "ｄ": "d",
    "ｅ": "e",
    "ｆ": "f",
    "ｇ": "g",
    "ｈ": "h",
    "ｉ": "i",
    "ｊ": "j",
    "ｋ": "k",
    "ｌ": "l",
    "ｍ": "m",
    "ｎ": "n",
    "ｏ": "o",
    "ｐ": "p",
    "ｑ": "q",
    "ｒ": "r",
    "ｓ": "s",
    "ｔ": "t",
    "ｕ": "u",
    "ｖ": "v",
    "ｗ": "w",
    "ｘ": "x",
    "ｙ": "y",
    "ｚ": "z",
}
SUBSTITUTIONS = {
    "～": "〜",
    "~": "〜",
    "ー": "-",
    "－": "-",
    "−": "-",
    "＆": "&",
    "＋": "+",
    "　": " ",
    "-": "-",
    "\\u3000": " ",
    "！": "!",
    "．": ".",
    "’": "'",
    "`": "'",
    "･": ".",
    "・": ".",
    "·": ".",
}
SUBSTITUTIONS_ALL = {}
SUBSTITUTIONS_ALL.update(FULLWIDTH)
SUBSTITUTIONS_ALL.update(SUBSTITUTIONS)


def is_in_with_subst(str1: str, bigstr: str) -> bool:
    return normalize_for_match(str1) in normalize_for_match(bigstr)


def normalize_for_match(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    for key, value in SUBSTITUTIONS_ALL.items():
        text = text.replace(key, value)
    return re.sub(r"\s+", "", text).casefold()


def is_equal_with_subst(str1: str, str2: str) -> bool:
    return normalize_for_match(str1) == normalize_for_match(str2)


def is_equal_or_group_member(str1: str, str2: str) -> bool:
    target = normalize_for_match(str1)
    if target == normalize_for_match(str2):
        return True
    annotated_target = re.sub(r"[（(][^（）()]*[）)]$", "", str1)
    if target != normalize_for_match(annotated_target):
        target = normalize_for_match(annotated_target)
    normalized_group = normalize_for_match(str2)
    group_members = re.split(r"[&+/]|vs", normalized_group)
    group_members.extend(
        part for member in list(group_members) for part in re.split(r"と", member)
    )
    return any(target == member for member in group_members)


RTS5_SPECIAL_MATCHES = {
    "RiceCandy": "Ricenady vs 少女頭巾",
    "はちみつくまさん": "はつみつくまさん",
    "まるちら": "まるちらダイオキシン",
    "ダイオキシン": "まるちらダイオキシン",
}


def is_rts5_name_match(secondary_name: str, official_name: str) -> bool:
    if is_equal_or_group_member(secondary_name, official_name):
        return True
    official_target = RTS5_SPECIAL_MATCHES.get(secondary_name)
    return official_target is not None and is_equal_with_subst(
        official_target, official_name
    )


def get_rts5_match_keys(name: str) -> set[str]:
    normalized_name = normalize_for_match(name)
    keys = {normalized_name}
    group_members = re.split(r"[&+/]|vs", normalized_name)
    keys.update(group_members)
    keys.update(part for member in group_members for part in re.split(r"と", member))
    return {key for key in keys if key}


def ensure_unicity(texts: list[str]) -> list[str]:
    """Ensure that the list of texts contains unique entries, ignoring case and substitutions."""
    seen = set()
    unique_texts = []
    for text in texts:
        normalized_text = text.lower()
        for key, value in SUBSTITUTIONS_ALL.items():
            normalized_text = normalized_text.replace(key, value)
        if normalized_text not in seen:
            seen.add(normalized_text)
            unique_texts.append(text)
    return unique_texts


def remove_wayback_prefix(url: str) -> str:
    return re.sub(r"^(?:https?:)?//web\.archive\.org/web/\d+(?:[a-z]{2}_)?/", "", url)


def main():
    """Create circles.json"""
    print(f"Retrieving circles information for {NAME} ...")
    circles: list[Circle] = []

    # Official source
    circles_info = []
    for i, base_url in enumerate(
        [
            "https://web.archive.org/web/20170227062610id_/http://reitaisai.com/rts12/name-circle",
        ]
    ):
        official_soup = retrieve_soup_fetch_if_needed(
            base_url,
            f"raw_official_{i}.html",
        )
        table_div = official_soup.find("div", class_="entry-content")
        if not table_div:
            continue

        tables = official_soup.find_all("table")

        for table in tables:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) < 3:
                    continue
                if "配置" in cells[0].text:
                    continue
                position = sanitize_string(cells[0].get_text(strip=True))
                circle_name = sanitize_string(cells[1].get_text(strip=True))
                pen_name = sanitize_string(cells[2].get_text(strip=True))
                if not position or not circle_name:
                    continue
                links = []
                # for cell in cells[1:]:
                #     for a in cell.find_all("a", href=True):
                #         href = remove_wayback_prefix(a["href"])
                #         if href:
                #             links.append(href)

                circle_info = {
                    "circle_name": circle_name,
                    "circle_penname": pen_name,
                    "position": position,
                    "links": links,
                    "description": [],
                }
                circles_info.append(circle_info)

    print(f"Found {len(circles_info)} circles across {i+1} official source pages")

    for info in circles_info:
        info["links"] = ensure_unicity(info["links"])

    official_name_index: dict[str, list[int]] = {}
    for index, info in enumerate(circles_info):
        for key in get_rts5_match_keys(info["circle_name"]):
            official_name_index.setdefault(key, []).append(index)

    secondary_links = [
        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC12%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9EN%E9%83%A8%E5%88%86",
        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC12%E5%B1%8A%E6%91%8A%E4%BD%8D/O%EF%BD%9E%E3%81%97%E9%83%A8%E5%88%86",
        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC12%E5%B1%8A%E6%91%8A%E4%BD%8D/%E3%81%99%EF%BD%9E%E3%81%AD%E9%83%A8%E5%88%86"
    ]
    secondary_match_count = 0
    for secondary_index, secondary_url in enumerate(secondary_links):
        secondary_soup = retrieve_soup_fetch_if_needed(
            secondary_url,
            f"raw_secondary_{secondary_index}.html",
            f"https://web.archive.org/web/2/{secondary_url}",
        )
        for row in secondary_soup.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) != 5:
                continue
            circle_name = cols[1].get_text(strip=True)
            links = [
                remove_wayback_prefix(str(a["href"]))
                for a in cols[2].find_all("a", href=True)
            ]
            for index in official_name_index.get(normalize_for_match(circle_name), []):
                if is_equal_or_group_member(
                    circle_name, circles_info[index]["circle_name"]
                ):
                    circles_info[index]["links"].extend(links)
                    secondary_match_count += 1
                    break

    print(f"Merged {secondary_match_count} secondary rows")

    for info in circles_info:
        circles.append(
            Circle(
                position=info["position"] if is_to_add(info["position"]) else None,
                description=info["description"]
                if is_to_add(info["description"])
                else None,
                links=ensure_unicity(info["links"])
                if is_to_add(info["links"])
                else None,
                aliases=[info["circle_name"]],
                pen_names=[info["circle_penname"]]
                if is_to_add(info["circle_penname"])
                else None,
            )
        )
    circles.sort(key=lambda c: c.position or "")

    # Save the extracted circle information to a JSON file
    with open(PATH_CIRCLES_JSON, "w", encoding="utf-8") as f:
        json.dump([c.get_json() for c in circles], f, ensure_ascii=False, indent=2)
    print(f"Saved {len(circles)} circles to {PATH_CIRCLES_JSON}")


if __name__ == "__main__":
    main()
