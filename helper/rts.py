# Notes:
import sys
import json
from pathlib import Path
from typing import Any

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
)

RT, OT = ReliabilityTypes, OriginTypes

PATH_HELPER = Path(__file__).parent
PATH_EVENT_GROUP = PATH_HELPER.parent
PATH_MEDIA = PATH_EVENT_GROUP / "media"


def retrieve_circles(event_name: str) -> list[Circle]:
    """Retrieve circles of given event. In the circle file has not been created, execute the creation script first."""
    circles_json_path = PATH_HELPER / event_name / "circles.json"
    if not circles_json_path.exists():
        print(
            f"Circle file for {event_name} not found, running the creation script ..."
        )
        creation_script_path = PATH_HELPER / event_name / "main.py"
        if not creation_script_path.exists():
            raise FileNotFoundError(
                f"Creation script for {event_name} not found at {creation_script_path}"
            )
        # Import main() from the creation script and execute
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            f"{event_name}.main", creation_script_path
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "main"):
                module.main()

        if not circles_json_path.exists():
            raise FileNotFoundError(
                f"Creation script {creation_script_path} failed to create {circles_json_path}"
            )

    with circles_json_path.open("r", encoding="utf-8") as f:
        circles_raw = json.load(f)
    return [Circle.load_from_json(c) for c in circles_raw]


