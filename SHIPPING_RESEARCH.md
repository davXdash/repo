# Versandvergleich – geprüfter Stand 28.10.2026

Die Benutzeroberfläche bleibt auf GitHub Pages. Persönliche Listen werden nur auf verbundenen Geräten automatisch per GitHub Contents API verschlüsselt im separaten Zweig `user-data` abgeglichen. Dafür muss Dave einmal pro Gerät einen Fine-grained Personal Access Token nur für `davXdash/repo` mit Contents: Read and write direkt auf der Seite hinterlegen. Der Token bleibt lokal; er wird weder exportiert noch in GitHub gespeichert. Die bestehende ChatGPT-GitHub-Verbindung ist kein Browser-Login für die Webseite. Ohne diese Einrichtung zeigt die Seite ausdrücklich lokale Speicherung an.

Die Synchronisierung nutzt AES-GCM mit zufälligem IV und Salt, PBKDF2-SHA256 mit 210000 Iterationen sowie gzip. Pro Eintrag gespeicherte Änderungsstände und Löschmarkierungen erlauben unabhängige Änderungen; bei gleichzeitigem Ändern desselben Felds gewinnt der neuere Zeitstempel, bei gleichem Zeitstempel die deterministische Geräte-ID. Deshalb sollten die Geräteuhren korrekt sein. GitHub-Dateikonflikte werden mit erneutem Lesen und Zusammenführen behandelt. Es existiert kein anonymer Schreibzugang.

## Offizielle Rechner und beobachtete Werte

Diese Stichproben sind keine universellen Tarife und werden nicht automatisch auf andere Gewichte, Warengruppen, Konten oder Hauls angewendet. Währungen bleiben als USD dokumentiert, weil genau diese Beträge angezeigt wurden. Im Katalog werden EUR-Quellpreise separat geführt.

| Agent | Quelle | Parameter / Beobachtung | Ergebnis |
| --- | --- | --- | --- |
| Pikobuy | https://www.pikobuy.com/shipping-cost | Germany, 2 kg, Sensible Ware, keine Paketmaße; öffentliche Abfrage | EU DHL Sensitive LD, 7–15 Werktage; angezeigter Preis 34,94 USD, daneben 58,23 USD und „40% OFF“. Rabattberechtigung nicht geprüft; keine pauschale Umrechnung in €/kg. |
| Litbuy | https://litbuy.com/shipping-estimate | Germany, 2000 g, Schuhe / International Brand, keine Paketmaße | Unter anderem LIT-Economy-DHL-DE: angezeigt 30,36 USD, daneben 43,51 USD und „40% OFF“, 10–15 Werktage. Die Rabattangabe und die Beträge lassen sich nicht als einfache 40-%-Rechnung erklären. Keine eigenständige Rabattformel daraus ableiten. |
| Litbuy | Derselbe Rechner, Show more für LIT-Economy-DHL-DE | Tarifdetails | First Weight und Additional Weight zeigen `undefinedUSD/undefinedg`, Limits 0 g, Fuel Surcharge und Handling Fee 0 USD. Diese unvollständigen Tarifdetails sind nicht als verifizierte Gewichtsformel nutzbar. |
| USFans | https://www.usfans.com/estimation | Öffentliche Ansicht | Formular zunächst sichtbar, danach Weiterleitung auf Login mit redirect=/estimation. Kein belastbarer Paketpreis ohne angemeldete Sitzung erhoben. |

USFans nennt im Help Center Warenpreis, Inlandsversand, internationalen Versand und ggf. Abgaben als Bestandteile: https://www.usfans.com/help/HCON_STATIC_008 . Ein anderer offizieller Vertragstext nennt Plattformgebühren: https://www.usfans.com/page/serviceAgreement . Daher weder 0 % noch 8 % pauschal als sichere Gebühr voreinstellen.

## Aktiver Funktionsumfang

- Produkte dauerhaft ausblenden und wiederherstellen; aus normaler Auswahl, Gesamtkatalog und Merkliste entfernen, ohne Originalquellen zu löschen.
- Angebote derselben ursprünglichen Produkt-ID bei mehreren Agenten gegenüberstellen. Ähnliche Bilder oder Markennamen sind kein Identitätsnachweis.
- Einen Haul mit konkretem Angebot und Menge pro Agent planen; alternative Agenten können mit denselben Produkt-IDs separat geplant werden.
- Warenwert, internationalen Versand, Packing, Inlandsversand, Gebühren und zusätzliche Abgaben separat führen. Leere Kosten sind unbekannt; ausdrücklich 0 bedeutet kostenlos oder bereits enthalten. Erst vollständig bekannte Kosten ergeben eine Gesamtsumme.

## Noch offen

Ein automatischer Gesamtpreisvergleich mit regelmäßig aktualisierten Versandangeboten ist nicht aktiv. Dafür braucht jeder Agent eine verlässlich abfragbare Tarifquelle beziehungsweise eine vom Nutzer autorisierte angemeldete Sitzung. Ein einzelner Paketpreis ist kein allgemeiner Kilopreis. Benötigt werden unter anderem Grundgewicht, Folgeschritte, Aufrundung, Volumengewicht, Grenzen, Produktrestriktionen, Währung, Gebühren und nachgewiesene Couponbedingungen. Individuelle Warenkorbpreise und Verpackungsmaße sind derzeit nicht in den Sheets enthalten.

GitHub API: https://docs.github.com/en/rest/repos/contents
