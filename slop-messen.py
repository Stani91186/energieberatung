# -*- coding: utf-8 -*-
"""Misst den sichtbaren Text der Website auf KI-Floskeln und Strukturmuster.

Ergaenzung zum Skill `no-ai-slop` (petergyang/no-ai-slop), der global
installiert ist: Dessen Wortlisten sind ausschliesslich englisch und
greifen auf dieser Seite nicht. Seine STRUKTURregeln gelten sprach-
unabhaengig - die werden hier gemessen, dazu die deutschen Entsprechungen
der Floskellisten.

    python slop-messen.py

Der Sinn ist nicht, bestehende Texte zu saeubern - die sind sauber, siehe
BASIS unten. Der Sinn ist eine Messlatte fuer NEUE Texte, vor allem fuer
die woechentlich automatisch veroeffentlichten Meldungen und kuenftige
Ratgeberartikel. Steigt eine Zahl deutlich ueber die Basis, ist Floskel-
sprache eingezogen.
"""
import re
import io
import sys
import glob
import collections

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Messung vom 05.11.2026: 27 Seiten, 31.718 Woerter sichtbarer Text.
# Wer Texte aendert, laesst das Skript laufen und traegt neue Werte ein.
BASIS = {
    "floskeln": 4,          # Summe aller Treffer aus FLOSKELN
    "binaer": 15,           # "nicht X, sondern Y" und "kein X, sondern Y"
    "strich_je_1000": 15.9  # Gedankenstriche je 1.000 Woerter
}

# --------------------------------------------------------------- Floskeln
# Deutsche Entsprechung zu den Wortlisten des Skills. Keine davon ist fuer
# sich genommen verboten - "grundsaetzlich" in einem Fachsatz ist richtig.
# Auffaellig wird erst die Haeufung.
FLOSKELN = [
    ("Fuellformel", r"darüber hinaus"),
    ("Fuellformel", r"des [Ww]eiteren"),
    ("Fuellformel", r"\bzudem\b"),
    ("Fuellformel", r"nicht zuletzt"),
    ("Fuellformel", r"in der heutigen Zeit|heutzutage"),
    ("Fuellformel", r"letztendlich|letzten Endes"),
    ("Fuellformel", r"im Grunde genommen"),
    ("Fuellformel", r"grundsätzlich"),
    ("Fuellformel", r"selbstverständlich"),
    ("Fuellformel", r"in diesem (Artikel|Beitrag|Ratgeber)"),
    ("Wichtigtuerei", r"spielt eine (wichtige|entscheidende|zentrale|große) Rolle"),
    ("Wichtigtuerei", r"von (entscheidender|großer|zentraler|besonderer) Bedeutung"),
    ("Wichtigtuerei", r"nicht zu unterschätzen"),
    ("Wichtigtuerei", r"[Ee]s ist wichtig,? zu"),
    ("Wichtigtuerei", r"gilt es,? zu beachten|zu beachten gilt"),
    ("Wichtigtuerei", r"sei (erwähnt|gesagt|angemerkt)"),
    ("Marketing", r"maßgeschneidert"),
    ("Marketing", r"nahtlos"),
    ("Marketing", r"ganzheitlich"),
    ("Marketing", r"zukunftssicher|zukunftsfähig"),
    ("Marketing", r"innovativ"),
    ("Marketing", r"hochwertig"),
    ("Marketing", r"aus einer Hand"),
    ("Marketing", r"[Rr]undum.?sorglos"),
    ("Marketing", r"effizient und nachhaltig|nachhaltig und effizient"),
    ("Marketing", r"Ihr (starker |verlässlicher |kompetenter )?Partner|stehen Ihnen zur Seite"),
    ("Marketing", r"individuell (auf .{0,30} )?(zugeschnitten|abgestimmt)"),
    ("Weasel", r"(Experten|Fachleute)\s+(empfehlen|raten|sind sich einig)"),
    ("Weasel", r"Studien zeigen|Untersuchungen zeigen"),
    ("Schlussfloskel", r"\bFazit\b|[Zz]usammenfassend|[Aa]bschließend lässt sich"),
]


