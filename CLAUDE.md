# Projekt: Energieberatung-Website mit Sanierungsrechner

Statische Zwei-Seiten-Website, direkt über GitHub Pages ausgeliefert.
Kein Build-Schritt, kein Framework, keine Abhängigkeiten.

## Dateien

- `index.html` – Startseite (Landingpage) der Energieberatung
- `sanierungsrechner.html` – interaktiver Rechner mit Lead-Formular vor dem PDF-Download
- `impressum.html`, `datenschutz.html` – Pflichtseiten, aus beiden Hauptseiten verlinkt
- `robots.txt`, `sitemap.xml` – SEO (Domain muss zur echten Domain passen)
- `404.html` – Fehlerseite
- `fonts/` – lokal gehostete Schrift Roboto (Apache 2.0)
- `logo.png` – Logo „EBA Energieberater Albdonau“ (vom Betreiber geliefert,
  transparente Ränder beschnitten, auf 365×240 px verkleinert). Wird per
  `<img>` in Kopf- und Fußzeile aller Seiten eingebunden – NICHT durch
  SVG-Nachbauten ersetzen, das ist ausdrücklicher Wunsch des Betreibers.
  **Die Größe nicht wieder erhöhen:** Die Originaldatei war 1471×968 px und
  959 KB schwer bei 99 px Anzeigehöhe und machte damit 92 % des Ladegewichts
  jeder Seite aus. 240 px Höhe reicht für dreifache Punktdichte. Das Original
  liegt unverändert als `logo-original.png` daneben.
- `vorschau.jpg` – Vorschaubild 1200×630 für WhatsApp, LinkedIn, Facebook
  (`og:image`). Aus Logo und Seitenfarben gebaut. Die Ratgeberseiten setzen
  stattdessen ihr eigenes Artikelfoto ein; die Ortsseiten dürfen ihr Stadtfoto
  NICHT nehmen – die stehen unter CC-BY/CC-BY-SA und verlangen Namensnennung,
  die in einer geteilten Vorschau nicht mitreist.
- `CNAME` – enthält `energieberater-albdonau.de`. GitHub Pages braucht die
  Datei für eine eigene Domain **zusätzlich** zu den DNS-A-Records
  (185.199.108–111.153). Nicht löschen.
- `htaccess.txt` – nur für klassische Apache-Hoster relevant, auf GitHub Pages ohne Funktion

## Eiserne Regeln

1. **Alles bleibt in einer Datei**: CSS und JavaScript inline, keine externen
   Bibliotheken (kein Three.js, GSAP, jQuery, Chart.js …). Die Seiten sind bewusst
   leichtgewichtig – das ist ein SEO-/Performance-Feature, kein Zufall.
2. **Nichts von fremden Servern nachladen.** Insbesondere KEINE Google Fonts –
   das ist in Deutschland ein Abmahnrisiko. Die Schrift liegt in `fonts/` und
   wird per `@font-face` lokal eingebunden. Gilt auch für Icons, Bilder,
   Analytics und CDN-Skripte.
3. **Kein localStorage/sessionStorage** – Zustand nur in JavaScript-Variablen.
4. **Deutsch** in UI-Texten, Kommentaren und Commit-Messages.
5. Design-Farben nur über die CSS-Variablen im `:root`-Block ändern
   (Creme/Amber/Waldgrün-Palette, beide Dateien identisch halten).
6. Fachliche Kennwerte (U-Werte, Kosten, Fördersätze) stehen NUR im
   `CONFIG`-Objekt am Anfang des Scripts in `sanierungsrechner.html` –
   nie tief im Code ändern. Wird dort eine Kostenspanne geändert, gehört der
   Ratgebertext mitgeprüft, der sie nennt (Hinweis steht als Kommentar am
   betreffenden `ARTIKEL`-Eintrag).
