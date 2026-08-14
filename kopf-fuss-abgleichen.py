#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOPF UND FUSS ABGLEICHEN
========================
Schiebt Kopfzeile, Handy-Menue, Aktionsleiste und Fussbereich aus
index.html in alle anderen von Hand gepflegten Seiten.

    Aufruf:  python kopf-fuss-abgleichen.py

WARUM ES DAS GIBT
-----------------
Jede Seite hatte ihre eigene Kopie von Kopf und Fuss. Dadurch liefen sie
auseinander: die Startseite hatte fuenf Fussspalten mit Siegelleiste, die
Ortsseiten vier, die Ratgeber drei, Impressum und Datenschutz gar keine.
Auch die Menuepunkte unterschieden sich von Seite zu Seite. Das faellt beim
Wechseln zwischen den Seiten sofort auf.

Jetzt gilt: index.html ist die Vorlage. Wer Kopf oder Fuss aendert, aendert
sie DORT und laesst danach dieses Skript und die beiden Generatoren laufen.

    python kopf-fuss-abgleichen.py
    python ortsseiten-erzeugen.py
    python ratgeber-erzeugen.py

WAS UEBERTRAGEN WIRD
--------------------
1. Das Markup zwischen <header class="site-header"> und <main>
2. Der komplette <footer class="site-footer">
3. Die zugehoerigen CSS-Regeln (Kopf, Menue, Knoepfe, Fuss, Siegel)
4. Ein kleiner Skriptblock fuer Burger-Menue und schrumpfende Kopfzeile

Die eingesetzten Bereiche stehen zwischen Markierungen (GEMEINSAM:...) und
werden bei jedem weiteren Lauf einfach ersetzt.

WAS BEWUSST NICHT UEBERTRAGEN WIRD
----------------------------------
--maxw: Der Rechner ist schmaler als die Startseite. Wuerde die Breite
mitkommen, liefe sein Layout auseinander.
"""

import io, os, re

VORLAGE = "index.html"
ZIELE = ["sanierungsrechner.html", "sanierungsfahrplan.html",
         "impressum.html", "datenschutz.html"]

# CSS-Regeln, die zum gemeinsamen Rahmen gehoeren. Alles, was mit einem
# dieser Namen anfaengt, wird mit uebernommen.
RAHMEN = (".site-header", ".header-inner", ".header-cta", ".header-links",
          ".header-phone", ".cta-kurz", ".cta-lang",
          ".logo", ".nav", ".burger", ".mobile-nav", ".mobile-bar",
          ".skip-link", ".site-footer", ".footer-", ".badges", ".badge",
          ".btn")

# Die Startseite setzt globale Grundregeln (a ohne Unterstrich, svg als Block),
# auf die der Rahmen baut. Die Zielseiten haben eigene, teils andere
# Grundregeln - deshalb kommen diese hier NUR fuer den Rahmen mit, auf die
# Rahmen-Container eingegrenzt, damit sie den Seiteninhalt nicht umstylen.
RESETS = """\
.site-header a,.site-footer a,.mobile-nav a,.mobile-bar a{text-decoration:none;color:inherit}
.site-header img,.site-header svg,.site-footer img,.site-footer svg,
.mobile-bar svg{display:block;max-width:100%}
.site-header ul,.site-footer ul{list-style:none;margin:0;padding:0}
.burger{font:inherit;cursor:pointer}
/* Der Rahmen bringt seine Breite selbst mit: Impressum/Datenschutz begrenzen
   .wrap auf 820px (richtig fuer den Fliesstext), der Rechner auf 980px. Ohne
   diese Regel erbt der Kopf die schmale Breite - auf dem Impressum wurde das
   Logo dadurch bis auf 0px zusammengedrueckt. 1180px = --maxw der Startseite. */
.site-header .wrap,.site-footer .wrap{max-width:1180px}"""

SKRIPT = """<script>
'use strict';
/* Gemeinsamer Rahmen: Burger-Menue und schrumpfende Kopfzeile.
   Aus index.html uebernommen - nicht hier aendern, sondern dort. */
