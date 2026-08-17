#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AKTUELLES ERZEUGEN
==================
Baut aktuelles.html - die Sammelseite fuer Meldungen zu Gesetzen, Foerderung
und Markt. Eine Seite, Meldungen stapeln sich, neueste oben.

    Aufruf:  python news-erzeugen.py

WARUM EINE SEITE UND NICHT EIN BLOG MIT WOCHENSEITEN
----------------------------------------------------
Kurze Zusammenfassungen auf je eigener Seite ergeben nach einem Jahr 52 duenne
Seiten. Genau das wertet Google ab, und genau davor haben drei SEO-Pruefungen
dieses Projekts gewarnt. Eine starke Seite mit Sprungzielen je Meldung bringt
das Frische-Signal, ohne den Seitenbestand zu verwaessern. Wird eine Meldung
gross genug fuer eine eigene Seite, gehoert sie in den Ratgeber.

WOHER KOPF, FUSS UND CSS KOMMEN
-------------------------------
Nicht aus einer vierten Kopie, sondern aus ratgeber-erzeugen.py. Dieses Projekt
hatte schon einmal das Problem, dass vier Dateien je eigene Kopfzeilen pflegten
und auseinanderliefen - dagegen gibt es kopf-fuss-abgleichen.py. Ein weiterer
Generator mit eigener Kopie waere derselbe Fehler noch einmal.

    ratgeber-erzeugen.py  ->  kopfbereich(), FUSS, stil(), krumen(), json_ld()
    index.html            ->  Quelle von allem, zur Laufzeit geschnitten