if __name__ == "__main__":
    events: list[Event] = []
    disabled_events: list[int | str] = []
    main_page_with_history = "https://web.archive.org/web/2/https://reitaisai.com/"

    i = 1  # ==== rts1 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "01_rts1.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E6%96%87%E4%BB%B6:%E4%BE%8B%E5%A4%A7%E7%A5%AD%E7%AC%AC%E4%B8%80%E5%B1%8A%E6%8F%92%E7%94%BB5.jpg",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.5587817, 139.7240667),
                address="1-chōme-20-20 Minamikamata, Ota City, Tokyo 144-0035, Japan",
                description="大田区産業プラザPiO",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC1%E5%B1%8A%E6%91%8A%E4%BD%8D",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWlM30iutkku0DTSgB6rPTEw19CjIMC8icvKceGIJ2eTMqA35cGcD96nMco5OldsWWRdWwEFDXLxoAAXei1t3Zf7GGFGgyWvsUa8bPofUHCGvcxTY3TlJhQNxQFHYYg4fqCFHSE=w408-h544-k-no",
                url="https://maps.app.goo.gl/7ebCWMtzDWoLJQms5",
            ),
        ]
        event = Event(
            aliases=[
                "例大祭1",
                "博麗神社例大祭",
                "Hakurei Jinja Reitaisai",
                "Reitaisai 1",
                "RTS1",
                "第一回 博麗神社例大祭",
            ],
            dates="2004.04.18",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://jiyugiga.sakura.ne.jp/reitaisai_list.html",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://x.com/KOR_jiyugiga/status/1240620466961670145/photo/1",
                    (ReliabilityTypes.Reliable, OriginTypes.OfficialExt),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC1%E5%B1%8A%E6%91%8A%E4%BD%8D (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
                Source(
                    "Participating circles (notes): Circles in Tweeter picture / thwiki.cc but not on reitaisai_list: 'Twinkle Snows', 'まりおねっと装甲猟兵', '月黄泉の街', Circles on reitaisai_list but not on thwiki.cc: 'マリオネット装甲猟兵', 'ＮＥＫＯＧＯＹＡ'",
                    (ReliabilityTypes.Doubtful, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            comments="For more media, see https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
            last_edited="2026.09.02",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 2  # ==== rts2 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "02_rts2.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.655153, 139.7607689),
                address="Japan, 〒105-7501 Tokyo, Minato City, Kaigan, 1 Chome−7−1 東京ポートシティ竹芝オフィスタワ",
                comments=None,
                description="東京都立産業貿易センター浜松町館",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC2%E5%B1%8A%E6%91%8A%E4%BD%8D",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmihIGbPitN7h8Vc_sXo8I679FTgrlkYst2LWaAy_Wl45MDqMaFnozSO4Y2Vud8h07FgRpXdq_CPW3IWnFwj-AyKuJ0L7ShZyQ41TQcBAFNOouYZR3jFZXxn_SQsgsK-FST-5JK8g=w408-h544-k-no",
                url="https://maps.app.goo.gl/ZF8XaGQinUTwnNMw6",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第二回 博麗神社例大祭",
            ],
            dates="2005.05.04",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20050828173158/http://www.reitaisai.com/clist.html",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC2%E5%B1%8A%E6%91%8A%E4%BD%8D (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            comments=None,
            last_edited="2026.09.03",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 3  # ==== rts3 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "03_rts3.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.7284509, 139.7180429),
                address="Japan, 〒170-8630 Tokyo, Toshima City, Higashiikebukuro, 3 Chome−1−4 サンシャインシティ 青エリア",
                description="サンシャインシティ",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC2%E5%B1%8A%E6%91%8A%E4%BD%8D",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWlh79QV2PqUMK69IvfW9afI4WCFPZ4G5B6zUsqcdv05bWI0QsSbAhGHCM94alRNdrNYMGdRkIFQmInqUcyQj7PncjMI3AJIzK7Yb4lWYRZ-Jw1b6KbFi2-x6RlJQ5ExGwwSZEcaKw=s0?imgmax=0",
                url="https://maps.app.goo.gl/W3NY9KfiAJQKQAdq7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第三回 博麗神社例大祭",
            ],
            dates="2006.05.21",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20060423161331/http://www.reitaisai.com/clist.html",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC3%E5%B1%8A%E6%91%8A%E4%BD%8D (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.03",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 4  # ==== rts4 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            Medium(
                "04_2007reitaisai_map.pdf",
                [
                    Source(
                        "https://web.archive.org/web/20260411013937/http://www.green.dti.ne.jp/maisan/gensoukyou/image/2007reitaisai_map.pdf",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.7284509, 139.7180429),
                address="Japan, 〒170-8630 Tokyo, Toshima City, Higashiikebukuro, 3 Chome−1−4 サンシャインシティ 青エリア",
                description="サンシャインシティ 展示ホールD",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC2%E5%B1%8A%E6%91%8A%E4%BD%8D",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWlh79QV2PqUMK69IvfW9afI4WCFPZ4G5B6zUsqcdv05bWI0QsSbAhGHCM94alRNdrNYMGdRkIFQmInqUcyQj7PncjMI3AJIzK7Yb4lWYRZ-Jw1b6KbFi2-x6RlJQ5ExGwwSZEcaKw=s0?imgmax=0",
                url="https://maps.app.goo.gl/W3NY9KfiAJQKQAdq7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第四回 博麗神社例大祭",
            ],
            dates="2007.05.20",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20070427051959/http://www5b.biglobe.ne.jp/~cck/r4_list.htm",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC4%E5%B1%8A%E6%91%8A%E4%BD%8D (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.03",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 5  # ==== rts5 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト 西4ホール",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC5%E5%B1%8A%E6%91%8A%E4%BD%8D",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第五回 博麗神社例大祭",
            ],
            dates="2008.05.25",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20251012230741/http://www5b.biglobe.ne.jp/~cck/list/rei5_list_tu.htm",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC5%E5%B1%8A%E6%91%8A%E4%BD%8D 	2008-05-25 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.04",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 6  # ==== rts6 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "06_rts6.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東3・4・5・6ホール",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC6%E5%B1%8A%E6%91%8A%E4%BD%8D/%E3%81%82%EF%BD%9E%E3%81%91%E9%83%A8%E5%88%86",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第六回 博麗神社例大祭",
            ],
            dates="2009.03.08",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): http://www.green.dti.ne.jp/maisan/gensoukyou/reitaisai6_list.html",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC6%E5%B1%8A%E6%91%8A%E4%BD%8D/%E3%81%82%EF%BD%9E%E3%81%91%E9%83%A8%E5%88%86 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.04",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 7  # ==== rts7 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東2・3・4・5・6ホール",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC7%E5%B1%8A%E6%91%8A%E4%BD%8D/%E3%81%82%EF%BD%9E%E3%81%91%E9%83%A8%E5%88%86",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第七回 博麗神社例大祭",
            ],
            dates="2010.03.14",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): http://www.green.dti.ne.jp/maisan/gensoukyou/reitaisai7_list.html",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC7%E5%B1%8A%E6%91%8A%E4%BD%8D/%E3%81%82%EF%BD%9E%E3%81%91%E9%83%A8%E5%88%86 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.04",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 8  # ==== rts8 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            Medium(
                "08_2011_reitaisai8_map.pdf",
                [
                    Source(
                        "http://www.green.dti.ne.jp/maisan/gensoukyou/image/2011_reitaisai8_map.pdf",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東1・2・3・4・5・6ホール",
                sources=[
                    Source(
                        "https://web.archive.org/web/20110928120540/http://www.reitaisai.com/circlelists/",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第八回 博麗神社例大祭",
            ],
            dates="2011.05.08",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20110928120540/http://www.reitaisai.com/circlelists/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC8%E5%B1%8A%E6%91%8A%E4%BD%8D/%EF%BB%BF%E3%81%82%EF%BD%9E%E3%81%95%E9%83%A8%E5%88%86 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.04",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 9  # ==== rts9 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "09_rts9.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東1・2・3・4・5・6ホール",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC9%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9EM%E9%83%A8%E5%88%86",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第九回 博麗神社例大祭",
            ],
            dates="2012.05.27",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): http://g-mirror.gptwm.com/reitaisai/reitaisai9_poslist.pdf",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC9%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9EM%E9%83%A8%E5%88%86 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.05",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 10  # ==== rts10 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "10_rts10.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            Medium(
                "10_rts10_map_e123.png",
                [
                    Source(
                        "https://web.archive.org/web/20130727024137/http://reitaisai.com/list_circle2/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            Medium(
                "10_rts10_map_e456.png",
                [
                    Source(
                        "https://web.archive.org/web/20130727024137/http://reitaisai.com/list_circle2/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東1・2・3・4・5・6ホール",
                sources=[
                    Source(
                        "https://web.archive.org/web/20130727035307/http://reitaisai.com/list_circle1#circlelist_top",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十回 博麗神社例大祭",
            ],
            dates="2013.05.26",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20130727035307/http://reitaisai.com/list_circle1#circlelist_top",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC10%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9EM%E9%83%A8%E5%88%86 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.05",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 11  # ==== rts11 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "11_rts11.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            Medium(
                "11_rts11_top.jpg",
                [
                    Source(
                        "https://web.archive.org/web/20150316084312/https://reitaisai.com/rts11/rts11/block123",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東1・2・3・4・5・6ホール",
                sources=[
                    Source(
                        "https://web.archive.org/web/20150316084312/https://reitaisai.com/rts11/rts11/block123",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十一回 博麗神社例大祭",
            ],
            dates="2014.05.11",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20150316084312/https://reitaisai.com/rts11/rts11/block123",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://web.archive.org/web/20170708043332/https://reitaisai.com/rts11/rts11/block456",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (3): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC11%E5%B1%8A%E6%91%8A%E4%BD%8D/%E3%81%99%EF%BD%9E%E3%81%AD%E9%83%A8%E5%88%86 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.06",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 12  # ==== rts12 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "12_rts12.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            Medium(
                "12_cropped-a282587d09933cd3f726bda94fb0f69f.jpg",
                [
                    Source(
                        "https://web.archive.org/web/20170227062610/http://reitaisai.com/rts12/name-circle",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東1・2・3・4・5・6ホール",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC12%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9EN%E9%83%A8%E5%88%86 (well sourced)",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十二回 博麗神社例大祭",
            ],
            dates="2016.05.08",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20170227062610/http://reitaisai.com/rts12/name-circle",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC12%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9EN%E9%83%A8%E5%88%86 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.06",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 13  # ==== rts13 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "13_rts13.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東1・2・3・4・5・6ホール",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC13%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9E%E3%81%88%E9%83%A8%E5%88%86",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十三回 博麗神社例大祭",
            ],
            dates="2016.05.08",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20250821211501/http://s.reitaisai.com/rts13/name-circle/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC13%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9E%E3%81%88%E9%83%A8%E5%88%86 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.06",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 14  # ==== rts14 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "14_rts14.jpg",
                [
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東1・2・3・4・5・6ホール",
                sources=[
                    Source(
                        "https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC14%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9ES%E9%83%A8%E5%88%86",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十四回 博麗神社例大祭",
            ],
            dates="2017.05.07",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://reitaisai.com/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20230801074707/http://s.reitaisai.com/rts14/block/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles (2): https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD/%E7%AC%AC14%E5%B1%8A%E6%91%8A%E4%BD%8D/A%EF%BD%9ES%E9%83%A8%E5%88%86 (well sourced)",
                    (ReliabilityTypes.Reliable, OriginTypes.External),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.06",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 15  # ==== rts15 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "15_rts15.jpg",
                [
                    Source(
                        main_page_with_history,
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト 東ホール",
                sources=[
                    Source(
                        "https://web.archive.org/web/20260512005313/https://reitaisai.com/rts15/?p=532",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十五回 博麗神社例大祭",
            ],
            dates="2018.05.06",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://web.archive.org/web/20260512005313/https://reitaisai.com/rts15/?p=532",
                    (RT.Reliable, OT.Official),
                ),
                Source(
                    "Participating circles: https://web.archive.org/web/20231018052347/http://s.reitaisai.com/rts15block/",
                    (RT.Reliable, OT.Official),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.06",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 16  # ==== rts16 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "16_rts16.jpg",
                [
                    Source(
                        main_page_with_history,
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト 西ホール",
                sources=[
                    Source(
                        main_page_with_history,
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十六回 博麗神社例大祭",
            ],
            dates="2019.05.05",
            circles=[],
            media=media_,
            sources=[
                Source("Date: main_page_with_history", (RT.Reliable, OT.Official)),
                Source(
                    "Participating circles: https://web.archive.org/web/20260130135218/http://s.reitaisai.com/rts16/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.06",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 17  # ==== rts17 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "17_rts17.jpg",
                [
                    Source(
                        "https://web.archive.org/web/20200318042625/https://reitaisai.com/rts17/?p=519",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
            ),
            Medium(  # Not sure really eg scope (TH17 circle list page)
                "17_reitaisai_illust0725-860x1214.jpg",
                [
                    Source(
                        "https://web.archive.org/web/20251016142017/https://reitaisai.com/rts17/?p=222",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(34.9713021, 138.403819),
                address="Japan, 〒422-8006 Shizuoka, Suruga Ward, Magarikane, 3 Chome−1−10 西館",
                description="ツインメッセ静岡 (CANCELLED)",
                sources=[
                    Source(
                        "https://web.archive.org/web/20200318042625/https://reitaisai.com/rts17/?p=519",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://maps.app.goo.gl/rMQ2csVhzjv39cpT9",
                url="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmxrusm9oXeDGfebZn1cc-XxrxsyXLw8CKmlHRwzlLJ9XVrCYPUjJR-bFYfj3cked2QbGmX4gOgAExEn2iuxaM0DdyeJsjf48AfEIH0pomBKS9L_r2HuwnT9dCzEXykzvJ1hsvpCkcojFg=s0?imgmax=0",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十七回 博麗神社例大祭",
            ],
            dates="2020.03.22 -> 2020.05.17 -> CANCELLED",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://web.archive.org/web/20200318042625/https://reitaisai.com/rts17/?p=519",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles: https://web.archive.org/web/20251016142017/https://reitaisai.com/rts17/?p=222",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "First postpone: https://web.archive.org/web/20260512005315/https://reitaisai.com/rts17/?p=574",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Cancelled: https://web.archive.org/web/20260904010034/https://reitaisai.com/rts17/?p=616",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.06",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 18  # ==== rts18 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "18_rts18.jpg",
                [
                    Source(
                        main_page_with_history,
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
            ),
            Medium(
                "18_top_img_pc2.jpg",
                [
                    Source(
                        "https://web.archive.org/web/20260719040849/https://reitaisai.com/rts18/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(34.9713021, 138.403819),
                address="Japan, 〒422-8006 Shizuoka, Suruga Ward, Magarikane, 3 Chome−1−10 西館",
                description="ツインメッセ静岡",
                sources=[
                    Source(
                        "https://web.archive.org/web/20260719040849/https://reitaisai.com/rts18/",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://maps.app.goo.gl/rMQ2csVhzjv39cpT9",
                url="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmxrusm9oXeDGfebZn1cc-XxrxsyXLw8CKmlHRwzlLJ9XVrCYPUjJR-bFYfj3cked2QbGmX4gOgAExEn2iuxaM0DdyeJsjf48AfEIH0pomBKS9L_r2HuwnT9dCzEXykzvJ1hsvpCkcojFg=s0?imgmax=0",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十八回 博麗神社例大祭",
                # Shizokua 1
                "例大祭in静岡1",
                "博麗神社例大祭in静岡1",
                "Hakurei Jinja Reitaisai in Shizuoka 1",
                "Reitaisai in Shizuoka 1",
                "RTS S1",
                "第一回博麗神社例大祭in静岡",
            ],
            dates="2021.03.21",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://web.archive.org/web/20260719040849/https://reitaisai.com/rts18/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles: https://web.archive.org/web/20250521183216/https://reitaisai.com/rts18/list_1/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Is also 例大祭in静岡1, guess based on location + date (being previous to the second edition)",
                    (ReliabilityTypes.Guess, OriginTypes.Unsourced),
                ),
            ],
            locations=locations,
            description=None,
            comments=None,
            last_edited="2026.09.06",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 19  # ==== rts19 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "19_rts19.png",
                [
                    Source(
                        main_page_with_history,
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
            ),
            Medium(
                "19_8908737d0e88543529d40271143c5420-3.png",
                [
                    Source(
                        "https://web.archive.org/web/20260512005258/https://reitaisai.com/rts19/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("19_Circle_bosyu.gif", [Source("https://web.archive.org/web/20220325072223/https://reitaisai.com/rts19/accepted-circle-list/", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト 東ホール",
                sources=[
                    Source(
                        "https://web.archive.org/web/20260512005258/https://reitaisai.com/rts19/",
                        (ReliabilityTypes.Likely, OriginTypes.External),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第十九回 博麗神社例大祭",
            ],
            dates="2022.05.08",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://web.archive.org/web/20260512005258/https://reitaisai.com/rts19/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles: https://reitaisai.com/rts19/accepted-circle-list/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.06",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 20  # ==== rts20 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "20_rts20.png",
                [
                    Source(
                        main_page_with_history,
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
            ),
            Medium(
                "20_ab2b25419a9c827132521c8dc89ca9e3-1.png",
                [
                    Source(
                        "https://web.archive.org/web/20260512005327/https://reitaisai.com/rts20/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト 東ホール",
                sources=[
                    Source(
                        "https://web.archive.org/web/20260512005327/https://reitaisai.com/rts20/",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第二十回 博麗神社例大祭",
            ],
            dates="2023.05.07",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://web.archive.org/web/20260512005327/https://reitaisai.com/rts20/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles: https://web.archive.org/web/20260417084948/https://reitaisai.com/rts20/place-assign/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.07",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 21  # ==== rts21 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "21_rts21.png",
                [
                    Source(
                        main_page_with_history,
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
            ),
            Medium(
                "21_RTS21_WebTopImg_Catalog_Pc-4.png",
                [
                    Source(
                        "https://web.archive.org/web/20260623174902/https://reitaisai.com/rts21/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            Medium(
                "21_e032046d2bfff3731ad96091eeba60f2.png",
                [
                    Source(
                        "https://web.archive.org/web/20260623174902/https://reitaisai.com/rts21/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東4・5・6ホール",
                sources=[
                    Source(
                        "https://web.archive.org/web/20260623174902/https://reitaisai.com/rts21/",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第二十一回 博麗神社例大祭",
            ],
            dates="2024.05.03",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://web.archive.org/web/20260623174902/https://reitaisai.com/rts21/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
                Source(
                    "Participating circles: https://web.archive.org/web/20260512005320/https://reitaisai.com/rts21/circle-place-assign/",
                    (ReliabilityTypes.Reliable, OriginTypes.Official),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.07",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 22  # ==== rts22 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "22_rts22.png",
                [
                    Source(
                        main_page_with_history,
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
            ),
            Medium(
                "22_RTS22_firstView_pc_catalog.png",
                [
                    Source(
                        "https://web.archive.org/web/20260710081327/https://reitaisai.com/rts22/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            Medium(
                "https://web.archive.org/web/20250608183927/https://reitaisai.com/rts22/wp-content/uploads/sites/45/2025/04/RTS22_almighty_1.2.1.pdf",
                [
                    Source(
                        "https://web.archive.org/web/20260512005321/https://reitaisai.com/rts22/before-circle-docs/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            Medium(
                "https://web.archive.org/web/20250608183927/https://reitaisai.com/rts22/wp-content/uploads/sites/45/2025/04/RTS22_DigiAnaAlmighty_1.1.0.pdf",
                [
                    Source(
                        "https://web.archive.org/web/20260512005321/https://reitaisai.com/rts22/before-circle-docs/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            Medium(
                "https://web.archive.org/web/20260215210545/https://reitaisai.com/rts22/wp-content/uploads/sites/45/2025/04/RTS22_map-for-circle_v3.pdf",
                [
                    Source(
                        "https://web.archive.org/web/20260512005321/https://reitaisai.com/rts22/before-circle-docs/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("https://web.archive.org/web/20260512005321/https://reitaisai.com/rts22/before-circle-docs/", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("https://web.archive.org/web/20260512005321/https://reitaisai.com/rts22/before-circle-docs/", (RT.Reliable, OT.Official))]),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東3・4・5・6ホール",
                sources=[
                    Source(
                        "https://web.archive.org/web/20260710081327/https://reitaisai.com/rts22/",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第二十二回 博麗神社例大祭",
            ],
            dates="2025.05.05",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://web.archive.org/web/20260710081327/https://reitaisai.com/rts22/",
                    (RT.Reliable, OT.Official),
                ),
                Source(
                    "Participating circles (1): https://web.archive.org/web/20260417090718id_/https://reitaisai.com/rts22/accepted-circle-list/",
                    (RT.Reliable, OT.Official),
                ),
                Source(
                    "Participating circles (2): https://web.archive.org/web/20260511032221id_/https://reitaisai.com/rts22/accepted-additional-circles-list/",
                    (RT.Reliable, OT.Official),
                ),
            ],
            locations=locations,
            description=None,
            comments="A circle.ms entry seem to have existed but I could not find it: https://reitaisai.com/rts22/circle-ms/",
            last_edited="2026.09.07",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 23  # ==== rts23 ====
    if i not in disabled_events:
        event_name = f"rts{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "23_a60addd0861b0933f9dafa82daecf126.png",
                [Source("main_page_with_history", (RT.Reliable, OT.Official))],
            ),
            Medium(
                "23_Img_pc.png",
                [
                    Source(
                        "https://web.archive.org/web/20260812171832/https://reitaisai.com/rts23/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.6284445, 139.7926734),
                address="3 Chome-11-1 Ariake, Koto City, Tokyo 135-0063, Japan",
                description="東京ビッグサイト東ホール",
                sources=[
                    Source(
                        "https://web.archive.org/web/20260812171832/https://reitaisai.com/rts23/",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWmniRNV84lzB1SNXuy60c0lznxgbqmNtYyJ8rkHQXk9u4qwSBeDafMEeWY7SaHOPcgw9m9BObYv4SvxJATFOtwEErABiE-oZjeBkl96ni8hTFClnpIJNnLLpRCBg6Ue9K__BWAAVQ=s0?imgmax=0",
                url="https://maps.app.goo.gl/6EYu64eY7PRhWRxu7",
            ),
        ]
        event = Event(
            aliases=[
                f"例大祭{i}",
                f"博麗神社例大祭{i}",
                f"Hakurei Jinja Reitaisai {i}",
                f"Reitaisai {i}",
                f"RTS{i}",
                "第二十三回 博麗神社例大祭",
            ],
            dates="2026.05.04",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://web.archive.org/web/20260812171832/https://reitaisai.com/rts23/",
                    (RT.Reliable, OT.Official),
                ),
                Source(
                    "Participating circles: https://web.archive.org/web/20260502053653/https://reitaisai.com/rts23/circle-place-assign/",
                    (RT.Reliable, OT.Official),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.09.07",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    # i =   # ==== rts ====
    # if i not in disabled_events:
    #     event_name = f"rts{i}"
    #     print(f"Processing {event_name} ...")

    #     media_ = [
    #         # Medium("", [Source("", (RT.Reliable, OT.Official))]),
    #         # Medium("", [Source("", (RT.Reliable, OT.Official))]),
    #         # Medium("", [Source("", (RT.Reliable, OT.Official))]),
    #     ]
    #     locations = [
    #         # Location(
    #         #     coordinates=(35.5587817, 139.7240667),
    #         #     address="1-chōme-20-20 Minamikamata, Ota City, Tokyo 144-0035, Japan",
    #         #     description="大田区産業プラザPiO",
    #         #     sources=[
    #         #         Source(
    #         #             "",
    #         #             (ReliabilityTypes.Reliable, OriginTypes.Official),
    #         #         )
    #         #     ],
    #         #     # comments=None,
    #         #     imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWlM30iutkku0DTSgB6rPTEw19CjIMC8icvKceGIJ2eTMqA35cGcD96nMco5OldsWWRdWwEFDXLxoAAXei1t3Zf7GGFGgyWvsUa8bPofUHCGvcxTY3TlJhQNxQFHYYg4fqCFHSE=w408-h544-k-no",
    #         #     url="https://maps.app.goo.gl/7ebCWMtzDWoLJQms5",
    #         # ),
    #     ]
    #     event = Event(
    #         aliases=[
    #             f"例大祭{i}",
    #             f"博麗神社例大祭{i}",
    #             f"Hakurei Jinja Reitaisai {i}",
    #             f"Reitaisai {i}",
    #             f"RTS{i}",
    #             @@
    #         ],
    #         dates="",
    #         circles=[],
    #         media=media_,
    #         sources=[
    #             # Source(f"Date: {}", (RT.Reliable, OT.Official)),
    #             # Source("Participating circles: ", (RT.Reliable, OT.Official)),
    #         ],
    #         locations=locations,
    #         description=None,
    #         # comments=None,
    #         last_edited="2026.09.07",
    #     )

    #     # Retrieve circles
    #     # event.circles = retrieve_circles(event_name)
    #     events.append(event)

    # ==== event group ====
    media = [
        # Medium("",
        #        [Source("", (RT.Reliable, OT.Official))]),
        # Medium("",
        #        [Source("", (RT.Reliable, OT.Official))]),
    ]
    links = [
        "https://reitaisai.com/",
        "https://x.com/HakureijinjyaS",
        "https://www.youtube.com/channel/UCWgWAk02r-HKSYX2h6wnJVA",
    ]

    event_group = EventGroup(
        aliases=["博麗神社例大祭", "例大祭", "Reitaisai", "RTS"],
        events=events,
        media=media,
        links=links,
        sources=[
            # Source(
            #     "",
            #     (ReliabilityTypes.Reliable, OriginTypes.Official),
            # ),
        ],
        comments="Many sources from https://thwiki.cc/%E5%8D%9A%E4%B8%BD%E7%A5%9E%E7%A4%BE%E4%BE%8B%E5%A4%A7%E7%A5%AD#15. As on thwiki.cc, several circle count discrepancies exist compared to official sources (not sourced here but can be seen on thwiki.cc).",
        description=None,
        last_edited="2026.09.02",
    )

    raise ValueError("Fix Date sources")
    raise ValueError("Location source, avoid External")
    print(f"Saving {Path(__file__).stem} database...")
    event_group.save(PATH_EVENT_GROUP, indent=None)
    print("Done")
