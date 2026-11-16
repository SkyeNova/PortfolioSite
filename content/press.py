"""Press kit: bios, facts and downloadable assets for /press/.

Nothing here is invented. Facts come from content/core.py, content/about.py
and the studio's own sites. Files are relative to images/.
"""
from .core import GAME_NAME

# TODO(skye): this is assembled from what the site already says about you. Read it and fix anything off.
BIO_SHORT = (
    "Skye is the founder and CEO of Astrofox Studios, and its creative lead. Astrofox "
    "runs Callisto (hosting and infrastructure), the Minecraft server Solaris, and a "
    "game development division working on an original game."
)

BIO_LONG = [
    "Skye founded Astrofox Studios in 2021, starting with Destiny Games, a Minecraft "
    "event series. The studio now has three divisions: Callisto, which hosts game "
    "servers and builds the Aurora Panel; Minecraft, home to Solaris and Destiny "
    "Games; and Game Development, which is building the studio's first original game.",
    "Skye and Lutraa run Astrofox as co-CEOs, and Skye leads its creative direction: "
    "the brand, the interfaces and the art direction across everything it makes. "
    "Skye is also head of software at Callisto, art director on Solaris and VP of "
    "game development"
    + (f", leading {GAME_NAME}." if GAME_NAME else ", leading a game that hasn't been announced yet."),
]

FACTS = [
    {"k": "Name", "v": "Skye (SkyeNova)"},
    {"k": "Company", "v": "Astrofox Studios, founded 2021"},
    {"k": "Titles", "v": "Founder & CEO, creative lead. VP of game development. Head of software, Callisto. Art director, Solaris."},
    {"k": "Divisions", "v": "Callisto (hosting and infrastructure), Minecraft (Solaris, Destiny Games), Game Development"},
    {"k": "Based", "v": None},  # TODO(skye): country or city, if you want it public
    {"k": "Pronouns", "v": None},  # TODO(skye): if you want them on the press page
]

PORTRAITS = [
    {
        "image": "press/skye-render.webp", "size": (700, 1190), "download": "press/skye-render.png",
        "alt": "Skye's Minecraft character: pink hat, green and cream outfit, waving",
        "label": "Character render", "note": "PNG, transparent",
    },
    {
        "image": "about/me.webp", "size": (800, 800), "download": "me.jpg",
        "alt": "Skye, a mirror selfie: long red hair, round glasses and a black spider top",
        "label": "Photo", "note": "JPG, 1500 px",
    },
]

LOGOS = [
    {"name": "Astrofox Studios", "note": "Wordmark, white", "image": "brand/astrofox-wordmark-white.webp",
     "size": (720, 233), "download": "press/astrofox-wordmark-white.png"},
    {"name": "Astrofox Studios", "note": "Wordmark, colour", "image": "press/astrofox-wordmark-colour.png",
     "size": (1400, 454), "download": "press/astrofox-wordmark-colour.png"},
    {"name": "Astrofox Studios", "note": "Fox mark, white", "image": "brand/astrofox-mark-white.webp",
     "size": (400, 400), "download": "press/astrofox-mark-white.png"},
    {"name": "Callisto", "note": "Wordmark, white", "image": "brand/callisto-wordmark-white.webp",
     "size": (720, 189), "download": "press/callisto-wordmark-white.png"},
    {"name": "Callisto", "note": "Planet mark, colour", "image": "brand/callisto-mark-colour.webp",
     "size": (400, 400), "download": "press/callisto-mark-colour.png"},
    {"name": "Solaris", "note": "Mark", "image": "brand/solaris-mark.webp",
     "size": (400, 400), "download": "press/solaris-mark.png"},
]

# The studio's own brand page has the full sets and usage rules.
BRAND_URL = "https://astrofoxstudios.com/brand"

SCREENSHOTS = [
    {"image": "work/solaris/street-sunset.webp", "size": (1600, 901),
     "alt": "A Solaris city street at sunset with teal lamp posts and a purple van", "caption": "Solaris, main street"},
    {"image": "work/solaris-city.webp", "size": (1600, 901),
     "alt": "The Solaris city plaza at dusk with a fountain and tall dark towers", "caption": "Solaris, the plaza"},
    {"image": "studio/tower-night.webp", "size": (1600, 901),
     "alt": "A tall dark tower with lit windows at night in Solaris", "caption": "Solaris, the tower"},
    {"image": "work/solaris-cataclysm.webp", "size": (1600, 901),
     "alt": "Timber houses on a riverbank below a pine forest", "caption": "Solaris, a Cataclysm map"},
    {"image": "work/solaris/snn-tower.webp", "size": (1600, 901),
     "alt": "The SNN news tower in the Solaris city", "caption": "Solaris, the SNN tower"},
    {"image": "studio/aurora-multitasking.webp", "size": (1600, 900),
     "alt": "Aurora Panel with several app windows open side by side", "caption": "Callisto, Aurora Panel"},
    {"image": "studio/destiny-cave.webp", "size": (1600, 900),
     "alt": "A Destiny Games map: a cave of purple crystals and blue coral, with players", "caption": "Destiny Games"},
    {"image": "work/destiny-games/boat-race.webp", "size": (1600, 900),
     "alt": "Boat Race, a Destiny Games course: an ice track through a stone cave, lit by tall glowing green pillars", "caption": "Destiny Games, Boat Race"},
]
