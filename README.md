# Energieberatung Tsukerman – Website

Statische Website mit Sanierungsrechner. Kein Build, kein Framework, keine
Abhängigkeiten – die Dateien werden so hochgeladen, wie sie hier liegen.

| Datei | Zweck |
|---|---|
| `index.html` | Startseite |
| `sanierungsrechner.html` | Rechner mit Bericht-Download und Lead-Formular |
| `impressum.html` | Pflichtseite nach §5 DDG |
| `datenschutz.html` | Pflichtseite nach DSGVO |
| `404.html` | Fehlerseite |
| `fonts/` | Schriften Inter und Fraunces, lokal gehostet |
| `robots.txt`, `sitemap.xml` | für Google |
| `.nojekyll` | technische Datei für GitHub Pages, drin lassen |
| `htaccess.txt` | nur für klassische Hoster, bei GitHub Pages überflüssig |
| `CLAUDE.md` | Projektregeln für die Weiterarbeit mit Claude Code |

---

## ⚠️ Vor dem Livegang

Diese Punkte sind noch offen. Die ersten drei sind rechtlich zwingend.

1. **E-Mail-Adresse** eintragen – im Impressum Pflichtangabe.
   Suchen nach `kontakt@ihre-domain.de` in `index.html`, `impressum.html`,
   `datenschutz.html`.
2. **USt-IdNr und Berufshaftpflicht** – `impressum.html`.
3. **AVV mit Supabase abschließen** – Supabase-Dashboard →
   Settings → Legal Documents. Ohne ihn dürfen die Formulare nicht laufen.
   Danach den Hinweiskasten in `datenschutz.html`, Abschnitt 6, löschen.
4. **Hosting-Anbieter** in `datenschutz.html`, Abschnitt 3 – bei GitHub Pages
   steht der fertige Text als Kommentar direkt daneben.
5. **Domain** eintragen – suchen nach `ihre-domain.de` in beiden HTML-Seiten
   (canonical, og:url, JSON-LD) sowie in `robots.txt` und `sitemap.xml`.
6. **Portraitfoto** in `index.html`, Sektion „Über mich".
7. **Kundenstimmen** – aktuell Platzhalter. Entweder echte Zitate oder die
   Sektion entfernen. Erfundene Bewertungen sind abmahnfähig.
8. **Förderbeträge prüfen** – die Prozentsätze und Höchstbeträge gegen die
   aktuelle BAFA-/KfW-Richtlinie abgleichen.

Alle offenen Stellen stehen in `[eckigen Klammern]`.

---

## Wo die Anfragen landen

Beide Formulare schreiben direkt in eine **eigene Supabase-Datenbank** –
kein Formspree, kein Zwischendienst.

- Projekt: `energieberatung-website`
- Region: `eu-central-1` (Frankfurt am Main, EU)
- Tabelle: `leads`

**Anfragen ansehen:** [supabase.com](https://supabase.com) → Projekt
`energieberatung-website` → Table Editor → Tabelle `leads`.
Die Spalten `bearbeitet` und `notiz` sind zum Abhaken und für eigene Notizen da.

### Zur Sicherheit

Im Quelltext der Seiten steht ein Zugangsschlüssel (`SUPABASE_KEY`). Das ist
Absicht und ungefährlich: Die Datenbank erlaubt damit ausschließlich das
**Anlegen** neuer Einträge. Lesen, Ändern und Löschen sind gesperrt. Wer den
Schlüssel aus dem Quelltext kopiert, kommt an keine einzige gespeicherte
Anfrage – geprüft und mit `401` bestätigt.

Nicht anfassen: die Row-Level-Security-Regeln der Tabelle `leads`.

### E-Mail-Benachrichtigung

Aktuell keine – neue Anfragen sehen Sie im Dashboard. Lässt sich jederzeit
nachrüsten (Supabase Database Webhook + Edge Function).

---

## Online stellen mit GitHub Pages

Einmalig im Terminal anmelden:

```bash
gh auth login
```

Dann Identität für Commits setzen:

```bash
git config --global user.name "Stanislaw Tsukerman"
```

Und die E-Mail dazu:

```bash
git config --global user.email "ihre@email.de"
```

Danach in diesem Ordner:

```bash
git init && git add . && git commit -m "Website mit Sanierungsrechner"
```

Repository anlegen und hochladen:

```bash
gh repo create energieberatung --public --source=. --push
```

GitHub Pages aktivieren: Repository → **Settings → Pages** → Branch `main`,
Ordner `/ (root)` → **Save**. Nach 1–2 Minuten erreichbar unter
`https://IHR-NUTZERNAME.github.io/energieberatung/`.

> **Wichtig bei Adressen mit `/energieberatung/` am Ende:** In `404.html` die
> beiden Links von `/` auf `/energieberatung/` ändern. Mit eigener Domain
> passt `/` und die Datei bleibt, wie sie ist.

**Eigene Domain (empfohlen):** Settings → Pages → „Custom domain" eintragen,
beim Domain-Anbieter einen CNAME-Eintrag `www → IHR-NUTZERNAME.github.io`
anlegen. HTTPS aktiviert GitHub automatisch.

## Alternative: klassischer Webspace

Alle Dateien ins Hauptverzeichnis hochladen, `htaccess.txt` auf dem Server in
`.htaccess` umbenennen. Der Ordner `fonts/` muss mit hoch – sonst greift nur
die Ersatzschrift.

---

## Änderungen später

Datei ändern, dann:

```bash
git add . && git commit -m "Was geändert wurde" && git push
```

Nach 1–2 Minuten ist die Änderung live.

Bei Änderungen am Rechner **immer** die Browser-Konsole prüfen: Es muss
`✅ SELBSTTEST BESTANDEN` erscheinen. Erscheint das nicht, wurde das
Rechenmodell beschädigt.

Nach dem Livegang lohnen sich zwei kostenlose Dinge:
[Google Search Console](https://search.google.com/search-console) einrichten
und `sitemap.xml` einreichen, sowie ein Google-Unternehmensprofil anlegen und
die Website dort verlinken – für lokale Suchanfragen der wichtigste Hebel.
