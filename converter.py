import json
import os
import datetime
from typing import Tuple, Optional, Dict, List

"""
Modul zur Berechnung der Benzodiazepin- und Opioid-Äquivalenzdosen.
Basiert auf einer 10mg Diazepam-Referenz für Benzos und OME für Opioide.
"""

# Pfad für benutzerdefinierte Medikamente und Historie
CUSTOM_DRUGS_FILE = "custom_drugs.json"
HISTORY_FILE = "history.json"
DATA_VERSION = "1.5.0"

# Fest kodierte Historie für interne Datenänderungen
INTERNAL_HISTORY = [
    {"date": "2026-08-01", "type": "Update", "drug": "All", "change": "Initialer Release mit Benzo-Daten."},
    {"date": "2026-08-03", "type": "Update", "drug": "Opioide", "change": "Opioid-Umrechnungstabelle hinzugefügt."},
    {"date": "2026-08-04", "type": "Alias", "drug": "Tilidin/Morphin", "change": "Deutsche Aliase für bessere Suche hinzugefügt."},
    {"date": "2026-08-05", "type": "Feature", "drug": "Custom", "change": "Unterstützung für benutzerdefinierte Medikamente."},
    {"date": "2026-08-05", "type": "Feature", "drug": "Benzo", "change": "Toleranz-Modell für Benzodiazepine hinzugefügt."},
    {"date": "2026-08-05", "type": "Feature", "drug": "Conversion", "change": "Direkte Umrechnung zwischen Medikamenten (Umstellung) hinzugefügt."},
]

# Daten laden aus JSON
DATA_FILE = "data.json"
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden von {DATA_FILE}: {e}")
        return {}

_DATA = load_data()
EQUIVALENCE_TABLE = _DATA.get("equivalence_table", {})
DISPLAY_NAMES = _DATA.get("display_names", {})

# Opioid Tabelle konvertieren von "drug_route" zu (drug, route)
_RAW_OPIOID = _DATA.get("opioid_table", {})
OPIOID_TABLE = {}
for key, val in _RAW_OPIOID.items():
    parts = key.rsplit("_", 1)
    if len(parts) == 2:
        OPIOID_TABLE[(parts[0], parts[1])] = val
    else:
        OPIOID_TABLE[(key, "oral")] = val

DISCLAIMER = (
    "HINWEIS: Alle Umrechnungen sind nur Richtwerte und ersetzen keine ärztliche Beratung.\n"
    "Die individuelle Wirkung kann variieren."
)

# # SUEYS RECHNER
DRUG_ALIASES = {
    "tilidin": "tilidine",
    "morphin": "morphine",
    "hydromorphon": "hydromorphone",
    "oxycodon": "oxycodone",
    "codein": "codeine",
    "hydrocodon": "hydrocodone",
    "fentanyl": "fentanyl",
    "buprenorphin": "buprenorphine",
    "methadon": "methadone",
    "tramadol": "tramadol",
    "nalbuphin": "nalbuphine"
}

# Globale Variable für benutzerdefinierte Opioide
# Format: { (drug_key, route): factor }
USER_OPIOID_TABLE: Dict[Tuple[str, str], float] = {}

