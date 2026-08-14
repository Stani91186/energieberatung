#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORTSSEITEN ERZEUGEN
===================
Baut aus der Tabelle ORTE je eine fertige HTML-Datei. Das Ergebnis ist
statisches HTML wie der Rest der Website - der Generator laeuft nur hier auf
dem Rechner, nicht auf dem Server. Damit bleibt die Projektregel "alles in
einer Datei, kein Build-Schritt" fuer die ausgelieferte Seite erhalten, und
trotzdem muss man eine Aenderung am Aufbau nur EINMAL machen.

    Aufruf:  python ortsseiten-erzeugen.py

WICHTIG ZUM INHALT
------------------
Google straft Seiten ab, die sich nur im Ortsnamen unterscheiden
("Doorway Pages"). Deshalb hat jeder Ort eigene Absaetze zu Lage, Klima und
Bausubstanz. Die mit [PRUEFEN] markierten Stellen sind fachliche Aussagen,
die der Betreiber bestaetigen oder ersetzen muss - erfundene Ortsdetails
waeren schlimmer als gar keine.
"""

import io, os, re

DOMAIN = "https://energieberater-albdonau.de"
TEL_ANZEIGE = "0152 24290826"
TEL_LINK = "+4915224290826"

# ---------------------------------------------------------------------------
# ORTE – hier pflegen. Jeder Eintrag braucht eigenen, ortsspezifischen Text.
# ---------------------------------------------------------------------------
ORTE = [
  {
    "datei": "energieberatung-ulm.html",
    "ort": "Ulm",
    "typisch": "Häufigster Fall in Ulm sind Eigentumswohnungen und Reihenhäuser aus den Wiederaufbaujahren. Dort ist die Einzelmaßnahme oft nicht frei wählbar, weil die Eigentümergemeinschaft mitentscheidet. Wir bereiten die Zahlen deshalb so auf, dass sie in einer Eigentümerversammlung bestehen – mit Kosten je Wohneinheit statt nur für das Gesamtgebäude. Für Wohnungseigentümergemeinschaften gibt es beim Sanierungsfahrplan zusätzlich 250 Euro Förderung für die Erläuterung vor der Versammlung.",
    "artikel": "in",              # "in Ulm"
    "plz": "89073",
    "einwohner": "rund 128.000",
    "entfernung": "etwa 10 Kilometer",
    "titel_zusatz": "Energieberatung Ulm",
    "beschreibung": "Energieberatung in Ulm: Sanierungsfahrplan, Förderung und Energieausweis. Vor Ort in Ulm und Umgebung, produktneutral und ohne Provision.",
    "lage": "Ulm ist das Zentrum der Region und liegt an der Donau, klimatisch deutlich "
            "milder als die Albhochfläche wenige Kilometer weiter nordwestlich. Für die "
            "Heizlastberechnung macht das einen spürbaren Unterschied – wer Werte von der "
            "Alb auf ein Ulmer Gebäude überträgt, dimensioniert zu groß.",
    "bausubstanz": "Ulm hat eine ungewöhnlich gemischte Bausubstanz: eine im Krieg stark "
            "zerstörte und in den 1950er und 1960er Jahren wieder aufgebaute Innenstadt, "
            "dazu ausgedehnte Wohngebiete der 1960er bis 1980er Jahre am Eselsberg, in "
            "Wiblingen und Böfingen. Gerade diese Baualtersklassen sind energetisch "
            "interessant: massiv gebaut, langlebig, aber fast immer ohne nennenswerte "
            "Dämmung und mit Fenstern aus der ersten oder zweiten Generation.",
    "besonderheit": "In der Altstadt und im Fischerviertel gelten Denkmalschutz und "
            "Erhaltungssatzungen. Dort ist Außendämmung meist ausgeschlossen – die Lösung "
            "liegt dann in Innendämmung, Dach, Kellerdecke und Anlagentechnik. Das will "
            "sorgfältig gerechnet werden, sonst drohen Feuchteschäden.",
  },
  {
    "datei": "energieberatung-blaustein.html",
    "ort": "Blaustein",
    "typisch": "Was wir in Blaustein am häufigsten sehen: ein Haus aus den 1970ern, Fenster in den 1990ern erneuert, Heizung um 2000 getauscht, Wand und Dach unverändert. Die Versuchung ist dann, wieder die Heizung anzufassen. Rechnerisch bringt hier meist die oberste Geschossdecke den schnellsten Ertrag – oft an einem Wochenende in Eigenleistung machbar und mit unter zwei Jahren Amortisation.",
    "artikel": "in",
    "plz": "89134",
    "einwohner": "rund 16.000",
    "entfernung": "etwa 8 Kilometer",
    "titel_zusatz": "Energieberatung Blaustein",
    "beschreibung": "Energieberatung in Blaustein: Sanierungsfahrplan, Fördermittel und Energieausweis. Vor Ort im Blautal, produktneutral und ohne Provision.",
    "lage": "Blaustein liegt im Blautal am Fuß der Schwäbischen Alb, westlich von Ulm. "
            "Die Tallage schützt vor Wind, gleichzeitig sammelt sich in den Wintermonaten "
            "kalte Luft im Tal – ein Umstand, der bei der Auslegung von Wärmepumpen "
            "gelegentlich unterschätzt wird.",
    "bausubstanz": "Der Ort ist stark durch Wohnbebauung der Nachkriegsjahrzehnte geprägt, "
            "dazu kommen die gewachsenen Ortsteile mit älterem Bestand. Ein- und "
            "Zweifamilienhäuser aus den 1960er bis 1980er Jahren bilden den größten Anteil "
            "– typischerweise mit ungedämmter Außenwand, teilweise erneuerten Fenstern und "
            "einer Heizung, die zwei bis drei Jahrzehnte auf dem Buckel hat.",
    "besonderheit": "Wo Häuser in Hanglage stehen, lohnt der genaue Blick auf die "
            "erdberührten Bauteile: Ein beheizter Keller im Hang verliert deutlich mehr "
            "Wärme als die Faustformel vermuten lässt.",
  },
  {
    "datei": "energieberatung-langenau.html",
    "ort": "Langenau",
    "typisch": "In Langenau treffen wir überdurchschnittlich oft auf Gebäude, die bereits teilsaniert sind. Das ist eine andere Ausgangslage als beim unsanierten Altbau: Hier geht es weniger um große Dämmpakete als darum, die vorhandene Anlagentechnik richtig einzustellen. Hydraulischer Abgleich und eine abgesenkte Vorlauftemperatur bringen in solchen Häusern häufig mehr als jede weitere Dämmschicht.",
    "artikel": "in",
    "plz": "89129",
    "einwohner": "rund 15.500",
    "entfernung": "etwa 20 Kilometer",
    "titel_zusatz": "Energieberatung Langenau",
    "beschreibung": "Energieberatung in Langenau: Sanierungsfahrplan, Förderung und Energieausweis. Vor Ort im Alb-Donau-Kreis, produktneutral und ohne Provision.",
    "lage": "Langenau liegt nordöstlich von Ulm im flachen Donauried. Die offene Lage "
            "bedeutet mehr Windangriff als in den Tälern der Alb – bei undichten Gebäuden "
            "macht sich das unmittelbar in der Heizkostenabrechnung bemerkbar.",
    "bausubstanz": "Langenau ist über die vergangenen Jahrzehnte kontinuierlich gewachsen. "
            "Neben dem historischen Ortskern prägen Siedlungsgebiete verschiedener "
            "Bauperioden das Bild, von den 1960er Jahren bis in die 2000er. Diese Mischung "
            "ist für die Beratung günstig: Bei Gebäuden ab etwa 1995 lohnt sich oft eher "
            "die Anlagentechnik, bei älteren zuerst die Gebäudehülle.",
    "besonderheit": "Im Donauried ist der Grundwasserstand vielerorts hoch. Für "
            "Erdwärmesonden ist das ein relevanter Punkt, der vor jeder Planung geklärt "
            "sein muss – Luft-Wasser-Wärmepumpen sind hier häufig die praktikablere Lösung.",
  },
  {
    "datei": "energieberatung-ehingen.html",
    "ort": "Ehingen",
    "typisch": "Ein wiederkehrendes Thema in Ehingen und den Teilorten sind Gebäude, die deutlich größer sind als der tatsächliche Wohnbedarf. Beheizte Flure, kaum genutzte Obergeschosse, angebaute Wirtschaftsteile. Bevor über Dämmung gesprochen wird, lohnt die Frage, welche Bereiche künftig überhaupt beheizt werden sollen – das verändert die Heizlast oft stärker als jede Maßnahme an der Hülle.",
    "artikel": "in",
    "plz": "89584",
    "einwohner": "rund 26.500",
    "entfernung": "etwa 30 Kilometer",
    "titel_zusatz": "Energieberatung Ehingen (Donau)",
    "beschreibung": "Energieberatung in Ehingen an der Donau: Sanierungsfahrplan, Fördermittel und Energieausweis. Produktneutral und ohne Provision.",
    "lage": "Ehingen ist die größte Stadt im Alb-Donau-Kreis und liegt an der Donau "
            "südwestlich von Ulm. Mit ihren zahlreichen Teilorten reicht das Stadtgebiet "
            "von der Donauniederung bis auf die Ausläufer der Alb – die klimatischen "
            "Bedingungen unterscheiden sich innerhalb der Stadt spürbar.",
    "bausubstanz": "Die historische Altstadt mit ihrer geschlossenen Bebauung steht neben "
            "Wohngebieten der Nachkriegszeit und neueren Baugebieten in den Teilorten. "
            "Gerade in den Ortsteilen finden sich viele landwirtschaftlich geprägte "
            "Anwesen, bei denen Wohnteil und ehemalige Wirtschaftsgebäude energetisch "
            "getrennt betrachtet werden müssen.",
    "besonderheit": "Bei umgenutzten Scheunen und Anbauten lohnt die Frage, welche Flächen "
            "überhaupt beheizt werden sollen. Oft ist die wirtschaftlichste Maßnahme, die "
            "beheizte Hülle zu verkleinern, statt sie zu dämmen.",
  },
  {
    "datei": "energieberatung-laichingen.html",
    "ort": "Laichingen",
    "typisch": "Wegen der Höhenlage sehen wir in Laichingen viele Gebäude mit Dämmungen aus den 1980er und 1990er Jahren. Diese Bauteile gelten als saniert, erreichen aber bei Weitem nicht die heutigen Anforderungen. Für die Förderung heißt das: Eine Aufdopplung ist möglich und wird bezuschusst, sofern der Ziel-U-Wert erreicht wird. Das wird häufig übersehen, weil man das Bauteil für erledigt hält.",
    "artikel": "in",
    "plz": "89150",
    "einwohner": "rund 11.500",
    "entfernung": "etwa 30 Kilometer",
    "titel_zusatz": "Energieberatung Laichingen",
    "beschreibung": "Energieberatung in Laichingen auf der Schwäbischen Alb: Sanierungsfahrplan, Förderung und Energieausweis. Produktneutral, ohne Provision.",
    "lage": "Laichingen liegt auf der Albhochfläche in rund 750 Metern Höhe. Das ist der "
            "entscheidende Unterschied zu Ulm oder dem Donautal: Die Heizperiode ist "
            "länger, die Normaußentemperatur niedriger. Wer hier mit Kennwerten aus dem "
            "Tal rechnet, unterschätzt den Wärmebedarf.",
    "bausubstanz": "Neben dem alten Ortskern prägen Wohngebiete der zweiten Hälfte des "
            "20. Jahrhunderts das Bild. Wegen der rauen Lage wurde vielerorts früher "
            "gedämmt als im Umland – das heißt aber auch, dass viele Dämmungen aus den "
            "1980er und 1990er Jahren heute technisch überholt sind und die Anforderungen "
            "der Förderung nicht mehr erfüllen.",
    "besonderheit": "Auf der Alb ist der Untergrund verkarstet. Erdwärmebohrungen sind "
            "wasserrechtlich heikel und werden nicht überall genehmigt. Vor jeder Planung "
            "mit Sole-Wasser-Wärmepumpe gehört deshalb die Genehmigungsfrage geklärt.",
  },
  {
    "datei": "energieberatung-blaubeuren.html",
    "ort": "Blaubeuren",
    "typisch": "Bei denkmalgeschützten Gebäuden in Blaubeuren beginnt jede Beratung mit der Denkmalbehörde, nicht mit dem Rechenblatt. Erst wenn feststeht, was zulässig ist, ergibt eine Wirtschaftlichkeitsrechnung Sinn. Häufig bleiben dann Kellerdecke, oberste Geschossdecke, Fenster in Zweitfassung und die Heizungsanlage – zusammen erreicht man damit erstaunlich viel, ohne das Erscheinungsbild anzutasten.",
    "artikel": "in",
    "plz": "89143",
    "einwohner": "rund 12.500",
    "entfernung": "etwa 15 Kilometer",
    "titel_zusatz": "Energieberatung Blaubeuren",
    "beschreibung": "Energieberatung in Blaubeuren: Sanierungsfahrplan und Förderung, auch für denkmalgeschützte Gebäude. Produktneutral und ohne Provision.",
    "lage": "Blaubeuren liegt eingebettet im engen Blautal, umgeben von den Felswänden der "
            "Alb. Die Tallage bringt im Winter ausgeprägte Kaltluftansammlungen mit sich, "
            "gleichzeitig ist der Ort vor Wind gut geschützt.",
    "bausubstanz": "Der historische Ortskern mit Fachwerk und dem Kloster steht unter "
            "besonderem Schutz. Daneben gibt es Wohngebiete der Nachkriegszeit und die "
            "Teilorte auf der Albhochfläche, die klimatisch schon zur Höhenlage zählen – "
            "innerhalb einer Gemeinde also zwei unterschiedliche Ausgangslagen.",
    "besonderheit": "Denkmalschutz ist hier keine Randnotiz, sondern die Regel. Bei "
            "geschützten Gebäuden gelten erleichterte Anforderungen im "
            "Gebäudeenergiegesetz, gleichzeitig sind viele Standardmaßnahmen nicht "
            "zulässig. Fachwerk verträgt zudem nur bestimmte Dämmsysteme – hier ist die "
            "Reihenfolge besonders wichtig.",
  },
  {
    "datei": "energieberatung-erbach.html",
    "ort": "Erbach",
    "typisch": "Viele Häuser in Erbach stammen aus einer Bauphase, in der die Kellerdecke praktisch nie gedämmt wurde. Das merkt man im Erdgeschoss an kalten Böden. Diese Maßnahme ist die günstigste im ganzen Katalog, in Eigenleistung machbar und förderfähig – und sie ist fast immer der richtige erste Schritt, bevor über die Heizung gesprochen wird.",
    "artikel": "in",
    "plz": "89155",
    "einwohner": "rund 14.000",
    "entfernung": "etwa 15 Kilometer",
    "titel_zusatz": "Energieberatung Erbach (Donau)",
    "beschreibung": "Energieberatung in Erbach an der Donau: Sanierungsfahrplan, Fördermittel und Energieausweis. Produktneutral und ohne Provision.",
    "lage": "Erbach liegt westlich von Ulm im Donautal. Die Lage im Tal bedeutet milde "
            "Durchschnittstemperaturen, aber auch Nebel und Feuchte in den Wintermonaten – "
            "ein Punkt, der bei Luft-Wasser-Wärmepumpen und ihrem Abtauverhalten "
            "mitgedacht gehört.",
    "bausubstanz": "Erbach ist in den vergangenen Jahrzehnten deutlich gewachsen. Der "
            "Bestand reicht vom älteren Ortskern über die Siedlungen der 1970er und 1980er "
            "Jahre bis zu neueren Baugebieten. In den Teilorten Dellmensingen, Donaurieden "
            "und Bach findet sich zusätzlich älterer, oft landwirtschaftlich geprägter "
            "Bestand.",
    "besonderheit": "Bei Gebäuden aus den 1970er Jahren lohnt der Blick auf die "
            "Rollladenkästen: Sie sind oft die größte einzelne Schwachstelle der ganzen "
            "Hülle – und mit geringem Aufwand in Eigenleistung zu verbessern.",
  },
  {
    "datei": "energieberatung-dornstadt.html",
    "ort": "Dornstadt",
    "typisch": "In Dornstadt und den Teilorten kennen wir die typischen Bauphasen aus eigener Anschauung. Bei Häusern derselben Siedlung lassen sich Erfahrungswerte oft direkt übertragen – wir wissen dann schon vor dem Termin, worauf wir achten müssen. Das verkürzt die Aufnahme und macht die Zahlen belastbarer, weil sie an vergleichbaren Gebäuden geprüft sind.",
    "artikel": "in",
    "plz": "89160",
    "einwohner": "rund 8.700",
    "entfernung": "direkt vor Ort",
    "titel_zusatz": "Energieberatung Dornstadt",
    "beschreibung": "Energieberatung in Dornstadt: Sanierungsfahrplan, Förderung und Energieausweis – vom Energieberater direkt aus dem Ort.",
    "lage": "Dornstadt liegt nördlich von Ulm am Übergang zur Albhochfläche, auf rund "
            "600 Metern Höhe. Damit ist es klimatisch weder Donautal noch Alb, sondern "
            "liegt dazwischen – ein Detail, das bei der Heizlast durchaus ins Gewicht fällt.",
    "bausubstanz": "Dornstadt ist seit den 1960er Jahren stark gewachsen, mit einem hohen "
            "Anteil an Ein- und Zweifamilienhäusern. Dazu kommen die Teilorte Bollingen, "
            "Temmenhausen, Scharenstetten und Tomerdingen mit älterem, dörflich geprägtem "
            "Bestand.",
    "besonderheit": "Als hier ansässiges Büro sind wir schnell vor Ort – für einen "
            "Vor-Ort-Termin, für Rückfragen während der Bauphase und für die Abnahme. Bei "
            "Nachbargebäuden ähnlichen Baujahrs lassen sich Erfahrungswerte oft direkt "
            "übertragen.",
  },
]

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# BAUSTEINE AUS DER STARTSEITE
# Werden bei JEDEM Lauf frisch aus index.html geschnitten. Frueher lagen sie
# als Zwischendateien daneben und konnten veralten - bei der Umstellung auf
# Roboto hatten die Ortsseiten dadurch noch die alten Schriften.
# ---------------------------------------------------------------------------
_CACHE = {}

def _startseite():
    if "html" not in _CACHE:
        _CACHE["html"] = io.open("index.html", encoding="utf-8").read()
    return _CACHE["html"]

def _schnitt(muster, name):
    m = re.search(muster, _startseite(), re.S)
    if not m:
        raise SystemExit(f"Baustein '{name}' nicht in index.html gefunden - "
                         f"wurde die Startseite umgebaut? Muster pruefen.")
    return m.group(1)

def stil():
    """CSS der Startseite plus die Ergaenzungen fuer die Ortsseiten."""
    return _schnitt(r"<style>\n(.*?)\n</style>", "CSS") + ORTS_CSS

def hero_teil():
    """Hero-Grafik ohne die anklickbaren Flaechen und ohne Popup - dafuer
    muesste sonst das gesamte Popup-JavaScript auf jede Ortsseite."""
    h = _schnitt(r'(<div class="hero-visual">.*?</div>\s*</div>\s*\n)', "Hero")
    h = re.sub(r'\s*<div class="illu-pop".*?</div>\s*</div>\s*$', '\n      </div>', h, flags=re.S)
    h = re.sub(r'\s*<!-- Unsichtbare Klick-.*?(?=\s*<!-- Beschriftungen -->)', '', h, flags=re.S)
    h = h.replace('class="il-tag hotspot"', 'class="il-tag"').replace(' class="hotspot"', '')
    h = re.sub(r'\s*tabindex="0" role="button" aria-label="[^"]*"', '', h)
    h = re.sub(r'<li data-key="[^"]*"[^>]*>', '<li>', h)
    return h.rstrip()

def defs_teil():
    return _schnitt(r'(<svg width="0" height="0".*?</svg>)', "SVG-Definitionen")

def abschnitt(name):
    return _schnitt(r"(<!-- ={10,} " + name + r" ={10,} -->.*?</section>)", name)

ORTS_CSS = """

