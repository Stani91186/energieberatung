# Projekt: Energieberatung-Website mit Sanierungsrechner

Statische Website mit 27 Seiten, direkt über GitHub Pages ausgeliefert.
Kein Build-Schritt, kein Framework, keine Abhängigkeiten. Von Hand gepflegt
werden nur acht Seiten – Ortsseiten, Ratgeber, Aktuelles und die Sitemap
entstehen aus Generatoren (siehe unten).

## Dateien

- `index.html` – Startseite (Landingpage) der Energieberatung
- `sanierungsrechner.html` – interaktiver Rechner mit Lead-Formular vor dem PDF-Download
- `u-wert-rechner.html` – zweiter Rechner: U-Werte aus dem Schichtaufbau,
  Dämmstärke für einen Zielwert, Hüllbilanz H′T mit Effizienzhaus-Einstufung.
  Eigener Selbsttest in der Konsole, siehe unten.
- `sanierungsfahrplan.html`, `energieausweis-ulm.html`,
  `hydraulischer-abgleich-ulm.html` – Leistungsseiten mit Festpreisen. Die
  beiden neuen sind aus der Hülle von `sanierungsfahrplan.html` gebaut und
  werden von `kopf-fuss-abgleichen.py` mitgepflegt (stehen in `ZIELE`).
  Fachliche Konsistenz der Abgleich-Seite mit dem Rechner: Einsparung
  „rund 8 %“ = `CONFIG.abgleichEinsparung`, Spanne „800–1.800 €“ =
  `CONFIG.kosten.abgleich`, „bei Wärmepumpe im Angebot enthalten“ =
  `CONFIG.imWpAngebotEnthalten` – wer eine Seite ändert, ändert beide.
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
   nie tief im Code ändern. **Der U-Wert-Rechner kopiert sie nicht**, sondern
   bekommt sie von `kopf-fuss-abgleichen.py` in seinen Block
   `GEMEINSAM:KENNWERTE` gelegt (Liste `KENNWERTE_KEYS` im Skript).
   Dort nichts von Hand ändern – beim nächsten Lauf ist es weg.
   Wird eine Kostenspanne geändert, gehört der Ratgebertext mitgeprüft, der
   sie nennt (Hinweis steht als Kommentar am betreffenden `ARTIKEL`-Eintrag).
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

## Aktuelles (News)

`aktuelles.html` wird von `news-erzeugen.py` erzeugt – **nicht von Hand
bearbeiten**. Meldungen stehen in der Liste `MELDUNGEN`, neueste zuerst; der
Generator sortiert ohnehin selbst.

Bewusst **eine** Seite mit Sprungzielen je Meldung statt einer Seite pro Woche:
Kurze Zusammenfassungen auf je eigener Seite ergäben 52 dünne Seiten im Jahr –
genau das Muster, vor dem drei SEO-Prüfungen gewarnt haben. Wird ein Thema groß
genug für eine eigene Seite, gehört es in den Ratgeber. Ab 40 Meldungen wandern
die ältesten automatisch nach `aktuelles-JAHR.html`.

Kopf, Fuß, CSS und die Bausteine `krumen()`, `json_ld()`, `CTA_BAND` kommen
**per Import aus `ratgeber-erzeugen.py`**, nicht aus einer vierten Kopie. Vier
eigene Kopfzeilen-Kopien waren schon einmal das Problem dieses Projekts.

**Der Bereich veröffentlicht vollautomatisch** (Wunsch des Betreibers, wöchentlich).
Deshalb stehen die Regeln nicht nur im Auftragstext, sondern als harte Prüfungen
in `pruefe()` – was durchfällt, wird gar nicht erst geschrieben:

- Quellen **nur** von `QUELL_HOSTS` (BAFA, KfW, dena, Energie-Effizienz-Expertenliste,
  BMWK, Bundesregierung, Bundestag, Bundesrat, gesetze-im-internet.de,
  Bundesanzeiger, recht.bund.de). Fachportale und Hersteller sind ausgeschlossen –
  über zweite Hand wird eine Förderaussage falsch.