7. Texte in `[eckigen Klammern]` sind bewusste Platzhalter des Betreibers.
   Das gilt auch für die beiden sichtbaren `[TODO]`-Kästen in
   `datenschutz.html` (AVV mit Supabase, Analytics) – sie sind Erinnerungen
   vor dem Livegang und müssen dann verschwinden, nicht vorher.
8. **Wenn sich die Datenverarbeitung ändert, muss `datenschutz.html` mitwachsen.**
   Neues Formularfeld, neuer Dienst, neues Cookie → Datenschutztext anpassen.
   Eine Erklärung, die nicht zur Seite passt, ist schlimmer als keine.
9. **Das Honorar steht ausschließlich im Abschnitt `PREISE` von `index.html`**,
   maschinenlesbar am `<section>`-Tag (`data-preis-isfp-ab`,
   `data-preis-foerderung-max`, `data-preis-eigen-ab`). Alle drei Skripte lesen
   es von dort: `kopf-fuss-abgleichen.py` füllt die
   `<b class="preis-wert" data-preis="…">`-Marken der handgepflegten Seiten,
   die beiden Generatoren setzen es über `preise()` bzw. die Platzhalter
   `{{PREIS_ISFP}}`, `{{PREIS_FOERDER}}`, `{{PREIS_EIGEN}}` ein.
   Preise nie an zweiter Stelle hart hinschreiben. Das FAQ-JSON-LD in
   `index.html` kann keine Marken tragen – `kopf-fuss-abgleichen.py` warnt
   deshalb, wenn die Beträge dort nicht mehr vorkommen.
   Rechtlich: Endpreise inklusive Umsatzsteuer (PAngV), Förderung immer mit
   „bis zu" und „sofern bewilligt".
10. **Keine erfundenen Kundenstimmen.** Der Abschnitt `#stimmen` in
   `index.html` ist gebaut, aber leer und trägt `hidden`; er erscheint erst,
   wenn echte Zitate eingesetzt werden. Vorlagen stehen als Kommentar darüber,
   das Vorgehen in `STIMMEN-SAMMELN.md`. Erfundene Bewertungen verstoßen gegen
   Anhang Nr. 23 zu §3 Abs. 3 UWG. Kein `Review`- oder `AggregateRating`-Schema:
   selbst gesammelte Bewertungen schließt Google von Rich Results aus.
   Echte Kundendaten gehören NICHT ins Repository – es ist öffentlich.

## Formulare und Leads

Beide Formulare (Kontakt auf der Startseite, Bericht-Anforderung im Rechner)
schreiben direkt in eine eigene Supabase-Datenbank:

- Projekt `energieberatung-website`, Region `eu-central-1` (Frankfurt)
- Tabelle `public.leads`, ansehen im Supabase Table Editor
- Zugangsdaten stehen als `SUPABASE_URL` / `SUPABASE_KEY` im Script beider Seiten

Der Schlüssel im Quelltext ist ein Publishable Key und bewusst öffentlich.
Die Sicherheit kommt aus der Datenbank: Row Level Security erlaubt `anon`
ausschließlich `INSERT`, die übrigen Rechte sind per `REVOKE` entzogen.
**Diese Regeln nicht aufweichen** – sonst kann jeder die Leads auslesen.
Prüfbefehl nach Änderungen an der Datenbank: ein `GET` auf
`/rest/v1/leads?select=*` mit dem öffentlichen Schlüssel muss `401` liefern.


## Ortsseiten

`energieberatung-*.html` werden von `ortsseiten-erzeugen.py` erzeugt – **nicht
von Hand bearbeiten**, Änderungen gehen beim nächsten Lauf verloren. Der
Generator schneidet CSS, Förderblock, Rechner-Teaser, Ablauf, Kontaktabschnitt
sowie die interaktive Haus-Grafik **samt Popup-JavaScript und Ereignis-Tracking**
bei jedem Durchlauf frisch aus `index.html`; Orts- und Startseite können also
nicht auseinanderlaufen. Aufbau je Ortsseite: Stadtfoto im Hero (Tabelle
`ORTSFOTOS`, Lizenzen in `bilder/LIZENZ.txt`), das anklickbare Haus steht
neben dem Ortstext. Nach Änderungen an `index.html` einmal
`python ortsseiten-erzeugen.py` ausführen.

