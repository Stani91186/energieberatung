#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SITEMAP ERZEUGEN
================
Schreibt sitemap.xml aus dem tatsaechlichen Dateibestand.

    Aufruf:  python sitemap-erzeugen.py

WARUM ES DAS GIBT
-----------------
Die Sitemap war bis August 2026 von Hand gepflegt. Das ging, solange sich die
Seite selten aenderte. Mit dem woechentlich aktualisierten Aktuelles-Bereich
ist es die Stelle, die als Erstes vergessen wird - und ein veraltetes lastmod
kostet genau das Frische-Signal, wegen dem der Bereich gebaut wurde.

Jetzt gilt: Datei da = Adresse drin. Wer eine Seite anlegt oder loescht, muss
nichts weiter tun, als dieses Skript laufen zu lassen.

WAS lastmod BEDEUTET
--------------------
Das Aenderungsdatum der Datei, nicht das des Inhalts. Bei generierten Seiten
ist das jeder Generatorlauf - auch wenn sich der Text nicht geaendert hat.
Google behandelt lastmod ohnehin als Hinweis und nicht als Tatsache.
Ausnahme: aktuelles.html bekommt das Datum der juengsten Meldung, weil das
die ehrlichere Angabe ist.
"""

import io, os, re, glob
from datetime import date, datetime

DOMAIN = "https://energieberater-albdonau.de"

# 404 taucht in einer Sitemap nichts zu suchen: Sie soll indexierbare Seiten
# nennen, und die Fehlerseite ist keine.
AUSGENOMMEN = {"404.html"}

# Muster -> (Prioritaet, Aenderungshaeufigkeit). Erste Uebereinstimmung gewinnt,
# deshalb steht das Spezielle vor dem Allgemeinen.
REGELN = [
    (r"^index\.html$",                    "1.0", "monthly"),
    (r"^aktuelles\.html$",                "0.8", "weekly"),
    (r"^aktuelles-\d{4}\.html$",          "0.4", "yearly"),
    (r"^sanierungsrechner\.html$",        "0.9", "monthly"),
    (r"^u-wert-rechner\.html$",           "0.9", "monthly"),
    (r"^sanierungsfahrplan\.html$",       "0.9", "monthly"),
    (r"^energieausweis-.*\.html$",        "0.9", "monthly"),
    (r"^hydraulischer-abgleich-.*\.html$", "0.9", "monthly"),
    (r"^ratgeber\.html$",                 "0.8", "monthly"),
    (r"^ratgeber-.*\.html$",              "0.8", "monthly"),
    (r"^energieberatung-.*\.html$",       "0.7", "monthly"),
    (r"^(impressum|datenschutz)\.html$",  "0.2", "yearly"),
]
RUECKFALL = ("0.5", "monthly")


def einordnen(datei):
    for muster, prio, freq in REGELN:
        if re.match(muster, datei):
            return prio, freq
    return RUECKFALL


def juengste_meldung():
    """Datum der neuesten Meldung aus news-erzeugen.py - ohne das Modul zu
    laden, denn das wuerde index.html einlesen und den Ratgeber-Generator
    mitziehen. Ein Blick in den Quelltext reicht."""
    if not os.path.exists("news-erzeugen.py"):
        return None
    s = io.open("news-erzeugen.py", encoding="utf-8").read()
    daten = re.findall(r'"datum":\s*"(\d{4}-\d{2}-\d{2})"', s)
    return max(daten) if daten else None


def lastmod(datei):
    if datei == "aktuelles.html":
        d = juengste_meldung()
        if d:
            return d
    return datetime.fromtimestamp(os.path.getmtime(datei)).date().isoformat()


def adresse(datei):
    return f"{DOMAIN}/" if datei == "index.html" else f"{DOMAIN}/{datei}"


def sortierschluessel(datei):
    prio, _ = einordnen(datei)
    return (-float(prio), datei)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists("index.html"):
        raise SystemExit("index.html nicht gefunden - Skript im Projektordner starten.")

    seiten = sorted((p for p in glob.glob("*.html") if p not in AUSGENOMMEN),
                    key=sortierschluessel)
    if not seiten:
        raise SystemExit("Keine HTML-Seiten gefunden - das kann nicht stimmen.")

    ohne_canonical = [p for p in seiten
                      if 'rel="canonical"' not in io.open(p, encoding="utf-8").read()]
    if ohne_canonical:
        raise SystemExit("Diese Seiten haben kein canonical und gehoeren so nicht in "
                         "die Sitemap:\n  " + "\n  ".join(ohne_canonical))

    # Seiten, die sich selbst per noindex ausschliessen, gehoeren nicht hinein
    versteckt = [p for p in seiten
                 if re.search(r'name="robots"[^>]*content="[^"]*noindex',
                              io.open(p, encoding="utf-8").read())]
    seiten = [p for p in seiten if p not in versteckt]

    teile = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<!-- ERZEUGT von sitemap-erzeugen.py - nicht von Hand bearbeiten.',
             '     Neue Seite angelegt? Skript laufen lassen, fertig.',
             f'     Zuletzt erzeugt: {date.today().isoformat()} -->',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in seiten:
        prio, freq = einordnen(p)
        teile += ["  <url>",
                  f"    <loc>{adresse(p)}</loc>",
                  f"    <lastmod>{lastmod(p)}</lastmod>",
                  f"    <changefreq>{freq}</changefreq>",
                  f"    <priority>{prio}</priority>",
                  "  </url>"]
    teile.append("</urlset>")

    io.open("sitemap.xml", "w", encoding="utf-8", newline="\n").write(
        "\n".join(teile) + "\n")

    print(f"sitemap.xml geschrieben: {len(seiten)} Adressen")
    if versteckt:
        print(f"  ausgelassen (noindex): {', '.join(versteckt)}")
    print(f"  ausgelassen (Fehlerseite): {', '.join(sorted(AUSGENOMMEN))}")
    d = juengste_meldung()
    if d:
        print(f"  aktuelles.html mit lastmod {d} (juengste Meldung)")