- Pflichtfelder vollständig, `datum` ISO und nicht in der Zukunft
- `text` höchstens 400 Zeichen, ohne `€`, „wir", „unser" – eine Meldung
  **referiert die Quelle** und macht keine eigene Aussage
- Titel und Quell-URL je einmalig, Sprungziele eindeutig, Bilddatei vorhanden

**Diese Prüfungen nicht aufweichen** – sie sind die einzige Sicherung dagegen,
dass unbelegte Aussagen zu Förderrecht unter dem Namen des Betreibers live gehen.
Geprüft mit zwölf Testfällen, alle brechen korrekt ab.

Kategoriebilder in `bilder/news-*.jpg` werden wiederverwendet (`KATEGORIEN`);
wöchentlich ein neues Foto zu lizenzieren wäre der teuerste Teil.

## Sitemap

`sitemap.xml` wird von `sitemap-erzeugen.py` aus dem Dateibestand geschrieben –
**nicht mehr von Hand pflegen**. Datei da = Adresse drin. Prioritäten und
`changefreq` stehen als Musterliste `REGELN` im Skript; `aktuelles.html` bekommt
`weekly` und als `lastmod` das Datum der jüngsten Meldung. Seiten mit `noindex`
und `404.html` bleiben draußen, fehlendes `canonical` bricht ab.

## Kopf und Fuß

`index.html` ist die Vorlage für Kopfzeile, Handy-Menü, Aktionsleiste und
Fußbereich. Wer daran etwas ändert, ändert es **dort** und lässt danach laufen:

    python kopf-fuss-abgleichen.py     # Rechner, Fahrplan, Leistungsseiten, Rechtstexte
    python ortsseiten-erzeugen.py
    python ratgeber-erzeugen.py
    python news-erzeugen.py
    python sitemap-erzeugen.py         # immer zuletzt, liest den Dateibestand

Die abgeglichenen Bereiche stehen zwischen `GEMEINSAM:`-Markierungen – von Hand
Geändertes wird beim nächsten Lauf überschrieben. Nicht mit übertragen wird
`--maxw`: Der Rechner ist absichtlich schmaler als die Startseite.

## U-Wert-Rechner

`u-wert-rechner.html` ist der zweite Rechner und beantwortet eine andere Frage
als der erste: nicht „lohnt sich das?", sondern „welcher Aufbau ergibt welchen
U-Wert, und was fehlt zum Effizienzhaus?".

**Die Ehrlichkeitsgrenze ist Absicht und darf nicht aufgeweicht werden.** Eine
Effizienzhausstufe hat zwei Kriterien: Primärenergiebedarf QP und spezifischer
Transmissionswärmeverlust H′T. Der Rechner kann H′T exakt und QP gar nicht – QP
verlangt DIN V 18599 mit Anlagentechnik. Die Seite sagt deshalb nie „Sie
erreichen Effizienzhaus 55", sondern „Ihre Hülle erfüllt das H′T-Kriterium für
Effizienzhaus 55". Wer das zu einer Zusage umformuliert, macht aus einem
Werkzeug eine Falschaussage auf der Seite eines Fachberaters.

Normative Grundlage, alles im Objekt `UK` am Anfang des Scripts:

| Größe | Wert | Quelle |
|---|---|---|
| Effizienzhaus 40 / 55 / 70 / 85 | H′T ≤ 55 / 70 / 85 / 100 % | KfW |
| Referenzgebäude | Wand 0,28 · Dach 0,20 · Boden 0,35 · Fenster 1,3 · ΔU_WB 0,05 | Anlage 1 GEG/GModG |
| Höchstwerte bei Erneuerung | Wand 0,24 · Dach 0,24 · Fenster 1,3 · Erdreich 0,30 | Anlage 7 GEG/GModG |
| Innendämmung | R ≤ 0,5 nachweisfrei · bis 1,0 mit s_d ≥ 0,5 m · darüber Nachweis | DIN 4108-3 |
| Luftdichtheit | n50 ≤ 3,0 ohne, ≤ 1,5 mit Lüftungsanlage | GEG/GModG |
| Übergangswiderstände | Wand 0,13/0,04 · Dach 0,10/0,04 · Keller 0,17/0,17 · Boden 0,17/0 | DIN EN ISO 6946 |