(function(){
  var kopf = document.querySelector('.site-header');
  if(kopf){
    var beimScrollen = function(){ kopf.classList.toggle('stuck', window.scrollY > 24); };
    beimScrollen();
    window.addEventListener('scroll', beimScrollen, {passive:true});
  }
  var burger = document.getElementById('burger');
  var menue  = document.getElementById('mobileNav');
  if(burger && menue){
    var setzen = function(offen){
      menue.classList.toggle('open', offen);
      burger.classList.toggle('open', offen);
      burger.setAttribute('aria-expanded', offen ? 'true' : 'false');
      burger.setAttribute('aria-label', offen ? 'Menü schließen' : 'Menü öffnen');
    };
    burger.addEventListener('click', function(){ setzen(!menue.classList.contains('open')); });
    menue.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){ setzen(false); });
    });
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape' && menue.classList.contains('open')){ setzen(false); burger.focus(); }
    });
  }
})();
</script>"""


# ---------------------------------------------------------------------------
# CSS zerlegen
# ---------------------------------------------------------------------------
def bloecke(css):
    """Zerlegt CSS in Bloecke der obersten Ebene: (Selektor, Rumpf, Ganzes)."""
    aus, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        kopf = css[i:j]
        tiefe, k = 1, j + 1
        while k < n and tiefe:
            if css[k] == "{":
                tiefe += 1
            elif css[k] == "}":
                tiefe -= 1
            k += 1
        aus.append((kopf, css[j + 1:k - 1], css[i:k]))
        i = k
    return aus


def nur_selektor(kopf):
    return re.sub(r"/\*.*?\*/", "", kopf, flags=re.S).strip()


def ist_rahmen(kopf):
    sel = nur_selektor(kopf)
    if not sel:
        return False
    return any(t.strip().startswith(RAHMEN) for t in sel.split(","))


def rahmen_css(css):
    """Alle Regeln des gemeinsamen Rahmens, Reihenfolge bleibt erhalten."""
    teile = []
    for kopf, rumpf, ganz in bloecke(css):
        sel = nur_selektor(kopf)
        if sel.startswith("@media"):
            innen = [g.strip() for k2, r2, g in bloecke(rumpf) if ist_rahmen(k2)]
            # die Kopfhoehen-Variablen haengen am :root im selben Block
            wurzel = [g.strip() for k2, r2, g in bloecke(rumpf)
                      if nur_selektor(k2) == ":root" and "--kopf" in r2]
            if innen or wurzel:
                teile.append(sel + "{\n" + "\n".join(wurzel + innen) + "\n}")
        elif sel.startswith("@"):
            continue
        elif ist_rahmen(kopf):
            teile.append(ganz.strip())
    return "\n".join(teile)


def kopfhoehen(css):
    """Nur --kopf und --kopf-klein aus dem :root der Vorlage. Die uebrigen
    Variablen bleiben aussen vor - der Rechner hat zum Beispiel eine eigene
    Maximalbreite, die nicht ueberschrieben werden darf."""
    werte = []
    for name in ("--kopf", "--kopf-klein"):
        m = re.search(re.escape(name) + r":\s*([^;]+);", css)
        if not m:
            raise SystemExit(f"{name} nicht in {VORLAGE} gefunden")
        werte.append(f"{name}:{m.group(1).strip()}")
    return ":root{" + ";".join(werte) + "}"


# ---------------------------------------------------------------------------
# Markup schneiden
# ---------------------------------------------------------------------------
def schneide(text, von, bis, name, mit_ende=True):
    i = text.find(von)
    if i < 0:
        raise SystemExit(f"'{name}': Anfang nicht gefunden")
    j = text.find(bis, i)
    if j < 0:
        raise SystemExit(f"'{name}': Ende nicht gefunden")
    return text[i:j + len(bis)] if mit_ende else text[i:j]


def absolut(markup):
    """Sprungmarken der Startseite absolut machen. Auf einer Unterseite
    zeigt '#leistungen' sonst auf einen Abschnitt, den es nicht gibt."""
    markup = markup.replace('href="#top"', 'href="index.html"')
    return re.sub(r'href="#(?!\s*")', 'href="index.html#', markup)


def ersetze_bereich(s, marke, inhalt, von, bis, name, mit_ende=True):
    """Beim ersten Lauf wird der vorhandene Bereich gesucht und durch den
    markierten ersetzt; danach genuegt die Markierung."""
    a, e = f"<!-- GEMEINSAM:{marke} -->", f"<!-- /GEMEINSAM:{marke} -->"
    neu = f"{a}\n{inhalt}\n{e}"
    if a in s and e in s:
        i, j = s.find(a), s.find(e) + len(e)
        return s[:i] + neu + s[j:]
    i = s.find(von)
    if i < 0:
        raise SystemExit(f"{name}: '{von}' nicht gefunden")
    j = s.find(bis, i)
    if j < 0:
        raise SystemExit(f"{name}: '{bis}' nicht gefunden")
    ende = j + len(bis) if mit_ende else j
    return s[:i] + neu + ("\n" if not mit_ende else "") + s[ende:]


# ---------------------------------------------------------------------------
def main():
    if not os.path.exists(VORLAGE):
        raise SystemExit("index.html nicht gefunden - im Projektordner starten.")
    v = io.open(VORLAGE, encoding="utf-8").read()

    # Der Kopfbereich endet mit der Aktionsleiste, NICHT erst bei <main>:
    # dazwischen stehen in index.html die gemeinsamen SVG-Definitionen
    # (rund 10 KB), die auf den anderen Seiten nichts zu suchen haben.
    i = v.find('<header class="site-header"')
    mb = v.find('<div class="mobile-bar">', i)
    if i < 0 or mb < 0:
        raise SystemExit("Kopfbereich oder Aktionsleiste nicht in index.html gefunden")
    ende = v.find("</div>", mb) + len("</div>")
    kopf_markup = absolut(v[i:ende])
    fuss_markup = absolut(schneide(v, '<footer class="site-footer">', "</footer>",
                                   "Fussbereich"))
    css_v = re.search(r"<style>\n(.*?)\n</style>", v, re.S).group(1)
    css = kopfhoehen(css_v) + "\n" + RESETS + "\n" + rahmen_css(css_v)

    print(f"Vorlage {VORLAGE}: {len(kopf_markup)} Zeichen Kopf, "
          f"{len(fuss_markup)} Zeichen Fuss, {len(css)} Zeichen CSS\n")

    for p in ZIELE:
        s = io.open(p, encoding="utf-8").read()
        s = ersetze_bereich(s, "KOPF", kopf_markup, '<header class="site-header"',
                            "<main", p, mit_ende=False)   # erster Lauf: bis <main
        s = ersetze_bereich(s, "FUSS", fuss_markup, '<footer class="site-footer">',
                            "</footer>", p)
        # CSS ans Ende des Stylesheets - spaeter heisst gewinnt
        css_block = ("/* GEMEINSAM:CSS */\n"
                     "/* Kopf, Menue, Knoepfe und Fuss stammen aus index.html.\n"
                     "   Aenderungen dort vornehmen, dann kopf-fuss-abgleichen.py\n"
                     "   laufen lassen - hier werden sie ueberschrieben. */\n"
                     + css + "\n/* /GEMEINSAM:CSS */")
        if "/* GEMEINSAM:CSS */" in s:
            s = re.sub(r"/\* GEMEINSAM:CSS \*/.*?/\* /GEMEINSAM:CSS \*/",
                       lambda m: css_block, s, flags=re.S)
        else:
            s = s.replace("\n</style>", "\n\n" + css_block + "\n</style>", 1)
        # Skript vor </body>
        js_block = f"<!-- GEMEINSAM:JS -->\n{SKRIPT}\n<!-- /GEMEINSAM:JS -->"
        if "<!-- GEMEINSAM:JS -->" in s:
            s = re.sub(r"<!-- GEMEINSAM:JS -->.*?<!-- /GEMEINSAM:JS -->",
                       lambda m: js_block, s, flags=re.S)
        else:
            s = s.replace("\n</body>", "\n\n" + js_block + "\n</body>", 1)
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        print("  abgeglichen:", p)

    print("\nJetzt noch die Generatoren laufen lassen:")
    print("  python ortsseiten-erzeugen.py")
    print("  python ratgeber-erzeugen.py")


if __name__ == "__main__":
    main()
