"""The studio: Astrofox and its three divisions, for the homepage panels and
the press kit.

Astrofox is the company. Callisto, Minecraft and Game Development are
divisions of it, not separate businesses. Images are relative to images/.
Real facts only: where something isn't known it's None with a TODO.
"""
from .core import GAME_NAME

COMPANY = {
    "name": "Astrofox Studios",
    "role": "Founder & CEO, creative lead",
    "since": "2021",
    "logo": "brand/astrofox-wordmark-white.webp",
    "logo_size": (720, 233),
    "line": (
        "Astrofox is the company. It started in 2021 as a Minecraft event series and "
        "now has three divisions: hosting, Minecraft and game development. Lutraa and "
        "I run it as co-CEOs. I founded it and I lead the creative side."
    ),
    "url": "https://astrofoxstudios.com",
    "url_label": "astrofoxstudios.com",
}

DIVISIONS = [
    {
        "key": "callisto",
        "name": "Callisto",
        "kind": "Hosting and infrastructure",
        "logo": "brand/callisto-wordmark-white.webp",
        "logo_size": (720, 189),
        "logo_alt": "Callisto",
        "line": (
            "Game server hosting, and the Aurora Panel to run it from. It began as "
            "ExpHost in 2023 so we had somewhere to keep our own servers online, and "
            "became Callisto in 2026."
        ),
        "role": "Head of software",
        "role_note": "I build the panel and the site, and run Callisto day to day.",
        "image": "studio/aurora-workspace.webp",
        "image_size": (1600, 900),
        "image_alt": "The Aurora Panel workspace: a clock over a purple wave wallpaper, with app icons down the left edge",
        "caption": "Aurora Panel, the workspace",
        "links": [
            {"label": "callisto.host", "url": "https://callisto.host"},
            {"label": "Case study", "endpoint": "work.detail", "slug": "callisto"},
        ],
    },
    {
        "key": "minecraft",
        "name": "Minecraft",
        "kind": "Solaris and Destiny Games",
        "logo": "brand/solaris-mark.webp",
        "logo_size": (400, 400),
        "logo_alt": "Solaris",
        "line": (
            "Solaris is a competitive Minecraft Java server with ranked play and "
            "seasons, in Early Access since June 2026. Destiny Games is the event "
            "series the studio started with."
        ),
        "role": "Art director, Solaris",
        "role_note": "The identity, the interfaces and how the whole thing looks.",
        "image": "studio/city-day.webp",
        "image_size": (1600, 901),
        "image_alt": "Solaris by day: the central tower seen between two trees, with shopfronts either side of the plaza",
        "caption": "Solaris, the plaza by day",
        "links": [
            {"label": "playsolaris.net", "url": "https://playsolaris.net"},
            {"label": "destinygames.org", "url": "https://destinygames.org"},
            {"label": "Case study", "endpoint": "work.detail", "slug": "solaris"},
        ],
    },
    {
        "key": "gamedev",
        "name": "Game Development",
        "kind": GAME_NAME or "Original games",
        "logo": None,
        "line": (
            "Original games, built from scratch instead of on top of Minecraft. "
            + (f"{GAME_NAME} is the first." if GAME_NAME else "The first one isn't announced yet, so there is nothing to show here.")
        ),
        "role": "VP, game development" + (f", head of {GAME_NAME}" if GAME_NAME else ""),
        "role_note": "I run the division and lead the first game.",
        "image": None,  # TODO(skye): key art, once there's something public
        "caption": None,
        "links": [
            {"label": "What I can say", "endpoint": "work.detail", "slug": "unannounced"},
        ],
    },
]

# Full-bleed stills between sections. All in-game Solaris, all real.
STILLS = {
    "hero": {
        "image": "work/solaris/street-sunset.webp", "size": (1600, 901),
        "alt": "A Solaris city street at sunset: teal lamp posts, a purple van, the sun low between the buildings",
        "caption": "Solaris, in game. Main street at sunset.",
    },
    "tower": {
        "image": "studio/tower-night.webp", "size": (1600, 901),
        "alt": "Solaris at night: a tall dark tower with lit windows between two smaller buildings, under stars",
        "caption": "Solaris, in game. The tower at night.",
    },
    "sunset": {
        "image": "studio/tower-sunset.webp", "size": (1600, 900),
        "alt": "Solaris buildings in white and teal against an orange sunset",
        "caption": "Solaris, in game.",
    },
}