/* ==== Ortsseiten ==== */
.ort-text{max-width:74ch}
.ort-text h3{margin:34px 0 10px;font-size:1.2rem}
.ort-text p{margin-bottom:15px;color:var(--ink-2)}
.ort-text .liste{margin:0 0 18px}
.ort-text .liste li{display:flex;gap:11px;margin-bottom:10px;color:var(--ink-2)}
.ort-text .liste li::before{content:"";width:7px;height:7px;flex:none;margin-top:10px;border-radius:50%;background:var(--amber)}
.ort-text .merksatz{background:var(--forest-soft);border-radius:var(--radius-sm);padding:20px 24px;margin:26px 0;color:var(--forest);font-size:.97rem}
.ort-text .merksatz b{display:block;font-size:.74rem;letter-spacing:.11em;text-transform:uppercase;margin-bottom:7px;opacity:.75}
.krumen{padding:22px 0 0;font-size:.82rem;color:var(--muted)}
.krumen ol{display:flex;flex-wrap:wrap;gap:8px;list-style:none}
.krumen li::after{content:"\\203A";margin-left:8px;color:var(--line)}
.krumen li:last-child::after{content:""}
.krumen a:hover{color:var(--amber-deep);text-decoration:underline;text-underline-offset:3px}
.ort-nachbarn{display:flex;flex-wrap:wrap;gap:10px;margin-top:30px}
.ort-nachbarn a{
  font-size:.86rem;font-weight:500;color:var(--ink-2);background:var(--white);
  border:1px solid var(--line);border-radius:100px;padding:8px 16px;transition:.25s var(--ease);
}
.ort-nachbarn a:hover{border-color:var(--amber);color:var(--amber-deep);transform:translateY(-2px)}
"""

def seite(o):
    ort = o["ort"]
    titel = f'{o["titel_zusatz"]} – Sanierungsfahrplan & Förderung'
    if len(titel) > 60:
        titel = f'{o["titel_zusatz"]} | Tsukerman'
    url = f'{DOMAIN}/{o["datei"]}'

    andere = [x for x in ORTE if x["datei"] != o["datei"]]
    nachbar_chips = "\n".join(
        f'      <a href="{x["datei"]}">Energieberatung {x["ort"]}</a>' for x in andere)

    # Bausteine aus der Startseite - halten Orts- und Startseite im Gleichstand
    hero_grafik  = hero_teil()
    foerderblock = abschnitt("ZAHLEN")
    ablauf       = abschnitt("ABLAUF")
    kontakt      = abschnitt("KONTAKT")
    defs_svg     = defs_teil()

    artikel   = o["artikel"];   plz          = o["plz"]
    einwohner = o["einwohner"]; entfernung   = o["entfernung"]
    lage      = o["lage"];      bausubstanz  = o["bausubstanz"]
    besonderheit = o["besonderheit"]; typisch = o["typisch"]
    tel_link  = TEL_LINK
    nachbar_links = "\n".join(
        f'        <a href="{x["datei"]}">Energieberatung {x["ort"]}</a>' for x in andere)

    return f"""<!DOCTYPE html>