AUTOMATISCHER BETRIEB
---------------------
Ein woechentlicher Auftrag traegt hier neue Meldungen ein und veroeffentlicht
ohne Freigabeschritt. Deshalb stehen die Regeln unten NICHT nur im Auftragstext,
sondern als harte Pruefungen in pruefe(): Was durchfaellt, wird gar nicht erst
geschrieben. Wer eine Pruefung aufweicht, hebelt genau die Sicherung aus, die
verhindert, dass unbelegte Aussagen zu Foerderrecht live gehen.
"""

import io, os, re, sys, importlib.util
from datetime import date

DOMAIN = "https://energieberater-albdonau.de"
ZIEL = "aktuelles.html"

# Ab dieser Zahl wandern die aeltesten Meldungen ins Jahresarchiv. Ohne Grenze
# waechst die Seite unbemerkt ins Endlose.
MAX_AUF_SEITE = 40


# ---------------------------------------------------------------------------
# GEMEINSAMER RAHMEN aus ratgeber-erzeugen.py
# ---------------------------------------------------------------------------
def _lade_ratgeber():
    pfad = "ratgeber-erzeugen.py"
    if not os.path.exists(pfad):
        raise SystemExit(f"{pfad} nicht gefunden - dort stehen Kopf, Fuss und CSS.")
    spec = importlib.util.spec_from_file_location("rg", pfad)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RG = _lade_ratgeber()


# ---------------------------------------------------------------------------
# KATEGORIEN
# Jede Meldung bekommt das Bild ihrer Kategorie. Bewusst wiederverwendet -
# woechentlich ein neues Foto zu beschaffen und zu lizenzieren waere der
# teuerste Teil des Ganzen. Nachweis: bilder/LIZENZ.txt
# ---------------------------------------------------------------------------
KATEGORIEN = {
    "gesetz":     ("Gesetz",       "bilder/news-gesetz.jpg", 1200, 800,
                   "Aufgeschlagener Gesetzestext mit Paragrafen und Stempel"),
    "foerderung": ("Förderung",    "bilder/news-foerderung.jpg", 1200, 800,
                   "Euroscheine, Taschenrechner und Auswertungen auf einem Tisch"),
    "heizung":    ("Heizung",      "bilder/news-heizung.jpg", 1200, 801,
                   "Heizungsverteiler mit Thermometer und Umwälzpumpe"),
    "daemmung":   ("Dämmung",      "bilder/news-daemmung.jpg", 1200, 800,
                   "Dämmplatten an einem Rohbau"),
    "ausweis":    ("Energieausweis", "bilder/news-ausweis.jpg", 1200, 801,
                   "Grundriss, Schlüssel und Bauhelm auf einer Fläche"),
    "markt":      ("Markt",        "bilder/news-markt.jpg", 1200, 800,
                   "Gedrucktes Balkendiagramm mit Auswertung"),
}

# ---------------------------------------------------------------------------
# ZUGELASSENE QUELLEN
# Nur amtliche Stellen und Gesetzestexte. Keine Fachportale, keine Hersteller,
# keine Wettbewerber, keine Presseaggregatoren - deren Zusammenfassungen sind
# genau die Stille-Post-Stufe, an der Foerdersaetze falsch werden.
# ---------------------------------------------------------------------------
QUELL_HOSTS = (
    "bafa.de", "kfw.de", "dena.de", "energie-effizienz-experten.de",
    "bmwk.de", "bundeswirtschaftsministerium.de", "bundesregierung.de",
    "gesetze-im-internet.de", "bundesanzeiger.de", "recht.bund.de",
    "bundestag.de", "bundesrat.de",
)

# Woerter, die eine Meldung zur eigenen Werbe- oder Rechtsaussage machen wuerden.
# Die Meldungen referieren, was die Quelle sagt - mehr nicht.
VERBOTEN = ("wir ", "unser", "uns ", "€", "EUR ", "Honorar", "Angebot")


def _host(url):
    return re.sub(r"^https://(?:www\.)?([^/]+).*$", r"\1", url).lower()


MONATE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember")


def lang(iso):
    """2026-07-10 -> 10. Juli 2026"""
    j, m, t = (int(x) for x in iso.split("-"))
    return f"{t}. {MONATE[m-1]} {j}"


def marke(m):
    """Sprungziel je Meldung. Stabil, damit ein einmal verschickter Link
    dauerhaft funktioniert - deshalb aus Datum und Titel, nicht aus der
    Position in der Liste."""
    wort = re.sub(r"[^a-z0-9]+", "-", m["titel"].lower()
                  .replace("ä", "ae").replace("ö", "oe")
                  .replace("ü", "ue").replace("ß", "ss")).strip("-")
    return "m-" + m["datum"] + "-" + "-".join(wort.split("-")[:4])


# ---------------------------------------------------------------------------
# MELDUNGEN
# Neueste zuerst. Der Generator sortiert ohnehin, aber von Hand einzufuegen
# geht oben am schnellsten.
#
# Pflichtfelder: datum, kategorie, titel, text, quelle, quelle_url, abgerufen
# Der Text referiert die Quelle in zwei bis vier Saetzen. Keine Auslegung,
# keine Empfehlung, keine eigenen Zahlen - dafuer sind die Ratgeber da.
# ---------------------------------------------------------------------------
MELDUNGEN = [
{
 "datum": "2026-07-29",
 "kategorie": "gesetz",
 "titel": "Gebäudemodernisierungsgesetz löst das Gebäudeenergiegesetz ab",
 "text": "Der Bundestag hat am 10. Juli 2026 mit 323 zu 271 Stimmen das "
         "Gebäudemodernisierungsgesetz beschlossen. Öl- und Gasheizungen dürfen "
         "danach weiter betrieben und auch neu eingebaut werden; die bisherige "
         "Vorgabe, dass neue Heizungen zu 65 Prozent mit erneuerbaren Energien "
         "laufen müssen, entfällt. Stattdessen greift ab 2029 eine stufenweise "
         "steigende Pflicht zur Beimischung klimaneutraler Brennstoffe.",
 "quelle": "Deutscher Bundestag",
 "quelle_url": "https://www.bundestag.de/dokumente/textarchiv/2026/kw28-de-heizungsgesetz-1194534",
 "abgerufen": "2026-08-18",
},
{
 "datum": "2026-07-21",
 "kategorie": "foerderung",
 "titel": "Neue Förderkonditionen der Bundesförderung für effiziente Gebäude",
 "text": "Seit dem 21. Juli 2026 gelten geänderte Konditionen der BEG. Das BAFA "
         "nennt unter anderem eine erweiterte Antragsberechtigung, angepasste "
         "Höchstgrenzen bei Wohn- und Nichtwohngebäuden, geänderte Sätze der Boni "
         "und neue Bedingungen für den iSFP-Bonus. Für Anträge nach den neuen "
         "Konditionen müssen neue TPB-IDs erzeugt werden.",
 "quelle": "BAFA",
 "quelle_url": "https://www.bafa.de/DE/Energie/Effiziente_Gebaeude/Foerderprogramm_im_Ueberblick/foerderprogramm_im_ueberblick_node.html",
 "abgerufen": "2026-08-18",
},
{
 "datum": "2026-07-21",
 "kategorie": "foerderung",
 "titel": "KfW passt den Wohngebäude-Kredit 261 an",
 "text": "Zeitgleich mit der BEG-Reform hat die KfW die Bedingungen des Programms "
         "261 geändert. Nach Angaben der Bank entfällt der Effizienz-Bonus, der "
         "Förderhöchstbetrag je Wohneinheit steigt und der Tilgungszuschuss wird "
         "abgesenkt. Anträge zu den bisherigen Bedingungen waren nur bis zum "
         "20. Juli 2026 möglich.",
 "quelle": "KfW",
 "quelle_url": "https://www.kfw.de/inlandsfoerderung/Privatpersonen/Bestehende-Immobilie/F%C3%B6rderprodukte/Bundesf%C3%B6rderung-f%C3%BCr-effiziente-Geb%C3%A4ude-Wohngeb%C3%A4ude-Kredit-(261-262)/",
 "abgerufen": "2026-08-18",
},
{
 "datum": "2026-08-01",
 "kategorie": "markt",
 "titel": "Übergangsregelung für die Energieeffizienz-Expertenliste endet zum Jahresende",
 "text": "Im BAFA-Antragsverfahren gilt für eingetragene Energieberaterinnen und "
         "Energieberater eine Übergangsregelung bis zum 31. Dezember 2026. Wer ab "
         "dem 1. Januar 2027 weiter im Antragsverfahren tätig sein will, muss den "
         "Eintrag in der Expertenliste erneuern. Für Eigentümer heißt das: vor der "
         "Beauftragung prüfen, ob der Eintrag gültig ist.",
 "quelle": "BAFA",
 "quelle_url": "https://www.bafa.de/SharedDocs/Kurzmeldungen/DE/Energie/Energieberatung_fuer_Wohngebaeude/20240626_eee-uebergangsregelung_eingetragene_energieberater.html",
 "abgerufen": "2026-08-18",
},
]


# ---------------------------------------------------------------------------
# PRUEFUNGEN
# Laufen vor dem Schreiben. Jede bricht ab statt zu warnen: Der woechentliche
# Auftrag laeuft unbeaufsichtigt, eine Warnung wuerde niemand lesen.
# ---------------------------------------------------------------------------
PFLICHT = ("datum", "kategorie", "titel", "text", "quelle", "quelle_url", "abgerufen")


def pruefe(meldungen):
    heute = date.today().isoformat()
    titel_gesehen, url_gesehen, marken = {}, {}, {}

    for i, m in enumerate(meldungen, 1):
        wo = f"Meldung {i} ({m.get('titel', 'ohne Titel')[:50]})"

        fehlt = [f for f in PFLICHT if not m.get(f)]
        if fehlt:
            raise SystemExit(f"{wo}: Pflichtfeld fehlt: {', '.join(fehlt)}")

        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", m["datum"]):
            raise SystemExit(f"{wo}: datum muss JJJJ-MM-TT sein, ist '{m['datum']}'")
        if m["datum"] > heute:
            raise SystemExit(f"{wo}: datum {m['datum']} liegt in der Zukunft")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", m["abgerufen"]):
            raise SystemExit(f"{wo}: abgerufen muss JJJJ-MM-TT sein")

        if m["kategorie"] not in KATEGORIEN:
            raise SystemExit(f"{wo}: unbekannte Kategorie '{m['kategorie']}'. "
                             f"Erlaubt: {', '.join(KATEGORIEN)}")

        if not m["quelle_url"].startswith("https://"):
            raise SystemExit(f"{wo}: quelle_url muss mit https:// beginnen")
        host = _host(m["quelle_url"])
        if not any(host == h or host.endswith("." + h) for h in QUELL_HOSTS):
            raise SystemExit(
                f"{wo}: Quelle '{host}' steht nicht auf der Liste zugelassener "
                f"Stellen.\nZugelassen sind ausschliesslich: {', '.join(QUELL_HOSTS)}\n"
                f"Fachportale, Hersteller und Presseseiten sind bewusst "
                f"ausgeschlossen - eine Foerderaussage wird ueber zweite Hand falsch.")

        if len(m["text"]) > 400:
            raise SystemExit(f"{wo}: text hat {len(m['text'])} Zeichen, erlaubt sind 400. "
                             f"Wird es laenger, gehoert das Thema in den Ratgeber.")
        treffer = [w for w in VERBOTEN if w.lower() in m["text"].lower()]
        if treffer:
            raise SystemExit(
                f"{wo}: text enthaelt {treffer} - eine Meldung referiert die Quelle "
                f"und macht keine eigene Aussage ueber Leistungen oder Betraege.")

        for feld, gesehen in (("titel", titel_gesehen), ("quelle_url", url_gesehen)):
            if m[feld] in gesehen:
                raise SystemExit(f"{wo}: {feld} steht schon in Meldung {gesehen[m[feld]]}")
            gesehen[m[feld]] = i

        mk = marke(m)
        if mk in marken:
            raise SystemExit(f"{wo}: Sprungziel '{mk}' doppelt (auch Meldung {marken[mk]})")
        marken[mk] = i

    fehlende_bilder = sorted({KATEGORIEN[k][1] for k in
                              {m["kategorie"] for m in meldungen}
                              if not os.path.exists(KATEGORIEN[k][1])})
    if fehlende_bilder:
        raise SystemExit("Diese Bilddateien fehlen:\n  " + "\n  ".join(fehlende_bilder))

    return sorted(meldungen, key=lambda m: (m["datum"], m["titel"]), reverse=True)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
NEWS_CSS = """
/* ===== Aktuelles ===== */
.news-liste{display:grid;gap:20px;padding-bottom:24px}
.news-eintrag{
  display:grid;grid-template-columns:210px 1fr;gap:26px;align-items:start;
  background:var(--white);border:1px solid var(--line-soft);border-radius:var(--radius);
  box-shadow:var(--shadow-sm);padding:22px 26px;scroll-margin-top:120px;
}
.news-eintrag>*{min-width:0}
.news-bild{width:100%;height:150px;object-fit:cover;border-radius:var(--radius-sm);display:block}
.news-kopf{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:9px}
.news-datum{font-size:.82rem;color:var(--muted);font-variant-numeric:tabular-nums}
.news-kat{
  font-size:.7rem;letter-spacing:.09em;text-transform:uppercase;font-weight:700;
  padding:3px 10px;border-radius:100px;background:var(--forest-soft);color:var(--forest);
}
.news-kat-foerderung{background:var(--amber-soft);color:#6B5638}
.news-kat-markt{background:#EDEFF2;color:#4A5560}
.news-eintrag h2{font-size:1.16rem;line-height:1.35;margin:0 0 9px}
.news-eintrag p{font-size:.95rem;color:var(--ink-2);margin:0 0 12px}
.news-quelle{font-size:.84rem;color:var(--muted);margin:0}
.news-quelle a{color:var(--amber-deep);font-weight:600;text-decoration:underline;text-underline-offset:3px}
.news-leer{
  background:var(--forest-soft);border-radius:var(--radius);padding:26px 28px;
  color:var(--forest);font-size:.96rem;
}
.news-fuss{
  margin:8px 0 44px;padding-top:18px;border-top:1px solid var(--line-soft);
  font-size:.85rem;color:var(--muted);max-width:70ch;
}
.news-archiv{margin:0 0 44px;font-size:.92rem}
.news-archiv a{color:var(--amber-deep);font-weight:600}
@media (max-width:760px){
  .news-eintrag{grid-template-columns:1fr;gap:16px;padding:18px 20px}
  .news-bild{height:170px}
}
"""


def stil():
    return RG.stil() + NEWS_CSS


# ---------------------------------------------------------------------------
# SEITENBAU
# ---------------------------------------------------------------------------
def kopf(titel, beschreibung, datei):
    return f"""<!DOCTYPE html>
<!--
  ============================================================================
  AKTUELLES – ERZEUGT, NICHT VON HAND BEARBEITEN!
  Meldungen stehen in news-erzeugen.py, Liste MELDUNGEN. Danach das Skript
  erneut laufen lassen, sonst sind Aenderungen beim naechsten Durchlauf weg.
  ============================================================================
-->
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titel}</title>
<meta name="description" content="{beschreibung}">
<link rel="canonical" href="{DOMAIN}/{datei}">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#FDFBF7">
{RG._schnitt(r'(<link rel="icon"[^>]*>)', 'Favicon')}
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="EBA Energieberater Albdonau">
<meta property="og:title" content="{titel}">
<meta property="og:description" content="{beschreibung}">
<meta property="og:url" content="{DOMAIN}/{datei}">
<meta property="og:image" content="{DOMAIN}/vorschau.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="EBA Energieberater Albdonau, Ulm und Alb-Donau-Kreis">
<meta name="twitter:card" content="summary_large_image">
<style>
{stil()}
</style>
</head>
<body>
<script>document.documentElement.classList.add('js')</script>

<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>
{RG.kopfbereich(ZIEL)}"""


def meldung_html(m):
    label, bild, bw, bh, alt = KATEGORIEN[m["kategorie"]]
    zusatz = f" news-kat-{m['kategorie']}" if m["kategorie"] in ("foerderung", "markt") else ""
    return f"""      <article class="news-eintrag reveal" id="{marke(m)}">
        <img class="news-bild" src="{bild}" width="{bw}" height="{bh}"
             alt="{alt}" loading="lazy" decoding="async">
        <div>
          <div class="news-kopf">
            <time class="news-datum" datetime="{m['datum']}">{lang(m['datum'])}</time>
            <span class="news-kat{zusatz}">{label}</span>
          </div>
          <h2>{m['titel']}</h2>
          <p>{m['text']}</p>
          <p class="news-quelle">Quelle:
            <a href="{m['quelle_url']}" target="_blank" rel="noopener">{m['quelle']}</a>
            · abgerufen am {lang(m['abgerufen'])}</p>
        </div>
      </article>
"""


def seite(meldungen, archivjahre):
    titel = "Aktuelles: Förderung, Gesetze und Sanierung | EBA Albdonau"
    beschreibung = ("Änderungen bei Förderung und Gesetzen rund um die energetische "
                    "Sanierung – kurz zusammengefasst, jede Meldung mit amtlicher Quelle.")
    stand = meldungen[0]["datum"] if meldungen else date.today().isoformat()

    graph = [{
        "@type": "CollectionPage",
        "name": "Aktuelles zu Förderung, Gesetzen und Sanierung",
        "description": beschreibung,
        "inLanguage": "de-DE",
        "url": f"{DOMAIN}/{ZIEL}",
        "dateModified": stand,
    }, {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Aktuelles"},
        ],
    }, {
        "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": m["titel"],
             "url": f"{DOMAIN}/{ZIEL}#{marke(m)}"}
            for i, m in enumerate(meldungen)
        ],
    }]

    if meldungen:
        liste = "".join(meldung_html(m) for m in meldungen)
    else:
        liste = """      <div class="news-leer">
        Zurzeit liegen keine neuen Meldungen vor. Das ist kein Fehler: Hier steht
        nur etwas, wenn sich tatsächlich etwas geändert hat.
      </div>
"""

    archiv = ""
    if archivjahre:
        eintraege = " · ".join(
            f'<a href="aktuelles-{j}.html">Meldungen aus {j}</a>' for j in archivjahre)
        archiv = f'  <div class="wrap news-archiv">Ältere Meldungen: {eintraege}</div>\n'

    return (
        kopf(titel, beschreibung, ZIEL)
        + RG.json_ld({"@context": "https://schema.org", "@graph": graph})
        + f"""
<main id="inhalt">
{RG.krumen(("Startseite", "index.html"), ("Aktuelles", None))}
  <header class="wrap rg-kopf">
    <span class="eyebrow">Aktuelles</span>
    <h1>Was sich bei Förderung und Gesetzen ändert</h1>
    <p class="lead">
      Fördersätze, Fristen und Gesetze ändern sich schneller, als die meisten
      Ratgeber im Netz nachziehen. Hier steht wöchentlich in wenigen Sätzen, was
      sich geändert hat – jede Meldung mit der amtlichen Quelle zum Nachlesen.
    </p>
    <div class="rg-meta">
      <span>Zuletzt aktualisiert: {lang(stand)}</span>
      <span>{len(meldungen)} Meldungen</span>
    </div>
  </header>

  <div class="wrap news-liste">
{liste}  </div>

{archiv}  <div class="wrap">
    <p class="news-fuss">
      Diese Übersicht wird automatisch aus den Veröffentlichungen von BAFA, KfW,
      dena, der Energieeffizienz-Expertenliste, Bundestag und Bundesregierung
      zusammengestellt. Die Meldungen geben wieder, was in der jeweils verlinkten
      Quelle steht, und ersetzen weder deren Lektüre noch eine Beratung.
      <strong>Maßgeblich ist immer die Quelle</strong> in der Fassung, die zum
      Zeitpunkt Ihrer Antragstellung gilt. Was eine Änderung für Ihr Gebäude
      bedeutet, klären wir im Erstgespräch.
    </p>
  </div>

  <div class="wrap">
{RG.CTA_BAND}  </div>
</main>
"""
        + RG.FUSS
    )


def archivseite(jahr, meldungen):
    titel = f"Aktuelles {jahr}: Förderung und Gesetze | EBA Albdonau"
    beschreibung = (f"Meldungen aus {jahr} zu Förderung, Gesetzen und Sanierung – "
                    f"jede mit amtlicher Quelle. Archiv der Seite Aktuelles.")
    datei = f"aktuelles-{jahr}.html"
    graph = [{
        "@type": "CollectionPage", "name": f"Aktuelles {jahr}",
        "description": beschreibung, "inLanguage": "de-DE",
        "url": f"{DOMAIN}/{datei}",
    }, {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Aktuelles",
             "item": f"{DOMAIN}/{ZIEL}"},
            {"@type": "ListItem", "position": 3, "name": str(jahr)},
        ],
    }]
    return (
        kopf(titel, beschreibung, datei)
        + RG.json_ld({"@context": "https://schema.org", "@graph": graph})
        + f"""
<main id="inhalt">
{RG.krumen(("Startseite", "index.html"), ("Aktuelles", ZIEL), (str(jahr), None))}
  <header class="wrap rg-kopf">
    <span class="eyebrow">Archiv</span>
    <h1>Meldungen aus {jahr}</h1>
    <p class="lead">
      Ältere Meldungen zu Förderung und Gesetzen. Bitte beachten Sie das Datum –
      viele dieser Angaben sind inzwischen überholt.
      <a href="{ZIEL}">Zu den aktuellen Meldungen</a>
    </p>
  </header>

  <div class="wrap news-liste">
{"".join(meldung_html(m) for m in meldungen)}  </div>
</main>
"""
        + RG.FUSS
    )


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists("index.html"):
        raise SystemExit("index.html nicht gefunden - Skript im Projektordner starten.")

    sortiert = pruefe(MELDUNGEN)
    print(f"{len(sortiert)} Meldungen geprüft: Quellen, Datum, Dubletten, Länge – alles sauber.")

    auf_seite = sortiert[:MAX_AUF_SEITE]
    ins_archiv = sortiert[MAX_AUF_SEITE:]
    jahre = sorted({m["datum"][:4] for m in ins_archiv}, reverse=True)

    io.open(ZIEL, "w", encoding="utf-8", newline="\n").write(
        RG.fuell(seite(auf_seite, jahre)))
    print(f"  geschrieben: {ZIEL} ({len(auf_seite)} Meldungen)")

    for jahr in jahre:
        des_jahres = [m for m in ins_archiv if m["datum"][:4] == jahr]
        datei = f"aktuelles-{jahr}.html"
        io.open(datei, "w", encoding="utf-8", newline="\n").write(
            RG.fuell(archivseite(jahr, des_jahres)))
        print(f"  geschrieben: {datei} ({len(des_jahres)} Meldungen)")

    print("\nNicht vergessen: python sitemap-erzeugen.py")
