# Kundenstimmen einsammeln

Der Bereich „Stimmen" auf der Startseite ist fertig gebaut und **unsichtbar**,
solange kein Zitat eingetragen ist. Sobald das erste drinsteht, erscheint er
automatisch. Diese Anleitung beschreibt, wie Sie an brauchbare Zitate kommen.

> **Wichtig, bevor Sie anfangen:** In diese Datei gehören **keine** Kundendaten.
> Das Repository ist öffentlich und GitHub Pages liefert jede Datei aus –
> eine Liste mit Namen und E-Mail-Adressen wäre unter
> `energieberater-albdonau.de/STIMMEN-SAMMELN.md` für jeden abrufbar.
> Die eigentliche Sammelliste führen Sie außerhalb des Projektordners,
> zum Beispiel als Notiz am Lead im Supabase-Dashboard.

---

## Warum keine erfundenen Zitate

Anhang Nr. 23 zu §3 Abs. 3 UWG stellt gefälschte Bewertungen ausdrücklich als
unlautere geschäftliche Handlung fest. Seit 2022 verlangt §5b Abs. 3 UWG
zusätzlich, dass Sie offenlegen, ob und wie Sie die Echtheit sicherstellen –
diese Zeile steht bereits unter dem Slider.

Abmahnungen dazu sind häufig und teuer. Ein Bereich, der drei Monate leer
bleibt, kostet Sie nichts. Ein erfundenes Zitat kann Sie vierstellig kosten.

---

## Der beste Zeitpunkt

**Direkt nach dem Erläuterungsgespräch.** Dann ist die Erleichterung frisch und
das Ergebnis konkret. Zwei Wochen später erinnert sich niemand mehr daran, was
vorher unklar war – und genau das macht ein Zitat wertvoll.

---

## Anschreiben (E-Mail oder WhatsApp)

```
Betreff: Kurze Bitte – zwei Sätze zu unserer Zusammenarbeit

Hallo [Name],

wir haben gestern Ihren Sanierungsfahrplan besprochen. Wenn Sie mit dem
Ergebnis zufrieden sind, würden Sie mir zwei bis drei Sätze dazu schreiben?

Ich würde sie gern auf meiner Website zeigen – mit Ihrem Namen, dem Gebäudetyp
und dem Ort, zum Beispiel „Maria Schmidt, Einfamilienhaus 1968, Blaustein".
Wenn Ihnen das zu persönlich ist, geht auch nur der Vorname oder die Initialen.

Damit es Ihnen leichter fällt, drei Fragen als Anregung:

  1. Was war vor unserem Termin Ihre größte Unsicherheit?
  2. Welche Entscheidung ist Ihnen danach leichter gefallen?
  3. Was hätten Sie ohne die Beratung vermutlich anders gemacht?

Antworten Sie einfach auf diese Nachricht. Damit ich es veröffentlichen darf,
schreiben Sie bitte einen Satz dazu, zum Beispiel: „Sie dürfen meine Aussage
mit Namen und Ort auf Ihrer Website veröffentlichen."

Sie können das jederzeit widerrufen, dann nehme ich es umgehend herunter.

Viele Grüße
Stanislaw Tsukerman
EBA Energieberater Albdonau
```

---

## Was ein Zitat stark macht

Brauchbar ist, was **eine Zahl, eine Summe oder eine Entscheidung** enthält.

| Schwach | Stark |
|---|---|
| „Alles super, gerne wieder." | „Wir wollten die Heizung tauschen. Nach der Berechnung haben wir zuerst das Dach gedämmt – die Wärmepumpe ist jetzt zwei Nummern kleiner und 6.000 € günstiger." |
| „Sehr kompetent und freundlich." | „Ich hätte den Förderantrag nach der Auftragsvergabe gestellt. Das hätte 8.000 € gekostet." |
| „Hat uns gut beraten." | „Nach dem Termin wussten wir zum ersten Mal, in welcher Reihenfolge wir die nächsten zehn Jahre vorgehen." |

Kürzen dürfen Sie – aber nur so, dass der Sinn erhalten bleibt, und Auslassungen
mit `[…]` kennzeichnen. Umformulieren dürfen Sie nicht.

---

## Einwilligung dokumentieren

Rechtsgrundlage ist Art. 6 Abs. 1 lit. a DSGVO. Sie brauchen:

- die Aussage im Wortlaut
- Name in der Form, die veröffentlicht werden soll
- Gebäudetyp und Ort
- das Datum der Freigabe und in welcher Form sie vorliegt (E-Mail, WhatsApp, Papier)

**Aufbewahren, aber außerhalb dieses Projektordners.** Bei Widerruf nehmen Sie
das Zitat zeitnah von der Seite und lassen die Skripte neu laufen.

---

## Zitat auf die Seite bringen

1. `index.html` öffnen, den Kommentar `<!-- ===== BAUKASTEN: 10 Plaetze … -->`
   suchen (steht direkt unter dem Stimmen-Abschnitt).
2. Einen der zehn Blöcke herauskopieren und in
   `<div class="quote-track" id="quoteTrack">` einsetzen.
3. Ausfüllen: `ZITAT WOERTLICH EINSETZEN`, `XY` (Initialen), `NAME`,
   `GEBAEUDETYP, ORT`.
4. Speichern. Der Abschnitt erscheint automatisch, Zähler und Pfeile stellen
   sich selbst ein.
5. Danach die drei Skripte laufen lassen:

```bash
python kopf-fuss-abgleichen.py && python ortsseiten-erzeugen.py && python ratgeber-erzeugen.py
```

---

## Der wirksamere zweite Schritt

Zitate auf der eigenen Website zählen für Google **nicht** als Bewertungen –
Sterne in den Suchergebnissen gibt es dafür nicht, weil Google auf der eigenen
Seite gesammelte Bewertungen als eigennützig einstuft.

Bitten Sie dieselben Kundinnen und Kunden deshalb **zusätzlich** um eine
Bewertung im **Google-Unternehmensprofil**. Für lokale Suchanfragen ist das der
stärkste Hebel überhaupt: Der überregionale Wettbewerber führt in Ulm 786
Bewertungen bei 4,9 Sternen ins Feld. Zwanzig echte Bewertungen aus dem
Alb-Donau-Kreis wiegen dort schwer.

Ein Satz genügt im Anschreiben:

> „Falls Sie zwei Minuten haben: Über eine kurze Bewertung in unserem
> Google-Profil würde ich mich sehr freuen – [Link]."