<!--
  ============================================================================
  ORTSSEITE {ort.upper()} – ERZEUGT, NICHT VON HAND BEARBEITEN!
  Änderungen in ortsseiten-erzeugen.py vornehmen und das Skript erneut laufen
  lassen, sonst sind sie beim nächsten Durchlauf wieder weg.
  ============================================================================
-->
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titel}</title>
<meta name="description" content="{o['beschreibung']}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#FDFBF7">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23C07A2E'/%3E%3Cg fill='none' stroke='%23fff' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M7 15 16 8l9 7'/%3E%3Cpath d='M9.5 13.6V24h13V13.6'/%3E%3Cpath d='M13.5 24v-5h5v5'/%3E%3C/g%3E%3C/svg%3E">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="Tsukerman Energieberatung">
<meta property="og:title" content="{o['titel_zusatz']} – erst rechnen, dann sanieren">
<meta property="og:description" content="{o['beschreibung']}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<style>
{stil()}
</style>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Tsukerman Energieberatung",
  "description": "Energieberatung für Wohngebäude {o['artikel']} {ort}: Sanierungsfahrplan, Fördermittel und Energieausweis.",
  "url": "{url}",
  "telephone": "{TEL_LINK}",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "Griesweg 20",
    "postalCode": "89160",
    "addressLocality": "Dornstadt",
    "addressRegion": "Baden-Württemberg",
    "addressCountry": "DE"
  }},
  "areaServed": {{ "@type": "City", "name": "{ort}" }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{ "@type": "ListItem", "position": 1, "name": "Startseite", "item": "{DOMAIN}/" }},
    {{ "@type": "ListItem", "position": 2, "name": "Energieberatung {ort}", "item": "{url}" }}
  ]
}}
</script>
</head>
<body>

