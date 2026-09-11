import streamlit as st
import converter
import pandas as pd

# Seitenkonfiguration
st.set_page_config(
    page_title="Med-Umrechner", 
    page_icon="💊", 
    layout="centered"
)

# Styling für den Disclaimer
st.markdown("""
    <style>
    .disclaimer {
        color: #ff4b4b;
        font-size: 0.9rem;
        font-style: italic;
        border: 1px solid #ff4b4b;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("💊 Medizinischer Umrechner")
st.markdown(f'<div class="disclaimer">{converter.DISCLAIMER}</div>', unsafe_allow_html=True)

# Navigation über Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Benzodiazepine", "Opioide", "Umstellung", "Erweitert", "Historie"
])

# --- Tab 1: Benzodiazepine ---
with tab1:
    st.header("Benzodiazepin Umrechner")
    
    col1, col2 = st.columns(2)
    with col1:
        med_name = st.selectbox("Medikament auswählen", sorted(list(converter.DISPLAY_NAMES.values())))
    with col2:
        dose = st.number_input("Dosis in mg", min_value=0.0, value=0.0, step=0.1)
    
    if st.button("Umrechnen", key="btn_benzo"):
        try:
            med_key = next(k for k, v in converter.DISPLAY_NAMES.items() if v == med_name)
            equiv, factor = converter.convert_to_diazepam(med_key, dose)
            st.success(f"**Ergebnis:** {dose} mg {med_name} ≈ **{equiv:.2f} mg Diazepam**")
            st.info(f"Verhältnis: 1 mg {med_name} ≈ {factor:.2f} mg Diazepam")
        except Exception as e:
            st.error(f"Fehler: {e}")

    st.markdown("---")
    st.subheader("Äquivalenztabelle")
    st.markdown(converter.get_equivalence_markdown())

# --- Tab 2: Opioide ---
with tab2:
    st.header("Opioid Umrechner")
    
    col1, col2 = st.columns(2)
    with col1:
        op_name = st.selectbox("Opioid auswählen", sorted(list(set(d.capitalize() for (d, r) in converter.OPIOID_TABLE.keys()))))
    with col2:
        route = st.selectbox("Verabreichungsweg", ["oral", "iv", "sc", "sl", "td"])
    
    col3, col4 = st.columns(2)
    with col3:
        op_dose = st.number_input("Dosis (mg / µg für Fentanyl)", min_value=0.0, value=0.0, step=0.1)
    with col4:
        prev_ome = st.number_input("Vorherige OME (nur für Methadon)", min_value=0.0, value=0.0, step=1.0)
        if prev_ome == 0.0: prev_ome = None

    discount = st.slider("Cross-Tolerance Abschlag (%)", 0, 100, 0)

    if st.button("Umrechnen", key="btn_opioid"):
        try:
            ome = converter.to_morphine_ome(op_name, op_dose, route, prev_ome, float(discount))
            unit = "µg" if "fentanyl" in op_name.lower() else "mg"
            if "fentanyl" in op_name.lower() and route == "td": unit = "µg/h"
            
            st.success(f"**Ergebnis:** {op_dose} {unit} {op_name} ({route}) ≈ **{ome} mg OME**")
        except Exception as e:
            st.error(f"Fehler: {e}")

# --- Tab 3: Umstellung ---
with tab3:
    st.header("Dosis Umstellung")
    
    conv_type = st.radio("Typ auswählen", ["Benzodiazepine", "Opioide"], horizontal=True)
    
    if conv_type == "Benzodiazepine":
        col1, col2 = st.columns(2)
        with col1:
            from_med = st.selectbox("Von:", sorted(list(converter.DISPLAY_NAMES.values())))
        with col2:
            to_med = st.selectbox("Auf:", sorted(list(converter.DISPLAY_NAMES.values())))
        dose_conv = st.number_input("Dosis (mg)", min_value=0.0, value=0.0, step=0.1)
        
        if st.button("Umstellen", key="btn_conv_benzo"):
            try:
                from_k = next(k for k, v in converter.DISPLAY_NAMES.items() if v == from_med)
                to_k = next(k for k, v in converter.DISPLAY_NAMES.items() if v == to_med)
                diaz_equiv, _ = converter.convert_to_diazepam(from_k, dose_conv)
                target_dose = converter.from_diazepam(to_k, diaz_equiv)
                st.success(f"**{dose_conv} mg {from_med} ≈ {target_dose:.2f} mg {to_med}**\n(entspricht {diaz_equiv:.2f} mg Diazepam)")
            except Exception as e:
                st.error(f"Fehler: {e}")
                
    else:
        col1, col2 = st.columns(2)
        with col1:
            from_op = st.selectbox("Von:", sorted(list(set(d.capitalize() for (d, r) in converter.OPIOID_TABLE.keys()))))
            from_route = st.selectbox("Weg (von):", ["oral", "iv", "sc", "sl", "td"])
        with col2:
            to_op = st.selectbox("Auf:", sorted(list(set(d.capitalize() for (d, r) in converter.OPIOID_TABLE.keys()))))
            to_route = st.selectbox("Weg (auf):", ["oral", "iv", "sc", "sl", "td"])
        dose_conv_op = st.number_input("Dosis", min_value=0.0, value=0.0, step=0.1)
        
        if st.button("Umstellen", key="btn_conv_op"):
            try:
                ome_equiv = converter.to_morphine_ome(from_op, dose_conv_op, from_route)
                target_dose = converter.from_morphine_ome(to_op, ome_equiv, to_route)
                st.success(f"**{dose_conv_op} mg {from_op} ({from_route}) ≈ {target_dose:.2f} mg {to_op} ({to_route})**\n(entspricht {ome_equiv:.2f} mg OME)")
            except Exception as e:
                st.error(f"Fehler: {e}")

# --- Tab 4: Erweitert ---
with tab4:
    st.header("Erweiterte Funktionen")
    
    with st.expander("Benutzerdefiniertes Opioid hinzufügen"):
        c_name = st.text_input("Name")
        c_route = st.text_input("Weg (z.B. oral)")
        c_fact = st.number_input("Faktor zu oralem Morphin", min_value=0.0, step=0.1)
        if st.button("Speichern"):
            try:
                converter.save_custom_drug(c_name, c_route, c_fact)
                st.success(f"Medikament {c_name} gespeichert!")
            except Exception as e:
                st.error(f"Fehler: {e}")

    with st.expander("Toleranz-Modell"):
        t_type = st.radio("Typ", ["Opioid (OME)", "Benzo (mg Diazepam)"], horizontal=True)
        t_start = st.number_input("Start-Dosis", min_value=0.0, step=1.0)
        t_days = st.number_input("Zeitraum (Tage)", min_value=0, step=1)
        t_rate = st.number_input("Steigerungsrate (z.B. 0.02)", value=0.02, step=0.01)
        
        if st.button("Toleranz berechnen"):
            res = converter.calculate_tolerance_development(t_start, t_days, t_rate)
            unit = "mg OME" if t_type == "Opioid (OME)" else "mg Diazepam"
            st.success(f"Erwartete Dosis nach {t_days} Tagen: **{res} {unit}**")

# --- Tab 5: Historie ---
with tab5:
    st.header("Änderungshistorie")
    history = converter.get_history()
    if history:
        for h in history:
            st.write(f"**[{h['date']}]** {h['type']} - {h['drug']}: {h['change']}")
    else:
        st.write("Keine Einträge vorhanden.")