**Zwei Kriterien, zwei getrennte Werkzeuge – das ist die Kernaussage der Seite:**
Beim H′T lässt sich nur zwischen Bauteilen umverteilen (Stellschrauben je
Bauteil, der Löser gleicht über einen kleineren Faktor k aus). Beim
Primärenergiebedarf wirken Wärmeerzeuger, Lüftung und PV. **Eine Wärmepumpe
rettet kein H′T-Kriterium** – dieser Satz steht bewusst im Rechner.

Die Primärenergiefaktoren in `FP` stammen aus Anlage 4 GEG/GModG (Gas 1,1 ·
Strom 1,8 · Holz 0,2 · PV vom eigenen Dach 0,0 · Umweltwärme 0,0) und sind
amtlich. Die Nutzungsgrade und Jahresarbeitszahlen in `ERZEUGER` sind
Anhaltswerte – deshalb rechnet der Rechner nur den **Vergleich der Erzeuger
untereinander** und nie eine QP-Zahl fürs Haus.

**Effizienzhaus Denkmal** erscheint nur, wenn im Fragebogen Denkmalschutz oder
besonders erhaltenswerte Bausubstanz gewählt wurde. Es hat kein
H′T-Kriterium – nur Primärenergie ≤ 160 % und angepasste Bauteilwerte – und
verlangt eine Eintragung der Kategorie „BEG: Wohngebäude Denkmal".

`BAUSTOFFE` enthält rund 55 Materialien mit λ-Anhaltswerten. Der sichtbare
Hinweis, dass für Förderanträge der deklarierte λ_D des Produkts zählt, gehört
zur Seite und bleibt stehen.

Zielwerte je Bauteil kommen aus `KENNWERTE.zielU`, also aus dem CONFIG des
Sanierungsrechners. `BASISZIEL` ist nur noch ein Alias darauf – vorher standen
dieselben sieben Zahlen an zwei Stellen.

### Zwei Richtungen, ein Löser

Der Rechner beantwortet zwei entgegengesetzte Fragen mit derselben Mechanik.
Je Bauteil hat der Nutzer vier Zustände zur Wahl (`G[id].modus`):

| Zustand | Bedeutung | im Löser |
|---|---|---|
| `offen` | der Löser entscheidet | frei über `k` |
| `geplant` | „ich mache 14 cm Mineralwolle" | fester U-Wert |
| `hoechstens` | „mehr geht bei mir nicht" | Untergrenze |
| `bleibt` | wird nicht angefasst | fester U-Wert = Ist |

Daraus entstehen zwei Karten: `festKarte()` und `grenzenKarte()`. Beide gehen
durch `zielUFuer(id, k, grenzen, fest)` in `paketFuer`. **Ein zweiter
Algorithmus wäre falsch** – die Ausgleichsrechnung fällt aus dieser einen
Mechanik heraus, weil `k` sinkt, sobald ein Bauteil festhängt.

`renderPlan()` zeigt daraus die Ampel je Stufe und darunter, welches Bauteil
wie viel brächte. **Die Wirkung ist exakt, nicht geschätzt**: H′T,ref hängt nur
an der Geometrie, deshalb gilt Δ%-Punkte = 100 · fx · ΔU · A / htRef
(`wirkung()`). Ein Selbsttest prüft das gegen die tatsächlich gerechnete
Bilanz.

Sind alle Bauteile festgelegt und die Stufe trotzdem verfehlt, wechselt der
Text von „was noch fehlt" zu „was Sie am Plan ändern müssten" – dann wird der
Löser einmal **ohne** die festen Werte gefragt. Die Summenzeile rechnet immer
selbst nach (`ergibt()`), nie über den Löserwert: Sobald eine wirkungslose
Zeile weggelassen wird, stimmte der sonst nicht mehr.