<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>

{defs_svg}

<header class="site-header">
  <div class="wrap header-inner">
    <a href="index.html" class="logo">
      <span class="logo-mark">
        <svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.6V20h14V9.6"/><path d="M10 20v-5h4v5"/>
        </svg>
      </span>
      <span class="logo-text"><b>Tsukerman</b><span>Energieberatung</span></span>
    </a>
    <nav class="nav" aria-label="Hauptnavigation">
      <a href="sanierungsfahrplan.html">Sanierungsfahrplan</a>
      <a href="sanierungsrechner.html">Rechner</a>
      <a href="ratgeber.html">Ratgeber</a>
      <a href="index.html#leistungen">Leistungen</a>
      <a href="index.html#kontakt">Kontakt</a>
    </nav>
    <div class="header-cta">
      <a href="index.html#kontakt" class="btn btn-primary btn-sm">Kostenloses Erstgespräch</a>
      <button class="burger" id="burger" aria-label="Menü öffnen" aria-expanded="false" aria-controls="mobileNav">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>

<nav class="mobile-nav" id="mobileNav" aria-label="Mobile Navigation">
  <a href="index.html">Startseite</a>
  <a href="sanierungsfahrplan.html">Sanierungsfahrplan</a>
  <a href="sanierungsrechner.html">Sanierungsrechner</a>
  <a href="ratgeber.html">Ratgeber</a>
  <a href="index.html#leistungen">Leistungen</a>
  <a href="index.html#kontakt">Kontakt</a>
  <a href="index.html#kontakt" class="btn btn-primary">Kostenloses Erstgespräch</a>
