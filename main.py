import sys
import argparse
from gui import ConverterGUI
from converter import (
    convert_to_diazepam,
    EQUIVALENCE_TABLE,
    DISPLAY_NAMES,
    DISCLAIMER,
    get_equivalence_markdown,
    to_morphine_ome,
    list_all_equivalences,
    OPIOID_TABLE,
    normalize_drug_name,
    save_custom_drug,
    USER_OPIOID_TABLE,
    calculate_tolerance_development,
    get_history,
    DATA_VERSION,
    from_diazepam,
    from_morphine_ome
)

def run_cli():
    """Startet das Kommandozeilen-Interface."""
    parser = argparse.ArgumentParser(description="Medizinischer Umrechner für Benzodiazepine und Opioide.")

    # Gemeinsame Optionen
    parser.add_argument("-d", "--drug", help="Name des Medikaments (z.B. hydromorphone, tilidin, alprazolam)")
    parser.add_argument("-q", "--dose", type=float, help="Dosis (mg, µg für Fentanyl IV, µg/h für Fentanyl TD)")
    parser.add_argument("--list", action="store_true", help="Gibt die Äquivalenztabelle aus.")
    parser.add_argument("--gui", action="store_true", help="Startet die grafische Benutzeroberfläche.")
    parser.add_argument("--history", action="store_true", help="Zeigt die Historie der Datenänderungen an.")

    # Opioid-spezifische Optionen
    parser.add_argument("-r", "--route", default="oral", help="Verabreichungsweg (oral, iv, sc, sl, td). Standard: oral.")
    parser.add_argument("--previous-ome", type=float, help="Vorherige tägliche Morphin-OME (nur für Methadon nötig).")
    parser.add_argument("--discount", type=float, default=0.0, help="Abschlag für unvollständige Kreuztoleranz in Prozent (z.B. 30).")

    # Benzo-spezifische Optionen (optional zur Kompatibilität)
    parser.add_argument("--benzo", action="store_true", help="Explizit den Benzo-Umrechner nutzen.")

    args = parser.parse_args()

    if args.list:
        print(f"Daten-Version: {DATA_VERSION}")
        print("\n".join(list_all_equivalences()))
        print("\n" + get_equivalence_markdown())
        return

    if args.history:
        print(f"Historie der Datenänderungen (Version {DATA_VERSION}):")
        print("-" * 60)
        for entry in get_history():
            print(f"[{entry['date']}] {entry['type']} - {entry['drug']}: {entry['change']}")
        return

    if args.gui or len(sys.argv) == 1:
        app = ConverterGUI()
        app.mainloop()
        return

    if not args.drug or args.dose is None:
        parser.print_help()
        return

    try:
        drug_norm = normalize_drug_name(args.drug)

        # Prüfen ob es ein Opioid ist
        is_opioid = False
        for (d, r) in OPIOID_TABLE.keys():
            if d == drug_norm:
                is_opioid = True
                break

        if is_opioid and not args.benzo:
            ome = to_morphine_ome(args.drug, args.dose, args.route, args.previous_ome, args.discount)
            unit = "µg" if "fentanyl" in drug_norm else "mg"
            if "fentanyl" in drug_norm and args.route == "td":
                unit = "µg/h"
            print(f"\nErgebnis: {args.dose} {unit} {args.drug} ({args.route}) ≈ {ome} mg Morphin PO (OME)")
            if args.discount > 0:
                print(f"HINWEIS: Ein {args.discount}% Abschlag wurde angewendet.")
            else:
                print(f"HINWEIS: Bei Umstellung auf ein neues Opioid wird oft ein Abschlag von 30-50% empfohlen.")
        else:
            # Benzo Umrechnung
            equiv, factor = convert_to_diazepam(args.drug, args.dose)
            print(f"\nErgebnis: {args.dose} mg {args.drug} ≈ {equiv:.2f} mg Diazepam")
            print(f"Verhältnis: 1 mg {args.drug} ≈ {factor:.2f} mg Diazepam (Basis 10mg)")

        print(f"\n{DISCLAIMER}")

    except (ValueError, KeyError) as e:
        print(f"Fehler: {e}")
        if "Unbekanntes" in str(e):
            print("\nNutzen Sie --list um alle verfügbaren Medikamente anzuzeigen.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

def main():
    run_cli()

if __name__ == "__main__":
    main()