Ortsspezifische Texte stehen in der Tabelle `ORTE` im Generator: `lage`,
`bausubstanz`, `besonderheit`, `typisch` und `isfp_hinweis` – jedes Feld ist
je Ort einzeln geschrieben, kein Baukasten mit ausgetauschtem Ortsnamen.
Ebenfalls je Ort: `entfernung_kurz` (Chip) und `entfernung_satz` (Fließtext).
Die beiden sind getrennt, weil ein einziges Feld in vier verschiedene Satzbauten
eingesetzt wurde und Dornstadt dadurch „wir sind direkt vor Ort entfernt" las.

Achtung: Seiten, die sich nur im Ortsnamen unterscheiden, straft Google als
Doorway Pages ab – die Wortüberschneidung sollte gemessen unter 65 % bleiben.
**Gemessen am 15.08.2026: 79,3 % im Mittel, schlechtestes Paar 80,3 %.** Der
Wert liegt also über der Grenze. Grund ist nicht zu wenig eigener Text, sondern
zu viel gemeinsamer: 1.194 von rund 1.541 Achtwortfolgen jeder Seite stehen
wortgleich auf allen acht Seiten (Förderblock, Rechner-Teaser, Ablauf, Kontakt,
FAQ – auf Wunsch des Betreibers überall gleich). Wer den Wert senken will, hat
zwei Wege: je Ort deutlich mehr eigenen Text, oder weniger gemeinsame Blöcke.
Ein weiterer gemeinsamer Abschnitt treibt ihn nach oben – vor dem Einbau messen:

    python -c "
    import re,io,glob,itertools
    def t(p):
        s=io.open(p,encoding='utf-8').read()
        s=re.sub(r'(?s)<script.*?</script>|<style.*?</style>|<!--.*?-->','',s)
        return re.findall(r'[A-Za-zÄÖÜäöüß]{2,}',re.sub(r'(?s)<[^>]+>',' ',s).lower())
    def sh(w,n=8): return set(tuple(w[i:i+n]) for i in range(len(w)-n+1))
    o=sorted(glob.glob('energieberatung-*.html'))
    v=[100*len(sh(t(a))&sh(t(b)))/len(sh(t(a))) for a,b in itertools.combinations(o,2)]
    print('Mittel',round(sum(v)/len(v),1),'% | schlechtestes',round(max(v),1),'%')"

## Ratgeber

`ratgeber.html` und `ratgeber-*.html` werden von `ratgeber-erzeugen.py` erzeugt –
ebenfalls **nicht von Hand bearbeiten**. Kopfzeile, Fußbereich und CSS schneidet
der Generator bei jedem Lauf frisch aus `index.html`.

Artikeltexte stehen in der Liste `ARTIKEL` im Generator; jeder Eintrag bringt
seine eigenen FAQ-Paare mit, aus denen das `FAQPage`-Schema entsteht. Neue
Artikel dort ergänzen, dann `python ratgeber-erzeugen.py` ausführen und die
Adresse in `sitemap.xml` eintragen.

Zwei Dinge, die man leicht übersieht:

- **Die Reihenfolge in `ARTIKEL` ist nicht kosmetisch.** `seitenspalte()` zeigt
  auf jeder Artikelseite die ersten drei Einträge der Liste. Deshalb steht
  „Was kostet eine Energieberatung?" auf Platz 1 – die kommerziellste Anfrage
  bekommt so von jedem anderen Artikel einen Link.