</nav>

<div class="mobile-bar">
  <a href="tel:{TEL_LINK}" class="btn btn-amber">Anrufen</a>
  <a href="index.html#kontakt" class="btn btn-primary">Anfrage senden</a>
</div>

<main id="inhalt">

<!-- ========================= HERO ========================= -->
<section class="hero" id="top">
  <div class="dots"></div>
  <div class="wrap hero-grid">

    <div class="hero-copy">
      <span class="eyebrow">Erst rechnen. Dann sanieren.</span>
      <h1>Energieberatung <span class="accent">{ort}</span></h1>
      <p class="hero-sub">
        <strong>Energieberatung für {ort} und Umgebung.</strong> Sanieren ist teuer –
        falsch sanieren ist teurer. Wir rechnen Ihnen vor, welche Maßnahmen sich bei
        <em>Ihrem</em> Gebäude wirklich lohnen, in welcher Reihenfolge sie sinnvoll sind
        und welche Fördermittel Sie dafür bekommen.
      </p>

      <div class="hero-actions">
        <a href="#kontakt" class="btn btn-primary">
          Gratis Erstgespräch vereinbaren
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </a>
        <a href="sanierungsrechner.html" class="btn btn-ghost">Sanierungsrechner starten</a>
      </div>

      <div class="trust-row">
        <span class="trust-item"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#icCheck"/></svg> Energie-Effizienz-Expertenliste (dena)</span>
        <span class="trust-item"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#icCheck"/></svg> BAFA- &amp; KfW-förderfähig</span>
        <span class="trust-item"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#icCheck"/></svg> Keine Provisionen, kein Produktverkauf</span>
        <span class="trust-item"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#icCheck"/></svg> {ort}: {entfernung} von unserem Büro</span>
      </div>
    </div>

