SCHRIFTEN – lokal gehostet (DSGVO)
==================================

Diese Dateien liegen bewusst auf dem eigenen Server, damit beim Aufruf der
Website KEINE Verbindung zu Google (fonts.googleapis.com / fonts.gstatic.com)
aufgebaut wird. Genau diese Verbindung überträgt die IP-Adresse der Besucher in
die USA und ist in Deutschland wiederholt abgemahnt worden.

WICHTIG: Nicht wieder auf die Google-Einbindung zurückwechseln.


Enthaltene Dateien
------------------
fraunces-latin-var.woff2   Fraunces, Variable Font, Subset "latin"
inter-latin-var.woff2      Inter, Variable Font, Subset "latin"

Beide sind Variable Fonts – eine Datei deckt den kompletten Gewichtsbereich
400–700 ab. Deshalb reicht je Schrift ein einziger @font-face-Block
(siehe <style> in index.html).

Das Subset "latin" enthält alle deutschen Umlaute, ß, das Euro-Zeichen und die
typografischen Anführungszeichen „ “. Nicht enthalten ist der Pfeil → (U+2192);
den stellt der Browser automatisch aus einer Systemschrift dar.


Herkunft und Lizenz
-------------------
Beide Schriften stehen unter der SIL Open Font License 1.1. Selbst-Hosting auf
der eigenen Website ist dadurch ausdrücklich erlaubt.

Fraunces  – Undercase Type, https://github.com/undercasetype/Fraunces
            Lizenztext: OFL-Fraunces.txt
Inter     – Rasmus Andersson, https://github.com/rsms/inter
            Lizenztext: OFL-Inter.txt

Die Lizenztexte müssen mitgeliefert werden – die beiden .txt-Dateien also beim
Upload nicht weglassen.


Beim Upload beachten
--------------------
Der Ordner "fonts" muss relativ zur index.html an derselben Stelle liegen, sonst
greift nur der System-Fallback (Georgia / Segoe UI). Die Seite bleibt dann
benutzbar, sieht aber anders aus.

Kontrolle nach dem Livegang: Browser öffnen, F12, Reiter "Netzwerk", Seite neu
laden. Es darf kein einziger Eintrag mit "googleapis" oder "gstatic" auftauchen.
