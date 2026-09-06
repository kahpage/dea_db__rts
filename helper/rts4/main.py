import sys
import json
from pathlib import Path
from typing import Any
import requests
from bs4 import BeautifulSoup
import lxml
import re
import unicodedata

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
    is_to_add
)

PATH_EVENT = Path(__file__).parent
PATH_CIRCLES_JSON = PATH_EVENT / "circles.json"
NAME = PATH_EVENT.name



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
        response = requests.get(url)
        if response.status_code != 200 and fallback_url is not None:
            print(f"Primary source returned {response.status_code}; fetching from fallback (OUTDATED, consider providing the html file manually) !) ...")
            response = requests.get(fallback_url)
        if response.status_code != 200:
            raise Exception(
                f"Failed to retrieve data from {url}, status code: {response.status_code}"
            )
        html_path.write_bytes(response.content)
    with html_path.open("rb") as f:
        return BeautifulSoup(f, "lxml", from_encoding=encoding)

def sanitize_string(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[\s\n\t]+", " ", s)
    return s

FULLWIDTH = {
 '０': '0','１': '1','２': '2','３': '3','４': '4','５': '5','６': '6','７': '7','８': '8','９': '9','Ａ': 'A','Ｂ': 'B','Ｃ': 'C','Ｄ': 'D','Ｅ': 'E','Ｆ': 'F','Ｇ': 'G','Ｈ': 'H','Ｉ': 'I','Ｊ': 'J','Ｋ': 'K','Ｌ': 'L','Ｍ': 'M','Ｎ': 'N','Ｏ': 'O','Ｐ': 'P','Ｑ': 'Q','Ｒ': 'R','Ｓ': 'S','Ｔ': 'T','Ｕ': 'U','Ｖ': 'V','Ｗ': 'W','Ｘ': 'X','Ｙ': 'Y','Ｚ': 'Z','ａ': 'a','ｂ': 'b','ｃ': 'c','ｄ': 'd','ｅ': 'e','ｆ': 'f','ｇ': 'g','ｈ': 'h','ｉ': 'i','ｊ': 'j','ｋ': 'k','ｌ': 'l','ｍ': 'm','ｎ': 'n','ｏ': 'o','ｐ': 'p','ｑ': 'q','ｒ': 'r','ｓ': 's','ｔ': 't','ｕ': 'u','ｖ': 'v','ｗ': 'w','ｘ': 'x','ｙ': 'y','ｚ': 'z',
}
SUBSTITUTIONS = {
    '～': '〜',
    '~': '〜',
    'ー': '-',
    '－': '-',
    '−': '-',
    '＆': '&',
    '＋': '+',
    '　': ' ',
    '-': '-',
    '\\u3000': ' ',
    '！': '!',
    '．': '.',
    '’': "'",
    '`': "'",
    '･': '.',
    '・': '.',
    '·': '.',
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
    group_members = re.split(r"[&+と]", normalize_for_match(str2))
    return any(target == member for member in group_members)

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

def main():
    """Create circles.json"""
    print(f"Retrieving circles information for {NAME} ...")
    circles: list[Circle] = []
    
    # Official source
    # Parse the HTML content to extract circle information
    soup = retrieve_soup_fetch_if_needed("https://web.archive.org/web/20070427051959/http://www5b.biglobe.ne.jp/~cck/r4_list.htm", "raw_official.html", encoding="cp932")

    circles_info = []
    circles_info_used_indices = []
    table = soup.find_all('table')[-1]
    rows = table.find_all('tr')

    for row in rows[1:]:
        cols = row.find_all('td') 
        if len(cols) < 4:
            continue
        position = cols[0].get_text(strip=True)
        circle_name = cols[1].get_text(strip=True)
        pen_name = cols[2].get_text(strip=True)
        description_parts: list[str] = []
        description = cols[3].get_text(strip=True)
        if description:
            description_parts.append(description)
        links = []
        hp_tag = cols[1].find('a')
        if hp_tag and 'href' in hp_tag.attrs:
            links.append(hp_tag['href'])

        # if booth_name and "みょふ～会" in booth_name:
        #     print(f"Found special case circle: {circle_name} booth={booth_name}")
        
        circle_info = {
            "circle_name": circle_name,
            "circle_penname": pen_name,
            # "booth_name": booth_name,
            "position": position,
            "links": links,
            "description": description_parts,
        }

        circle_info["combined"] = f"{circle_info}"
        circles_info.append(circle_info)

        # if "ＭＡＮＩＡ" in circle_info["combined"]:
        #     print(circle_info["combined"])

    # Secondary source
    # Parse the HTML content to extract circle information
    soup = retrieve_soup_fetch_if_needed("https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC4%E5%B1%8A%E6%91%8A%E4%BD%8D",
            "raw_secondary.html",
            "https://web.archive.org/web/2/https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC4%E5%B1%8A%E6%91%8A%E4%BD%8D")

    table = soup.find_all('table')[-1]
    rows = table.find_all('tr')
    print(f"Found {len(rows)} rows in secondary source")

    for row in rows:
        cols = row.find_all('td')
        if len(cols) != 5:
            continue

        position = cols[0].text.strip()
        circle_name = cols[1].text.strip()
        link_tags = cols[2].find_all('a')
        links = []
        if link_tags:
            links = [a['href'] for a in link_tags if 'href' in a.attrs]
        # Find matching circle in primary source
        circle_info = None
        circle_additional_alias = None
        for index, info in enumerate(circles_info):
            if is_equal_or_group_member(circle_name, info["circle_name"]):
                circle_info = info
                circles_info_used_indices.append(index)
                if circle_name not in info["combined"]:
                    circle_additional_alias = circle_name
                break
            if circle_name == "C.S.C→luv" and info["circle_name"] == "C.S.C→lav":
                circle_info = info
                circles_info_used_indices.append(index)
                circle_additional_alias = circle_name
                break
            
        # if circle_info is None:
        #     # Special cases
        #     if circle_name == "DRAGIN":
        #         for index, info in enumerate(circles_info):
        #             if is_in_with_subst("ＤＯＲＡＧＩＮ'", info["combined"]):
        #                 circle_info = info
        #                 circles_info_used_indices.append(index)
        #                 circle_additional_alias = circle_name
        #                 break
        #     elif circle_name == "twirl-look":
        #         for index, info in enumerate(circles_info):
        #             if is_in_with_subst("twirl-lock", info["combined"]):
        #                 circle_info = info
        #                 circles_info_used_indices.append(index)
        #                 circle_additional_alias = circle_name
        #                 break
        #     elif circle_name == 'SeaFox':
        #         for index, info in enumerate(circles_info):
        #             if is_in_with_subst("Sea Fox", info["combined"]):
        #                 circle_info = info
        #                 circles_info_used_indices.append(index)
        #                 circle_additional_alias = circle_name
        #                 break
        #     elif circle_name == 'P-MANIA':
        #         for index, info in enumerate(circles_info):
        #             if is_in_with_subst("丁稚↑", info["combined"]):
        #                 circle_info = info
        #                 circles_info_used_indices.append(index)
        #                 circle_additional_alias = circle_name
        #                 break
        #     elif circle_name == 'FelisOvum':
        #         for index, info in enumerate(circles_info):
        #             if is_in_with_subst("Felis Ovum", info["combined"]):
        #                 circle_info = info
        #                 circles_info_used_indices.append(index)
        #                 circle_additional_alias = circle_name
        #                 break
        #     elif circle_name == 'mistbell':
        #         for index, info in enumerate(circles_info):
        #             if is_in_with_subst("mist bell", info["combined"]):
        #                 circle_info = info
        #                 circles_info_used_indices.append(index)
        #                 circle_additional_alias = circle_name
        #                 break
        #     elif circle_name == 'Twinkle Snows':
        #         # Was not in primary source
        #         circle_info = {
        #             "circle_name": "Twinkle Snows",
        #             "circle_penname": "",
        #             "booth_name": "",
        #             "links": [],
        #             "comments": [],
        #         }
        #         circle_additional_alias = "Ｔｗｉｎｋｌｅ　Ｓｎｏｗｓ"
        #     elif circle_name == 'まりおねっと装甲猟兵':
        #         # Was not in primary source
        #         circle_info = {
        #             "circle_name": "まりおねっと装甲猟兵",
        #             "circle_penname": "",
        #             "booth_name": "",
        #             "links": [],
        #             "comments": [],
        #         }
        #     elif circle_name == '月黄泉の街':
        #         # Was not in primary source
        #         circle_info = {
        #             "circle_name": "月黄泉の街",
        #             "circle_penname": "",
        #             "booth_name": "",
        #             "links": [],
        #             "comments": [],
        #         }

        if circle_info is None: # No match found
            print(f"Circle from secondary source not found in primary: {circle_name}")
            continue
        
        circle_links = circle_info["links"]
        if is_to_add(links):
            circle_links.extend(links)
        # booth_name = circle_info["booth_name"]
        aliases = [circle_name]
        # if is_to_add(booth_name):
        #     aliases.append(booth_name)
        circle_penname = circle_info["circle_penname"]
        position = circle_info["position"]
        description = circle_info["description"]
        circle = Circle(
            position=position if is_to_add(position) else None,
            description=description if is_to_add(description) else None,
            links=ensure_unicity(circle_links) if is_to_add(circle_links) else None,
            aliases=ensure_unicity(aliases),
            pen_names=[circle_penname] if is_to_add(circle_penname) else None,
        )
        circles.append(circle)
    
    # circles.sort(key=lambda c: c.position)
    # List all indices not used from primary source
    unused_indices = [i for i in range(len(circles_info)) if circles_info[i]["circle_name"] and i not in circles_info_used_indices]
    print(f"Unused: {unused_indices}")
    for i in unused_indices:
        info = circles_info[i]
        print(f"Unused circle: {info['combined']}")
    # # This revealed some not found circles, let's add them too
    # circles.append(Circle(
    #         position=None,
    #         aliases=["マリオネット装甲猟兵"],
    # ))
    # circles.append(Circle(
    #         position=None,
    #         aliases=["ＮＥＫＯＧＯＹＡ"],
    # ))



    # Save the extracted circle information to a JSON file
    with open(PATH_CIRCLES_JSON, "w", encoding="utf-8") as f:
        json.dump([c.get_json() for c in circles], f, ensure_ascii=False, indent=2)
    print(f"Saved {len(circles)} circles to {PATH_CIRCLES_JSON}")


if __name__ == "__main__":
    main()
