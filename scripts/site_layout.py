"""Site layout for the Silver Family Archive: one folder per person, with a hub index.

Used by the restructure (17 Oct 2026) and by the letter build scripts in
Grandpa's Letters, so rebuilt pages land in the right folder with the right
aliases and back-links:

    import sys; sys.path.insert(0, SITE + "/scripts")
    from site_layout import site_path, finalize
    open(site_path(SITE, "Henlow-Letters"), "w").write(finalize("Henlow-Letters", text))
"""
import os
import re

RAF = ["Skegness-Letters", "Cosford-Letters", "Little-Horwood-Letters", "Oulton-Letters",
       "Oakington-Letters", "Henlow-Letters", "Isle-of-Man-Letters", "Wellesbourne-Letters"]

# old slug -> new slug (both relative to content/, no .md)
MOVES = {
    "David-Silver": "David-Silver/Biography",
    "Bruton-Letters": "David-Silver/Bruton-Letters",
    "WWII-Interview": "David-Silver/WWII-Interview",
    "Bristol-Letters": "David-Silver/Bristol-Letters",
    "France-Letters": "David-Silver/France-Letters",
    **{s: "David-Silver/RAF-Letters/" + s for s in RAF},
    "Anthea-Silver": "Anthea-Silver/A-Topsham-Childhood",
    "Clifford-Marking-Silver": "Clifford-Marking-Silver/Biography",
    "Acott-Letters": "Gladys-Silver/Acott-Letters",
    "Christopher-Silver/index": "Christopher-Silver/Biography",
    "Trip-on-the-River": "Jago-Silver/Trip-on-the-River",
    "When-The-Wind-Blows": "Jago-Silver/When-The-Wind-Blows",
    "Dissertation": "Jago-Silver/Dissertation",
    "Kings-School-Bruton": "Places/Kings-School-Bruton",
    "Denver-Excavation": "Places/Denver-Excavation",
}

# the old URL of these now belongs to the person's folder hub, so no alias
NO_ALIAS = {"David-Silver", "Anthea-Silver", "Clifford-Marking-Silver", "Christopher-Silver/index"}

HUB_NAMES = {
    "David-Silver": "David Silver",
    "Anthea-Silver": "Anthea Silver",
    "Clifford-Marking-Silver": "Clifford Marking Silver",
    "Gladys-Silver": "Gladys Silver",
    "Christopher-Silver": "Christopher Patrick Silver",
    "Jago-Silver": "Jago Silver",
    "Places": "Places & history",
}

HOME = "*← [Silver Family Archive](./)*"


def site_path(site, old_slug):
    return os.path.join(site, "content", MOVES.get(old_slug, old_slug) + ".md")


def fix_links(text):
    """Point links at the person hubs / moved biographies. Moved pages with unique
    file names (Bruton-Letters etc.) still resolve through Quartz's shortest-path links."""
    for person, bio in (("David-Silver", "David-Silver/Biography"),
                        ("Anthea-Silver", "Anthea-Silver/A-Topsham-Childhood"),
                        ("Clifford-Marking-Silver", "Clifford-Marking-Silver/Biography")):
        text = re.sub(r"\]\((?:\.\./)?%s#" % person, "](%s#" % bio, text)
        text = re.sub(r"\]\((?:\.\./)?%s\)" % person, "](%s/)" % person, text)
    text = text.replace("](Christopher-Silver/#", "](Christopher-Silver/Biography#")
    for s in list(MOVES) + ["Christopher-Silver/Letters"]:
        text = text.replace("](../%s)" % s, "](%s)" % s)
    return text


def finalize(old_slug, text):
    new = MOVES.get(old_slug, old_slug)
    if old_slug in MOVES and old_slug not in NO_ALIAS and "\naliases:" not in text:
        text = re.sub(r"^---\n", "---\naliases:\n  - %s\n" % old_slug, text, count=1)
    if new.startswith("David-Silver/RAF-Letters/"):
        back = "*← [Letters from the RAF](David-Silver/RAF-Letters/) · [David Silver](David-Silver/) · [Silver Family Archive](./)*"
    else:
        owner = new.split("/")[0]
        back = "*← [%s](%s/) · [Silver Family Archive](./)*" % (HUB_NAMES.get(owner, ""), owner)
    if "/" in new:
        text = text.replace(HOME, back, 1)
    return fix_links(text)
