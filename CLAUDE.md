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
6. Fachliche Kennwerte (U-Werte, Kosten, Fördersätze, Preise) stehen NUR im
   `CONFIG`-Objekt am Anfang des Scripts in `sanierungsrechner.html` –
   nie tief im Code ändern.
7. Texte in `[eckigen Klammern]` sind bewusste Platzhalter des Betreibers.
8. **Wenn sich die Datenverarbeitung ändert, muss `datenschutz.html` mitwachsen.**
   Neues Formularfeld, neuer Dienst, neues Cookie → Datenschutztext anpassen.
   Eine Erklärung, die nicht zur Seite passt, ist schlimmer als keine.

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
Generator schneidet CSS, Hero-Grafik, Förderblock, Ablauf und Kontaktabschnitt
bei jedem Durchlauf frisch aus `index.html`; Orts- und Startseite können also
nicht auseinanderlaufen. Nach Änderungen an `index.html` einmal
`python ortsseiten-erzeugen.py` ausführen.

Ortsspezifische Texte stehen in der Tabelle `ORTE` im Generator. Achtung:
Seiten, die sich nur im Ortsnamen unterscheiden, straft Google als
Doorway Pages ab – die Wortüberschneidung sollte gemessen unter 65 % bleiben.

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
