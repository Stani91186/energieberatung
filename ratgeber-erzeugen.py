#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RATGEBER ERZEUGEN
=================
Baut die Ratgeber-Uebersicht und die einzelnen Artikel. Wie bei den
Ortsseiten: Der Generator laeuft nur hier auf dem Rechner, das Ergebnis ist
statisches HTML.

    Aufruf:  python ratgeber-erzeugen.py

Kopfzeile, Fussbereich und CSS werden bei jedem Lauf frisch aus index.html
geschnitten - Ratgeber und Startseite koennen also nicht auseinanderlaufen.

THEMENWAHL
----------
Ausgewaehlt nach zwei Kriterien: Wonach wird tatsaechlich gesucht, und wo
kann dieses Buero etwas sagen, das ueberregionale Anbieter nicht sagen. Der
Alb-Artikel hat wenig Suchvolumen, aber praktisch keinen Wettbewerb.
"""

import io, os, re

DOMAIN = "https://energieberater-albdonau.de"
TEL_ANZEIGE = "0152 24290826"
TEL_LINK = "+4915224290826"

# ---------------------------------------------------------------------------
_CACHE = {}

def _start():
    if "html" not in _CACHE:
        _CACHE["html"] = io.open("index.html", encoding="utf-8").read()
    return _CACHE["html"]

def _schnitt(muster, name):
    m = re.search(muster, _start(), re.S)
    if not m:
        raise SystemExit(f"Baustein '{name}' nicht in index.html gefunden.")
    return m.group(1)


# ---------------------------------------------------------------------------
# GEMEINSAMER RAHMEN
# Kopf und Fuss stammen aus index.html und werden bei jedem Lauf frisch
# geschnitten. Vorher pflegte jeder Generator eigene Kopien - dadurch hatten
# Start-, Orts- und Ratgeberseiten unterschiedliche Menuepunkte und
# unterschiedlich viele Fussspalten.
# ---------------------------------------------------------------------------
def _absolut(markup):
    """Sprungmarken der Startseite absolut machen - '#leistungen' zeigt auf
    einer Unterseite sonst auf einen Abschnitt, den es dort nicht gibt."""
    markup = markup.replace('href="#top"', 'href="index.html"')
    return re.sub(r'href="#(?!\s*")', 'href="index.html#', markup)


def preise():
    """Honorare aus dem PREISE-Abschnitt von index.html.

    Gelesen, nie geschrieben: index.html ist die einzige Quelle. Stuenden die
    Betraege hier noch einmal, liefen sie frueher oder spaeter auseinander."""
    if "preise" not in _CACHE:
        m = re.search(r'<section[^>]*id="preise"[^>]*>', _start())
        if not m:
            raise SystemExit("Abschnitt PREISE fehlt in index.html - "
                             "die Honorare koennen nicht gelesen werden.")
        roh = dict(re.findall(r'data-preis-([a-z-]+)="(\d+)"', m.group(0)))
        for k in ("isfp-ab", "foerderung-max", "eigen-ab"):
            if k not in roh:
                raise SystemExit(f"data-preis-{k} fehlt im PREISE-Abschnitt "
                                 f"von index.html.")
        _CACHE["preise"] = {k.replace("-", "_"): f"{int(v):,}".replace(",", ".")
                            for k, v in roh.items()}
    return _CACHE["preise"]


# Platzhalter im Artikeltext. Bewusst am Schluss auf die FERTIGE Seite
# angewendet und nicht in artikel_seite(): so werden Fliesstext, FAQ,
# Meta-Beschreibung, Uebersichtskarte und JSON-LD in einem Zug bedient. Bei
# drei getrennten Aufrufstellen wuerde eine davon vergessen - und die
# Meta-Beschreibung naennte dann einen anderen Preis als der Text darunter.
MARKEN = {
    "{{PREIS_ISFP}}":      "isfp_ab",
    "{{PREIS_FOERDER}}":   "foerderung_max",
    "{{PREIS_EIGEN}}":     "eigen_ab",
    "{{PREIS_AUSWEIS_V}}": "ausweis_verbrauch",
    "{{PREIS_AUSWEIS_B}}": "ausweis_bedarf",
    "{{PREIS_ABGLEICH}}":  "abgleich",
}


def fuell(seite):
    P = preise()
    for marke, schluessel in MARKEN.items():
        seite = seite.replace(marke, P[schluessel])
    rest = re.search(r"\{\{[A-Z_]+\}\}", seite)
    if rest:
        raise SystemExit(f"Unbekannter Platzhalter im Artikeltext: {rest.group(0)}")
    return seite


def kopfbereich(aktuell=None):
    """Kopfzeile, Handy-Menue und Aktionsleiste aus index.html.

    Der Bereich endet mit der Aktionsleiste, nicht erst bei <main>: dazwischen
    stehen in index.html die gemeinsamen SVG-Definitionen, die hier nichts zu
    suchen haben."""
    v = _start()
    i = v.find('<header class="site-header"')
    mb = v.find('<div class="mobile-bar">', i)
    if i < 0 or mb < 0:
        raise SystemExit("Kopfbereich nicht in index.html gefunden")
    k = _absolut(v[i:v.find("</div>", mb) + len("</div>")])
    if aktuell:
        k = k.replace(f'<a href="{aktuell}">', f'<a href="{aktuell}" aria-current="page">')
    return k


def fussbereich(aktuell=None):
    """Fussbereich aus index.html."""
    f = _absolut(_schnitt(r'(<footer class="site-footer">.*?</footer>)', "Fussbereich"))
    if aktuell:
        f = f.replace(f'<a href="{aktuell}">', f'<a href="{aktuell}" aria-current="page">')
    return f


RATGEBER_CSS = """

/* ==== Ratgeber ==== */
.rg-kopf{padding:30px 0 40px}
.rg-meta{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:18px;font-size:.84rem;color:var(--muted)}
.rg-meta span{display:inline-flex;align-items:center;gap:7px}
.rg-inhalt{display:grid;grid-template-columns:1fr 320px;gap:56px;align-items:start;padding-bottom:76px}
/* Ohne min-width:0 waechst die 1fr-Spalte auf die Mindestbreite der Tabelle
   (min-width:420px) - auf dem Handy scrollt dann die ganze Seite seitwaerts. */
.rg-inhalt>*{min-width:0}
.rg-text{max-width:70ch}
.rg-text h2{font-size:clamp(1.5rem,2.6vw,2rem);margin:46px 0 14px}
.rg-text h3{font-size:1.16rem;margin:30px 0 10px}
.rg-text p{margin-bottom:15px;color:var(--ink-2)}
.rg-text ul{margin:0 0 18px}
/* Punkt absolut positioniert, NICHT als Flexcontainer: In einem Flex-li
   werden <strong> und der restliche Text zu getrennten Spalten - die fette
   Einleitung ("Beheizter Keller:") brach dann schmal um und der Satz stand
   daneben statt dahinter. Mit padding-left fliesst alles normal. */
.rg-text ul li{position:relative;padding-left:20px;margin-bottom:10px;color:var(--ink-2);hyphens:auto}
.rg-text ul li::before{content:"";position:absolute;left:2px;top:11px;width:7px;height:7px;border-radius:50%;background:var(--amber)}
.rg-text ol{counter-reset:rg;list-style:none;margin:0 0 18px}
.rg-text ol li{counter-increment:rg;position:relative;padding-left:44px;margin-bottom:14px;color:var(--ink-2)}
.rg-text ol li::before{content:counter(rg);position:absolute;left:0;top:-1px;width:30px;height:30px;border-radius:50%;background:var(--forest-soft);color:var(--forest);display:grid;place-items:center;font-weight:700;font-size:.92rem}
.rg-text strong{color:var(--ink)}
.rg-text a{color:var(--amber-deep);font-weight:600;text-decoration:underline;text-underline-offset:3px}
.rg-kasten{background:var(--forest-soft);border-radius:var(--radius-sm);padding:20px 24px;margin:26px 0;color:var(--forest);font-size:.96rem}
.rg-kasten b{display:block;font-size:.74rem;letter-spacing:.11em;text-transform:uppercase;margin-bottom:7px;opacity:.75}
.rg-warnung{background:var(--amber-soft);border-left:4px solid var(--amber);border-radius:var(--radius-sm);padding:18px 22px;margin:24px 0;font-size:.94rem;color:#6B5638}
.rg-warnung b{color:#5A4526}
.rg-tabelle{overflow-x:auto;margin:22px 0}
.rg-tabelle table{border-collapse:collapse;width:100%;font-size:.92rem;min-width:420px}
.rg-tabelle th,.rg-tabelle td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line-soft)}
.rg-tabelle th{font-size:.74rem;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:700}
.rg-tabelle td{color:var(--ink-2)}
.rg-tabelle td:first-child{color:var(--ink);font-weight:500}
/* Artikelbild - Foto aus bilder/ (Pexels, selbst gehostet). In der
   Karte auf feste Hoehe beschnitten, damit alle Karten gleich hoch
   beginnen; object-fit haelt dabei den Bildausschnitt. */
