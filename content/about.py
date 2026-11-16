"""About page data: roles per organisation, the Astrofox team, skills.

Team groups mirror astrofoxstudios.com (names, Minecraft IGNs, roles).
Heads come from https://minotar.net/helm/<ign>/128.png.
Never name the unannounced game here: it's still secret.
"""

# The hats: one card per organisation, in the order Skye put them on.
HATS = [
    {
        "org": "Astrofox Studios",
        "role": "Founder & CEO, creative lead",
        "since": "2021",
        "logo": "about/astrofox-logo.webp",
        "logo_alt": "Astrofox Studios logo: a fox in white",
        "logo_size": (400, 400),
        "body": "The company. It has three divisions: Callisto, Minecraft and game development. I set the creative direction and do the brand and the interfaces for everything we make. Lutraa and I are co-CEOs, and Lutraa runs the Minecraft side.",
        "url": "https://astrofoxstudios.com",
    },
    {
        "org": "Callisto",
        "role": "Head of software",
        "since": "2023",
        "logo": "work/callisto-logo.webp",
        "logo_alt": "Callisto logo: a ringed planet in blue and purple",
        "logo_size": (400, 400),
        "body": "Astrofox's hosting and infrastructure division. It started as ExpHost in 2023 so we had somewhere to run our own servers, and became Callisto in 2026. I look after the software side, the site and the panel, and run it day to day.",
        "url": "https://callisto.host",
    },
    {
        "org": "Solaris",
        "role": "Art director",
        "since": "2024",
        "logo": "work/solaris-logo.webp",
        "logo_alt": "Solaris logo",
        "logo_size": (400, 400),
        "body": "A competitive Minecraft Java server with ranked play and seasons, in Early Access. I own how it looks: the identity, the UI and the art direction.",
        "url": "https://playsolaris.net",
    },
    {
        "org": "Game development",
        "role": "VP, game development",
        "since": None,
        "logo": None,
        "body": "The division for original games, not Minecraft. I run it and lead the first one. That's all I can say until we announce it.",
        "url": None,
    },
]

TEAM_GROUPS = [
    {
        "name": "Management",
        "members": [
            {"name": "Skye", "ign": "SkyeNova_", "role": "Founder & CEO, creative lead, VP of game development"},
            {"name": "Lutraa", "ign": "Lutraa", "role": "CEO, head of Minecraft, development lead"},
            {"name": "Exp", "ign": "Exp_YT", "role": "COO, systems lead, VP of Callisto"},
        ],
    },
    {
        "name": "Staff",
        "members": [
            {"name": "Sophie", "ign": "iSophes", "role": "Game dev, system admin at Callisto"},
            {"name": "Moss", "ign": "moss_is_sleepy", "role": "Artist, the unannounced game"},
            {"name": "Bingum", "ign": "bingumm", "role": "Game designer, the unannounced game"},
        ],
    },
    {
        "name": "Callisto",
        "members": [
            {"name": "Exp", "ign": "Exp_YT", "role": "Director, head of security"},
            {"name": "Skye", "ign": "SkyeNova_", "role": "Head of software"},
            {"name": "Sophie", "ign": "iSophes", "role": "System admin"},
            {"name": "Foxy", "ign": "gamingfoxy81", "role": "Support"},
        ],
    },
    {
        "name": "Solaris",
        "members": [
            {"name": "Arielle", "ign": "ImValari", "role": "Director"},
            {"name": "Lutraa", "ign": "Lutraa", "role": "Director"},
            {"name": "Skye", "ign": "SkyeNova_", "role": "Art director"},
            {"name": "Cookie", "ign": "Cookiedoughnut2", "role": "Lead builder"},
            {"name": "Chaz", "ign": "ChazLovell", "role": "Community lead"},
            {"name": "Nate", "ign": "pokemada", "role": "Manager"},
            {"name": "TrashBuffoon", "ign": "TrashBuffoon", "role": "Admin"},
            {"name": "Bitzkyl", "ign": "Bitzkyl", "role": "Soundtrack"},
            {"name": "Exp", "ign": "Exp_YT", "role": "Lead systems admin"},
        ],
    },
]

ME = "SkyeNova_"

from .core import SKILL_GROUPS  # noqa: E402  (one list, shared with core)

PORTRAIT = {
    "image": "about/me.webp",
    "alt": "Skye, a mirror selfie: long red hair, round glasses and a black spider top",
    "size": (800, 800),
}

STILLS = {
    # Keys kept as the template expects ("lobby", "management"); neither
    # image is of the Destiny Games lobby any more, on purpose.
    "lobby": {
        "image": "work/destiny-games/voidclash-arena.webp",
        "alt": "VoidClash, a Destiny Games arena at night: a round central platform ringed by team bases, with beams of coloured light shooting into the sky",
        "size": (1600, 900),
        "caption": "VoidClash, one of the Destiny Games maps. This is where it started.",
    },
    "management": {
        "image": "work/destiny-games/cosmic-combat.webp",
        "alt": "Cosmic Combat, a Destiny Games map: teal and white space stations on long arms around a central hub, floating in a dark void",
        "size": (1600, 900),
        "caption": "Cosmic Combat, a Destiny Games map the team built together.",
    },
}


def team_count(groups=TEAM_GROUPS):
    return len({m["ign"] for g in groups for m in g["members"]})
