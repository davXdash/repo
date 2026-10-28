# Daves Finds

Persönlicher Katalog auf **GitHub Pages**, mit zwei Ansichten:

- **Alles:** alle vom Importer erkannten Produkte.
- **Meine Auswahl:** deine Marken und Modelle – Autry, Axel Arigato, AMI, Nike P-6000, alle erkannten Spezial und Campus, Golden Goose (auch GGS/GGDB), Birkenstock und die bisherigen Suchgruppen.

## Neue Sheets importieren
1. Im Repository **Actions → Sheets importieren und Pages veröffentlichen → Run workflow** öffnen.
2. Weitere Google-Sheets-Links in `sheet_links` einfügen. Ohne Eingabe werden die vorhandenen Links erneut eingelesen.
3. Workflow starten. Er speichert die Importergebnisse und veröffentlicht `dist/` auf GitHub Pages.

Alternativ hier im Chat neue Links geben; sie können in `sources.json` ergänzt werden. Keine Tabellenkopien oder neue Dateiformate erforderlich.

## Wie der Import funktioniert
Der Importer liest alle angebotenen Tabellenblätter über Googles lesbare HTML-Ansicht, einschließlich dargestellter Produktlinks und Bilder. Falls diese Ansicht nicht verfügbar ist, versucht er den XLSX-Download. Der XLSX-Parser verarbeitet auch IMAGE-Formeln und eingebettete Rasterbilder.

Originalpreise bleiben erhalten. Eindeutige Währungen werden mit dem aktuellen EZB-Referenzkurs umgerechnet. Unklare Währungen bleiben offen. Es werden keine Produktseiten, auswählbaren Größen/Farben oder Versandkosten zusätzlich ausgelesen. Bilder werden lazy geladen; extern gesperrte oder gelöschte Bilddateien können nicht garantiert werden.

Tabellenlayouts werden anhand von Produktnamen, Linkzellen, Bildern und Preiszellen erkannt. Der Importbericht nennt fehlende Werte, nicht zugeordnete Links und fehlgeschlagene Tabellenblätter. Ein neues oder ungewöhnliches Layout kann eine Anpassung des Parsers erfordern. Wenn Google auch die lesbare Ansicht und den Export tatsächlich nur nach Anmeldung erlaubt, erhält der Importer keine privaten Daten. Vorhandene erfolgreiche Importe bleiben bei Zugriffsfehlern erhalten.

## Passwort und Veröffentlichung
Die Startseite lädt sofort. Der bisherige Katalog ist mit PBKDF2/AES-GCM verschlüsselt. Weitere Importe werden mit einem öffentlichen RSA-Schlüssel verschlüsselt; der passende private Schlüssel liegt passwortverschlüsselt vor. Das Passwort steht weder im JavaScript noch im Actions-Workflow. Deshalb benötigt der Import kein Passwort-Secret.

Der Workflow veröffentlicht ausschließlich auf GitHub Pages. In den Repository-Einstellungen unter **Pages → Build and deployment → Source** muss **GitHub Actions** ausgewählt sein. Bei Veröffentlichung über einen Branch leitet die Root-Startseite zunächst auf `dist/` weiter.

Eigene Ergänzungen auf der Seite bleiben browserlokal, bis sie in eine gemeinsame Veröffentlichung übernommen werden. Exportierte JSON-Dateien enthalten unverschlüsselte Daten und werden nicht automatisch in das öffentliche Repository geschrieben.

## Lokal ausführen
Python 3.12 und Abhängigkeiten aus `tools/requirements.txt`:

```sh
pip install -r tools/requirements.txt
python tools/import_sheets.py
python tools/import_sheets.py --links 'https://docs.google.com/spreadsheets/d/ID/edit'
python tools/test_import_sheets.py
```

Der bestehende Passwortzugang bleibt beim Aktualisieren erhalten. Die Live-Dateien liegen in `dist/`; `sources.json` enthält die Eingangslinks.
