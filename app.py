# -*- coding: utf-8 -*-
import streamlit as st
import math

# Configuración de la página
st.set_page_config(page_title="Evaluador Preanestésico Avanzado", page_icon="🩺", layout="wide")

st.title("🩺 Asistente de Evaluación Preanestésica y Riesgo Perioperatorio")
st.write("Desarrollado para la optimización clínica intraoperatoria y seguridad del paciente.")

# Dividir la pantalla en dos columnas: Entradas (Izquierda) y Reporte (Derecha)
col_izq, col_der = st.columns([1, 1.2])

with col_izq:
    st.header("📋 Datos de Entrada del Paciente")
    
    # 1. Datos Demográficos y Antropometría
    with st.expander("1. Datos Demográficos y Antropometría", expanded=True):
        c1, c2, c3 = st.columns(3)
        sexo = c1.radio("Sexo", ["Masculino", "Femenino"])
        edad = c2.number_input("Edad (años)", min_value=1, max_value=120, value=50)
        peso_real = c3.number_input("Peso Real (kg)", min_value=30.0, max_value=250.0, value=70.0)
        talla_cm = c3.number_input("Talla (cm)", min_value=100, max_value=220, value=165)

    # 2. Seguridad, Alergias y Medicamentos
    with st.expander("2. Seguridad, Alergias y Medicamentos"):
        alergias = st.text_input("Alergias Conocidas", "Negadas")
        medicamentos = st.text_input("Medicamentos Críticos en Uso", "Ninguno")
        st.markdown("**Antecedentes Clínicos:**")
        c_ant1, c_ant2 = st.columns(2)
        tiene_infarto = c_ant1.checkbox("Infarto de Miocardio (< 6 meses)")
        tiene_ic = c_ant1.checkbox("Insuficiencia Cardíaca Congestiva")
        tiene_acv = c_ant1.checkbox("Historia de ACV o AIT")
        tiene_insulina = c_ant2.checkbox("Diabetes bajo tratamiento con Insulina")
        tiene_ev = c_ant2.checkbox("> 5 Extrasístoles Ventriculares/min")
        tiene_ritmo_no_s = c_ant2.checkbox("Ritmo no sinusal / EAs en EKG")
        tiene_cancer = c_ant1.checkbox("Cáncer Activo o previo")
        tiene_epoc = c_ant2.checkbox("EPOC o Enfermedad Pulmonar Crónica")

    # 3. Vía Aérea
    with st.expander("3. Valoración Estructural de la Vía Aérea"):
        c_va1, c_va2 = st.columns(2)
        mallampati = c_va1.selectbox("Clasificación Mallampati", ["Clase I", "Clase II", "Clase III", "Clase IV"])
        dtm = c_va1.number_input("Distancia Tiromentoniana (cm)", min_value=2.0, max_value=20.0, value=7.0)
        dem = c_va2.number_input("Distancia Esternomentoniana (cm)", min_value=5.0, max_value=25.0, value=13.0)
        cuello = c_va2.number_input("Circunferencia de Cuello (cm)", min_value=20, max_value=60, value=38)
        protrusion = st.selectbox("Protrusión Mandibular", ["Clase I", "Clase II", "Clase III"])
        historia_vad = st.checkbox("Historia previa de VAD")
        patologia_vad = st.checkbox("Patología asociada a VAD")
        apertura_bucal = st.checkbox("Apertura Bucal < 3.5 cm")
        movilidad_cervical = st.selectbox("Movilidad Cabeza/Cuello", ["> 90° (Normal)", "90° ± 10° (Limitación moderada)", "< 80° (Limitación severa)"])

    # 4. Laboratorios
    with st.expander("4. Laboratorios y Paraclínicos"):
        creatinina = st.number_input("Creatinina Sérica (mg/dL)", min_value=0.1, max_value=15.0, value=0.9, step=0.1)
        alteraciones_lab = st.text_area("Otras alteraciones de laboratorio", "Sin alteraciones de importancia perioperatoria.")

    # 5. EKG Patológico
    with st.expander("5. Hallazgos EKG"):
        ekg_sinusal = st.checkbox("Ritmo Sinusal Normal", value=True)
        ekg_fa = st.checkbox("Fibrilación Auricular / Flutter")
        ekg_bav1 = st.checkbox("Bloqueo AV 1er Grado")
        ekg_bav2 = st.checkbox("Bloqueo AV 2do Grado")
        ekg_bav3 = st.checkbox("Bloqueo AV 3er Grado")
        ekg_bicia = st.checkbox("Bloqueo de Rama (BRIHH/BRDHH)")
        ekg_st_supra = st.checkbox("Supradesnivel ST")
        ekg_st_infra = st.checkbox("Infradesnivel ST / T Inv")
        ekg_hvi = st.checkbox("Hipertrofia Ventricular (HVI)")
        ekg_qt_largo = st.checkbox("Intervalo QT Prolongado")
        otros_hallazgos_ekg = st.text_input("Otros hallazgos EKG", "Ninguno")

    # 6. Quirúrgicos + Plan Anestésico
    with st.expander("6. Datos Quirúrgicos y Plan Anestésico"):
        cx_dict = {
            "Colecistectomía Lap.": "Intermedio", "Apendicectomía": "Intermedio",
            "Hernioplastia": "Bajo", "Artroplastia": "Intermedio",
            "Cesárea": "Bajo", "Bypass Coronario (CRM)": "Alto",
            "Laparotomía": "Alto", "Otra": "Intermedio"
        }
        cx_sel = st.selectbox("Procedimiento:", list(cx_dict.keys()))
        if cx_sel == "Otra":
            nombre_cx = st.text_input("Nombre Cx:", "Cirugía General")
            riesgo_cx_tipo = st.selectbox("Riesgo:", ["Bajo", "Intermedio", "Alto"])
        else:
            nombre_cx = cx_sel
            riesgo_cx_tipo = cx_dict[cx_sel]
        cirugia_emergencia = st.checkbox("Cirugía de Emergencia")
        plan_anestesico = st.selectbox("Plan Anestésico:", ["General", "Sedación", "Raquídea", "Epidural"])

    # 7. Riesgos Adicionales
    with st.expander("7. Riesgos Adicionales (Caprini/Apfel)"):
        no_fumador = st.checkbox("Paciente es NO Fumador", value=True)
        historia_nvpo = st.checkbox("Historia previa de NVPO")
        opioides_post = st.checkbox("Uso planeado de opioides post-op", value=True)
        varices = st.checkbox("Várices")
        edema_mi = st.checkbox("Edema MMII")
        inmovilizacion = st.checkbox("Inmovilización > 72 horas")
        trombofilia = st.checkbox("Trombofilia")
        acceso_central = st.checkbox("Acceso central")

