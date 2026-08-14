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

import io, os

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

def stil():
    return io.open("_ortsseite-stil.css", encoding="utf-8").read()

def seite(o):
    ort = o["ort"]
    titel = f'{o["titel_zusatz"]} – Sanierungsfahrplan & Förderung'
    if len(titel) > 60:
        titel = f'{o["titel_zusatz"]} | Tsukerman'
    url = f'{DOMAIN}/{o["datei"]}'

    andere = [x for x in ORTE if x["datei"] != o["datei"]]
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
  <a href="index.html#leistungen">Leistungen</a>
  <a href="index.html#kontakt">Kontakt</a>
  <a href="index.html#kontakt" class="btn btn-primary">Kostenloses Erstgespräch</a>
</nav>

<div class="mobile-bar">
  <a href="tel:{TEL_LINK}" class="btn btn-amber">Anrufen</a>
  <a href="index.html#kontakt" class="btn btn-primary">Anfrage senden</a>
</div>

<main id="inhalt">

<div class="wrap">
  <nav class="krumen" aria-label="Brotkrumennavigation">
    <ol>
      <li><a href="index.html">Startseite</a></li>
      <li>Energieberatung {ort}</li>
    </ol>
  </nav>
</div>

<section class="wrap seiten-kopf">
  <span class="eyebrow">Alb-Donau-Kreis &amp; Umgebung</span>
  <h1>Energieberatung {ort}</h1>
  <p class="lead">
    Erst rechnen, dann sanieren – auch {o['artikel']} {ort}. Wir zeigen Ihnen, welche
    Maßnahmen sich bei Ihrem Gebäude wirklich lohnen, in welcher Reihenfolge sie sinnvoll
    sind und welche Fördermittel Sie dafür bekommen. Produktneutral, ohne Provision.
  </p>
  <div class="kopf-aktionen">
    <a href="index.html#kontakt" class="btn btn-primary">Kostenloses Erstgespräch</a>
    <a href="tel:{TEL_LINK}" class="btn btn-ghost">{TEL_ANZEIGE}</a>
  </div>
</section>

<div class="wrap inhalt">
  <article class="text">

    <h2>Energieberatung {o['artikel']} {ort} – wir sind {o['entfernung']} entfernt</h2>
    <p>{o['lage']}</p>
    <p>
      Unser Büro sitzt in Dornstadt, {ort} ({o['plz']}, {o['einwohner']} Einwohner) liegt
      {o['entfernung']} entfernt. Vor-Ort-Termine sind damit kurzfristig möglich – auch
      mehrfach, wenn es die Bauphase erfordert.
    </p>

    <h2>Gebäudestruktur und energetische Ausgangslage {o['artikel']} {ort}</h2>
    <p>{o['bausubstanz']}</p>
    <p>{o['besonderheit']}</p>

    <h2>Was {ort} typischerweise bedeutet</h2>
    <p>{o['typisch']}</p>

    <div class="merksatz">
      <b>Warum das für Ihre Sanierung zählt</b>
      Wer die örtlichen Gegebenheiten kennt, rechnet genauer. Klimaregion, Baualter und
      Untergrund entscheiden mit darüber, welche Maßnahme sich lohnt – und welche man
      besser sein lässt.
    </div>

    <h2>Was wir {o['artikel']} {ort} für Sie tun</h2>
    <ul class="liste">
      <li><a href="sanierungsfahrplan.html">Individueller Sanierungsfahrplan (iSFP)</a> mit Kosten, Einsparung und Amortisation je Maßnahme</li>
      <li>Fördermittel-Management: Antrag bei BAFA und KfW, Fristen im Blick, Verwendungsnachweis</li>
      <li>Energieausweis nach GEG – Bedarfs- und Verbrauchsausweis</li>
      <li>Baubegleitung und Qualitätssicherung während der Umsetzung</li>
      <li>Heizlastberechnung und hydraulischer Abgleich</li>
      <li>Zweitmeinung zu vorliegenden Handwerkerangeboten</li>
    </ul>

    <h2>Vorab selbst rechnen</h2>
    <p>
      Bevor wir sprechen, können Sie sich selbst ein Bild machen: Der kostenlose
      <a href="sanierungsrechner.html">Sanierungsrechner</a> ermittelt in etwa zehn Minuten
      die Energieklasse Ihres Gebäudes und zeigt für jede Maßnahme, was sie spart und was
      sie kosten darf. Ohne Anmeldung, ohne Datenübertragung, solange Sie nur rechnen.
    </p>

    <h2>Häufige Fragen aus {ort}</h2>

    <div class="faq-item">
      <button class="faq-q">Kommen Sie für den Vor-Ort-Termin nach {ort}?<span class="faq-icon"></span></button>
      <div class="faq-a"><p>Ja. {ort} liegt {o['entfernung']} von unserem Büro in Dornstadt entfernt und gehört zum regulären Einsatzgebiet. Anfahrtskosten fallen innerhalb des Alb-Donau-Kreises und im Umkreis von rund 50 Kilometern um Ulm nicht gesondert an.</p></div>
    </div>

    <div class="faq-item">
      <button class="faq-q">Was kostet eine Energieberatung {o['artikel']} {ort}?<span class="faq-icon"></span></button>
      <div class="faq-a"><p>Das hängt von Gebäudegröße und Umfang ab. Für ein Einfamilienhaus liegt ein individueller Sanierungsfahrplan üblicherweise im niedrigen vierstelligen Bereich – abzüglich der Förderung von 50 % bleibt ein deutlich kleinerer Eigenanteil. Sie erhalten vorab ein Festpreisangebot.</p></div>
    </div>

    <div class="faq-item">
      <button class="faq-q">Wie schnell bekomme ich einen Termin?<span class="faq-icon"></span></button>
      <div class="faq-a"><p>Das Erstgespräch am Telefon meist innerhalb weniger Tage. Für den Vor-Ort-Termin planen wir gemeinsam einen Zeitpunkt, an dem Sie ohnehin zu Hause sind – er dauert zwei bis drei Stunden.</p></div>
    </div>

  </article>

  <aside class="spalte">
    <div class="karte karte-kontakt">
      <h3>Kurz sprechen?</h3>
      <p>20 Minuten, kostenlos, unverbindlich. Danach wissen Sie, ob und wie es für Ihr Gebäude weitergeht.</p>
      <a href="tel:{TEL_LINK}" class="tel-gross">
        <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>
        {TEL_ANZEIGE}
      </a>
      <p style="font-size:.8rem;margin:0">Montag bis Freitag, 8–18 Uhr</p>
    </div>

    <div class="karte">
      <h3>Erst selbst rechnen</h3>
      <p>Energieklasse und Einsparpotenzial Ihres Hauses in zehn Minuten – kostenlos und ohne Anmeldung.</p>
      <a href="sanierungsrechner.html" class="btn btn-amber btn-sm">Rechner starten</a>
    </div>

    <div class="karte">
      <h3>Auch in Ihrer Nähe</h3>
      <nav class="spalte-links" aria-label="Weitere Orte">
{nachbar_links}
      </nav>
    </div>
  </aside>
</div>

<section class="abschluss">
  <div class="wrap abschluss-inner">
    <div>
      <h2>Reden wir über Ihr Gebäude {o['artikel']} {ort}.</h2>
      <p>Das Erstgespräch dauert etwa 20 Minuten, kostet nichts und endet entweder mit einem Angebot oder mit einer ehrlichen Empfehlung, was Sie stattdessen tun sollten.</p>
    </div>
    <a href="index.html#kontakt" class="btn btn-primary">Kostenloses Erstgespräch</a>
  </div>
</section>

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
