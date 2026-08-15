# Sichtbarkeit aufbauen: Google-Profil, Verzeichnisse, Backlinks

Die Website ist fertig und technisch sauber. Was jetzt über die Platzierung
entscheidet, passiert **außerhalb** der Website – und das kann nur der
Betreiber selbst tun, weil überall Konten und Bestätigungen nötig sind.

Reihenfolge ist bewusst gewählt: erst die Domain, dann Google, dann der Rest.
Alles darunter wirkt erst, wenn die Domain auf GitHub Pages zeigt
(siehe README, Punkt 0).

---

## 1. Google-Unternehmensprofil – der stärkste Hebel

Bei „energieberater ulm" zeigt Google zuerst die Karte mit drei lokalen
Einträgen, erst darunter die normalen Treffer. In diese Karte kommt man
**nur** über das Unternehmensprofil – keine Website der Welt ersetzt das.

**Anlegen:** business.google.com → Unternehmen hinzufügen.

Beim Ausfüllen wichtig:

- **Name:** exakt `EBA Energieberater Albdonau` – NICHT „Energieberater Ulm
  Albdonau" oder ähnliche Keyword-Anreicherungen. Das verstößt gegen die
  Google-Richtlinien und führt zur Sperrung des Profils.
- **Kategorie:** Hauptkategorie „Energieberater". Weitere Kategorien:
  „Gutachter", „Beratung".
- **Adresse:** Griesweg 20, 89160 Dornstadt – **zeichengenau** wie im
  Impressum. Google gleicht Name/Adresse/Telefon über alle Quellen ab;
  jede Abweichung („Str." vs „Straße") kostet Vertrauen.
- **Telefon:** 0152 24290826 – dieselbe Schreibweise wie auf der Website.
- **Einzugsgebiet:** Dornstadt, Ulm, Blaustein, Langenau, Ehingen,
  Laichingen, Blaubeuren, Erbach. Als „Unternehmen mit Einzugsgebiet"
  eintragen, wenn Kunden nicht ins Büro kommen.
- **Website:** https://energieberater-albdonau.de/
- **Öffnungszeiten:** Mo–Fr 8–18 Uhr (wie auf der Website).
- **Leistungen:** die vier Leistungsseiten als einzelne Leistungen anlegen
  (Sanierungsfahrplan, Energieausweis, Hydraulischer Abgleich,
  Baubegleitung) – Preise dürfen dort stehen, sie sind ja veröffentlicht.
- **Fotos:** echtes Porträt, Bürogebäude, ein Termin vor Ort (mit
  Einverständnis). Profile mit Fotos bekommen messbar mehr Anfragen.

**Nach der Bestätigung** (Postkarte oder Video-Verifizierung, dauert Tage):

- **Bewertungen sind der Rankingfaktor Nummer eins der Karte.** Nach jedem
  abgeschlossenen Auftrag den Profil-Kurzlink per E-Mail mitschicken – die
  Vorlage aus STIMMEN-SAMMELN.md um den Google-Link ergänzen. Niemals
  Bewertungen kaufen oder von Bekannten schreiben lassen; Google erkennt
  Muster, und gekaufte Bewertungen sind zusätzlich wettbewerbswidrig.
- **Auf jede Bewertung antworten**, auch auf kritische – sachlich, kurz.
- Alle paar Wochen einen **Beitrag** einstellen (neuer Ratgeberartikel
  eignet sich: Bild + zwei Sätze + Link).

**Danach in `index.html` nachtragen:** im JSON-LD-Kommentar ist ein
`sameAs`-Feld vorbereitet – die Profil-URL dort eintragen und
`python kopf-fuss-abgleichen.py`, `python ortsseiten-erzeugen.py`,
`python ratgeber-erzeugen.py` laufen lassen.

---

## 2. Einträge, die Sie ohnehin haben – nur ohne Link

Die wertvollsten Backlinks für einen Energieberater sind die, die
Qualifikation belegen. Zwei davon existieren schon und müssen nur um die
Website ergänzt werden:

| Wo | Was tun | Warum |
|---|---|---|
| **Energie-Effizienz-Expertenliste** (energie-effizienz-experten.de) | Im eigenen Profil die Website-URL eintragen | Der Eintrag ist die fachliche Grundlage des Geschäfts – und ein Link von einer Bundes-Website. Die Seite verweist an 29 Stellen auf diese Liste; der Rückweg fehlt noch. |
| **BAFA-Beraterliste** | Prüfen, ob der Eintrag die Website nennt | dito |
| **dena-Profil** | Website und Telefonnummer prüfen | Muss mit Impressum übereinstimmen |

---

## 3. Verzeichnisse: wenige, aber konsistent

Nicht in 50 Verzeichnisse eintragen – das bringt nichts und erzeugt
Karteileichen mit veralteten Daten. Diese reichen:

- Google-Unternehmensprofil (Punkt 1)
- Bing Places (bingplaces.com – importiert das Google-Profil automatisch)
- Apple Business Connect (businessconnect.apple.com – für Apple Maps)
- 11880.com und Gelbe Seiten (kostenlose Basiseinträge)
- Handwerkskammer/IHK-Firmenverzeichnis, je nach Mitgliedschaft

**Eiserne Regel:** überall exakt dieselben Angaben – Name, Anschrift,
Telefonschreibweise, Öffnungszeiten. Ein Dokument mit den Stammdaten
anlegen und nur daraus kopieren.

---

## 4. Backlinks, die realistisch erreichbar sind

Für ein lokales Einzelbüro zählen wenige gute regionale Links mehr als
hundert gekaufte. Gekaufte Links nie – das Risiko einer Google-Abstrafung
trägt die Domain jahrelang.

Realistische Wege, grob nach Aufwand:

1. **Gemeinde und Region:** Dornstadt hat ein Gewerbeverzeichnis auf
   dornstadt.de – Eintrag anfragen. Ebenso die Wirtschaftsförderung des
   Alb-Donau-Kreises.
2. **Energieagentur:** Die Regionale Energieagentur Ulm führt
   Beraterlisten und Veranstaltungen. Vortrag anbieten („Sanieren auf der
   Alb – was zuerst?") → Veranstaltungsseite verlinkt.
3. **Lokalpresse:** Südwest Presse und Wochenblätter nehmen Fachbeiträge
   zu Förderthemen. Der Ratgeber liefert die Vorlagen; ein Artikel über
   die Förderkulisse mit Nennung „Energieberater aus Dornstadt" bringt
   den wertvollsten Linktyp überhaupt.
4. **Handwerksbetriebe der Region:** Wer regelmäßig zusammenarbeitet,
   verlinkt sich gegenseitig unter „Partner" – natürlich und thematisch
   passend.
5. **Vereine/Sponsoring:** kleine Sponsorings werden fast immer mit
   Logo + Link auf der Vereinsseite bedankt.

---

## 5. Social Media: nur, was durchgehalten wird

Für Leadgewinnung in dieser Branche und Region zählt ein gepflegtes
Google-Profil mehr als alle sozialen Netzwerke zusammen. Wenn Social
Media, dann:

- **LinkedIn-Unternehmensseite** – geringer Pflegeaufwand, seriöses
  Umfeld, und der Eintrag verlinkt die Website. Je neuer Ratgeberartikel
  ein kurzer Beitrag.
- **Instagram nur mit echten Baustellenfotos** (Einverständnis der
  Eigentümer einholen). Ein seit Monaten totes Profil schadet mehr als
  keines.

Jedes angelegte Profil in das `sameAs`-Feld im JSON-LD von `index.html`
eintragen (Anleitung steht dort als Kommentar), danach die drei Skripte
laufen lassen.

---

## 6. Nach der DNS-Umstellung: Google anstoßen

Sobald die Domain auf GitHub Pages zeigt:

1. **Search Console** (search.google.com/search-console): Property
   `energieberater-albdonau.de` anlegen, per DNS-TXT-Eintrag bestätigen.
2. **Sitemap einreichen:** `https://energieberater-albdonau.de/sitemap.xml`
3. Unter „URL-Prüfung" die Startseite und die drei Leistungsseiten
   einzeln zur Indexierung anmelden – das beschleunigt die ersten Tage.
4. Nach zwei Wochen unter „Leistung" prüfen, für welche Suchanfragen
   Eindrücke entstehen. Das ist ab dann die ehrlichste Datenquelle –
   ehrlicher als jedes SEO-Tool.

---

*Keine Kundendaten in diese Datei – das Repository ist öffentlich.*