{hero_grafik}
  </div>
</section>

<div class="wrap">
  <nav class="krumen" aria-label="Brotkrumennavigation">
    <ol>
      <li><a href="index.html">Startseite</a></li>
      <li>Energieberatung {ort}</li>
    </ol>
  </nav>
</div>

<!-- ======= ORTSTEIL: der eigene Inhalt dieser Seite ======= -->
<section class="section-pad">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Vor Ort</span>
      <h2>Energieberatung {artikel} {ort} – wir sind {entfernung} entfernt</h2>
      <p class="lead">{lage}</p>
    </div>

    <div class="ort-text reveal">
      <p>
        Unser Büro sitzt in Dornstadt, {ort} ({plz}, {einwohner} Einwohner) liegt
        {entfernung} entfernt. Vor-Ort-Termine sind damit kurzfristig möglich – auch
        mehrfach, wenn es die Bauphase erfordert.
      </p>

      <h3>Gebäudestruktur und energetische Ausgangslage {artikel} {ort}</h3>
      <p>{bausubstanz}</p>
      <p>{besonderheit}</p>

      <h3>Was {ort} typischerweise bedeutet</h3>
      <p>{typisch}</p>

      <div class="merksatz">
        <b>Warum das für Ihre Sanierung zählt</b>
        Wer die örtlichen Gegebenheiten kennt, rechnet genauer. Klimaregion, Baualter und
        Untergrund entscheiden mit darüber, welche Maßnahme sich lohnt – und welche man
        besser sein lässt.
      </div>

      <h3>Was wir {artikel} {ort} für Sie tun</h3>
      <ul class="liste">
        <li><a href="sanierungsfahrplan.html">Individueller Sanierungsfahrplan (iSFP)</a> mit Kosten, Einsparung und Amortisation je Maßnahme</li>
        <li>Fördermittel-Management: Antrag bei BAFA und KfW, Fristen im Blick, Verwendungsnachweis</li>
        <li>Energieausweis nach GEG – Bedarfs- und Verbrauchsausweis</li>
        <li>Baubegleitung und Qualitätssicherung während der Umsetzung</li>
        <li>Heizlastberechnung und hydraulischer Abgleich</li>
        <li>Zweitmeinung zu vorliegenden Handwerkerangeboten</li>
      </ul>
    </div>

    <div class="cta-band reveal">
      <div class="cta-band-text">
        <b>Ihr Gebäude {artikel} {ort} durchrechnen lassen?</b>
        <span>20 Minuten am Telefon, kostenlos. Danach wissen Sie, ob und wie es weitergeht.</span>
      </div>
      <div class="cta-band-knoepfe">
        <a href="#kontakt" class="btn btn-primary">Kostenloses Erstgespräch</a>
        <a href="tel:{tel_link}" class="btn btn-ghost">Direkt anrufen</a>
      </div>
    </div>
  </div>
</section>

{foerderblock}

{ablauf}