- **Preise nur über Platzhalter.** `{{PREIS_ISFP}}`, `{{PREIS_FOERDER}}`,
  `{{PREIS_EIGEN}}` werden von `fuell()` auf der fertigen Seite ersetzt – das
  bedient Fließtext, FAQ, Meta-Beschreibung, Übersichtskarte und JSON-LD in
  einem Zug. Ein unbekannter Platzhalter bricht den Lauf ab, statt sichtbar
  auf der Seite zu landen.

Vor dem Schreiben prüft der Generator, ob jede Bilddatei existiert und kein
Dateiname doppelt vergeben ist. Beides schlug vorher erst im Browser auf.

In den Artikeltexten deutsche Anführungszeichen `„…“` verwenden (U+201E/U+201C,
so wie `index.html`). Ein gerades `"` als Schlusszeichen beendet in den
`"…"`-Feldern von `ARTIKEL` den Python-String und bricht den Generator.

Jeder Artikel bringt im Feld `bild` ein Foto aus `bilder/` mit (Wunsch des
Betreibers: echte Fotos von Pexels). Die Dateien liegen **selbst gehostet**
in `bilder/` – niemals von images.pexels.com hotlinken (Regel 2). Für jedes
Bild steht der Nachweis (ID, Fotograf, Quelle, Lizenz) in `bilder/LIZENZ.txt`;
neue Bilder dort nachtragen. Die Pexels-Lizenz erlaubt kommerzielle Nutzung
ohne Namensnennung, ist aber **nicht** CC0.

## Kopf und Fuß

`index.html` ist die Vorlage für Kopfzeile, Handy-Menü, Aktionsleiste und
Fußbereich. Wer daran etwas ändert, ändert es **dort** und lässt danach laufen:

    python kopf-fuss-abgleichen.py     # Rechner, Fahrplan, Impressum, Datenschutz
    python ortsseiten-erzeugen.py
    python ratgeber-erzeugen.py

Die abgeglichenen Bereiche stehen zwischen `GEMEINSAM:`-Markierungen – von Hand
Geändertes wird beim nächsten Lauf überschrieben. Nicht mit übertragen wird
`--maxw`: Der Rechner ist absichtlich schmaler als die Startseite.

## Qualitätsprüfung nach JEDER Änderung am Rechner

`sanierungsrechner.html` im Browser öffnen und die Konsole prüfen:
Es muss `✅ SELBSTTEST BESTANDEN` erscheinen (4 Referenzhäuser + Plausibilität).
Schlägt ein Fall fehl, wurde das Rechenmodell beschädigt – Änderung zurücknehmen
oder CONFIG korrigieren. Zusätzlich: Seite bei 390 px Breite ohne horizontales
Scrollen, Wizard einmal komplett durchklicken.

## Deployment

GitHub Pages veröffentlicht automatisch bei jedem Push auf `main`
(1–2 Minuten Verzögerung). Es gibt keinen weiteren Deploy-Schritt.

**Nach jeder abgeschlossenen, geprüften Änderung: committen und pushen**
(kurze deutsche Commit-Message, was und warum). Vor dem ersten Push einer
Sitzung `git pull` ausführen.

## Kontext für sinnvolle Vorschläge

Betreiber ist Stanislaw Tsukerman, selbstständiger Energieberater in Dornstadt
bei Ulm, eingetragen in der dena-Energie-Effizienz-Expertenliste. Einsatzgebiet
Alb-Donau-Kreis und rund 50 km um Ulm. Telefon 0152 24290826.
Zweck der Website: Anfragen (Leads) für Erstgespräche generieren.
Der Rechner ist bewusst neutral gehalten – die Wärmepumpe wird NICHT in den
Vordergrund gestellt; günstige Maßnahmen und Eigenleistung zuerst.
Rechtlich wichtig: Disclaimer („Orientierung, keine Energieberatung") und die
Förder-Fußnoten nie entfernen; keine Erfolgsversprechen ohne „bis zu"/„ca.".
