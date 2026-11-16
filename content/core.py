"""Shared content: homepage sections, contact links."""

# The unannounced game's name. Leave as None until it's public: everything that
# would name it reads this, and says "an unannounced game" while it's None.
# TODO(skye): set this to the game's name the day it's announced.
GAME_NAME = None

# Skye's headline title. Skye is Founder & CEO; Lutraa is also CEO but not a
# founder, so "co-CEO" only appears where both are named together. Templates
# (header meta, footer, hero kicker, RSS) read this, so it can't drift.
TITLE = "Founder & CEO"
TAGLINE = f"{TITLE} of Astrofox Studios"

# Astrofox is the company; Callisto, Minecraft and Game Development are its
# three divisions. `since` None means "no year shown".
ROLES = [
    {"org": "Astrofox Studios", "title": "Founder & CEO, creative lead", "since": "2021"},
    {"org": "Game Development", "title": "VP, game development", "since": None},  # TODO(skye): year you took this on
    {"org": "Callisto", "title": "Head of software", "since": "2023"},
    {"org": "Solaris", "title": "Art director", "since": "2024"},
]
for _r in ROLES:  # `text` is what the older templates print
    _r["text"] = f"{_r['org']}, {_r['title'][0].lower()}{_r['title'][1:]}"

STILL = {
    "image": "work/solaris-cataclysm.webp",
    "alt": "Solaris: timber houses on a riverbank below a pine forest",
    "size": (1600, 901),
    "caption": "Solaris, in game. Timber houses on the river.",
}

TIMELINE = [
    {"year": "2021", "title": "Destiny Games", "body": "A Minecraft event series. The studio and its community started here."},
    {"year": "2022", "title": "Tropiclash", "body": "A survival prototype. It didn't ship, but its systems became the base for Solaris."},
    {"year": "2023", "title": "ExpHost", "body": "We started hosting our own servers, then other people's."},
    {"year": "2024", "title": "Solaris", "body": "Enters development."},
    {"year": "2026", "title": "Astrofox, Callisto, Solaris", "body": "The studio rebrands. ExpHost becomes Callisto. Solaris opens in Early Access."},
]

# Skills, grouped. Built from what Skye's repos actually show (build files,
# dependencies, commit history), not from a wish list. Never mention the
# unannounced game's tech here.
SKILL_GROUPS = [
    {"group": "Minecraft and game dev", "items": [
        "Java plugins on Paper: the Destiny Games core, hub and games",
        "Multi-module Gradle builds, with GitHub Actions to build and ship",
        "A Fabric client mod for Destiny Games",
        "Solaris plugins and its Velocity proxy, with Lutraa",
        "Skript, which the original Destiny Games ran on",
        "Resource packs: textures, models, fonts, sounds and core shaders",
    ]},
    {"group": "Web", "items": [
        "Python and Flask, for every studio site and the Aurora Panel",
        "HTML, CSS and JavaScript",
        "Accounts and sign-in: OAuth, two-factor, sessions",
        "Billing with Stripe",
        "MySQL, MariaDB and SQLite",
        "Electron desktop apps, React and Vite",
        "Node APIs with Fastify and Drizzle",
    ]},
    {"group": "Infrastructure and hosting", "items": [
        "The Aurora Panel, Callisto's hosting panel, on top of Pterodactyl",
        "Linux servers and systemd services",
        "Node agents and SSH automation for game server hosts",
        "Discord bots in Python, like Andromeda for Solaris",
        "Self-hosted internal tools for finance and project tracking",
    ]},
    {"group": "Design and art direction", "items": [
        "UI and UX",
        "Brand identity and logos for Astrofox, Callisto, Solaris and Destiny Games",
        "Art direction across the studio",
        "Minecraft textures and Blockbench models",
    ]},
    {"group": "Leadership", "items": [
        "Founding and running a studio with three divisions",
        "Leading small teams of developers, builders and artists",
        "Running live events and a community",
    ]},
]
# Older shape: one comma-separated line per group.
SKILLS = [{"group": g["group"], "list": "; ".join(g["items"])} for g in SKILL_GROUPS]

DISCORD_URL = "https://discord.gg/vkFQDhJE9P"

LINKS = [
    {"label": "Discord", "url": DISCORD_URL},
    {"label": "GitHub", "url": "https://github.com/SkyeNova"},
    {"label": "astrofoxstudios.com", "url": "https://astrofoxstudios.com"},
    {"label": "callisto.host", "url": "https://callisto.host"},
    {"label": "playsolaris.net", "url": "https://playsolaris.net"},
]

# Press and business contact. None hides the line.
PRESS_EMAIL = None  # TODO(skye): a real press/business address, if you want one public
SITE_URL = "https://www.skyenova.dev"