.rg-bild{display:block;width:100%;height:auto;border-radius:var(--radius);margin:0 0 34px}
.rg-eintrag .rg-bild{margin:-28px -30px 18px;width:calc(100% + 60px);height:190px;object-fit:cover;border-radius:var(--radius) var(--radius) 0 0}
.rg-hinweis{margin-top:34px;padding-top:18px;border-top:1px solid var(--line-soft);font-size:.85rem;color:var(--muted)}
.rg-spalte{position:sticky;top:104px;display:grid;gap:18px}
.rg-karte{background:var(--white);border:1px solid var(--line-soft);border-radius:var(--radius);box-shadow:var(--shadow-sm);padding:24px 26px}
.rg-karte h3{margin:0 0 12px;font-size:1.05rem}
.rg-karte p{font-size:.89rem;color:var(--ink-2);margin-bottom:16px}
.rg-karte .btn{width:100%}
.rg-karte-kontakt{background:linear-gradient(165deg,var(--forest),#22392E);border-color:transparent;color:#F4EFE6}
.rg-karte-kontakt h3{color:#FBF8F2}
.rg-karte-kontakt p{color:rgba(244,239,230,.82)}
.rg-tel{display:flex;align-items:center;gap:10px;font-size:1.1rem;font-weight:700;color:#FBF8F2;margin-bottom:6px}
.rg-tel svg{width:19px;height:19px;stroke:#E8B87A;fill:none;stroke-width:1.9;flex:none}
.rg-mehr{display:grid;gap:2px}
.rg-mehr a{display:block;padding:9px 0;font-size:.9rem;color:var(--ink-2);border-bottom:1px solid var(--line-soft);transition:color .25s}
.rg-mehr a:last-child{border-bottom:none}
.rg-mehr a:hover{color:var(--amber-deep)}

/* Brotkrumen - stehen nicht im CSS der Startseite, dort gibt es sie nicht */
/* WICHTIG: Der Seitenkopf ist position:fixed und rund 77px hoch. Die
   Startseite loest das ueber das grosse Hero-Padding - die Ratgeber fangen
   aber direkt mit den Brotkrumen an, deshalb muss der Abstand HIER stehen,
   sonst liegen Brotkrumen und Ueberschrift unter dem festen Kopf. */
.krumen{padding:calc(var(--kopf) + 31px) 0 0;font-size:.82rem;color:var(--muted)}
.krumen ol{display:flex;flex-wrap:wrap;gap:8px;list-style:none}
.krumen li::after{content:"\\203A";margin-left:8px;color:var(--line)}
.krumen li:last-child::after{content:""}
.krumen a:hover{color:var(--amber-deep);text-decoration:underline;text-underline-offset:3px}

/* Das CTA-Band ist auf jeder Ratgeberseite das letzte Element - 50px
   Abstand zum Fussbereich, einheitlich mit allen anderen Seiten. */
main .cta-band{margin-bottom:50px}

/* Uebersichtsseite */
.rg-liste{display:grid;grid-template-columns:repeat(2,1fr);gap:22px;padding-bottom:70px}
.rg-eintrag{
  background:var(--white);border:1px solid var(--line-soft);border-radius:var(--radius);
  box-shadow:var(--shadow-sm);padding:28px 30px;display:flex;flex-direction:column;
  transition:transform .45s var(--ease),box-shadow .45s var(--ease),border-color .45s;
}
.rg-eintrag:hover{transform:translateY(-5px);box-shadow:var(--shadow-md);border-color:var(--line)}
.rg-eintrag .rubrik{display:block;font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--amber-deep);margin-bottom:11px}
.rg-eintrag h2{font-size:1.24rem;margin-bottom:10px;line-height:1.3}
.rg-eintrag h2 a:hover{color:var(--amber-deep)}
.rg-eintrag p{font-size:.92rem;color:var(--ink-2);margin-bottom:18px}
.rg-eintrag .weiter{margin-top:auto;font-size:.9rem;font-weight:600;color:var(--amber-deep);display:inline-flex;align-items:center;gap:7px}
.rg-eintrag:hover .weiter{gap:11px}

@media (max-width:1000px){ .rg-inhalt{grid-template-columns:1fr;gap:40px} .rg-spalte{position:static} }
@media (max-width:760px){ .rg-liste{grid-template-columns:1fr} }
"""

def stil():
    return _schnitt(r"<style>\n(.*?)\n</style>", "CSS") + RATGEBER_CSS

def vorschaubild(bild_tag=None):
    """og:image-Block. Ein Artikel nimmt sein eigenes Foto - das ist beim
    Teilen in WhatsApp aussagekraeftiger als eine immer gleiche Kachel.
    Die Uebersicht faellt auf vorschau.jpg zurueck."""
    quelle, breite, hoehe = "vorschau.jpg", 1200, 630
    if bild_tag:
        m = re.search(r'src="([^"]+)"[^>]*width="(\d+)"[^>]*height="(\d+)"', bild_tag)
        if m:
            quelle, breite, hoehe = m.group(1), m.group(2), m.group(3)
    return (f'<meta property="og:image" content="{DOMAIN}/{quelle}">\n'
            f'<meta property="og:image:width" content="{breite}">\n'
            f'<meta property="og:image:height" content="{hoehe}">\n'
            f'<meta property="og:image:alt" content="EBA Energieberater Albdonau, '
            f'Ulm und Alb-Donau-Kreis">')


def kopf(titel, beschreibung, datei, aktiv_ratgeber=True, bild=None):
    """Gemeinsamer Seitenkopf."""
    vorschau = vorschaubild(bild)
    return f"""<!DOCTYPE html>
<!--
  ============================================================================
  RATGEBER – ERZEUGT, NICHT VON HAND BEARBEITEN!
  Änderungen in ratgeber-erzeugen.py vornehmen und das Skript erneut laufen
  lassen, sonst sind sie beim nächsten Durchlauf wieder weg.
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
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%232E4A3C'/%3E%3Cg transform='translate(12.4,3.7) scale(0.78)'%3E%3Cpath d='M25 3 2 28 2 63 30 63 30 70 48 70 48 30Z' fill='none' stroke='%23FDFBF7' stroke-width='4.6' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M24.5 36C27.5 44 26.5 52 19 57 12 61.5 6.5 57.5 7.5 51 8.5 44 16 39 24.5 36ZM23.5 38.5C20 44 16 49 11.5 54.5 15.5 49.5 19 44.5 22.8 38.2Z' fill='%23E8B87A' fill-rule='evenodd'/%3E%3C/g%3E%3C/svg%3E">
<meta property="og:type" content="article">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="EBA Energieberater Albdonau">
<meta property="og:title" content="{titel}">
<meta property="og:description" content="{beschreibung}">
<meta property="og:url" content="{DOMAIN}/{datei}">
{vorschau}
<meta name="twitter:card" content="summary_large_image">
<style>
{stil()}
</style>
</head>
<body>

<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>

{kopfbereich('ratgeber.html')}
"""

FUSS = f"""
{fussbereich()}

<script>
'use strict';
(function(){{
  /* Kopfzeile beim Scrollen einfaerben. Ohne diesen Handler bleibt der fixe
     Kopf durchsichtig und der Artikeltext schiebt sich sichtbar durch die
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

  /* Scroll-Reveal - ohne diesen Teil bleiben alle .reveal-Elemente
     dauerhaft unsichtbar (opacity:0). Genau das ist bei den Ortsseiten
     einmal passiert. */
  var reveals = document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){{
    var io = new IntersectionObserver(function(entries){{
      entries.forEach(function(e){{
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
}})();
</script>

</body>
</html>
"""

# ---------------------------------------------------------------------------
# ARTIKEL
# Reihenfolge = Reihenfolge auf der Uebersichtsseite.
# Der Fliesstext ist bewusst hier und nicht in eigenen Dateien: so bleibt
# alles, was zu einem Artikel gehoert, an einer Stelle.
# 'bild': Foto aus bilder/ (Pexels, selbst gehostet - Quellen und Lizenz
# in bilder/LIZENZ.txt). loading=lazy, weil das Bild unter dem ersten
# Bildschirminhalt liegt; width/height verhindern Springen beim Laden.
# ---------------------------------------------------------------------------
ARTIKEL = [
{
 # Steht bewusst an erster Stelle: seitenspalte() zeigt auf jeder Artikelseite
 # die ersten drei Eintraege der Liste. Damit verlinkt jeder Beitrag auf die
 # Seite, die die kommerziellste Suchanfrage bedient.
 "datei": "ratgeber-energieberatung-kosten.html",
 "bild": """<img class="rg-bild" src="bilder/ratgeber-energieberatung-kosten.jpg" width="1200" height="800"
           alt="Grundriss, Kostenkurve und Bauhelm auf einem Schreibtisch"
           loading="lazy" decoding="async">""",
 "rubrik": "Kosten & Honorar",
 "titel": "Was kostet eine Energieberatung?",
 "seitentitel": "Was kostet eine Energieberatung? Preise und Förderung",
 "beschreibung": "Was eine Energieberatung für ein Einfamilienhaus kostet, wie viel die "
                 "BAFA davon übernimmt und woran Sie ein unseriöses Angebot erkennen.",
 "anriss": "Die häufigste Frage im ersten Telefonat – und die, auf die viele Anbieter "
           "keine klare Antwort geben. Hier stehen die Zahlen, bevor Sie anrufen.",
 "dauer": "6 Minuten",
 "inhalt": """
      <p>
        Wer nach den Kosten einer Energieberatung sucht, findet meist Spannen von
        „500 bis 2.500 €“ und danach ein Kontaktformular. Das hilft niemandem bei der
        Entscheidung. Für ein normales Ein- oder Zweifamilienhaus lässt sich der Preis
        vor dem ersten Termin benennen – und genau so handhaben wir es.
      </p>

      <div class="rg-kasten">
        <b>Das Wichtigste in einem Satz</b>
        Ein individueller Sanierungsfahrplan kostet bei uns ab {{PREIS_ISFP}} €
        inklusive Umsatzsteuer. Die BAFA-Förderung übernimmt 50 Prozent, höchstens
        {{PREIS_FOERDER}} € – Ihr Eigenanteil liegt damit ab {{PREIS_EIGEN}} €, sofern
        der Zuschuss bewilligt wird.
      </div>

      <h2>Welche Leistung Sie für welchen Betrag bekommen</h2>
      <p>
        „Energieberatung“ ist kein geschützter Begriff für eine einzelne Leistung.
        Dahinter stecken sehr verschiedene Arbeiten, die entsprechend verschieden viel
        kosten. Diese vier fragen Eigentümer am häufigsten nach:
      </p>

      <div class="rg-tabelle">
        <table>
          <thead>
            <tr><th>Leistung</th><th>Was dabei entsteht</th><th>Preis</th></tr>
          </thead>
          <tbody>
            <tr>
              <td>Erstgespräch</td>
              <td>Rund 20 Minuten am Telefon: Ist eine Beratung bei Ihrem Haus
                  überhaupt sinnvoll, und welche?</td>
              <td>kostenlos</td>
            </tr>
            <tr>
              <td>Sanierungsfahrplan (iSFP)</td>
              <td>Aufnahme vor Ort, Berechnung, schriftlicher Fahrplan mit
                  Maßnahmenreihenfolge, Erläuterungsgespräch</td>
              <td>ab {{PREIS_ISFP}} €</td>
            </tr>
            <tr>
              <td><a href="energieausweis-ulm.html">Energieausweis</a></td>
              <td>Bedarfs- oder Verbrauchsausweis für Verkauf oder Vermietung</td>
              <td>Verbrauch ab {{PREIS_AUSWEIS_V}} €, Bedarf ab {{PREIS_AUSWEIS_B}} €</td>
            </tr>
            <tr>
              <td><a href="hydraulischer-abgleich-ulm.html">Hydraulischer Abgleich</a></td>
              <td>Raumweise Heizlastberechnung nach Verfahren B, Einstellung,
                  Dokumentation für die Förderung</td>
              <td>ab {{PREIS_ABGLEICH}} €</td>
            </tr>
            <tr>
              <td>Zweitmeinung</td>
              <td>Prüfung eines vorliegenden Handwerker- oder Heizungsangebots</td>
              <td>Festpreis nach kurzem Telefonat</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>
        Alle genannten Beträge sind Startpreise für ein Ein- oder Zweifamilienhaus,
        inklusive Umsatzsteuer. Warum bei der Zweitmeinung trotzdem „nach Telefonat“
        steht: Ein einzelnes Heizungsangebot zu prüfen ist eine andere Arbeit als ein
        Leistungsverzeichnis über vier Gewerke. Eine Hausnummer, die für beides gilt,
        wäre für den einen zu teuer und für den anderen erfunden.
      </p>

      <h2>Der Sanierungsfahrplan: Preis, Förderung, Eigenanteil</h2>
      <p>
        Der individuelle Sanierungsfahrplan ist die Leistung, nach der die meisten
        suchen, wenn sie „Energieberatung“ sagen. Er ist bundesweit gefördert, und die
        Förderung ist der Grund, warum der Eigenanteil deutlich niedriger ausfällt als
        das Honorar:
      </p>
      <ul>
        <li><strong>Honorar ab {{PREIS_ISFP}} €</strong> inklusive Umsatzsteuer – ein
        Festpreis, den Sie vor der Beauftragung schriftlich bekommen.</li>
        <li><strong>Abzüglich bis zu {{PREIS_FOERDER}} € Zuschuss</strong> vom BAFA:
        50 Prozent der förderfähigen Kosten, gedeckelt auf diesen Betrag.</li>
        <li><strong>Bleibt ein Eigenanteil ab {{PREIS_EIGEN}} €</strong>, sofern der
        Antrag bewilligt wird.</li>
      </ul>
      <p>
        Den Antrag bereiten wir vor; gestellt wird er von Ihnen als Eigentümer. Das ist
        keine Schikane, sondern Vorgabe des Förderprogramms – Antragsteller und
        Zuschussempfänger müssen dieselbe Person sein.
      </p>

      <h3>Wie sich das zum Markt verhält</h3>
      <p>
        Damit Sie die Zahl einordnen können: Marktübersichten nennen für den
        Sanierungsfahrplan eines Einfamilienhauses derzeit Honorare zwischen etwa
        1.300 und 2.100 €, in Einzelfällen bis 2.500 €. Der Eigenanteil nach Abzug
        der Förderung liegt üblicherweise bei 940 bis 1.350 €.
      </p>
      <div class="rg-tabelle">
        <table>
          <thead>
            <tr><th></th><th>Marktüblich</th><th>Bei uns</th></tr>
          </thead>
          <tbody>
            <tr><td>Honorar Sanierungsfahrplan</td>
                <td>ca. 1.300 – 2.100 €</td><td>ab {{PREIS_ISFP}} €</td></tr>
            <tr><td>Eigenanteil nach Förderung</td>
                <td>ca. 940 – 1.350 €</td><td>ab {{PREIS_EIGEN}} €</td></tr>
          </tbody>
        </table>
      </div>
      <p>
        Wir liegen damit am unteren Rand der marktüblichen Spanne. Das hat einen
        einfachen Grund und keinen Haken: Ein Einzelbüro ohne Vertrieb, ohne
        Franchise-Gebühr und ohne Provisionen hat eine andere Kostenstruktur als eine
        bundesweite Plattform. Wo Ihr Gebäude mehr Aufwand macht – viele Wohneinheiten,
        fehlende Unterlagen, Denkmalschutz –, sagen wir das vorher und nennen einen
        entsprechend höheren Festpreis.
      </p>

      <div class="rg-warnung">
        <b>Reihenfolge beachten:</b> Der Förderantrag muss gestellt sein, bevor der
        Beratungsvertrag geschlossen wird. Das ist derselbe Fehler, der später bei
        Handwerkeraufträgen die meisten Zuschüsse kostet – nur eine Stufe früher.
      </div>

      <h2>Warum es keinen Pauschalpreis für jedes Haus gibt</h2>
      <p>
        Vier Dinge treiben den Aufwand, und damit den Preis, nach oben:
      </p>
      <ol>
        <li><strong>Größe und Zahl der Wohneinheiten.</strong> Jede Einheit bedeutet
        eigene Nutzungsprofile und eigene Heizflächen.</li>
        <li><strong>Zustand der Unterlagen.</strong> Liegt eine Baubeschreibung vor,
        geht die Aufnahme zügig. Fehlt sie, wird vor Ort gemessen und aus der Bauweise
        rückgeschlossen.</li>
        <li><strong>Anbauten und Umbauten.</strong> Ein Haus, an dem in vier Jahrzehnten
        dreimal etwas verändert wurde, ist rechnerisch vier Gebäude.</li>
        <li><strong>Denkmalschutz.</strong> Er schließt Maßnahmen aus und verlangt
        Alternativen, die einzeln geprüft werden müssen.</li>
      </ol>
      <p>
        Deshalb steht auf unseren Seiten „ab“ und keine Spanne bis 2.500 €. Nach einem
        kurzen Telefonat wissen wir, in welchem Fall Ihr Haus liegt, und nennen einen
        festen Betrag. Erst danach entscheiden Sie.
      </p>

      <h2>Was die Beratung auf der anderen Seite einbringt</h2>
      <p>
        Eine Beratung, die nur beschreibt, was Sie ohnehin ahnen, ist ihr Geld nicht
        wert. Rechnen lässt sie sich an drei Stellen:
      </p>
      <ul>
        <li><strong>Der iSFP-Bonus.</strong> Wer den Fahrplan hat, bekommt für jede
        spätere Maßnahme an der Gebäudehülle 5 Prozentpunkte mehr Förderung, und die
        förderfähigen Kosten verdoppeln sich. Bei einer Fassadendämmung über 40.000 €
        sind das rund 2.000 € zusätzlich – mehr, als der Fahrplan gekostet hat.</li>
        <li><strong>Die Reihenfolge.</strong> Wer die Heizung vor der Dämmung erneuert,
        kauft in aller Regel eine zu große Anlage. Die Differenz liegt oft im
        vierstelligen Bereich, und sie fällt bei jedem Betriebsjahr erneut an.</li>
        <li><strong>Die nicht gemachte Maßnahme.</strong> Der häufigste Nutzen unserer
        Berechnungen ist die Erkenntnis, dass sich eine geplante Investition am
        konkreten Haus <em>nicht</em> rechnet.</li>
      </ul>
      <p>
        Wie groß der Effekt bei Ihrem Gebäude ausfällt, hängt von Baujahr, Bauweise und
        Nutzung ab. Eine erste Einschätzung liefert der
        <a href="sanierungsrechner.html">Sanierungsrechner</a> in wenigen Minuten,
        kostenlos und ohne Anmeldung.
      </p>

      <h2>Vorsicht bei „kostenloser Energieberatung“</h2>
      <p>
        Beratung ist Arbeitszeit. Wenn sie nichts kostet, wird sie an anderer Stelle
        bezahlt – meistens durch das Produkt, das am Ende empfohlen wird. Drei Fragen
        klären das schnell:
      </p>
      <ul>
        <li>Verkauft der Anbieter auch Heizungen, Dämmstoffe oder Photovoltaik?</li>
        <li>Steht er in der
        <a href="https://www.energie-effizienz-experten.de" target="_blank" rel="noopener">
        Energie-Effizienz-Expertenliste des Bundes</a>? Ohne diesen Eintrag ist der
        Fahrplan nicht förderfähig.</li>
        <li>Bekommen Sie ein schriftliches Festpreisangebot, bevor jemand ins Haus
        kommt?</li>
      </ul>
      <p>
        Kostenlos ist bei uns das Erstgespräch – weil es kurz ist und weil es beiden
        Seiten die Fehlbeauftragung erspart. Alles, was danach kommt, hat einen Preis,
        den Sie vorher kennen. Die Konditionen im Überblick stehen unter
        <a href="index.html#preise">Preise</a>, die Leistungsbeschreibung auf der Seite
        <a href="sanierungsfahrplan.html#kosten">Sanierungsfahrplan</a>.
      </p>
 """,
 "faq": [
   ("Was kostet eine Energieberatung für ein Einfamilienhaus?",
    "Ein individueller Sanierungsfahrplan für ein Ein- oder Zweifamilienhaus beginnt bei "
    "{{PREIS_ISFP}} € inklusive Umsatzsteuer. Die BAFA-Förderung übernimmt 50 Prozent, "
    "höchstens {{PREIS_FOERDER}} €, sodass ein Eigenanteil ab {{PREIS_EIGEN}} € bleibt, "
    "sofern der Zuschuss bewilligt wird. Den genauen Festpreis nennen wir nach einem "
    "kurzen Telefonat."),
   ("Wird die Energieberatung gefördert?",
    "Ja. Das BAFA fördert den individuellen Sanierungsfahrplan für Ein- und "
    "Zweifamilienhäuser mit 50 Prozent der förderfähigen Kosten, höchstens "
    "{{PREIS_FOERDER}} €. Voraussetzung ist, dass der Berater in der "
    "Energie-Effizienz-Expertenliste des Bundes eingetragen ist und der Antrag vor "
    "Vertragsschluss gestellt wird."),
   ("Lohnt sich eine Energieberatung bei einem kleinen Haus?",
    "Häufig gerade dann. Je kleiner das Budget, desto teurer ist eine falsch gewählte "
    "erste Maßnahme. Ob sich der Aufwand bei Ihrem Gebäude rechnet, lässt sich im "
    "kostenlosen Erstgespräch in etwa 20 Minuten klären – wenn nicht, sagen wir das."),
 ],
},
{
 "datei": "ratgeber-heizung-tauschen-pflicht.html",
 "bild": """<img class="rg-bild" src="bilder/ratgeber-heizung.jpg" width="1200" height="797"
           alt="Hand an einem Thermostatventil eines Heizkörpers"
           loading="lazy" decoding="async">""",
 "rubrik": "Gesetz & Pflichten",
 "titel": "Heizung tauschen: Was gilt wirklich?",
 "seitentitel": "Heizung tauschen: Pflicht, Fristen, Ausnahmen | Ratgeber",
 "beschreibung": "Muss die alte Öl- oder Gasheizung raus? Was das Gebäudeenergiegesetz "
                 "wirklich verlangt, welche Fristen gelten und wann Sie nichts tun müssen.",
 "anriss": "Die verbreitetste Sorge unter Eigentümern – und in den meisten Fällen "
           "unbegründet. Was das Gesetz verlangt, welche Ausnahmen greifen und wann "
           "ein Austausch trotzdem sinnvoll ist.",
 "dauer": "7 Minuten",
 "inhalt": """
      <p>
        Kaum ein Thema verunsichert Eigentümer so sehr. Die Kurzfassung vorweg:
        <strong>Eine funktionierende Heizung dürfen Sie weiter betreiben und
        reparieren.</strong> Niemand kommt und lässt sie ausbauen. Die Regeln greifen
        erst, wenn ohnehin etwas passiert – oder wenn die Anlage sehr alt ist.
      </p>

      <div class="rg-kasten">
        <b>Das Wichtigste in einem Satz</b>
        Solange Ihre Heizung läuft und reparierbar ist, besteht kein Zwang zum
        Austausch. Die relevanten Fristen betreffen Kessel jenseits der 30 Jahre und
        den Fall, dass eine Anlage endgültig ausfällt.
      </div>

      <h2>Wann Sie tatsächlich handeln müssen</h2>
      <p>
        Es gibt im Wesentlichen drei Situationen, in denen aus einer Möglichkeit eine
        Pflicht wird:
      </p>
      <ol>
        <li><strong>Die Heizung ist irreparabel defekt.</strong> Dann greifen beim
        Ersatz die aktuellen Anforderungen – allerdings mit Übergangsfristen, in denen
        zunächst auch eine einfache Lösung eingebaut werden darf.</li>
        <li><strong>Der Kessel ist älter als 30 Jahre</strong> und ein
        Konstanttemperaturkessel. Niedertemperatur- und Brennwertkessel sind von
        dieser Austauschpflicht ausgenommen.</li>
        <li><strong>Sie haben das Haus geerbt oder gekauft.</strong> Dann gelten
        bestimmte Nachrüstpflichten innerhalb einer Frist nach dem
        Eigentümerwechsel.</li>
      </ol>
      <p>
        Selbst genutzte Ein- und Zweifamilienhäuser, in denen die Eigentümer schon
        lange wohnen, sind von mehreren dieser Pflichten ausgenommen. Genau deshalb
        lohnt der Blick auf den Einzelfall statt auf die Schlagzeile.
      </p>

      <div class="rg-warnung">
        <b>Zur Rechtslage:</b> Das Gebäudeenergiegesetz soll durch ein
        Gebäudemodernisierungsgesetz abgelöst werden. Solange der
        Gesetzgebungsprozess läuft, gilt weiter das bestehende Recht. Wer jetzt
        entscheidet, sollte beide Stände kennen – die wirtschaftlich beste Lösung ist
        allerdings meist in beiden dieselbe.
      </div>

      <h2>Warum die Frist selten das eigentliche Argument ist</h2>
      <p>
        In der Praxis ist nicht das Gesetz der Grund für einen Austausch, sondern die
        Rechnung. Ein 25 Jahre alter Standardkessel arbeitet mit einem Wirkungsgrad,
        der deutlich unter dem heute Möglichen liegt. Das kostet jedes Jahr Geld –
        unabhängig davon, ob jemand den Austausch verlangt.
      </p>
      <p>
        Umgekehrt gilt: Eine neue Heizung in ein ungedämmtes Haus zu setzen, ist fast
        immer die falsche Reihenfolge. Die Anlage wird dann auf den hohen Wärmebedarf
        ausgelegt, läuft zwanzig Jahre lang im falschen Betriebspunkt und ist nach
        einer späteren Dämmung überdimensioniert. Mehr dazu im Artikel
        <a href="ratgeber-reihenfolge-sanierung.html">In welcher Reihenfolge
        sanieren?</a>
      </p>

      <h2>Was der Austausch kostet – und was davon zurückkommt</h2>
      <p>
        Für eine Luft-Wasser-Wärmepumpe im Bestand sind je nach Gebäude und Aufwand
        etwa 27.000 bis 40.000 Euro realistisch, inklusive Speicher, Anpassung der
        Heizflächen und Inbetriebnahme. Davon geht die Förderung ab.
      </p>
      <div class="rg-tabelle">
        <table>
          <thead><tr><th>Baustein</th><th>Satz</th><th>Bedingung</th></tr></thead>
          <tbody>
            <tr><td>Grundförderung</td><td>30 %</td><td>für alle Antragsteller</td></tr>
            <tr><td>Klimageschwindigkeitsbonus</td><td>20 %</td><td>Austausch einer alten Öl- oder Gasheizung</td></tr>
            <tr><td>Einkommensbonus</td><td>30 %</td><td>selbstgenutzt, unterhalb der Einkommensgrenze</td></tr>
            <tr><td>Effizienzbonus</td><td>5 %</td><td>bestimmte Wärmepumpen</td></tr>
          </tbody>
        </table>
      </div>
      <p>
        Die Boni sind kombinierbar, der Gesamtsatz ist aber nach oben gedeckelt, und
        auch die förderfähigen Kosten sind begrenzt. Im Regelfall – Austausch einer
        alten Öl- oder Gasheizung im selbst bewohnten Haus – landet man bei rund
        50 %. Rechnen Sie Ihren Fall im
        <a href="sanierungsrechner.html">Sanierungsrechner</a> durch, dort sind die
        aktuellen Sätze und Deckel hinterlegt.
      </p>

      <h2>Was wir empfehlen</h2>
      <ul>
        <li>Keine Panikentscheidung, solange die Anlage läuft</li>
        <li>Vor dem Heizungstausch die Gebäudehülle prüfen – sonst wird die neue Anlage zu groß</li>
        <li>Den Förderantrag stellen, <strong>bevor</strong> der Handwerkerauftrag vergeben wird</li>
        <li>Bei sehr alten Kesseln das Ausfallrisiko einkalkulieren: Wer erst im Januar sucht, entscheidet unter Druck und zahlt drauf</li>
      </ul>
 """,
 "faq": [
   ("Muss ich meine funktionierende Gasheizung austauschen?",
    "Nein. Eine funktionierende Heizung darf weiter betrieben und repariert werden. "
    "Eine Austauschpflicht kann bei Konstanttemperaturkesseln greifen, die älter als "
    "30 Jahre sind, sowie beim irreparablen Ausfall der Anlage."),
   ("Wie hoch ist die Förderung für eine Wärmepumpe?",
    "Die Grundförderung liegt bei 30 Prozent. Mit Klimageschwindigkeitsbonus, "
    "Einkommensbonus und Effizienzbonus sind höhere Sätze möglich; der Gesamtsatz und "
    "die förderfähigen Kosten sind gedeckelt. Im Regelfall werden rund 50 Prozent "
    "erreicht."),
   ("Wann muss der Förderantrag gestellt werden?",
    "Vor der Vergabe des Handwerkerauftrags. Wer erst beauftragt und dann den Antrag "
    "stellt, verliert den Zuschuss."),
 ],
},
{
 # Nennt bewusst KEINE eigenen Foerdersaetze. Die stehen im Heizungs-Artikel
 # und im Foerderabschnitt der Startseite - eine dritte Fundstelle waere die
 # dritte Stelle, die bei der naechsten Richtlinienaenderung vergessen wird.
 "datei": "ratgeber-waermepumpe-altbau.html",
 "bild": """<img class="rg-bild" src="bilder/ratgeber-waermepumpe-altbau.jpg" width="1200" height="800"
           alt="Alter Gussheizkörper unter einem Fenster in einem Altbau"
           loading="lazy" decoding="async">""",
 "rubrik": "Heizung",
 "titel": "Wärmepumpe im Altbau: funktioniert das?",
 "seitentitel": "Wärmepumpe im Altbau: Wann sie wirklich funktioniert",
 "beschreibung": "Braucht eine Wärmepumpe Fußbodenheizung und gedämmte Wände? Der "
                 "Praxistest, den Sie in einer Heizperiode selbst machen können.",
 "anriss": "„Im Altbau geht das nicht“ ist genauso falsch wie „geht überall“. "
           "Es hängt an einer einzigen Zahl – und die können Sie an Ihrer eigenen "
           "Heizung ablesen.",
 "dauer": "7 Minuten",
 "inhalt": """
      <p>
        Zu kaum einer Frage kursieren so viele pauschale Antworten. Die einen sagen,
        eine Wärmepumpe brauche zwingend Fußbodenheizung und gedämmte Wände. Die
        anderen behaupten, sie laufe in jedem Gebäude. Beides ist falsch. Ob es
        funktioniert, entscheidet <strong>eine</strong> Größe – und die lässt sich in
        Ihrem Haus messen, statt sie zu vermuten.
      </p>

      <div class="rg-kasten">
        <b>Das Wichtigste in einem Satz</b>
        Nicht das Baujahr entscheidet, sondern die Vorlauftemperatur: Kommt Ihr Haus am
        kältesten Tag mit etwa 50 bis 55 Grad aus, ist eine Wärmepumpe technisch
        unproblematisch – ganz gleich, ob 1968 oder 2008 gebaut.
      </div>

      <h2>Die eine Zahl, auf die es ankommt</h2>
      <p>
        Eine Wärmepumpe holt Wärme aus der Außenluft oder dem Erdreich und hebt sie auf
        Heiztemperatur. Je höher sie heben muss, desto mehr Strom kostet das. Der
        Zusammenhang ist recht gleichmäßig: <strong>Jedes Grad weniger
        Vorlauftemperatur verbessert die Effizienz um grob 2,5 Prozent.</strong>
      </p>
      <p>
        Zwischen 55 und 35 Grad liegen damit rund 50 Prozent Unterschied im
        Stromverbrauch. Das ist der ganze Grund, warum bei Wärmepumpen ständig von
        Fußbodenheizung die Rede ist: Sie arbeitet mit niedriger Temperatur. Sie ist
        aber nur ein Weg dorthin – nicht der einzige.
      </p>

      <h2>Der Test, den Sie selbst machen können</h2>
      <p>
        Sie brauchen dafür keinen Fachmann und kein Messgerät, sondern einen kalten Tag
        und etwas Geduld:
      </p>
      <ol>
        <li>Warten Sie eine Frostperiode ab – idealerweise unter minus fünf Grad.</li>
        <li>Stellen Sie die Heizkurve Ihres Kessels so ein, dass die Vorlauftemperatur
        <strong>55 Grad nicht überschreitet</strong>. Die Einstellung finden Sie am
        Regler der Heizung; ein Heizungsbauer macht das in fünf Minuten.</li>
        <li>Öffnen Sie alle Thermostatventile vollständig.</li>
        <li>Beobachten Sie zwei bis drei Tage: Werden alle Räume warm?</li>
      </ol>
      <p>
        Wird es überall behaglich, kann eine Wärmepumpe Ihr Haus heizen. Bleibt genau
        ein Raum kühl, ist meist dieser eine Heizkörper zu klein – ein Austausch kostet
        einige Hundert Euro und nicht die Sanierung des ganzen Hauses. Bleiben mehrere
        Räume kalt, sollten Dämmung und Heizflächen vor der Heizung an die Reihe kommen.
      </p>

      <div class="rg-warnung">
        <b>Wichtig:</b> Der Test taugt nur bei echter Kälte. Bei zehn Grad
        Außentemperatur schafft praktisch jedes Haus niedrige Vorlauftemperaturen – das
        beweist nichts über den Januar.
      </div>

      <h2>Große Heizkörper schlagen teure Dämmung</h2>
      <p>
        Der häufigste Denkfehler: Um niedrige Vorlauftemperaturen zu erreichen, müsse
        man den Wärmebedarf senken. Man kann stattdessen die Fläche vergrößern, über die
        die Wärme abgegeben wird. Das ist meist erheblich billiger.
      </p>
      <ul>
        <li><strong>Alte Gussheizkörper sind oft ein Vorteil.</strong> Sie wurden großzügig
        ausgelegt und haben viel Oberfläche – genau das, was eine niedrige
        Vorlauftemperatur braucht.</li>
        <li><strong>Ein größerer Heizkörper im kritischen Raum</strong> kostet einige
        Hundert Euro. Eine Fassadendämmung, die dieselbe Absenkung bringt, kostet ein
        Vielfaches.</li>
        <li><strong>Der hydraulische Abgleich</strong> verteilt das vorhandene Wasser
        richtig. Ohne ihn braucht das ganze Haus die Temperatur, die der schlechteste
        Heizkörper verlangt.</li>
      </ul>
      <p>
        Beim Einbau einer Wärmepumpe liefert der Heizungsbetrieb den hydraulischen
        Abgleich in aller Regel mit – er ist Voraussetzung für die Förderung. Als
        <a href="hydraulischer-abgleich-ulm.html">eigene Maßnahme</a> lohnt er sich
        vorher trotzdem, weil er sofort wirkt und die spätere Anlage kleiner ausfallen
        lässt.
      </p>

      <h2>Was der Betrieb kostet</h2>
      <p>
        Die entscheidende Kennzahl im Betrieb ist die Jahresarbeitszahl: Wie viele
        Kilowattstunden Wärme entstehen aus einer Kilowattstunde Strom? Als grobe
        Orientierung:
      </p>
      <div class="rg-tabelle">
        <table>
          <thead>
            <tr><th>Vorlauftemperatur</th><th>Jahresarbeitszahl, ca.</th><th>Einordnung</th></tr>
          </thead>
          <tbody>
            <tr><td>35 °C (Fußbodenheizung)</td><td>4,0 bis 4,5</td><td>sehr wirtschaftlich</td></tr>
            <tr><td>45 °C (große Heizkörper)</td><td>3,3 bis 3,8</td><td>gut</td></tr>
            <tr><td>55 °C (Bestandsheizkörper)</td><td>2,7 bis 3,2</td><td>meist noch tragfähig</td></tr>
            <tr><td>65 °C und mehr</td><td>unter 2,5</td><td>zuerst andere Maßnahmen</td></tr>
          </tbody>
        </table>
      </div>
      <p>
        Ob sich das gegenüber Ihrer heutigen Heizung rechnet, hängt am Verhältnis von
        Wärmepumpenstrom- und Gas- oder Ölpreis. Der
        <a href="sanierungsrechner.html">Sanierungsrechner</a> stellt beides mit Ihren
        eigenen Verbrauchswerten gegenüber. Welche Zuschüsse es für den Heizungstausch
        gibt, steht im Beitrag
        <a href="ratgeber-heizung-tauschen-pflicht.html">Heizung tauschen</a> und im
        <a href="index.html#foerderung">Förderabschnitt</a> – dort gepflegt, damit es
        nicht an drei Stellen unterschiedlich steht.
      </p>

      <h2>Wann eine Wärmepumpe die falsche Antwort ist</h2>
      <p>
        Es gibt Häuser, bei denen wir davon abraten – zumindest vorerst:
      </p>
      <ul>
        <li><strong>Ungedämmtes Mauerwerk mit kleinen Heizkörpern</strong>, das im Test
        selbst bei 65 Grad nicht warm wird. Hier zuerst die Hülle.</li>
        <li><strong>Sehr hohe Warmwasseranforderung</strong> bei gleichzeitig schlechter
        Gebäudehülle – die Anlage läuft dann dauerhaft im ungünstigen Bereich.</li>
        <li><strong>Kein Platz für das Außengerät</strong> in ausreichendem Abstand zum
        Nachbarn. Der Schallschutz ist im Reihenhausgebiet ein echtes Thema, kein
        Nebenaspekt.</li>
        <li><strong>Anstehende Fassadensanierung.</strong> Wer ohnehin in zwei Jahren
        dämmt, sollte die Wärmepumpe danach auslegen – sonst kauft er sie eine Nummer
        zu groß und zahlt das zwanzig Jahre lang mit.</li>
      </ul>
      <p>
        Der letzte Punkt ist der häufigste. Deshalb steht in unseren Fahrplänen die
        Reihenfolge vor der Technik – warum, steht im Beitrag
        <a href="ratgeber-reihenfolge-sanierung.html">In welcher Reihenfolge
        sanieren?</a>.
      </p>
 """,
 "faq": [
   ("Funktioniert eine Wärmepumpe im Altbau?",
    "Ja, wenn das Gebäude am kältesten Tag mit etwa 50 bis 55 Grad Vorlauftemperatur "
    "auskommt. Das Baujahr allein sagt darüber wenig aus: Viele Altbauten haben "
    "großzügig ausgelegte Heizkörper und schaffen das, während manches Haus aus den "
    "1990er Jahren mit knapp bemessenen Flächen scheitert. Prüfen lässt sich das an "
    "der eigenen Heizung, indem die Heizkurve testweise abgesenkt wird."),
   ("Braucht eine Wärmepumpe zwingend eine Fußbodenheizung?",
    "Nein. Die Fußbodenheizung ist nur ein Weg zu niedriger Vorlauftemperatur. "
    "Ausreichend große Heizkörper und ein hydraulischer Abgleich erreichen häufig "
    "dasselbe – zu deutlich geringeren Kosten als eine Fußbodenheizung im Bestand."),
   ("Muss ich vor der Wärmepumpe erst dämmen?",
    "Nicht grundsätzlich. Nötig ist es dann, wenn das Haus die Räume bei abgesenkter "
    "Vorlauftemperatur nicht mehr warm bekommt. Sinnvoll ist die Reihenfolge außerdem, "
    "wenn eine Dämmung ohnehin ansteht: Nach der Dämmung fällt die Anlage kleiner und "
    "damit günstiger aus."),
 ],
},
{
 "datei": "ratgeber-reihenfolge-sanierung.html",
 "bild": """<img class="rg-bild" src="bilder/ratgeber-reihenfolge.jpg" width="1200" height="800"
           alt="Handwerker auf dem Gerüst bei Putzarbeiten an einer Hausfassade"
           loading="lazy" decoding="async">""",
 "rubrik": "Strategie",
 "titel": "In welcher Reihenfolge sanieren?",
 "seitentitel": "Sanierung: die richtige Reihenfolge spart fünfstellig",
 "beschreibung": "Dach, Fenster, Fassade oder Heizung zuerst? Warum die Reihenfolge über "
                 "die Wirtschaftlichkeit entscheidet – und welche Regel fast immer gilt.",
 "anriss": "Die falsche Reihenfolge kostet schnell fünfstellig und verbaut "
           "Fördermöglichkeiten. Die Regel dahinter ist einfacher, als die meisten "
           "denken.",
 "dauer": "6 Minuten",
 "inhalt": """
      <p>
        Die häufigste Frage im Erstgespräch – und die, bei der am meisten Geld auf dem
        Spiel steht. Denn nicht die Auswahl der Maßnahmen entscheidet über die
        Wirtschaftlichkeit, sondern ihre Abfolge.
      </p>

      <div class="rg-kasten">
        <b>Die Grundregel</b>
        Erst die Hülle dicht machen, dann die Technik darauf auslegen. Wer zuerst die
        Heizung tauscht, dimensioniert sie auf einen Wärmebedarf, den es nach der
        Dämmung gar nicht mehr gibt.
      </div>

      <h2>Warum die Heizung meist zuletzt kommt</h2>
      <p>
        Eine Heizung wird auf die <strong>Heizlast</strong> ausgelegt – auf die
        Leistung, die das Gebäude am kältesten Tag braucht. Dämmen Sie danach Dach und
        Fassade, sinkt diese Last erheblich. Die Anlage ist dann zu groß, taktet
        häufiger, verschleißt schneller und arbeitet mit schlechterer
        Jahresarbeitszahl.
      </p>
      <p>
        Bei einer Wärmepumpe wiegt das doppelt: Sie lebt von niedrigen
        Vorlauftemperaturen. Ein ungedämmtes Haus braucht hohe Vorlauftemperaturen –
        genau die, bei denen eine Wärmepumpe ineffizient wird. Erst die Dämmung macht
        sie wirtschaftlich.
      </p>

      <h2>Die übliche Reihenfolge</h2>
      <ol>
        <li><strong>Was fast nichts kostet:</strong> hydraulischer Abgleich,
        Heizungspumpe, Rohrdämmung im Keller. Amortisation oft unter drei Jahren.</li>
        <li><strong>Oberste Geschossdecke und Kellerdecke:</strong> die günstigsten
        Dämmmaßnahmen überhaupt, häufig in Eigenleistung machbar.</li>
        <li><strong>Dach:</strong> ohnehin fällig, wenn die Eindeckung erneuert wird –
        dann die Dämmung gleich mitmachen.</li>
        <li><strong>Fassade:</strong> die größte Einzelfläche, entsprechend hoher
        Effekt, aber auch die teuerste Maßnahme.</li>
        <li><strong>Fenster:</strong> sinnvoll zusammen mit der Fassade, sonst stimmen
        die Anschlüsse nicht.</li>
        <li><strong>Heizung:</strong> zum Schluss, ausgelegt auf das dann tatsächlich
        vorhandene Gebäude.</li>
      </ol>

      <div class="rg-warnung">
        <b>Die wichtigste Ausnahme:</b> Wenn die Heizung ausfällt, können Sie nicht
        erst drei Jahre lang dämmen. Dann gilt: die Anlage bewusst auf den
        <em>künftigen</em> Zustand auslegen, nicht auf den heutigen – und die
        geplanten Dämmmaßnahmen in der Berechnung vorwegnehmen.
      </div>

      <h2>Fenster ohne Dämmung – ein teurer Klassiker</h2>
      <p>
        Neue Fenster in eine ungedämmte Wand einzubauen, führt regelmäßig zu
        Problemen. Das Fenster ist danach das dichteste Bauteil im Haus, die Wand
        bleibt die kälteste Fläche. Feuchtigkeit, die vorher durch undichte Fenster
        entwich, schlägt sich anschließend an der Wand nieder. Schimmel ist die Folge –
        nicht wegen der Fenster, sondern wegen der Reihenfolge.
      </p>
      <p>
        Wer die Fenster trotzdem zuerst tauschen muss, sollte wenigstens das
        Lüftungskonzept mitdenken und die Anschlüsse so ausführen, dass eine spätere
        Fassadendämmung ohne Ausbau möglich bleibt.
      </p>

      <h2>Was das mit dem Sanierungsfahrplan zu tun hat</h2>
      <p>
        Genau diese Reihenfolge festzulegen, ist der Kern eines
        <a href="sanierungsfahrplan.html">individuellen Sanierungsfahrplans</a>. Er
        rechnet jede Maßnahme einzeln durch, ordnet sie und zeigt, welche
        Effizienzklasse Sie nach welchem Schritt erreichen. Als Nebeneffekt bringt er
        zusätzliche Förderprozente auf spätere Einzelmaßnahmen an der Gebäudehülle.
      </p>
      <p>
        Einen ersten Eindruck bekommen Sie kostenlos im
        <a href="sanierungsrechner.html">Sanierungsrechner</a> – er sortiert die
        Maßnahmen nach Wirtschaftlichkeit und zeigt, was jede davon maximal kosten
        darf, damit sie sich noch rechnet.
      </p>
 """,
 "faq": [
   ("Was saniert man zuerst, Heizung oder Dämmung?",
    "In der Regel zuerst die Gebäudehülle, danach die Heizung. Nur so lässt sich die "
    "neue Anlage auf den tatsächlichen Wärmebedarf auslegen. Fällt die Heizung "
    "vorher aus, wird sie auf den geplanten künftigen Dämmzustand ausgelegt."),
   ("Lohnt sich ein Fenstertausch ohne Fassadendämmung?",
    "Energetisch ja, bauphysikalisch ist er heikel: Die Außenwand bleibt die kälteste "
    "Fläche im Raum, während die Fenster dicht sind. Ohne angepasstes Lüftungsverhalten "
    "steigt das Schimmelrisiko."),
 ],
},
{
 "datei": "ratgeber-foerderung-oder-steuer.html",
 "bild": """<img class="rg-bild" src="bilder/ratgeber-foerderung.jpg" width="1200" height="800"
           alt="Euro-Geldscheine verschiedener Werte auf einem Haufen Münzen"
           loading="lazy" decoding="async">""",
 "rubrik": "Förderung",
 "titel": "Förderung oder Steuerermäßigung?",
 "seitentitel": "Förderung oder §35c EStG: Was lohnt sich mehr?",
 "beschreibung": "Zuschuss beantragen oder Sanierungskosten absetzen? Beides zusammen geht "
                 "nicht. Wie Sie den günstigeren Weg erkennen – mit Rechenbeispiel.",
 "anriss": "Zuschuss oder Steuerermäßigung – beides zusammen ist ausgeschlossen. Die "
           "Entscheidung fällt vor dem ersten Auftrag und lässt sich später nicht "
           "mehr korrigieren.",
 "dauer": "5 Minuten",
 "inhalt": """
      <p>
        Für energetische Sanierungen am selbst genutzten Wohneigentum gibt es zwei
        Wege: den Zuschuss über BAFA und KfW oder die Steuerermäßigung nach §35c
        Einkommensteuergesetz. <strong>Sie müssen sich für einen entscheiden</strong> –
        eine Kombination für dieselbe Maßnahme ist ausgeschlossen.
      </p>

      <div class="rg-warnung">
        <b>Zeitkritisch:</b> Die Entscheidung fällt praktisch mit dem ersten
        Handwerkerauftrag. Der Förderantrag muss <em>vorher</em> gestellt sein. Wer
        erst beauftragt und dann überlegt, hat den Zuschussweg bereits verloren.
      </div>

      <h2>Die beiden Wege im Vergleich</h2>
      <div class="rg-tabelle">
        <table>
          <thead><tr><th></th><th>Zuschuss (BEG)</th><th>Steuer (§35c)</th></tr></thead>
          <tbody>
            <tr><td>Höhe</td><td>15–20 % Hülle, deutlich mehr bei der Heizung</td><td>20 % der Kosten</td></tr>
            <tr><td>Auszahlung</td><td>nach Abschluss, als Geld</td><td>über drei Jahre, als Steuerminderung</td></tr>
            <tr><td>Antrag</td><td>vor Auftragsvergabe</td><td>mit der Steuererklärung</td></tr>
            <tr><td>Energieberater</td><td>vorgeschrieben</td><td>nur Fachunternehmerbescheinigung</td></tr>
            <tr><td>Voraussetzung</td><td>technische Mindestanforderungen</td><td>selbst genutzt, Mindestalter des Gebäudes</td></tr>
          </tbody>
        </table>
      </div>

      <h2>Wann der Zuschuss besser ist</h2>
      <ul>
        <li>Bei der <strong>Heizung</strong>: Mit den Boni sind Sätze erreichbar, die
        weit über 20 % liegen. Hier ist der Zuschuss praktisch immer überlegen.</li>
        <li>Wenn ein <strong>Sanierungsfahrplan</strong> vorliegt: Er hebt den Satz für
        Hüllmaßnahmen und ist selbst förderfähig.</li>
        <li>Wenn Sie das Geld <strong>zeitnah</strong> brauchen – der Zuschuss kommt
        nach Abschluss der Maßnahme, die Steuerermäßigung verteilt sich über drei
        Jahre.</li>
      </ul>

      <h2>Wann die Steuer die bessere Wahl ist</h2>
      <ul>
        <li>Bei <strong>hoher Steuerlast</strong> und Maßnahmen, die nur den
        Grundsatz von 15 % bekämen</li>
        <li>Wenn die <strong>technischen Mindestanforderungen</strong> der Förderung
        nicht erreichbar sind – etwa weil der Denkmalschutz die nötige Dämmstärke
        nicht zulässt</li>
        <li>Wenn der <strong>Antragszeitpunkt verpasst</strong> wurde: Dann ist die
        Steuerermäßigung oft das, was übrig bleibt</li>
      </ul>

      <div class="rg-kasten">
        <b>Rechenbeispiel Fassadendämmung, 40.000 Euro</b>
        Über die Förderung mit Sanierungsfahrplan: 20 % Zuschuss, also 8.000 Euro,
        ausgezahlt nach Abschluss. Über die Steuer: ebenfalls 20 %, aber verteilt auf
        drei Jahre – und nur dann in voller Höhe, wenn die Steuerlast in allen drei
        Jahren hoch genug ist, um den Betrag auszuschöpfen.
      </div>

      <h2>Der häufigste Fehler</h2>
      <p>
        Die Entscheidung wird oft erst getroffen, wenn die Handwerker schon da waren.
        Dann ist sie keine mehr. Wer den Zuschussweg offenhalten will, muss den Antrag
        vor der Auftragsvergabe stellen – und dafür braucht es einen eingetragenen
        Energie-Effizienz-Experten.
      </p>
      <p>
        Was in Ihrem Fall günstiger ist, hängt von der Maßnahme, Ihrer Steuerlast und
        dem Gebäudealter ab. Wir rechnen beide Wege durch, bevor irgendetwas
        beauftragt wird. Einen Überblick über die Programme gibt es auf der
        <a href="index.html#foerderung">Startseite</a>.
      </p>
      <p style="font-size:.86rem;color:var(--muted)">
        Dieser Text ist keine Steuerberatung. Für die steuerliche Behandlung Ihres
        Einzelfalls ist Ihr Steuerberater zuständig.
      </p>
 """,
 "faq": [
   ("Kann man BAFA-Förderung und §35c EStG kombinieren?",
    "Nein. Für dieselbe Maßnahme ist entweder der Zuschuss oder die Steuerermäßigung "
    "möglich. Bei mehreren getrennten Maßnahmen kann für jede einzeln entschieden "
    "werden."),
   ("Wie hoch ist die Steuerermäßigung nach §35c EStG?",
    "20 Prozent der Aufwendungen, verteilt auf drei Jahre. Voraussetzung sind ein "
    "selbst genutztes Wohngebäude ab einem bestimmten Mindestalter und eine "
    "Fachunternehmerbescheinigung."),
 ],
},
{
 # Die Spanne 130-250 EUR/m2 ist CONFIG.kosten.wand aus sanierungsrechner.html.
 # Wird sie dort angepasst, gehoert sie hier mitgeaendert - sonst widerspricht
 # der Ratgeber dem Rechner auf derselben Website.
 "datei": "ratgeber-fassade-daemmen.html",
 "bild": """<img class="rg-bild" src="bilder/ratgeber-fassade.jpg" width="1200" height="800"
           alt="Gerüst vor einer Hausfassade mit bereits angebrachten Dämmplatten"
           loading="lazy" decoding="async">""",
 "rubrik": "Dämmung",
 "titel": "Fassade dämmen: Kosten und Verfahren",
 "seitentitel": "Fassade dämmen: Kosten, Verfahren und Förderung",
 "beschreibung": "Was eine Fassadendämmung kostet, welche drei Verfahren es gibt und "
                 "wann sich die Außenwand zuerst lohnt – und wann eben nicht.",
 "anriss": "Die teuerste Einzelmaßnahme an der Gebäudehülle – und die, bei der der "
           "Zeitpunkt über die Wirtschaftlichkeit entscheidet. Zahlen, Verfahren, "
           "Fallstricke.",
 "dauer": "7 Minuten",
 "inhalt": """
      <p>
        Die Außenwand ist meist die größte zusammenhängende Fläche eines Hauses und je
        nach Baujahr für 20 bis 30 Prozent des Wärmeverlusts verantwortlich. Sie ist
        damit ein naheliegendes Ziel – und zugleich die Maßnahme, bei der am meisten
        Geld falsch eingesetzt wird. Nicht weil Dämmung nicht wirkt, sondern weil der
        Zeitpunkt selten stimmt.
      </p>

      <div class="rg-kasten">
        <b>Das Wichtigste in einem Satz</b>
        Eine Fassadendämmung rechnet sich fast immer dann, wenn die Fassade ohnehin
        ansteht – und selten, wenn sie nur wegen der Energieeinsparung gemacht wird.
      </div>

      <h2>Drei Verfahren, drei Preisklassen</h2>
      <p>
        „Fassade dämmen“ heißt je nach Wandaufbau etwas völlig anderes. Welches
        Verfahren infrage kommt, entscheidet nicht der Geschmack, sondern die Wand:
      </p>
      <div class="rg-tabelle">
        <table>
          <thead>
            <tr><th>Verfahren</th><th>Wofür</th><th>Kosten je m² Wand</th></tr>
          </thead>
          <tbody>
            <tr>
              <td>Wärmedämmverbundsystem (WDVS)</td>
              <td>Der Regelfall: Platten auf die bestehende Wand, darüber Putz</td>
              <td>ca. 130 bis 250 €</td>
            </tr>
            <tr>
              <td>Kerndämmung (Einblasdämmung)</td>
              <td>Nur bei zweischaligem Mauerwerk mit Hohlschicht</td>
              <td>ca. 25 bis 60 €</td>
            </tr>
            <tr>
              <td>Vorgehängte hinterlüftete Fassade</td>
              <td>Bei Schlagregen, unebenem Untergrund, gestalterischem Anspruch</td>
              <td>deutlich über WDVS</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p>
        Der Unterschied zwischen Zeile eins und Zeile zwei ist der wichtigste Satz
        dieses Beitrags: <strong>Wenn Ihr Haus eine Hohlschicht hat, kostet die Dämmung
        einen Bruchteil.</strong> Zweischaliges Mauerwerk war vor allem im Norden
        verbreitet, kommt aber auch hier vor – erkennbar an der Mauerwerksdicke an
        Fenster- und Türlaibungen. Eine Kamerauntersuchung durch eine kleine Bohrung
        klärt es zweifelsfrei.
      </p>

      <h2>Was am Ende auf der Rechnung steht</h2>
      <p>
        Bei einem freistehenden Einfamilienhaus mit rund 150 Quadratmetern Wandfläche
        landet ein WDVS damit grob zwischen 20.000 und 37.000 €. In dieser Spanne
        stecken vier Posten, die den Preis auseinandertreiben:
      </p>
      <ul>
        <li><strong>Gerüst.</strong> Fällt unabhängig von der Dämmstärke an – deshalb
        ist die Kombination mit Fenstertausch oder Dachüberstand so viel günstiger als
        zwei getrennte Baustellen.</li>
        <li><strong>Anschlussdetails.</strong> Fensterlaibungen, Rollladenkästen,
        Dachüberstand, Balkonplatten: Hier entsteht der Aufwand, nicht auf der freien
        Fläche.</li>
        <li><strong>Dämmstoff.</strong> Zwischen Standard-Polystyrol und
        Holzfaser oder Mineralschaum liegen leicht 40 Prozent.</li>
        <li><strong>Untergrund.</strong> Alter Putz, der nicht trägt, muss abgeschlagen
        werden.</li>
      </ul>
      <p>
        Was das an Ihrem Haus bedeutet, hängt an der tatsächlichen Wandfläche und dem
        heutigen Zustand. Der <a href="sanierungsrechner.html">Sanierungsrechner</a>
        rechnet die Einsparung gegen diese Spanne und zeigt, wie viel die Maßnahme bei
        Ihnen kosten <em>darf</em>, um sich zu tragen.
      </p>

      <h2>Wann sich die Fassade zuerst lohnt</h2>
      <p>
        In der Reihenfolge der Maßnahmen steht die Außenwand selten ganz vorn – oberste
        Geschossdecke und Kellerdecke sind pro eingesetztem Euro fast immer wirksamer.
        Es gibt aber klare Ausnahmen:
      </p>
      <ol>
        <li><strong>Der Putz ist ohnehin fällig.</strong> Dann zahlen Sie Gerüst und
        Putz sowieso; die Dämmung kostet nur noch die Differenz. Das ist der mit
        Abstand häufigste wirtschaftliche Fall.</li>
        <li><strong>Die Wand ist spürbar kalt.</strong> Ungedämmtes Mauerwerk der
        1950er bis 1970er Jahre verliert so viel Wärme, dass sich die Maßnahme auch
        einzeln trägt.</li>
        <li><strong>Eine Wärmepumpe ist geplant.</strong> Die gedämmte Wand senkt die
        nötige Vorlauftemperatur – die Anlage fällt kleiner aus und läuft effizienter.
        Näheres im Beitrag
        <a href="ratgeber-waermepumpe-altbau.html">Wärmepumpe im Altbau</a>.</li>
      </ol>

      <div class="rg-warnung">
        <b>Gesetzliche Vorgabe:</b> Wer mehr als zehn Prozent einer Fassadenfläche
        erneuert, muss den vorgeschriebenen Dämmstandard einhalten. Ein reiner
        Neuanstrich ist davon nicht betroffen, das Abschlagen und Neuverputzen sehr
        wohl. Wer „nur mal den Putz macht“, steht deshalb schneller in der Pflicht als
        gedacht.
      </div>

      <h2>Der Fehler, der die Fassade teuer macht</h2>
      <p>
        Die Fassade ohne Anlass zu dämmen, ist die eine Variante. Die andere, teurere:
        sie zu dämmen und dabei die Gelegenheit nicht zu nutzen. Wenn das Gerüst einmal
        steht, kosten diese Arbeiten nur noch einen Bruchteil:
      </p>
      <ul>
        <li>Fenstertausch samt Einbau in die Dämmebene – wärmebrückenfrei geht das
        später nicht mehr.</li>
        <li>Rollladenkästen dämmen oder ersetzen.</li>
        <li>Dachüberstand und Ortgang anpassen.</li>
        <li>Außensteckdosen, Leitungen und Vordächer versetzen.</li>
      </ul>
      <p>
        Wer diese Punkte auf später verschiebt, zahlt das zweite Gerüst – und bei
        Fenstern zusätzlich eine Wärmebrücke, die dauerhaft bleibt.
      </p>

      <h2>Schimmel und „das Haus muss atmen“</h2>
      <p>
        Der verbreitetste Einwand gegen Dämmung ist auch der am leichtesten zu
        entkräftende. Eine Wand tauscht praktisch keine Luft aus; der Luftwechsel läuft
        über Fenster und Undichtigkeiten. Was sich ändert, ist die Temperatur der
        Innenoberfläche – und die wird durch Dämmung <strong>höher</strong>. Warme
        Oberflächen sind der beste Schutz gegen Schimmel, nicht sein Auslöser.
      </p>
      <p>
        Ein reales Risiko gibt es trotzdem: Wenn gleichzeitig die Fenster getauscht
        werden, verschwinden die alten Undichtigkeiten, über die bisher unbemerkt
        gelüftet wurde. Die Feuchte sucht sich dann die kälteste verbliebene Stelle. Die
        Antwort darauf ist bewusstes Lüften oder eine Lüftungsanlage – nicht der
        Verzicht auf die Dämmung.
      </p>
      <p>
        Bei Innendämmung, etwa hinter denkmalgeschützten Fassaden, ist der Einwand
        dagegen ernst zu nehmen: Dort wird die Wand tatsächlich kälter, und der Aufbau
        muss bauphysikalisch gerechnet werden. Das ist keine Maßnahme für die
        Eigenleistung.
      </p>
 """,
 "faq": [
   ("Was kostet es, eine Fassade zu dämmen?",
    "Ein Wärmedämmverbundsystem kostet einschließlich Gerüst und Putz überschlägig 130 "
    "bis 250 € je Quadratmeter Wandfläche; bei einem Einfamilienhaus sind das grob "
    "20.000 bis 37.000 €. Hat die Wand eine Hohlschicht, ist eine Einblasdämmung für "
    "etwa 25 bis 60 € je Quadratmeter möglich."),
   ("Lohnt sich eine Fassadendämmung?",
    "Am ehesten dann, wenn die Fassade ohnehin erneuert werden muss – dann fallen "
    "Gerüst und Putz sowieso an und nur die Differenz zählt. Als reine Energiemaßnahme "
    "amortisiert sie sich bei einem Einfamilienhaus meist langsamer als Dach-, "
    "Geschossdecken- oder Kellerdeckendämmung."),
   ("Kann man eine Fassade ohne Gerüst dämmen?",
    "Bei zweischaligem Mauerwerk ja: Die Kerndämmung wird über Bohrlöcher in die "
    "Hohlschicht eingeblasen, meist an einem Tag und ohne Gerüst. Voraussetzung ist "
    "eine ausreichend breite, trockene und zusammenhängende Hohlschicht – das prüft "
    "eine Kamerauntersuchung vorab."),
 ],
},
{
 "datei": "ratgeber-kellerdecke-daemmen.html",
 "bild": """<img class="rg-bild" src="bilder/ratgeber-kellerdecke.jpg" width="1200" height="801"
           alt="Handwerker befestigt Dämmwolle zwischen Holzständern"
           loading="lazy" decoding="async">""",
 "rubrik": "Selbst machen",
 "titel": "Kellerdecke dämmen: der günstigste Einstieg",
 "seitentitel": "Kellerdecke dämmen: Kosten, Ablauf, Eigenleistung",
 "beschreibung": "Die günstigste Dämmmaßnahme überhaupt: Kosten, Amortisation und was Sie "
                 "am Wochenende selbst machen können – mit Hinweis zur Förderung.",
 "anriss": "Überschaubare Materialkosten, ein Wochenende Arbeit, spürbar wärmere Böden "
           "im Erdgeschoss. Warum diese Maßnahme fast immer der richtige erste Schritt "
           "ist.",
 "dauer": "5 Minuten",
 "inhalt": """
      <p>
        Wenn uns jemand fragt, womit er anfangen soll, und das Haus hat einen
        unbeheizten Keller, lautet die Antwort in den allermeisten Fällen: mit der
        Kellerdecke. Keine andere Maßnahme bringt so viel Wirkung für so wenig Geld.
      </p>

      <div class="rg-kasten">
        <b>Warum ausgerechnet die Kellerdecke</b>
        Sie ist von unten frei zugänglich, es muss kein Gerüst gestellt werden, es gibt
        keine Genehmigungsfragen und keine kniffligen Anschlussdetails wie bei Fenstern
        oder Fassade. Und man merkt den Unterschied sofort an den Füßen.
      </div>

      <h2>Was es kostet</h2>
      <p>
        Je nach Dämmstoff und Stärke rechnet man mit etwa 20 bis 60 Euro pro
        Quadratmeter, wenn ein Betrieb beauftragt wird. In Eigenleistung bleibt davon
        nur der Materialpreis übrig – bei einer typischen Kellerdecke von 80
        Quadratmetern liegt der häufig im niedrigen vierstelligen Bereich.
      </p>
      <p>
        Die Einsparung liegt bei rund 5 bis 10 Prozent der Heizenergie. Das klingt
        wenig, bezogen auf die Investition ist es aber der beste Wert im ganzen
        Maßnahmenkatalog. Amortisationszeiten von unter fünf Jahren sind keine
        Seltenheit.
      </p>

      <h2>Was Sie selbst machen können</h2>
      <ol>
        <li><strong>Höhe prüfen.</strong> Nach der Dämmung sinkt die lichte Höhe im
        Keller. Türen, Rohre und Kabeltrassen müssen weiterhin passen.</li>
        <li><strong>Untergrund prüfen.</strong> Die Decke muss trocken und tragfähig
        sein. Feuchte Stellen zuerst klären – Dämmung auf feuchtem Untergrund macht
        das Problem größer, nicht kleiner.</li>
        <li><strong>Dämmplatten ankleben oder dübeln.</strong> Bei glatter Betondecke
        ist das reine Fleißarbeit.</li>
        <li><strong>Ränder und Durchdringungen sauber anschließen.</strong> Hier
        entstehen sonst Wärmebrücken, die einen Teil des Effekts wieder
        auffressen.</li>
      </ol>

      <div class="rg-warnung">
        <b>Wenn Sie die Förderung wollen:</b> Der Zuschuss setzt voraus, dass ein
        bestimmter U-Wert erreicht wird und die Ausführung bestätigt wird. Material in
        Eigenleistung ist grundsätzlich förderfähig, die fachliche Bestätigung braucht
        es trotzdem. Wer ohne Förderung arbeitet, ist an diese Vorgaben nicht gebunden
        – dann zählt nur die Bauphysik.
      </div>

      <h2>Wo es Grenzen gibt</h2>
      <ul>
        <li><strong>Beheizter Keller:</strong> Dann ist die Kellerdecke keine
        Außenfläche und die Maßnahme bringt nichts. Die Wärmegrenze liegt in dem Fall
        an der Bodenplatte – und die lässt sich nachträglich praktisch nicht
        dämmen.</li>
        <li><strong>Gewölbekeller:</strong> Bei alten, gemauerten Gewölben ist die
        Sache bauphysikalisch heikler. Hier vorher fragen.</li>
        <li><strong>Zu geringe Höhe:</strong> Wo ohnehin schon geduckt gegangen wird,
        kann die Maßnahme an der Kopfhöhe scheitern.</li>
      </ul>

      <h2>Was danach kommt</h2>
      <p>
        Die Kellerdecke ist der Einstieg, nicht das Ziel. Sinnvoll ist, sie zusammen
        mit den anderen günstigen Maßnahmen zu denken: hydraulischer Abgleich,
        Rohrdämmung, oberste Geschossdecke. Zusammen kosten die vier oft weniger als
        ein Fenstertausch und bringen mehr. Die Systematik dahinter steht im Artikel
        <a href="ratgeber-reihenfolge-sanierung.html">In welcher Reihenfolge
        sanieren?</a>
      </p>
      <p>
        Ob es bei Ihrem Haus passt und was es konkret bringt, zeigt der
        <a href="sanierungsrechner.html">Sanierungsrechner</a> – Maßnahmen, die sich
        für Eigenleistung eignen, sind dort gekennzeichnet.
      </p>
 """,
 "faq": [
   ("Was kostet es, die Kellerdecke zu dämmen?",
    "Bei Vergabe an einen Betrieb etwa 20 bis 60 Euro pro Quadratmeter je nach "
    "Dämmstoff und Stärke. In Eigenleistung fallen nur die Materialkosten an."),
   ("Kann man die Kellerdecke selbst dämmen?",
    "Bei einer glatten, trockenen Betondecke ja – die Platten werden geklebt oder "
    "gedübelt. Wichtig sind die lichte Höhe, ein trockener Untergrund und saubere "
    "Anschlüsse an Rändern und Durchdringungen."),
 ],
},
{
 "datei": "ratgeber-energieausweis-bedarf-verbrauch.html",
 "bild": """<img class="rg-bild" src="bilder/ratgeber-energieausweis.jpg" width="1200" height="801"
           alt="Grundriss eines Hauses mit Brille und Stift auf einem Tisch"
           loading="lazy" decoding="async">""",
 "rubrik": "Nachweise",
 "titel": "Energieausweis: Bedarf oder Verbrauch?",
 "seitentitel": "Energieausweis: Bedarf oder Verbrauch? Der Unterschied",
 "beschreibung": "Bedarfsausweis oder Verbrauchsausweis: Was der Unterschied bedeutet, "
                 "wann Sie wählen dürfen und wann Sie einen Ausweis brauchen.",
 "anriss": "Zwei Dokumente mit demselben Namen, die völlig Verschiedenes aussagen – "
           "und der billigere ist oft der, der Ihnen schadet.",
 "dauer": "6 Minuten",
 "inhalt": """
      <p>
        Beim Verkauf oder bei der Vermietung braucht es einen Energieausweis. Was viele
        erst beim Angebot merken: Es gibt ihn in zwei Varianten, sie kosten
        unterschiedlich viel – und sie sagen nicht dasselbe aus. Der Unterschied ist
        keine Formalie. Er entscheidet darüber, welche Zahl später in Ihrem Inserat
        steht.
      </p>

      <div class="rg-kasten">
        <b>Das Wichtigste in einem Satz</b>
        Der Verbrauchsausweis misst, wie die bisherigen Bewohner geheizt haben. Der
        Bedarfsausweis berechnet, was das Gebäude selbst braucht – unabhängig davon,
        wer darin wohnt.
      </div>

      <h2>Zwei Ausweise, zwei verschiedene Aussagen</h2>
      <div class="rg-tabelle">
        <table>
          <thead>
            <tr><th></th><th>Verbrauchsausweis</th><th>Bedarfsausweis</th></tr>
          </thead>
          <tbody>
            <tr><td>Grundlage</td>
                <td>Heizkostenabrechnungen der letzten drei Jahre</td>
                <td>Berechnung aus Bauteilen, Dämmung und Anlagentechnik</td></tr>
            <tr><td>Beeinflusst durch</td>
                <td>Heizverhalten, Leerstand, milde Winter</td>
                <td>nichts davon – gerechnet wird mit Normklima und Normnutzung</td></tr>
            <tr><td>Aufwand</td>
                <td>gering, meist ohne Ortstermin</td>
                <td>Aufnahme des Gebäudes, deutlich aufwendiger</td></tr>
            <tr><td>Aussagekraft für Sanierung</td>
                <td>gering</td>
                <td>hoch – zeigt, wo die Verluste sitzen</td></tr>
          </tbody>
        </table>
      </div>
      <p>
        Beide Ausweise sind zehn Jahre gültig und beide erfüllen die gesetzliche
        Pflicht. Nur beantworten sie eben verschiedene Fragen.
      </p>

      <h2>Wann Sie wählen dürfen – und wann nicht</h2>
      <p>
        Das Gebäudeenergiegesetz lässt die freie Wahl nicht immer zu. Der
        <strong>Bedarfsausweis ist vorgeschrieben</strong>, wenn diese Punkte
        zusammenkommen:
      </p>
      <ul>
        <li>Es handelt sich um ein Wohngebäude mit weniger als fünf Wohnungen,</li>
        <li>der Bauantrag wurde vor dem 1. November 1977 gestellt,</li>
        <li>und das Gebäude wurde seither nicht mindestens auf den Dämmstandard der
        ersten Wärmeschutzverordnung gebracht.</li>
      </ul>
      <p>
        Genau das trifft auf einen großen Teil der Bestandshäuser im Alb-Donau-Kreis zu.
        Wurde nachträglich gedämmt, kann wieder gewählt werden – der Nachweis darüber
        liegt beim Eigentümer. In allen anderen Fällen, also bei Neubauten, größeren
        Wohngebäuden und ausreichend gedämmten Altbauten, steht die Wahl frei.
      </p>

      <div class="rg-warnung">
        <b>Vorsicht bei Billigangeboten:</b> Ein Verbrauchsausweis für 50 € im Internet
        ist schnell ausgestellt – aber wertlos, wenn für Ihr Gebäude ein Bedarfsausweis
        vorgeschrieben ist. Die Pflicht ist damit nicht erfüllt.
      </div>

      <h2>Warum der Verbrauchsausweis oft in die Irre führt</h2>
      <p>
        Der Verbrauchsausweis misst Menschen, nicht Gebäude. Drei Beispiele aus der
        Praxis, alle am selben Haus denkbar:
      </p>
      <ul>
        <li><strong>Ein älteres Ehepaar</strong> heizt zwei von sieben Räumen und hält
        18 Grad. Der Ausweis weist einen guten Kennwert aus – das Haus ist deswegen
        nicht gut gedämmt.</li>
        <li><strong>Eine Familie mit drei Kindern</strong> heizt alles auf 22 Grad. Der
        Kennwert ist schlecht, obwohl es dasselbe Gebäude ist.</li>
        <li><strong>Ein Jahr Leerstand</strong> in den drei Abrechnungsjahren zieht den
        Wert nach unten, ohne dass sich baulich etwas geändert hätte.</li>
      </ul>
      <p>
        Für Käufer ist das die entscheidende Schwäche: Der günstige Kennwert im Exposé
        sagt nichts darüber, was <em>sie</em> später zahlen werden. Wer kauft, sollte
        deshalb im Zweifel nach dem Bedarfsausweis fragen – und wer verkauft und ein
        gut saniertes Haus hat, fährt mit ihm oft besser.
      </p>

      <h2>Wann Sie einen brauchen – und was ohne passiert</h2>
      <p>
        Ein Energieausweis ist fällig bei Verkauf, Vermietung, Verpachtung und Leasing.
        Drei Pflichten hängen daran:
      </p>
      <ol>
        <li><strong>In der Immobilienanzeige</strong> müssen Art des Ausweises,
        Energiekennwert, wesentlicher Energieträger, Baujahr und Energieeffizienzklasse
        stehen. Der Ausweis muss also <em>vor</em> dem Inserat vorliegen.</li>
        <li><strong>Bei der Besichtigung</strong> ist er unaufgefordert vorzulegen.</li>
        <li><strong>Nach Vertragsschluss</strong> geht er an Käufer oder Mieter über.</li>
      </ol>
      <p>
        Wer diese Pflichten verletzt, begeht eine Ordnungswidrigkeit; das Gesetz sieht
        dafür Bußgelder bis zu 10.000 € vor. In der Praxis häufiger als das Bußgeld ist
        der Ärger im Kaufvertrag – ein fehlender oder falscher Ausweis liefert dem
        Käufer ein Argument in der Preisverhandlung.
      </p>
      <p>
        Für ein Bestandsgebäude im Alb-Donau-Kreis stellen wir beide Varianten aus:
        den Verbrauchsausweis ab {{PREIS_AUSWEIS_V}} €, den Bedarfsausweis ab
        {{PREIS_AUSWEIS_B}} € – Endpreise inklusive Umsatzsteuer, Details auf der
        Seite <a href="energieausweis-ulm.html">Energieausweis</a>. Was die übrigen
        Leistungen kosten, steht im Beitrag
        <a href="ratgeber-energieberatung-kosten.html">Was kostet eine
        Energieberatung?</a>.
      </p>

      <h2>Was der Energieausweis nicht ist</h2>
      <p>
        Er ist ein Etikett, kein Plan. Der Ausweis enthält zwar
        Modernisierungsempfehlungen, aber die sind standardisiert und nicht gerechnet –
        sie nennen keine Kosten, keine Reihenfolge und keine Wirtschaftlichkeit. Wer
        wissen will, welche Maßnahme sich am eigenen Haus zuerst lohnt, braucht den
        <a href="sanierungsfahrplan.html">individuellen Sanierungsfahrplan</a>. Nur der
        ist auch die Grundlage für den iSFP-Bonus bei späteren Maßnahmen.
      </p>
      <p>
        Eine erste Einordnung, in welcher Klasse Ihr Haus überhaupt steht, liefert der
        <a href="sanierungsrechner.html">Sanierungsrechner</a> in wenigen Minuten. Er
        ist eine Orientierung und ersetzt keinen Energieausweis – ausstellen darf den
        nur, wer nach dem Gebäudeenergiegesetz dazu berechtigt ist.
      </p>
 """,
 "faq": [
   ("Bedarfsausweis oder Verbrauchsausweis – was ist besser?",
    "Das kommt auf den Zweck an. Der Bedarfsausweis bewertet das Gebäude unabhängig vom "
    "Heizverhalten der Bewohner und ist damit für Kaufinteressenten und als Grundlage "
    "einer Sanierung aussagekräftiger. Der Verbrauchsausweis ist günstiger und schneller, "
    "spiegelt aber vor allem, wie die bisherigen Bewohner geheizt haben."),
   ("Wann ist ein Bedarfsausweis Pflicht?",
    "Bei Wohngebäuden mit weniger als fünf Wohnungen, deren Bauantrag vor dem "
    "1. November 1977 gestellt wurde und die seither nicht mindestens auf den "
    "Dämmstandard der ersten Wärmeschutzverordnung gebracht wurden. In den übrigen "
    "Fällen darf zwischen beiden Varianten gewählt werden."),
   ("Wie lange ist ein Energieausweis gültig?",
    "Zehn Jahre ab Ausstellungsdatum. Er verliert seine Gültigkeit nicht durch einen "
    "Eigentümerwechsel. Nach einer größeren Sanierung lohnt sich allerdings ein neuer "
    "Ausweis, weil der alte den verbesserten Zustand nicht abbildet."),
 ],
},
{
 "datei": "ratgeber-sanieren-schwaebische-alb.html",
 "bild": """<img class="rg-bild" src="bilder/ratgeber-alb.jpg" width="1200" height="800"
           alt="Hügelige Wiesenlandschaft der Albhochfläche mit kleiner Kapelle und Streuobstbäumen"
           loading="lazy" decoding="async">""",
 "rubrik": "Region",
 "titel": "Sanieren auf der Schwäbischen Alb",
 "seitentitel": "Sanieren auf der Alb: Was die Höhenlage ändert",
 "beschreibung": "Längere Heizperiode, tiefere Normaußentemperatur, verkarsteter Untergrund: "
                 "Was bei der Sanierung auf der Albhochfläche anders ist als im Donautal.",
 "anriss": "Wer Kennwerte aus dem Donautal auf ein Haus in 750 Metern Höhe überträgt, "
           "rechnet falsch. Was die Höhenlage für Heizlast, Wärmepumpe und Dämmung "
           "bedeutet.",
 "dauer": "6 Minuten",
 "inhalt": """
      <p>
        Zwischen Ulm und Laichingen liegen keine 30 Kilometer – energetisch sind es
        zwei verschiedene Welten. Die Albhochfläche liegt rund 250 Meter höher, die
        Heizperiode ist länger, die Normaußentemperatur niedriger. Wer das ignoriert,
        rechnet sein Gebäude systematisch zu gut.
      </p>

      <div class="rg-kasten">
        <b>Der Kern in einem Satz</b>
        Dasselbe Haus braucht auf der Alb spürbar mehr Heizenergie als im Donautal. Wer
        Kennwerte überträgt, unterschätzt Heizlast und Verbrauch – und dimensioniert
        die Anlage zu klein.
      </div>

      <h2>Was die Höhenlage konkret bedeutet</h2>
      <p>
        Für die Auslegung einer Heizung zählt die
        <strong>Normaußentemperatur</strong> – der kälteste anzunehmende Wert am
        Standort. Auf der Albhochfläche liegt sie deutlich unter der von Ulm. Dazu
        kommt die längere Heizperiode: Es wird früher geheizt und später aufgehört.
      </p>
      <p>
        Für die Praxis heißt das: Eine Wärmepumpe, die im Donautal für ein
        vergleichbares Haus reicht, kann auf der Alb an ihre Grenze kommen – besonders,
        wenn sie ohne nennenswerten Heizstabbetrieb auskommen soll. Die Berechnung muss
        die tatsächliche Lage abbilden, nicht einen Durchschnittswert für
        Baden-Württemberg.
      </p>

      <h2>Der Untergrund: Karst</h2>
      <p>
        Die Alb ist verkarstet. Für Erdwärmesonden ist das ein ernstes Thema:
        Bohrungen können Hohlräume treffen oder Grundwasserstockwerke miteinander
        verbinden. Die Genehmigungsbehörden sind entsprechend zurückhaltend, in
        manchen Bereichen sind Bohrungen ausgeschlossen.
      </p>
      <div class="rg-warnung">
        <b>Vor jeder Planung mit Sole-Wasser-Wärmepumpe:</b> zuerst die
        wasserrechtliche Genehmigungsfrage klären, bevor Angebote eingeholt werden.
        Sonst planen Sie eine Anlage, die am Standort gar nicht zulässig ist. In vielen
        Fällen ist die Luft-Wasser-Wärmepumpe hier die praktikablere Lösung.
      </div>

      <h2>Bausubstanz: früh gedämmt, heute überholt</h2>
      <p>
        Weil das Klima rauer ist, wurde auf der Alb vielerorts früher gedämmt als im
        Umland. Das ist zunächst gut – führt aber zu einem verbreiteten
        Missverständnis: Viele Eigentümer halten ein Bauteil für erledigt, weil es „ja
        gedämmt ist“.
      </p>
      <p>
        Eine Dämmung aus den 1980er oder frühen 1990er Jahren erreicht typischerweise
        U-Werte, die weit von den heutigen Anforderungen entfernt sind. Für die
        Förderung bedeutet das: <strong>Eine Aufdopplung ist möglich und wird
        bezuschusst</strong>, sofern der geforderte Zielwert am Ende erreicht wird. Das
        wird häufig übersehen.
      </p>

      <h2>Was wir in der Praxis empfehlen</h2>
      <ul>
        <li>Die Heizlast am tatsächlichen Standort rechnen, nicht mit einem Regionaldurchschnitt</li>
        <li>Bei Erdwärme zuerst die Genehmigungsfrage klären</li>
        <li>Vorhandene Altdämmungen messen statt annehmen – oft lohnt die Aufdopplung</li>
        <li>Luftdichtheit ernst nehmen: In exponierter Lage kostet jede Undichtigkeit mehr als im windgeschützten Tal</li>
      </ul>

      <p>
        Wir sitzen in Dornstadt, also genau am Übergang zwischen Donautal und
        Albhochfläche, und kennen beide Seiten. Seiten mit den örtlichen
        Besonderheiten gibt es unter anderem für
        <a href="energieberatung-laichingen.html">Laichingen</a>,
        <a href="energieberatung-blaubeuren.html">Blaubeuren</a> und
        <a href="energieberatung-ulm.html">Ulm</a>.
      </p>
 """,
 "faq": [
   ("Funktioniert eine Wärmepumpe auf der Schwäbischen Alb?",
    "Ja, auch bei tieferen Normaußentemperaturen. Entscheidend ist, dass die Heizlast "
    "am tatsächlichen Standort berechnet und die Anlage auf niedrige "
    "Vorlauftemperaturen gebracht wird. Sonst steigt der Heizstabanteil und damit die "
    "Stromrechnung."),
   ("Sind Erdwärmebohrungen auf der Alb erlaubt?",
    "Nicht überall. Wegen der Verkarstung ist die wasserrechtliche Genehmigung "
    "einzelfallabhängig, in manchen Bereichen sind Bohrungen ausgeschlossen. Die Frage "
    "gehört an den Anfang der Planung, nicht ans Ende."),
 ],
},
]

STAND = "August 2026"
DATUM_ISO = "2026-08-14"

# ---------------------------------------------------------------------------
# BAUSTEINE
# ---------------------------------------------------------------------------
def fuss(aktuell=None):
    """Fussbereich mit Ratgeber-Links; der aktuelle Artikel wird ausgelassen."""
    links = []
    for a in ARTIKEL:
        if a["datei"] == aktuell:
            continue
        links.append(f'<a href="{a["datei"]}">{a["titel"]}</a>')
        if len(links) >= 4:
            break
    if aktuell is not None:
        links.append('<a href="ratgeber.html">Alle Ratgeber</a>')
    return FUSS.replace("{ratgeber_links}", "\n        ".join(links))


def krumen(*stufen):
    """stufen: Liste aus (Titel, Datei-oder-None). Der letzte Eintrag ohne Link."""
    zeilen = []
    for titel, ziel in stufen:
        if ziel:
            zeilen.append(f'<li><a href="{ziel}">{titel}</a></li>')
        else:
            zeilen.append(f"<li>{titel}</li>")
    return ('<nav class="krumen wrap" aria-label="Sie sind hier">\n  <ol>\n    '
            + "\n    ".join(zeilen) + "\n  </ol>\n</nav>\n")


def json_ld(daten):
    import json
    return ('<script type="application/ld+json">\n'
            + json.dumps(daten, ensure_ascii=False, indent=2)
            + "\n</script>\n")


TELEFON_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
               '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 4.2 2 2 0 0 1 4 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.1a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>'
               "</svg>")


def seitenspalte(aktuell):
    """Rechte Spalte: Rechner, Kontakt, weitere Artikel.

    Die drei Empfehlungen rotieren. Vorher standen hier immer die ersten drei
    Eintraege der Liste - dadurch bekamen drei Artikel je acht interne Links
    und die hinteren gar keinen; "Fassade daemmen" hatte genau einen im ganzen
    Projekt. Jetzt steht der Kosten-Artikel fest (kommerziellste Anfrage), die
    beiden anderen sind die naechsten nach dem gerade gelesenen, rundum.
    """
    namen = [a["datei"] for a in ARTIKEL]
    i = namen.index(aktuell) if aktuell in namen else -1
    fest = [ARTIKEL[0]] if aktuell != ARTIKEL[0]["datei"] else []
    folgend = [ARTIKEL[(i + n) % len(ARTIKEL)] for n in range(1, len(ARTIKEL))]
    weitere = (fest + [a for a in folgend
                       if a["datei"] != aktuell and a not in fest])[:3]
    liste = "\n        ".join(
        f'<a href="{a["datei"]}">{a["titel"]}</a>' for a in weitere)
    return f"""  <aside class="rg-spalte">
    <div class="rg-karte">
      <h3>Erst rechnen, dann sanieren</h3>
      <p>Der Sanierungsrechner zeigt in wenigen Minuten, welche Maßnahme sich bei
         Ihrem Haus zuerst lohnt – kostenlos und ohne Anmeldung.</p>
      <a href="sanierungsrechner.html" class="btn btn-amber btn-sm">Zum Sanierungsrechner</a>
    </div>
    <div class="rg-karte rg-karte-kontakt">
      <h3>Frage zum Thema?</h3>
      <a class="rg-tel" href="tel:{TEL_LINK}">{TELEFON_SVG}{TEL_ANZEIGE}</a>
      <p>Erstgespräch kostenlos, ohne Verpflichtung. Wir melden uns in der Regel am
         selben Werktag zurück.</p>
      <a href="index.html#kontakt" class="btn btn-primary btn-sm">Rückruf anfordern</a>
    </div>
    <div class="rg-karte">
      <h3>Weitere Ratgeber</h3>
      <div class="rg-mehr">
        {liste}
        <a href="ratgeber.html">Alle Beiträge ansehen</a>
      </div>
    </div>
  </aside>
"""


CTA_BAND = """    <div class="cta-band reveal">
      <div class="cta-band-text">
        <b>Wie sieht das bei Ihrem Haus aus?</b>
        <span>Im kostenlosen Erstgespräch klären wir in 20 Minuten, welcher Schritt
              bei Ihnen wirklich der erste sein sollte.</span>
      </div>
      <div class="cta-band-knoepfe">
        <a href="index.html#kontakt" class="btn btn-primary">Kostenloses Erstgespräch</a>
        <a href="tel:%s" class="btn btn-ghost">Direkt anrufen</a>
      </div>
    </div>
""" % TEL_LINK


# ---------------------------------------------------------------------------
# SEITEN
# ---------------------------------------------------------------------------
def artikel_seite(a):
    graph = [{
        "@type": "Article",
        "headline": a["titel"],
        "description": a["beschreibung"],
        "inLanguage": "de-DE",
        "datePublished": DATUM_ISO,
        "dateModified": DATUM_ISO,
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{DOMAIN}/{a['datei']}"},
        "author": {"@type": "Person", "name": "Stanislaw Tsukerman",
                   "jobTitle": "Energieberater"},
        "publisher": {"@type": "Organization", "name": "EBA Energieberater Albdonau",
                      "url": DOMAIN},
    }, {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Startseite",
             "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Ratgeber",
             "item": f"{DOMAIN}/ratgeber.html"},
            {"@type": "ListItem", "position": 3, "name": a["titel"]},
        ],
    }]
    if a.get("faq"):
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f,
                 "acceptedAnswer": {"@type": "Answer", "text": t}}
                for f, t in a["faq"]
            ],
        })

    faq_html = ""
    if a.get("faq"):
        stuecke = "".join(
            f"      <h3>{f}</h3>\n      <p>{t}</p>\n" for f, t in a["faq"])
        faq_html = f"\n      <h2>Häufige Fragen</h2>\n{stuecke}"

    return (
        kopf(a["seitentitel"], a["beschreibung"], a["datei"], bild=a["bild"])
        + json_ld({"@context": "https://schema.org", "@graph": graph})
        + f"""
<main id="inhalt">
{krumen(("Startseite", "index.html"), ("Ratgeber", "ratgeber.html"), (a["titel"], None))}
  <article>
    <header class="wrap rg-kopf">
      <span class="eyebrow">{a["rubrik"]}</span>
      <h1>{a["titel"]}</h1>
      <p class="lead">{a["anriss"]}</p>
      <div class="rg-meta">
        <span>Lesezeit ca. {a["dauer"]}</span>
        <span>Stand: {STAND}</span>
        <span>Von Stanislaw Tsukerman, Energieberater</span>
      </div>
    </header>

    <div class="wrap">
      {a["bild"]}
    </div>

    <div class="wrap rg-inhalt">
      <div class="rg-text">
{a["inhalt"].strip()}
{faq_html}
        <p class="rg-hinweis">
          Dieser Beitrag gibt einen allgemeinen Überblick und ersetzt keine
          Energieberatung. Fördersätze und gesetzliche Vorgaben ändern sich; maßgeblich
          sind immer die zum Zeitpunkt der Antragstellung geltenden Richtlinien.
        </p>
      </div>
{seitenspalte(a["datei"])}    </div>

    <div class="wrap">
{CTA_BAND}    </div>
  </article>
</main>
"""
        + fuss(a["datei"])
    )


def uebersicht():
    beschreibung = ("Verständliche Antworten zu Heizungstausch, Sanierungsreihenfolge, "
                    "Förderung und Dämmung – von einem Energieberater aus dem "
                    "Alb-Donau-Kreis.")
    graph = [{
        "@type": "CollectionPage",
        "name": "Ratgeber Energetische Sanierung",
        "description": beschreibung,
        "inLanguage": "de-DE",
        "url": f"{DOMAIN}/ratgeber.html",
    }, {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Startseite",
             "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Ratgeber"},
        ],
    }, {
        "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": a["titel"],
             "url": f"{DOMAIN}/{a['datei']}"}
            for i, a in enumerate(ARTIKEL)
        ],
    }]

    karten = "".join(f"""      <article class="rg-eintrag reveal">
        {a["bild"]}
        <span class="rubrik">{a["rubrik"]}</span>
        <h2><a href="{a["datei"]}">{a["titel"]}</a></h2>
        <p>{a["anriss"]}</p>
        <a class="weiter" href="{a["datei"]}">Weiterlesen <span aria-hidden="true">&rarr;</span></a>
      </article>
""" for a in ARTIKEL)

    return (
        kopf("Ratgeber Energetische Sanierung | EBA Albdonau",
             beschreibung, "ratgeber.html")
        + json_ld({"@context": "https://schema.org", "@graph": graph})
        + f"""
<main id="inhalt">
{krumen(("Startseite", "index.html"), ("Ratgeber", None))}
  <header class="wrap rg-kopf">
    <span class="eyebrow">Ratgeber</span>
    <h1>Sanieren verstehen, bevor Sie investieren</h1>
    <p class="lead">
      Die Fragen, die uns im Erstgespräch am häufigsten gestellt werden – hier
      ausführlich beantwortet. Ohne Verkaufsabsicht, ohne Vorliebe für ein bestimmtes
      Gewerk.
    </p>
  </header>

  <div class="wrap rg-liste">
{karten}  </div>

  <!-- Einordnender Text unter den Karten: Die Uebersicht bestand vorher nur
       aus Kartenanrissen (208 Woerter) und hatte damit zu wenig eigenen
       Inhalt, um fuer eigene Suchanfragen zu ranken. -->
  <div class="wrap rg-inhalt">
    <div class="rg-text">
      <h2>Worauf es bei der energetischen Sanierung ankommt</h2>
      <p>
        Die meisten Fehler bei der Sanierung entstehen nicht beim Handwerk, sondern
        davor: bei der Reihenfolge, bei der Förderung und bei der Frage, welche
        Maßnahme sich am eigenen Haus überhaupt rechnet. Ein ungedämmtes
        Einfamilienhaus aus den 1970er Jahren verliert Wärme über Dach, Außenwand,
        Fenster und Kellerdecke – aber nicht gleichmäßig. Wer zuerst dort ansetzt, wo
        der größte Verlust sitzt, spart mit dem kleinsten Einsatz am meisten.
      </p>
      <p>
        Genauso wichtig ist der Zeitpunkt: <strong>Fördermittel müssen beantragt sein,
        bevor der Handwerkerauftrag vergeben wird.</strong> Wer erst beauftragt und
        dann den Antrag stellt, verliert den Zuschuss endgültig – das ist der
        häufigste und teuerste Fehler, den wir in der Beratung sehen.
      </p>

      <h2>Für wen diese Beiträge gedacht sind</h2>
      <p>
        Wir schreiben für Eigentümerinnen und Eigentümer von Ein- und
        Zweifamilienhäusern im Alb-Donau-Kreis und rund um Ulm, die vor einer
        Entscheidung stehen: Heizung erneuern, dämmen, Fenster tauschen – oder erst
        einmal rechnen. Die Beiträge nehmen niemandem die Entscheidung ab, aber sie
        machen die Grundlagen klar, auf denen sie getroffen wird.
      </p>
      <p>
        Jeder Beitrag nennt Größenordnungen statt Versprechen. Was Ihr Gebäude
        tatsächlich verbraucht und einspart, hängt von Baujahr, Bauweise, Lage und
        Nutzung ab – eine erste Einschätzung liefert der
        <a href="sanierungsrechner.html">Sanierungsrechner</a>, belastbare Zahlen der
        <a href="sanierungsfahrplan.html">individuelle Sanierungsfahrplan</a>.
      </p>

      <h2>Was hier bewusst nicht steht</h2>
      <p>
        Keine Produktempfehlungen und keine Herstellernamen. Wir verkaufen weder
        Heizungen noch Dämmstoffe und bekommen keine Provisionen – deshalb steht in
        diesen Texten, was sich rechnet, und nicht, was sich verkaufen lässt. Wo
        Fördersätze oder gesetzliche Vorgaben genannt werden, gilt der Stand zum
        Zeitpunkt der Veröffentlichung; maßgeblich sind immer die Richtlinien, die bei
        Ihrer Antragstellung gelten.
      </p>
    </div>
  </div>

  <div class="wrap">
{CTA_BAND}  </div>
</main>
"""
        + fuss()
    )


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists("index.html"):
        raise SystemExit("index.html nicht gefunden - Skript im Projektordner starten.")

    # Bilder zuerst pruefen. Ein fehlendes Foto faellt sonst erst im Browser
    # auf - als kaputtes Bild auf einer bereits veroeffentlichten Seite.
    fehlend = sorted({d for a in ARTIKEL
                      for d in re.findall(r'src="(bilder/[^"]+)"', a["bild"])
                      if not os.path.exists(d)})
    if fehlend:
        raise SystemExit("Diese Bilddateien fehlen:\n  " + "\n  ".join(fehlend))

    doppelt = [d for d in {a["datei"] for a in ARTIKEL}
               if sum(1 for a in ARTIKEL if a["datei"] == d) > 1]
    if doppelt:
        raise SystemExit("Dateiname doppelt vergeben: " + ", ".join(doppelt))

    for a in ARTIKEL:
        io.open(a["datei"], "w", encoding="utf-8", newline="\n").write(
            fuell(artikel_seite(a)))
        print(f"  geschrieben: {a['datei']}")

    io.open("ratgeber.html", "w", encoding="utf-8", newline="\n").write(
        fuell(uebersicht()))
    print("  geschrieben: ratgeber.html")
    print(f"\n{len(ARTIKEL)} Artikel + Uebersicht erzeugt.")
    print("Nicht vergessen: sitemap.xml ergaenzen und im Browser pruefen.")