<!-- ========================= FAQ ========================= -->
<section class="section-pad faq" id="faq">
  <div class="wrap faq-grid">
    <div class="reveal faq-intro">
      <span class="eyebrow">Häufige Fragen</span>
      <h2>Aus {ort} und Umgebung.</h2>
      <p class="lead" style="margin-top:16px">Wenn Ihre Frage nicht dabei ist: einfach stellen. Das Erstgespräch kostet nichts und verpflichtet zu nichts.</p>
    </div>

    <div class="reveal">
      <div class="faq-item">
        <button class="faq-q">Kommen Sie für den Vor-Ort-Termin nach {ort}?<span class="faq-icon"></span></button>
        <div class="faq-a"><p>Ja. {ort} liegt {entfernung} von unserem Büro in Dornstadt entfernt und gehört zum regulären Einsatzgebiet. Anfahrtskosten fallen innerhalb des Alb-Donau-Kreises und im Umkreis von rund 50 Kilometern um Ulm nicht gesondert an.</p></div>
      </div>
      <div class="faq-item">
        <button class="faq-q">Was kostet eine Energieberatung {artikel} {ort}?<span class="faq-icon"></span></button>
        <div class="faq-a"><p>Das hängt von Gebäudegröße und Umfang ab. Für ein Einfamilienhaus liegt ein individueller Sanierungsfahrplan üblicherweise im niedrigen vierstelligen Bereich – abzüglich der Förderung von 50 % bleibt ein deutlich kleinerer Eigenanteil. Sie erhalten vorab ein Festpreisangebot.</p></div>
      </div>
      <div class="faq-item">
        <button class="faq-q">Wie schnell bekomme ich einen Termin?<span class="faq-icon"></span></button>
        <div class="faq-a"><p>Das Erstgespräch am Telefon meist innerhalb weniger Tage. Für den Vor-Ort-Termin planen wir gemeinsam einen Zeitpunkt, an dem Sie ohnehin zu Hause sind – er dauert zwei bis drei Stunden.</p></div>
      </div>
    </div>
  </div>

  <div class="wrap">
    <div class="ort-nachbarn">
{nachbar_chips}
    </div>
  </div>
</section>

{kontakt}

</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="index.html" class="logo">
          <span class="logo-mark">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.6V20h14V9.6"/><path d="M10 20v-5h4v5"/>
            </svg>
          </span>
          <span class="logo-text"><b>Tsukerman</b><span>Energieberatung</span></span>
        </a>
        <p>Energieberatung für Wohngebäude in Ulm und im Alb-Donau-Kreis. Produktneutral, ohne Provision.</p>
        <a href="index.html#kontakt" class="btn btn-primary btn-sm">Kostenloses Erstgespräch</a>
      </div>
      <div class="footer-col">
        <h4>Orte</h4>
{nachbar_links}
      </div>
      <div class="footer-col">
        <h4>Ratgeber</h4>
        <a href="ratgeber-heizung-tauschen-pflicht.html">Heizung tauschen</a>
        <a href="ratgeber-reihenfolge-sanierung.html">Richtige Reihenfolge</a>
        <a href="ratgeber-foerderung-oder-steuer.html">Förderung oder Steuer</a>
        <a href="ratgeber-sanieren-schwaebische-alb.html">Sanieren auf der Alb</a>
        <a href="ratgeber.html">Alle Beiträge</a>
      </div>
      <div class="footer-col">
        <h4>Kontakt</h4>
        <a href="tel:{TEL_LINK}">{TEL_ANZEIGE}</a>
        <!-- [TODO] echte E-Mail-Adresse eintragen -->
        <a href="mailto:kontakt@energieberater-albdonau.de">[E-Mail eintragen]</a>
        <address>Griesweg 20<br>89160 Dornstadt</address>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 Stanislaw Tsukerman Energieberatung</span>
      <nav aria-label="Rechtliches">
        <a href="index.html">Startseite</a>
        <a href="impressum.html">Impressum</a>
        <a href="datenschutz.html">Datenschutz</a>
      </nav>
    </div>
  </div>
</footer>