def sichtbar(pfad):
    """Nur der Text, den ein Leser sieht - ohne Skript, Stil und Kommentare."""
    s = io.open(pfad, encoding="utf-8").read()
    s = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", s)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", s))


def messen():
    seiten = sorted(set(glob.glob("*.html")) - {"404.html"})
    text = {p: sichtbar(p) for p in seiten}
    worte = sum(len(re.findall(r"[A-Za-zÄÖÜäöüß]{2,}", t))
                for t in text.values())

    print("%d Seiten, %s Woerter sichtbarer Text\n" % (len(seiten), f"{worte:,}".replace(",", ".")))

    # 1. Floskeln
    fund = collections.Counter()
    wo = collections.defaultdict(set)
    for gruppe, rx in FLOSKELN:
        for p, t in text.items():
            n = len(re.findall(rx, t))
            if n:
                fund[rx] += n
                wo[rx].add(p)
    summe = sum(fund.values())
    print("FLOSKELN  %d Treffer bei %d von %d Mustern" % (summe, len(fund), len(FLOSKELN)))
    for gruppe, rx in FLOSKELN:
        if fund[rx]:
            seitenliste = ", ".join(sorted(s.replace(".html", "") for s in wo[rx])[:3])
            print("   %-16s %-34s %2dx   %s" % (gruppe, rx[:34], fund[rx], seitenliste))
    if not summe:
        print("   keine")

    # 2. Strukturmuster, die sprachunabhaengig gelten
    binaer = 0
    belege = []
    for p, t in text.items():
        for m in re.finditer(r"[^.!?;]{0,40}\b(?:nicht|kein[e]?[nmrs]?)\b[^.!?;]{3,70}?,\s*sondern[^.!?;]{0,45}", t):
            binaer += 1
            if len(belege) < 5:
                belege.append((p.replace(".html", ""), m.group(0).strip()))
    print("\nBINAERKONTRAST  „nicht X, sondern Y“: %d" % binaer)
    for p, s in belege:
        print("   [%s] %s" % (p, s[:95]))

    # 3. Gedankenstriche. Bis-Striche zwischen Zahlen sind korrekt und
    #    zaehlen nicht mit; gemessen wird nur der freistehende Strich.
    strich = sum(len(re.findall(r"(?<= )–(?= )", t)) for t in text.values())
    je1000 = 1000.0 * strich / max(worte, 1)
    haeufung = 0
    for t in text.values():
        for satz in re.split(r"(?<=[.!?]) +", t):
            if satz.count(" – ") >= 2:
                haeufung += 1
    print("\nGEDANKENSTRICHE  %d = %.1f je 1.000 Woerter (Basis %.1f)"
          % (strich, je1000, BASIS["strich_je_1000"]))
    print("   davon Saetze mit zwei oder mehr: %d" % haeufung)
    print("   Der Skill sagt: kein Standardrhythmus, Haeufungen aufloesen.")
    print("   Ein Einschub wie „Flächenheizungen – Boden, Wand – kommen mit 35 °C aus“")
    print("   ist korrektes Deutsch und bleibt.")

    # Urteil
    print("\n%s" % ("-" * 60))
    schlecht = []
    if summe > BASIS["floskeln"] * 3:
        schlecht.append("Floskeln %d statt %d" % (summe, BASIS["floskeln"]))
    if binaer > BASIS["binaer"] * 2:
        schlecht.append("Binaerkontraste %d statt %d" % (binaer, BASIS["binaer"]))
    if je1000 > BASIS["strich_je_1000"] * 1.5:
        schlecht.append("Gedankenstriche %.1f statt %.1f" % (je1000, BASIS["strich_je_1000"]))
    if schlecht:
        print("ANGESTIEGEN: " + " | ".join(schlecht))
        print("Neue Texte mit /no-ai-slop pruefen (Detect-Modus) und nacharbeiten.")
    else:
        print("Im Rahmen der Basiswerte - keine Floskelsprache eingezogen.")


if __name__ == "__main__":
    messen()