# --- LÓGICA DE CÁLCULO ---
talla_m = talla_cm / 100.0
imc = peso_real / (talla_m ** 2)
asc = math.sqrt((peso_real * talla_cm) / 3600)
peso_predicho = (50.0 if sexo == "Masculino" else 45.5) + 0.91 * (talla_cm - 152.4)
p_arne = (5 if historia_vad else 0) + (5 if patologia_vad else 0) + (2 if mallampati=="Clase III" else 5 if mallampati=="Clase IV" else 0)
p_lee = (1 if riesgo_cx_tipo=="Alto" else 0) + (1 if tiene_infarto else 0) + (1 if tiene_ic else 0) + (1 if tiene_acv else 0) + (1 if tiene_insulina else 0) + (1 if creatinina>2.0 else 0)
p_caprini = (1 if 41<=edad<=60 else 2 if 61<=edad<=74 else 3 if edad>=75 else 0) + (2 if riesgo_cx_tipo!="Bajo" else 0) + (2 if inmovilizacion else 0) + (2 if tiene_cancer else 0)
p_apfel = (1 if sexo=="Femenino" else 0) + (1 if no_fumador else 0) + (1 if historia_nvpo else 0) + (1 if opioides_post else 0)

lista_ekg = [k for k, v in [("Sinusal", ekg_sinusal), ("FA/Flutter", ekg_fa), ("BAV1", ekg_bav1), ("BAV2", ekg_bav2), ("BAV3", ekg_bav3), ("Bloqueo Rama", ekg_bicia), ("ST Supra", ekg_st_supra), ("ST Infra", ekg_st_infra), ("HVI", ekg_hvi), ("QT Largo", ekg_qt_largo)] if v]
if otros_hallazgos_ekg != "Ninguno": lista_ekg.append(otros_hallazgos_ekg)
diag_ekg = ", ".join(lista_ekg) if lista_ekg else "Normal"

# --- REPORTE Y PESTAÑAS ---
with col_der:
    st.header("📊 Reporte Clínico Consolidado")
    tab1, tab2 = st.tabs(["📝 Reporte Preanestésico", "⚙️ Plan Transquirúrgico"])
    
    with tab1:
        if st.button("🔄 ACTUALIZAR REPORTE", type="primary"):
            st.write(f"**Paciente:** {sexo}, {edad} años. **Cirugía:** {nombre_cx}.")
            st.write(f"**Plan Anestésico:** {plan_anestesico}")
            st.write(f"**Riesgo:** Arné: {p_arne}, Lee: {p_lee}, Caprini: {p_caprini}, Apfel: {p_apfel}/4.")
            st.write(f"**EKG:** {diag_ekg}")
            st.subheader("📋 Resumen para Copiar")
            texto_hc = f"PREANESTESIA: {sexo}, {edad}a. IMC {imc:.1f}. Cx: {nombre_cx}. Anestesia: {plan_anestesico}. Lee: {p_lee}. EKG: {diag_ekg}. Alergias: {alergias}. Arné: {p_arne} pts."
            st.code(texto_hc, language="text")
            
    with tab2:
        if st.button("⚙️ GENERAR PLAN", type="primary"):
            st.subheader("⚙️ Plan Intraoperatorio")
            vt = peso_predicho * 7
            st.write(f"• **Vt Protector:** {vt:.0f} mL")
            st.write(f"• **PEEP Sugerido:** {10 if imc>=30 else 5} cmH2O")
            st.write(f"• **Mantenimiento:** {peso_real+40:.0f} mL/hr")
            st.write(f"• **Plan Anestésico:** {plan_anestesico}")
            st.code(f"PLAN {plan_anestesico.upper()}: Vt {vt:.0f}mL. Mantenimiento {peso_real+40:.0f}mL/hr.", language="text")