**Hier ist die Ehrlichkeitsgrenze am dünnsten.** Ein Plan-Ergebnis verführt zu
„Sie erreichen Effizienzhaus 55". Der Rechner sagt ausschließlich „Kriterium
erfüllt" und erklärt darunter, dass QP fehlt. Wer das umformuliert, macht aus
dem Werkzeug eine Zusage.

### Förderwerte (TMA)

`TMA` enthält die Bauteil-Anforderungswerte aus den Technischen
Mindestanforderungen zur **BEG-EM-Förderrichtlinie vom 17.07.2026** (in Kraft
seit 21.07.2026), Spalte Wohngebäude ab 19 °C:

| Bauteil | Regelfall | Denkmal / erhaltenswerte Bausubstanz |
|---|---|---|
| Außenwand | 0,20 | 0,45 |
| Dach, oberste Geschossdecke | 0,14 | kein U-Wert, höchstmögliche Dicke λ ≤ 0,040 |
| Fenster | 0,95 | 1,40 |
| Kellerdecke, Bodenplatte | 0,25 | – |
| Haustür | 1,30 | – |

**Der Vorbehalt gehört an jede Stelle, die die gelockerten Werte zeigt:** Die
Richtlinie lässt sie nur zu, wenn ein Sachverständiger der Kategorie
„BEG – Wohngebäude Denkmal" beteiligt ist – auch bei der einfachen
Einzelmaßnahme, nicht erst beim Effizienzhaus. **Der Betreiber hat diese
Eintragung nicht** (Stand 23.08.2026). Der Text führt deshalb auf
Zusammenarbeit und Weiterempfehlung, nicht auf einen Auftrag. Ändert sich die
Eintragung, sind `renderDenkmal()` und `planFoerderung()` die beiden Stellen.

Die Stufe **erhaltenswerte Bausubstanz** ist nicht auf Denkmäler beschränkt:
Es genügt eine Erhaltungssatzung nach § 172 Abs. 1 Nr. 1 BauGB, ein
Sanierungsgebiet nach § 142 BauGB oder eine kommunale Ausweisung. Bestätigt
wird das **von der Kommune**, formlos – nicht von der Denkmalbehörde.

### Grundstücksgrenze

Wählt der Nutzer bei der Wand den Grund „Grundstücksgrenze", erscheint
`grenzHinweis()`: Nach § 7c Nachbarrechtsgesetz Baden-Württemberg muss der
Nachbar eine überstehende Wärmedämmung **bis 25 cm** dulden. Das ist
**Landesrecht** – der Hinweis sagt das ausdrücklich, weil er außerhalb
Baden-Württembergs nicht gilt. Er steht drin, weil im Einsatzgebiet
regelmäßig auf Innendämmung ausgewichen wird, wo außen zulässig wäre.

`flaechenMittel()` deckt den Fall „außen wo erlaubt, innen an den geschützten
Flächen" ab. Die technischen FAQ zur BEG lassen zu, dass eine Teilfläche den
Anforderungswert verfehlt, solange der flächengewichtete Mittelwert über die
gesamte neu gedämmte Fläche stimmt.

`AUFBAUTEN` sind **Beispiele**, keine Statistik. Der Selbsttest prüft sie nur
gegen ein Plausibilitätsband (Faktor 0,5 bis 2,0) um die Baualterstabelle des
Sanierungsrechners – er soll vertippte λ-Werte fangen, nicht Übereinstimmung
mit einem Bestandsmittelwert erzwingen.

## Qualitätsprüfung nach JEDER Änderung am Rechner

`sanierungsrechner.html` im Browser öffnen und die Konsole prüfen:
Es muss `✅ SELBSTTEST BESTANDEN` erscheinen (4 Referenzhäuser + Plausibilität).
Für `u-wert-rechner.html` gilt dasselbe: dort muss
`✅ SELBSTTEST U-WERT-RECHNER BESTANDEN` erscheinen (30 Fälle: Handrechnung,
Umkehrprobe, DIN-4108-3-Schwellen, H′T-Referenzhaus, Stufengrenzen, typische
Aufbauten, Grenzen und Ausgleich, Primärenergie, feste Werte, Wirkung,
BEG-Anforderungswerte, Flächenmittel).
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