def load_custom_drugs():
    """Lädt benutzerdefinierte Medikamente aus einer Datei."""
    global USER_OPIOID_TABLE
    if os.path.exists(CUSTOM_DRUGS_FILE):
        try:
            with open(CUSTOM_DRUGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for drug, routes in data.items():
                    for route, factor in routes.items():
                        USER_OPIOID_TABLE[(drug.lower(), route.lower())] = float(factor)
        except Exception as e:
            print(f"Fehler beim Laden der benutzerdefinierten Medikamente: {e}")

def save_custom_drug(drug: str, route: str, factor: float):
    """Speichert ein neues benutzerdefiniertes Medikament und loggt die Änderung."""
    drug_norm = drug.lower().strip()
    route_norm = route.lower().strip()
    
    old_factor = USER_OPIOID_TABLE.get((drug_norm, route_norm))
    USER_OPIOID_TABLE[(drug_norm, route_norm)] = factor
    
    # Datei aktualisieren
    data = {}
    if os.path.exists(CUSTOM_DRUGS_FILE):
        try:
            with open(CUSTOM_DRUGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            pass
    
    if drug_norm not in data:
        data[drug_norm] = {}
    data[drug_norm][route_norm] = factor
    
    with open(CUSTOM_DRUGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    # Historie loggen
    change_type = "Hinzugefügt" if old_factor is None else "Geändert"
    change_desc = f"Faktor auf {factor} gesetzt"
    if old_factor is not None:
        change_desc = f"Faktor von {old_factor} auf {factor} geändert"
        
    log_change(change_type, f"{drug.capitalize()} ({route})", change_desc)

def log_change(change_type: str, drug: str, change: str):
    """Schreibt eine Änderung in die history.json."""
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            pass
            
    new_entry = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": change_type,
        "drug": drug,
        "change": change
    }
    history.insert(0, new_entry) # Neueste zuerst
    
    # Auf 100 Einträge begrenzen
    history = history[:100]
    
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Fehler beim Speichern der Historie: {e}")

def get_history() -> List[Dict]:
    """Gibt die kombinierte Historie (intern + benutzerdefiniert) zurück."""
    user_history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                user_history = json.load(f)
        except:
            pass
            
    # Interne Historie mit Datum sortieren (einfache Verkettung)
    return user_history + INTERNAL_HISTORY

# Initiales Laden
load_custom_drugs()

def normalize_drug_name(name: str) -> str:
    """
    Normalisiert den Namen eines Medikaments und löst Aliase auf.
    """
    n = name.lower().strip().replace(" ", "_").replace("-", "_")
    return DRUG_ALIASES.get(n, n)

def get_equivalence_factor(drug: str, route: str) -> float:
    """
    Liefert den Faktor aus der Tabelle.
    Berücksichtigt auch benutzerdefinierte Medikamente.
    Wirft KeyError bei unbekanntem Medikament/Weg.
    """
    drug_norm = normalize_drug_name(drug)
    route_norm = route.lower().strip()
    
    # Erst in der Standardtabelle suchen
    if (drug_norm, route_norm) in OPIOID_TABLE:
        factor = OPIOID_TABLE[(drug_norm, route_norm)]
        if factor is None and drug_norm == "methadone":
            return 1.0 # Methadon wird separat berechnet, Faktor 1.0 als Platzhalter
        return factor
    
    # Dann in der Benutzertabelle suchen
    if (drug_norm, route_norm) in USER_OPIOID_TABLE:
        return USER_OPIOID_TABLE[(drug_norm, route_norm)]
    
    raise KeyError(f"Unbekanntes Opioid oder Weg: {drug} ({route})")

def to_morphine_ome(
    drug: str,
    dose: float,
    route: str = "oral",
    previous_ome: Optional[float] = None,
    discount_percent: float = 0.0,
) -> float:
    """
    Berechnet die OME (morphin-oral-equivalente Milligramm).

    Args:
        drug: Name des Opioids.
        dose: Verabreichte Dosis (mg, µg für Fentanyl).
        route: Verabreichungsweg (oral, iv, sc, sl, td).
        previous_ome: Vorherige tägliche OME (für Methadon).
        discount_percent: Abschlag für Kreuztoleranz in Prozent (0-100).

    Returns:
        OME gerundet auf 2 Dezimalstellen.

    Raises:
        ValueError: Bei negativer Dosis.
        KeyError: Bei unbekanntem Medikament/Weg.
    """
    if dose < 0:
        raise ValueError("Die Dosis muss positiv sein.")
    
    drug_norm = normalize_drug_name(drug)
    route_norm = route.lower().strip()
    
    if drug_norm == "methadone" and route_norm == "oral":
        if previous_ome is None:
            factor = 10.0 # Standard 1:10
        elif previous_ome < 100:
            factor = 10.0
        elif previous_ome < 200:
            factor = 8.0
        elif previous_ome < 300:
            factor = 6.0
        else:
            factor = 4.0
        ome = dose * factor
    else:
        factor = get_equivalence_factor(drug_norm, route_norm)
        ome = dose * factor
    
    # Cross-Tolerance Factor (CTF) / Abschlag anwenden
    if discount_percent > 0:
        multiplier = (100.0 - discount_percent) / 100.0
        ome = ome * multiplier
        
    return round(ome, 2)

def calculate_tolerance_development(
    initial_dose: float, 
    days: int, 
    increase_rate: float = 0.02
) -> float:
    """
    Berechnet die voraussichtliche Dosis nach einer bestimmten Anzahl von Tagen,
    basierend auf einem einfachen exponentiellen Toleranz-Modell.
    Funktioniert sowohl für OME als auch für Diazepam-Äquivalente.
    
    Args:
        initial_dose: Start-Dosis (z.B. in OME oder mg Diazepam).
        days: Zeitraum in Tagen.
        increase_rate: Tägliche Steigerungsrate (Standard 2%).
        
    Returns:
        Erwartete Dosis gerundet auf 2 Dezimalstellen.
    """
    if days < 0:
        return initial_dose
    
    # Formel: Dosis = Start * (1 + Rate)^Tage
    final_dose = initial_dose * ((1.0 + increase_rate) ** days)
    return round(final_dose, 2)

def list_all_equivalences() -> Tuple[str, ...]:
    """Gibt formatierte Zeilen der gesamten Tabelle zurück."""
    lines = [
        "Opioid-Äquivalenztabelle (zu oralem Morphin):",
        "| Medikament (Weg) | Faktor |",
        "|------------------|--------|"
    ]
    for (drug, route), factor in OPIOID_TABLE.items():
        if factor is not None:
            lines.append(f"| {drug.capitalize()} ({route}) | {factor} |")
        else:
            lines.append(f"| {drug.capitalize()} ({route}) | Variabel (siehe Methadon-Regel) |")
    
    if USER_OPIOID_TABLE:
        lines.append("\nBenutzerdefinierte Opioide:")
        for (drug, route), factor in USER_OPIOID_TABLE.items():
            lines.append(f"| {drug.capitalize()} ({route}) | {factor} (User) |")

    lines.append("\nSpezialfall Methadon (oral):")
    lines.append("- < 100 mg OME/Tag: 1:10")
    lines.append("- 100-199 mg OME/Tag: 1:8")
    lines.append("- 200-299 mg OME/Tag: 1:6")
    lines.append("- >= 300 mg OME/Tag: 1:4")
    
    return tuple(lines)

def convert_to_diazepam(med_name: str, dose: float) -> Tuple[float, float]:
    """
    Rechnet eine Dosis eines Benzodiazepins in die entsprechende Menge Diazepam um.

    Args:
        med_name: Name des Medikaments (case-insensitive)
        dose: Dosis in mg

    Returns:
        (Äquivalente Dosis in mg Diazepam, Verhältnis-Faktor)

    Raises:
        ValueError: Wenn das Medikament unbekannt ist oder die Dosis ungültig ist.
    """
    name_lower = med_name.lower().strip()
    
    if name_lower not in EQUIVALENCE_TABLE:
        raise ValueError(f"Unbekanntes Medikament: {med_name}")
    
    if dose < 0:
        raise ValueError("Die Dosis muss positiv sein.")
    
    # Faktor: 10mg Diazepam / X mg Medikament
    # Beispiel Alprazolam: 10 / 0.5 = 20 (1mg Alprazolam = 20mg Diazepam)
    base_dose = EQUIVALENCE_TABLE[name_lower]
    factor = 10.0 / base_dose
    
    equivalent_diazepam = dose * factor
    return equivalent_diazepam, factor

def from_diazepam(target_med: str, diazepam_dose: float) -> float:
    """
    Rechnet eine Diazepam-Dosis in die entsprechende Menge eines anderen Benzodiazepins um.
    """
    name_lower = target_med.lower().strip()
    if name_lower not in EQUIVALENCE_TABLE:
        raise ValueError(f"Unbekanntes Medikament: {target_med}")
    
    # Beispiel Alprazolam: 0.5 mg entsprechen 10 mg Diazepam.
    # dose_target = (diazepam_dose / 10) * base_dose_target
    base_dose = EQUIVALENCE_TABLE[name_lower]
    return (diazepam_dose / 10.0) * base_dose

def from_morphine_ome(target_drug: str, ome_dose: float, target_route: str = "oral") -> float:
    """
    Rechnet eine OME-Dosis in die entsprechende Menge eines anderen Opioids um.
    """
    drug_norm = normalize_drug_name(target_drug)
    route_norm = target_route.lower().strip()
    
    if drug_norm == "methadone" and route_norm == "oral":
        # Umkehrung der Methadon-Regel ist schwierig, da sie von der OME abhängt.
        # Wir nutzen hier den Faktor, der für die gegebene OME gelten würde.
        if ome_dose < 100:
            factor = 10.0
        elif ome_dose < 200:
            factor = 8.0
        elif ome_dose < 300:
            factor = 6.0
        else:
            factor = 4.0
        return ome_dose / factor
    
    factor = get_equivalence_factor(drug_norm, route_norm)
    if factor == 0:
        raise ValueError("Faktor ist 0, Umrechnung nicht möglich.")
    
    return ome_dose / factor

def get_equivalence_markdown() -> str:
    """
    Erstellt eine Markdown-Tabelle der Äquivalenzwerte.
    """
    lines = [
        "| Medikament | Menge entsprechend 10mg Diazepam |",
        "| :--- | :--- |"
    ]
    for key, val in EQUIVALENCE_TABLE.items():
        lines.append(f"| {DISPLAY_NAMES[key]} | {val} mg |")
    return "\n".join(lines)
