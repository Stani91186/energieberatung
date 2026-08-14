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
/* hyphens + overflow-wrap: Die Punkte sind Flexcontainer, deren Mindestbreite
   vom laengsten Wort bestimmt wird. Ein langes Kompositum ("Mindest-
   anforderungen") schob sonst auf schmalen Handys die ganze Seite auf. */
.rg-text ul li{display:flex;gap:11px;margin-bottom:10px;color:var(--ink-2);hyphens:auto;overflow-wrap:anywhere}
.rg-text ul li::before{content:"";width:7px;height:7px;flex:none;margin-top:10px;border-radius:50%;background:var(--amber)}
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
.krumen{padding:108px 0 0;font-size:.82rem;color:var(--muted)}
.krumen ol{display:flex;flex-wrap:wrap;gap:8px;list-style:none}
.krumen li::after{content:"\\203A";margin-left:8px;color:var(--line)}
.krumen li:last-child::after{content:""}
.krumen a:hover{color:var(--amber-deep);text-decoration:underline;text-underline-offset:3px}

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

def kopf(titel, beschreibung, datei, aktiv_ratgeber=True):
    """Gemeinsamer Seitenkopf."""
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
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23C07A2E'/%3E%3Cg fill='none' stroke='%23fff' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M7 15 16 8l9 7'/%3E%3Cpath d='M9.5 13.6V24h13V13.6'/%3E%3Cpath d='M13.5 24v-5h5v5'/%3E%3C/g%3E%3C/svg%3E">
<meta property="og:type" content="article">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="Tsukerman Energieberatung">
<meta property="og:title" content="{titel}">
<meta property="og:description" content="{beschreibung}">
<meta property="og:url" content="{DOMAIN}/{datei}">
<meta name="twitter:card" content="summary_large_image">
<style>
{stil()}
</style>
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
      <a href="ratgeber.html"{' aria-current="page"' if aktiv_ratgeber else ''}>Ratgeber</a>
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
  <a href="ratgeber.html">Ratgeber</a>
  <a href="sanierungsfahrplan.html">Sanierungsfahrplan</a>
  <a href="sanierungsrechner.html">Sanierungsrechner</a>
  <a href="index.html#kontakt">Kontakt</a>
  <a href="index.html#kontakt" class="btn btn-primary">Kostenloses Erstgespräch</a>
</nav>

<div class="mobile-bar">
  <a href="tel:{TEL_LINK}" class="btn btn-amber">Anrufen</a>
  <a href="index.html#kontakt" class="btn btn-primary">Anfrage senden</a>
</div>
"""

FUSS = f"""
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
        <h4>Ratgeber</h4>
        {{ratgeber_links}}
      </div>
      <div class="footer-col">
        <h4>Kontakt</h4>
        <a href="tel:{TEL_LINK}">{TEL_ANZEIGE}</a>
        <!-- [TODO] echte E-Mail-Adresse eintragen -->
        <a href="mailto:kontakt@energieberater-albdonau.de">[E-Mail eintragen]</a>
        <address style="font-style:normal">Griesweg 20<br>89160 Dornstadt</address>
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
# ---------------------------------------------------------------------------
ARTIKEL = [
{
 "datei": "ratgeber-heizung-tauschen-pflicht.html",
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
 "datei": "ratgeber-reihenfolge-sanierung.html",
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
 "datei": "ratgeber-kellerdecke-daemmen.html",
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
 "datei": "ratgeber-sanieren-schwaebische-alb.html",
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
        gedämmt ist".
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
    """Rechte Spalte: Rechner, Kontakt, weitere Artikel."""
    weitere = [a for a in ARTIKEL if a["datei"] != aktuell][:3]
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
        "publisher": {"@type": "Organization", "name": "Tsukerman Energieberatung",
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
        kopf(a["seitentitel"], a["beschreibung"], a["datei"])
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
        <span class="rubrik">{a["rubrik"]}</span>
        <h2><a href="{a["datei"]}">{a["titel"]}</a></h2>
        <p>{a["anriss"]}</p>
        <a class="weiter" href="{a["datei"]}">Weiterlesen <span aria-hidden="true">&rarr;</span></a>
      </article>
""" for a in ARTIKEL)

    return (
        kopf("Ratgeber Energetische Sanierung | Tsukerman Energieberatung",
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

    for a in ARTIKEL:
        io.open(a["datei"], "w", encoding="utf-8", newline="\n").write(artikel_seite(a))
        print(f"  geschrieben: {a['datei']}")

    io.open("ratgeber.html", "w", encoding="utf-8", newline="\n").write(uebersicht())
    print("  geschrieben: ratgeber.html")
    print(f"\n{len(ARTIKEL)} Artikel + Uebersicht erzeugt.")
    print("Nicht vergessen: sitemap.xml ergaenzen und im Browser pruefen.")