<script>
'use strict';
(function(){{
  var ORTSNAME = '{ort}';

  /* Kopfzeile beim Scrollen einfaerben. Ohne diesen Handler bleibt der fixe
     Kopf durchsichtig und der Seiteninhalt schiebt sich sichtbar durch die
     Navigation - die CSS-Klasse .stuck kommt aus der Startseite. */
  var kopfzeile = document.querySelector('.site-header');
  function beimScrollen(){{ kopfzeile.classList.toggle('stuck', window.scrollY > 24); }}
  beimScrollen();
  window.addEventListener('scroll', beimScrollen, {{passive:true}});

  var burger = document.getElementById('burger');
  var mobileNav = document.getElementById('mobileNav');
  function setNav(open){{
    mobileNav.classList.toggle('open', open);
    burger.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
  }}
  burger.addEventListener('click', function(){{ setNav(!mobileNav.classList.contains('open')); }});
  mobileNav.querySelectorAll('a').forEach(function(a){{ a.addEventListener('click', function(){{ setNav(false); }}); }});
  document.addEventListener('keydown', function(e){{
    if(e.key === 'Escape' && mobileNav.classList.contains('open')){{ setNav(false); burger.focus(); }}
  }});

  /* Scroll-Reveal. OHNE DAS BLEIBT DIE GANZE SEITE UNSICHTBAR:
     .reveal steht auf opacity:0 und wird erst durch die Klasse "in" sichtbar. */
  var reveals = document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){{
    var io = new IntersectionObserver(function(eintraege){{
      eintraege.forEach(function(e){{
        if(e.isIntersecting){{ e.target.classList.add('in'); io.unobserve(e.target); }}
      }});
    }}, {{threshold:.12, rootMargin:'0px 0px -60px 0px'}});
    reveals.forEach(function(el, i){{
      el.style.transitionDelay = (i % 4) * 70 + 'ms';
      io.observe(el);
    }});
  }} else {{
    reveals.forEach(function(el){{ el.classList.add('in'); }});
  }}

  /* Kontaktformular - dieselbe Supabase-Datenbank wie auf der Startseite */
  var SUPABASE_URL = 'https://lgabyzhzbosbzlyfnknf.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_sTIrPusPKapueKw7ARBQEw_HNIvKDRt';
  var form = document.getElementById('contactForm');
  var note = document.getElementById('formNote');
  var consentBox = document.getElementById('consentBox');
  var honeypot = document.getElementById('f-website');

  function markiere(el, ok){{
    var w = el.closest('.field');
    if(w) w.classList.toggle('invalid', !ok);
    el.setAttribute('aria-invalid', ok ? 'false' : 'true');
  }}
  function pruefe(){{
    var ersterFehler = null;
    var name = document.getElementById('f-name');
    var nameOk = name.value.trim().length >= 2;
    markiere(name, nameOk); if(!nameOk) ersterFehler = name;
    var mail = document.getElementById('f-mail');
    var mailOk = /^[^\\s@]+@[^\\s@]+\\.[a-zA-Z]{{2,}}$/.test(mail.value.trim());
    markiere(mail, mailOk); if(!mailOk && !ersterFehler) ersterFehler = mail;
    var consent = document.getElementById('f-consent');
    consentBox.classList.toggle('invalid', !consent.checked);
    if(!consent.checked && !ersterFehler) ersterFehler = consent;
    return ersterFehler;
  }}
  ['f-name','f-mail'].forEach(function(id){{
    var el = document.getElementById(id);
    el.addEventListener('input', function(){{
      if(el.closest('.field').classList.contains('invalid')) pruefe();
    }});
  }});
  document.getElementById('f-consent').addEventListener('change', function(){{
    if(consentBox.classList.contains('invalid')) pruefe();
  }});

  form.addEventListener('submit', function(e){{
    e.preventDefault();
    note.classList.remove('is-error','is-ok');
    if(honeypot && honeypot.value !== '') return;      // Bot
    var fehler = pruefe();
    if(fehler){{
      fehler.focus();
      note.textContent = 'Bitte prüfen Sie die markierten Felder.';
      note.classList.add('is-error');
      return;
    }}
    var btn = form.querySelector('button[type="submit"]');
    var btnText = btn.innerHTML;
    btn.disabled = true; btn.textContent = 'Wird gesendet …'; note.textContent = '';

    fetch(SUPABASE_URL + '/rest/v1/leads', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer ' + SUPABASE_KEY,
        'Prefer': 'return=minimal'
      }},
      body: JSON.stringify({{
        quelle: 'kontaktformular',
        name: document.getElementById('f-name').value.trim(),
        email: document.getElementById('f-mail').value.trim(),
        telefon: document.getElementById('f-phone').value.trim() || null,
        gebaeudetyp: document.getElementById('f-type').value,
        baujahr: document.getElementById('f-year').value.trim() || null,
        nachricht: (document.getElementById('f-msg').value.trim() || '') + ' [Ortsseite: ' + ORTSNAME + ']',
        einwilligung: true
      }})
    }})
    .then(function(r){{
      if(!r.ok) throw new Error('HTTP ' + r.status);
      form.reset(); btn.disabled = false; btn.innerHTML = btnText;
      note.textContent = 'Vielen Dank, Ihre Anfrage ist angekommen. Wir melden uns in der Regel innerhalb eines Werktags.';
      note.classList.add('is-ok');
    }})
    .catch(function(){{
      btn.disabled = false; btn.innerHTML = btnText;
      note.textContent = 'Das hat leider nicht geklappt. Bitte versuchen Sie es erneut oder rufen Sie an: 0152 24290826';
      note.classList.add('is-error');
    }});
  }});

  document.querySelectorAll('.faq-item').forEach(function(item, i){{
    var q = item.querySelector('.faq-q'), a = item.querySelector('.faq-a');
    q.id = 'fq'+(i+1); a.id = 'fa'+(i+1);
    q.setAttribute('aria-expanded','false');
    q.setAttribute('aria-controls', a.id);
    a.setAttribute('role','region');
    a.setAttribute('aria-labelledby', q.id);
    var ic = item.querySelector('.faq-icon'); if(ic) ic.setAttribute('aria-hidden','true');
    q.addEventListener('click', function(){{
      var offen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(function(o){{
        o.classList.remove('open');
        o.querySelector('.faq-a').style.maxHeight = null;
        o.querySelector('.faq-q').setAttribute('aria-expanded','false');
      }});
      if(!offen){{
        item.classList.add('open');
        a.style.maxHeight = a.scrollHeight + 'px';
        q.setAttribute('aria-expanded','true');
      }}
    }});
  }});
  var t = null;
  window.addEventListener('resize', function(){{
    clearTimeout(t);
    t = setTimeout(function(){{
      document.querySelectorAll('.faq-item.open .faq-a').forEach(function(a){{
        a.style.maxHeight = a.scrollHeight + 'px';
      }});
    }}, 120);
  }}, {{passive:true}});
}})();
</script>

</body>
</html>
"""

if __name__ == "__main__":
    for o in ORTE:
        io.open(o["datei"], "w", encoding="utf-8", newline="\n").write(seite(o))
        print("erzeugt:", o["datei"])
    print(f"\n{len(ORTE)} Ortsseiten erzeugt.")
    print("Nicht vergessen: sitemap.xml ergänzen und von der Startseite verlinken.")
