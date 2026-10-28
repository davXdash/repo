# Daves Finds

Einfache statische Seite in `dist/`, ohne Build oder externe Abhängigkeiten.

Die Startseite lädt sofort. Erst beim Öffnen wird der Katalog geladen und mit dem eingegebenen Passwort entschlüsselt (PBKDF2-SHA256, AES-256-GCM). Das Passwort steht nicht im Quellcode. Nach Neuladen ist die Sammlung erneut gesperrt. HTTPS und JavaScript werden benötigt.

## Inhalt
442 erfasste Produktlinks. Alle 17 bisherigen Quellen sind hinterlegt. Die neue Markensuche über sämtliche Online-Listen ist noch nicht vollständig; die Seite kennzeichnet den Stand.

## Aktualisieren
Die zentrale Sammlung liegt verschlüsselt in `dist/catalog.enc.json`. Nach dem Entsperren können Daten als JSON exportiert werden. Änderungen an der Sammlung werden erneut verschlüsselt veröffentlicht. Eigene Ergänzungen und Importe auf der Seite bleiben auf dem jeweiligen Gerät, bis sie in eine gemeinsame Veröffentlichung übernommen werden.

## Hosting
Live-Seite: https://daves-finds.navyaphid2048.chatgpt.site

Der Quellcode liegt in diesem Repository. Die Live-Seite wird separat veröffentlicht; GitHub-Pushes lösen derzeit keine automatische Bereitstellung aus. Auch andere statische Hosts können den Inhalt von `dist/` bereitstellen.
