"""Projects: shown as tiles on the homepage and as pages under /work/.

Homepage fields (don't rename): slug, name, summary, status, tone, url, image,
alt, size, style, wide, placeholder. `image` is relative to images/. `style`
is "photo" (cover crop), "logo" (centred mark on a surface) or "blank" (no art
yet, shows `placeholder`). `url` is the project's own external site.

Case-study fields, used by /work/ and /work/<slug>/:
  year      shown on the list and in the facts strip ("2024–" means ongoing)
  role      my role, one line
  platform  what it runs on
  tagline   one serif line under the title
  cover     list image; defaults to `image` (lets Callisto show the panel
            instead of its logo)
  intro     opening paragraph
  sections  [{"heading", "body": [paragraphs]}]
  gallery   [{"image", "alt", "size", "caption", "fit"}]; fit "contain"
            draws the image whole on a surface instead of cover-cropping
  credits   [{"name", "role"}], kept light
  links     extra pills in the facts strip, besides `url`

Never name the unannounced game: it's still secret on astrofoxstudios.com.
"""

PROJECTS = [
    {
        "slug": "solaris",
        "name": "Solaris",
        "summary": "Competitive Minecraft Java server with ranked play and seasons. Art direction, identity and UI.",
        "status": "Early Access",
        "tone": "live",
        "url": "https://playsolaris.net",
        "image": "work/solaris-city.webp",
        "alt": "Solaris: a city plaza at dusk with a fountain, tall dark towers and pink-lit buildings",
        "size": (1600, 901),
        "style": "photo",
        "wide": True,
        # case study
        "year": "2024–",
        "role": "Art director",
        "platform": "Minecraft Java",
        "tagline": "Competitive Minecraft, with a city to wait in.",
        "intro": (
            "Solaris is a competitive Minecraft Java server: placements, divisions, "
            "seasons and a top 50, under every game on it. It opened in Early Access "
            "in June 2026 as Season 0, First Light. Season 1 is called Starfall. "
            "I'm the art director, so the identity, the interfaces and how the whole "
            "thing looks are mine to get right."
        ),
        "sections": [
            {
                "heading": "What it is",
                "body": [
                    "Every game on Solaris has a full ranked system under it, not bolted "
                    "on later. Three placement games set a starting rank. There are seven "
                    "ranks, Bronze to Diamond in three divisions each, then Celestial, "
                    "Eclipse and Singularity. Wins and losses move you, kills add a little "
                    "on top, and matchmaking stays close in rank and only widens when it "
                    "has to.",
                    "The first game out was Cataclysm, a battle royale for 8 to 32 players. "
                    "Loot comes from crates, your inventory is capped to your hotbar, and "
                    "combat is paintball guns plus custom melee. It runs vanilla "
                    "server-side; all a player needs is the resource pack. Dodgeball is "
                    "the second game, 8 a side.",
                ],
            },
            {
                "heading": "What I do on it",
                "body": [
                    "The Solaris identity, the site, the in-game menus and the direction "
                    "of the builds. The city is the hub. It has a metro, a news network "
                    "with its own tower and newsroom, a bank, apartments, a theatre and a "
                    "club, and the game selector lives in the club. It's a lot of city for "
                    "a lobby. That's deliberate: I wanted somewhere people would wander "
                    "around while they wait.",
                ],
            },
            {
                "heading": "Where it came from",
                "body": [
                    "Solaris started as Lutraa's project and came fully under Astrofox once "
                    "it was clearly the one worth finishing. Underneath it are the systems "
                    "we built for Tropiclash, which never shipped.",
                    "Early Access was not tidy. Dodgeball had a matchmaking problem we "
                    "couldn't fix in time, so we pulled it on launch day rather than leave "
                    "a broken queue up, and said so. Season 1, Starfall, is the free "
                    "launch, with Corrupted Caverns and the first Unobtainable event.",
                ],
            },
        ],
        "gallery": [
            {"image": "work/solaris/street-sunset.webp", "size": (1600, 901),
             "alt": "A Solaris city street at sunset: teal lamp posts, a purple van, the sun low between the buildings",
             "caption": "Main street, sunset."},
            {"image": "work/solaris/snn-tower.webp", "size": (1600, 901),
             "alt": "The SNN tower, a dark skyscraper with purple SNN signs, against a clear blue sky",
             "caption": "SNN, the city's news network."},
            {"image": "work/solaris/metro.webp", "size": (1600, 901),
             "alt": "A pink and purple metro train stopped at an underground platform",
             "caption": "The metro."},
            {"image": "work/solaris/game-selector.webp", "size": (1600, 901),
             "alt": "Inside the Solaris club, lit pink and purple, with a sign reading Game Selector over the doorway",
             "caption": "The game selector is in the club."},
            {"image": "work/solaris/bank.webp", "size": (1600, 901),
             "alt": "A white stone bank with columns, rainbow flags along the roofline",
             "caption": "The bank."},
            {"image": "work/solaris/newsroom.webp", "size": (1600, 901),
             "alt": "The SNN newsroom: a cream desk, purple chairs and the letters S N N on the wall",
             "caption": "SNN newsroom."},
            {"image": "work/solaris/cataclysm-camp.webp", "size": (1600, 901),
             "alt": "Cataclysm: a mossy stone cabin with a campfire, in a pine wood",
             "caption": "Cataclysm, the battle royale map."},
        ],
        "credits": [
            {"name": "Arielle", "role": "Director"},
            {"name": "Lutraa", "role": "Director"},
            {"name": "Cookie", "role": "Lead builder"},
            {"name": "Bitzkyl", "role": "Soundtrack"},
            {"name": "Exp", "role": "Lead systems admin"},
            {"name": "Chaz", "role": "Community lead"},
            {"name": "Nate", "role": "Manager"},
        ],
    },
    {
        "slug": "callisto",
        "name": "Callisto",
        "summary": "Hosting and infrastructure for developers. Operations, software, the site and the panel.",
        "status": "Live",
        "tone": "live",
        "url": "https://callisto.host",
        "image": "work/callisto-logo.webp",
        "alt": "Callisto logo: a ringed planet in blue and purple",
        "size": (400, 400),
        "style": "logo",
        # case study
        "year": "2023–",
        "role": "Head of software",
        "platform": "Web, Aurora Panel",
        "tagline": "Hosting for developers, and the panel to run it from.",
        "cover": {
            "image": "work/callisto/workspace.webp", "size": (1600, 900),
            "alt": "Aurora Panel's workspace: app icons down the left edge, CPU, RAM and disk gauges, and a clock over a purple wave wallpaper",
        },
        "intro": (
            "Callisto is Astrofox's hosting and infrastructure division. It grew out of "
            "ExpHost, the hosting we set up in 2023 to keep our own servers online. "
            "It relaunched under the new name in February 2026 and it pays for most "
            "of what the studio does. I'm head of software: the panel, the "
            "site and how the software side gets built are my end of it."
        ),
        "sections": [
            {
                "heading": "Aurora Panel",
                "body": [
                    "Every Callisto server is managed through Aurora, our own control "
                    "panel. It isn't a reskin of Pterodactyl. It's a workspace: console, "
                    "files, backups, settings, billing and support each open as their own "
                    "window, and you can have two side by side, a file on the left and "
                    "the live log on the right. If you'd rather have a classic single-view "
                    "panel it can behave like one.",
                    "Theme, accent colours, wallpaper, density, motion and keybinds are "
                    "all user settings. The idea is that the panel fits how you work "
                    "rather than the other way round.",
                ],
            },
            {
                "heading": "Callisto Code",
                "body": [
                    "The in-panel editor. Tabs, syntax highlighting, search across every "
                    "file on the server, and it remembers which server, folders and tabs "
                    "you had open last time. For day-to-day changes you don't need an "
                    "SFTP client.",
                ],
            },
            {
                "heading": "Shipping it",
                "body": [
                    "Aurora 1.0 went out with the Callisto launch as a beta, with a public "
                    "list of known issues and a channel for people to tell us what felt "
                    "confusing. It's a live-service panel: updates roll out continuously, "
                    "and the help docs now cover 1.4.",
                ],
            },
        ],
        "gallery": [
            {"image": "work/callisto/multitasking.webp", "size": (1600, 900),
             "alt": "Two Aurora windows side by side: Callisto Code editing a Skript file on the left, the Destiny Dev console on the right",
             "caption": "Two windows: the editor and a console."},
            {"image": "work/callisto/mobile.webp", "size": (900, 1151), "fit": "contain",
             "alt": "Aurora on a phone, greeting Skye with server status and the next invoice",
             "caption": "Aurora on a phone."},
            {"image": "work/callisto/appearance.webp", "size": (1600, 900),
             "alt": "Aurora's Appearance settings: light, dark or auto, accent colour pickers, and a row of wallpapers",
             "caption": "Appearance settings."},
            {"image": "work/callisto/console.webp", "size": (1600, 900),
             "alt": "The Solaris server console in Aurora, with the live log and CPU, memory and disk readouts",
             "caption": "The console, on the Solaris server."},
            {"image": "work/callisto/disk-files.webp", "size": (1600, 900),
             "alt": "A disk usage sunburst for one server beside the Files window of another",
             "caption": "Disk usage and files."},
            {"image": "work/callisto/code.webp", "size": (1600, 900),
             "alt": "Callisto Code, the in-panel editor, open on a Skript file",
             "caption": "Callisto Code."},
            {"image": "work/callisto/billing.webp", "size": (1600, 900),
             "alt": "The Billing app dashboard: active services, invoices, recent activity and month progress",
             "caption": "Billing lives in the panel too."},
        ],
        "credits": [],
    },
    {
        "slug": "unannounced",
        "name": "Unannounced game",
        "summary": "An original game, not Minecraft. I'm leading it.",
        "status": "In development",
        "tone": "dev",
        "style": "blank",
        "placeholder": "Nothing to show yet.",
        # case study (deliberately thin)
        "year": "Not yet",
        "role": "Lead",
        "platform": "Not Minecraft",
        "tagline": "There's a game. That's the page.",
        "intro": (
            "We're building an original game outside Minecraft, and I lead it. The "
            "studio hasn't announced it, so this page has the shape of a case study "
            "and none of the contents."
        ),
        "sections": [
            {
                "heading": "What I can say",
                "body": [
                    "It exists. It's in active development. It isn't a server, a mod or "
                    "an event inside someone else's game. It's the first thing we've built "
                    "from scratch rather than on top of Minecraft.",
                ],
            },
            {
                "heading": "What I can't",
                "body": [
                    "The name, the art, the genre, the team, the date. When it's announced "
                    "this page gets a lot longer.",
                ],
            },
        ],
        "gallery": [],
        "credits": [],
    },
    {
        "slug": "destiny-games",
        "name": "Destiny Games",
        "summary": "Minecraft event series. Where the studio started.",
        "status": "2021, legacy",
        "url": "https://destinygames.org",
        "image": "work/destiny.webp",
        "alt": "Destiny Games: a pink dome arena in a Minecraft valley, with the Destiny Games wordmark",
        "size": (1400, 788),
        "style": "photo",
        # case study
        "year": "2021–2024",
        "role": "Founder, organiser, game dev",
        "platform": "Minecraft Java",
        "tagline": "The event series the studio started with.",
        "intro": (
            "Destiny Games is where Astrofox comes from: a Minecraft event series I ran "
            "with a small group from 2021. Teams, a lobby with a dome arena, and a set "
            "of games we wrote ourselves in Skript. It's on ice while we build Solaris. "
            "The plan is for it to come back as the organised, broadcast competitive "
            "layer on top of Solaris."
        ),
        "sections": [
            {
                "heading": "The events",
                "body": [
                    "Players were sorted into eight teams of five and voted for the next "
                    "game in a selection sphere. The games were ours: Speed Through Space, "
                    "Void Hunters, Cosmic Combat and Wipeout Rush, with Capture the Flag "
                    "as a finale for the top two teams. Between the real events we ran "
                    "tester events, so the community could help us find what broke before "
                    "it mattered.",
                ],
            },
            {
                "heading": "Tester 4",
                "body": [
                    "Tester 4, September 2024, is the one I'd point at if you want to know "
                    "what running these was like. Void Hunters, one of the first games I "
                    "ever wrote, was looping over 1,600 blocks every time someone broke a "
                    "block of concrete powder, and the tick time went to 600 ms. We wrote "
                    "up exactly what happened, game by game, fixed it, and promised a Part "
                    "2 with a guaranteed spot for everyone who'd been there. Wipeout Rush "
                    "ran perfectly. It wasn't mine.",
                ],
            },
        ],
        "gallery": [
            {"image": "work/destiny-games/lobby-night.webp", "size": (1600, 900),
             "alt": "The Destiny Games event grounds at night under a green and purple aurora, a billboard with the Astrofox fox on the left",
             "caption": "Night, under the aurora."},
            {"image": "work/destiny-games/tester-4.webp", "size": (1600, 900),
             "alt": "Players gathered during Tester 4 in front of a big screen showing the Destiny logo",
             "caption": "Tester 4, before it started lagging."},
            {"image": "work/destiny-games/grounds-dusk.webp", "size": (1600, 900),
             "alt": "The event grounds from above at dusk, the dome arena hazy in the distance",
             "caption": "The grounds from above."},
            {"image": "work/destiny-games/speed-through-space.webp", "size": (1600, 900),
             "alt": "Speed Through Space: players running through a cave of blue and purple crystals",
             "caption": "Speed Through Space."},
            {"image": "work/destiny-games/planets.webp", "size": (1600, 900),
             "alt": "Two planet builds in space, one blue and green, one pink",
             "caption": "Planets, 2023."},
            {"image": "work/destiny-games/space-islands.webp", "size": (1600, 900),
             "alt": "Floating islands and small planets on a space-themed map",
             "caption": "Islands in space."},
        ],
        "credits": [],
    },
    {
        "slug": "tropiclash",
        "name": "Tropiclash",
        "summary": "Survival prototype. Never shipped. Its systems became the base for Solaris.",
        "status": "2022",
        "image": "work/tropiclash.webp",
        "alt": "Tropiclash: a tropical island with a volcano, seen from the air, with the Tropiclash Season 1 wordmark",
        "size": (1400, 788),
        "style": "photo",
        # case study
        "year": "2022",
        "role": "Creative lead",
        "platform": "Minecraft Java",
        "tagline": "A tropical survival server that never shipped.",
        "intro": (
            "Tropiclash was our 2022 attempt at a public server: a tropical island, "
            "custom minigames and live events, with games ported over from Destiny "
            "Games. It never left development. The systems we built for it became the "
            "base of Solaris, and the IP has been folded into Solaris."
        ),
        "sections": [
            {
                "heading": "The idea",
                "body": [
                    "You start on Tropiclash Island with a raft. The raft is your base and "
                    "your farm: you expand it, automate it, and earn more by playing the "
                    "minigames than by farming passively. A train links the island to "
                    "Otter Outpost, Rocketeers Refuge and Skull Island, and underneath is "
                    "the Crystal Caverns, for gear upgrades and bosses. There was a "
                    "storyline about fractures between worlds that we never got to tell.",
                ],
            },
            {
                "heading": "What survived",
                "body": [
                    "Most of what we built was systems rather than content, and those "
                    "systems are what Solaris runs on now. We'd also planned seasons before "
                    "we had a server; the wordmarks below are the part of that which "
                    "survived.",
                ],
            },
        ],
        "gallery": [
            {"image": "work/tropiclash/wordmark.webp", "size": (1600, 261), "fit": "contain",
             "alt": "The Tropiclash wordmark in blocky green letters",
             "caption": "Wordmark."},
            {"image": "work/tropiclash/s6-mark.webp", "size": (900, 900), "fit": "contain",
             "alt": "The TC monogram in ice blue on a purple gradient",
             "caption": "Season 6 mark."},
            {"image": "work/tropiclash/s1-walk-the-plank.webp", "size": (1400, 253), "fit": "contain",
             "alt": "Tropiclash wordmark with the subtitle Walk the plank!",
             "caption": "Season 1: Walk the plank!"},
            {"image": "work/tropiclash/s3-undercover.webp", "size": (1400, 253), "fit": "contain",
             "alt": "Tropiclash wordmark with the subtitle Undercover...",
             "caption": "Season 3: Undercover."},
        ],
        "credits": [],
    },
]

ALSO = {
    "name": "Crescent",
    "url": "https://crescent.exphost.net",
    "text": "a self-hosted finance dashboard for Pterodactyl and Paymenter.",
    # /work/ only
    "year": "2025",
    "status": "Open source, alpha",
    "detail": (
        "Income by node, outgoings, and CPU, RAM and disk over time, for people "
        "running their own hosting. It connects to Pterodactyl and Paymenter."
    ),
    "github": "https://github.com/exphost-net/Crescent",
}


def get_project(slug):
    return next((p for p in PROJECTS if p["slug"] == slug), None)


def neighbours(slug):
    """(previous, next) project around `slug`, wrapping at the ends."""
    slugs = [p["slug"] for p in PROJECTS]
    i = slugs.index(slug)
    return PROJECTS[i - 1], PROJECTS[(i + 1) % len(PROJECTS)]
