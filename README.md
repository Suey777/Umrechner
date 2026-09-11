# Medizinischer Umrechner (Benzo & Opioid)

Ein modernes Tool zur Berechnung von Äquivalenzdosen für Benzodiazepine und Opioide.

## 🚀 Features
- **Benzodiazepin-Umrechner**: Schnelle Umrechnung verschiedener Benzos in Diazepam-Äquivalente.
- **Opioid-Umrechner**: Berechnung der oralen Morphin-Äquivalente (OME) unter Berücksichtigung verschiedener Verabreichungswege (oral, IV, SC, SL, TD).
- **Umstellungs-Modus**: Direkte Berechnung der Dosis beim Wechsel von einem Medikament auf ein anderes.
- **Toleranz-Modell**: Vorhersage der Dosisentwicklung basierend auf einem exponentiellen Modell.
- **Custom Medikamente**: Eigene Opioide und Faktoren hinzufügen und speichern.
- **Modernes Interface**: Grafische Benutzeroberfläche mit Dark/Light Mode und intuitivem Sidebar-Design.
- **CLI-Support**: Volle Bedienbarkeit über das Terminal für Power-User.

## 🛠 Installation

1. **Python installieren**: Stelle sicher, dass Python 3.10 oder neuer installiert ist.
2. **Repository klonen**:
   ```bash
   git clone <dein-github-link>
   cd BenzoUmrechner
   ```
3. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Nutzung

### GUI starten
```bash
python main.py --gui
```
oder einfach:
```bash
python main.py
```

### CLI nutzen
Beispiele:
- **Benzos umrechnen**: `python main.py -d alprazolam -q 0.5`
- **Opioide umrechnen**: `python main.py -d morphine -q 10 -r iv`
- **Tabelle anzeigen**: `python main.py --list`

## ⚠️ Wichtiger Haftungsausschluss
**Diese App dient ausschließlich Informationszwecken.** Alle Umrechnungen sind Richtwerte und ersetzen unter keinen Umständen eine ärztliche Beratung oder Diagnose. Die individuelle Wirkung von Medikamenten kann stark variieren. Die Nutzung erfolgt auf eigene Gefahr.

---
*Entwickelt von Junie*
