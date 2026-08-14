SCHRIFT – lokal gehostet (DSGVO)
================================

Diese Datei liegt bewusst auf dem eigenen Server, damit beim Aufruf der
Website KEINE Verbindung zu Google (fonts.googleapis.com / fonts.gstatic.com)
aufgebaut wird. Genau diese Verbindung überträgt die IP-Adresse der Besucher
in die USA und ist in Deutschland wiederholt abgemahnt worden.

WICHTIG: Nicht wieder auf die Google-Einbindung zurückwechseln.


Enthaltene Dateien
------------------
roboto-latin-var.woff2   Roboto, Variable Font, Subset "latin", 400–700

Ein Variable Font deckt den kompletten Gewichtsbereich ab. Deshalb reicht ein
einziger @font-face-Block (siehe <style> in index.html).

Das Subset "latin" enthält alle deutschen Umlaute, ß, das Euro-Zeichen und die
typografischen Anführungszeichen „ “. Nicht enthalten ist der Pfeil → (U+2192);
den stellt der Browser automatisch aus einer Systemschrift dar.

Die Website läuft durchgängig auf Roboto – auch die Überschriften. Vorher
waren es zwei Schriften (Inter für Fließtext, Fraunces für Überschriften);
deren Dateien wurden bei der Umstellung entfernt.


Herkunft und Lizenz
-------------------
Roboto – Google, https://github.com/googlefonts/roboto
Lizenz: Apache License 2.0, Lizenztext in LICENSE-Roboto.txt

Die Apache-Lizenz erlaubt Selbst-Hosting ausdrücklich. Der Lizenztext muss
mitgeliefert werden – LICENSE-Roboto.txt beim Upload also nicht weglassen.


Beim Upload beachten
--------------------
Der Ordner "fonts" muss relativ zur index.html an derselben Stelle liegen,
sonst greift nur der System-Fallback (Segoe UI / Arial). Die Seite bleibt dann
benutzbar, sieht aber anders aus.

Kontrolle nach dem Livegang: Browser öffnen, F12, Reiter "Netzwerk", Seite neu
laden. Es darf kein einziger Eintrag mit "googleapis" oder "gstatic"
auftauchen.
