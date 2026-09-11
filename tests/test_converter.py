import unittest
from converter import (
    convert_to_diazepam, 
    to_morphine_ome, 
    from_diazepam, 
    from_morphine_ome
)

class TestBenzoConverter(unittest.TestCase):
    """Unit-Tests für die Benzo-Umrechnungslogik."""

    def test_diazepam_to_diazepam(self):
        """10mg Diazepam sollten 10mg Diazepam ergeben."""
        equiv, factor = convert_to_diazepam("diazepam", 10.0)
        self.assertEqual(equiv, 10.0)
        self.assertEqual(factor, 1.0)

    def test_alprazolam_equivalence(self):
        """0.5mg Alprazolam entsprechen 10mg Diazepam."""
        equiv, factor = convert_to_diazepam("alprazolam", 0.5)
        self.assertEqual(equiv, 10.0)
        self.assertEqual(factor, 20.0)

    def test_lorazepam_equivalence(self):
        """1mg Lorazepam entspricht 10mg Diazepam."""
        equiv, factor = convert_to_diazepam("lorazepam", 1.0)
        self.assertEqual(equiv, 10.0)
        self.assertEqual(factor, 10.0)

    def test_bromazepam_equivalence(self):
        """6mg Bromazepam entsprechen 10mg Diazepam."""
        equiv, factor = convert_to_diazepam("bromazepam", 6.0)
        self.assertEqual(equiv, 10.0)
        self.assertAlmostEqual(factor, 1.66666666666, places=5)

    def test_tetrazepam_equivalence(self):
        """100mg Tetrazepam entsprechen 10mg Diazepam."""
        equiv, factor = convert_to_diazepam("tetrazepam", 100.0)
        self.assertEqual(equiv, 10.0)
        self.assertEqual(factor, 0.1)

    def test_midazolam_variants(self):
        """Testet verschiedene Midazolam-Gabeformen."""
        equiv_iv, _ = convert_to_diazepam("midazolam_iv", 5.0)
        equiv_oral, _ = convert_to_diazepam("midazolam_oral", 7.5)
        self.assertEqual(equiv_iv, 10.0)
        self.assertEqual(equiv_oral, 10.0)

    def test_case_insensitivity(self):
        """Eingaben sollten case-insensitive sein."""
        equiv, _ = convert_to_diazepam("AlPrAzOlAm", 0.5)
        self.assertEqual(equiv, 10.0)

    def test_unknown_medication(self):
        """Ein unbekanntes Medikament sollte einen ValueError auslösen."""
        with self.assertRaises(ValueError):
            convert_to_diazepam("unbekannt", 10.0)

    def test_negative_dose(self):
        """Eine negative Dosis sollte einen ValueError auslösen."""
        with self.assertRaises(ValueError):
            convert_to_diazepam("diazepam", -5.0)

    def test_invalid_input_type(self):
        """Ungültige Datentypen sollten einen Fehler werfen (Standard Python Verhalten)."""
        with self.assertRaises(TypeError):
            convert_to_diazepam("diazepam", "fünf")

    def test_aliases(self):
        """Testet ob deutsche Aliase korrekt aufgelöst werden."""
        # Tilidin -> tilidine
        ome = to_morphine_ome("Tilidin", 100.0)
        self.assertEqual(ome, 30.0)
        # Morphin -> morphine
        ome = to_morphine_ome("Morphin", 10.0)
        self.assertEqual(ome, 10.0)

    def test_from_diazepam(self):
        """Testet die Rückumrechnung von Diazepam."""
        # 10mg Diazepam -> 6mg Bromazepam
        dose = from_diazepam("bromazepam", 10.0)
        self.assertAlmostEqual(dose, 6.0)
        # 20mg Diazepam -> 1mg Alprazolam
        dose = from_diazepam("alprazolam", 20.0)
        self.assertEqual(dose, 1.0)

class TestOpioidConverter(unittest.TestCase):
    """Unit-Tests für die Opioid-Umrechnungslogik."""

    def test_morphine_oral(self):
        """10mg Morphin oral sollten 10mg OME ergeben."""
        ome = to_morphine_ome("morphine", 10.0, "oral")
        self.assertEqual(ome, 10.0)

    def test_morphine_iv(self):
        """10mg Morphin iv sollten 30mg OME ergeben."""
        ome = to_morphine_ome("morphine", 10.0, "iv")
        self.assertEqual(ome, 30.0)

    def test_hydromorphone_oral(self):
        """4mg Hydromorphon oral sollten 20mg OME ergeben."""
        ome = to_morphine_ome("hydromorphone", 4.0, "oral")
        self.assertEqual(ome, 20.0)

    def test_fentanyl_iv(self):
        """100µg Fentanyl iv sollten 1mg OME ergeben."""
        ome = to_morphine_ome("fentanyl", 100.0, "iv")
        self.assertEqual(ome, 1.0)

    def test_fentanyl_td(self):
        """25µg/h Fentanyl td sollten 60mg OME ergeben."""
        ome = to_morphine_ome("fentanyl", 25.0, "td")
        self.assertEqual(ome, 60.0)

    def test_methadone_low_ome(self):
        """Methadon Umrechnung bei niedriger OME (<100)."""
        # 5mg Methadon bei <100 OME -> 1:10 -> 50mg OME
        ome = to_morphine_ome("methadone", 5.0, "oral", previous_ome=50.0)
        self.assertEqual(ome, 50.0)

    def test_methadone_high_ome(self):
        """Methadon Umrechnung bei hoher OME (>300)."""
        # 20mg Methadon bei >300 OME -> 1:4 -> 80mg OME
        ome = to_morphine_ome("methadone", 20.0, "oral", previous_ome=400.0)
        self.assertEqual(ome, 80.0)

    def test_discount(self):
        """Testet den variablen Abschlag."""
        # 10mg Oxycodon oral = 15mg OME. Mit 30% Abschlag = 10.5mg
        ome = to_morphine_ome("oxycodone", 10.0, "oral", discount_percent=30.0)
        self.assertEqual(ome, 10.5)
        # Mit 50% Abschlag = 7.5mg
        ome = to_morphine_ome("oxycodone", 10.0, "oral", discount_percent=50.0)
        self.assertEqual(ome, 7.5)

    def test_from_morphine_ome(self):
        """Testet die Rückumrechnung von OME."""
        # 30mg OME -> 100mg Tilidin (oral)
        dose = from_morphine_ome("tilidine", 30.0, "oral")
        self.assertAlmostEqual(dose, 100.0)
        # 10mg OME -> 100mg Tramadol (oral)
        dose = from_morphine_ome("tramadol", 10.0, "oral")
        self.assertAlmostEqual(dose, 100.0)

    def test_tolerance_calculation(self):
        """Testet die Toleranz-Entwicklungs-Berechnung."""
        from converter import calculate_tolerance_development
        # 100mg OME, 10 Tage, 2% Rate -> 100 * (1.02^10) ≈ 121.90
        result = calculate_tolerance_development(100.0, 10, 0.02)
        self.assertEqual(result, 121.90)
        
        # Test für Benzos (mg Diazepam) - gleiche Logik
        # 20mg Diazepam, 30 Tage, 1% Rate -> 20 * (1.01^30) ≈ 26.96
        result = calculate_tolerance_development(20.0, 30, 0.01)
        self.assertEqual(result, 26.96)

    def test_custom_drug(self):
        """Testet benutzerdefinierte Medikamente."""
        from converter import save_custom_drug, get_equivalence_factor, CUSTOM_DRUGS_FILE
        import os
        
        try:
            save_custom_drug("SuperOpioid", "iv", 100.0)
            factor = get_equivalence_factor("superopioid", "iv")
            self.assertEqual(factor, 100.0)
        finally:
            # Aufräumen falls Datei erstellt wurde
            if os.path.exists(CUSTOM_DRUGS_FILE):
                os.remove(CUSTOM_DRUGS_FILE)

    def test_negative_dose(self):
        """Eine negative Dosis sollte einen ValueError auslösen."""
        with self.assertRaises(ValueError):
            to_morphine_ome("morphine", -5.0)

    def test_history_logging(self):
        """Testet ob Änderungen in der Historie geloggt werden."""
        from converter import save_custom_drug, get_history, HISTORY_FILE
        import os
        
        try:
            # Vorherige Historie laden oder leeren
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
                
            save_custom_drug("HistoryTest", "oral", 123.45)
            history = get_history()
            
            # Sollte mindestens einen Eintrag haben (den neuen)
            self.assertTrue(any(e['drug'] == "Historytest (oral)" for e in history))
            
        finally:
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)

if __name__ == '__main__':
    unittest.main()
