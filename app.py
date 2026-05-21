# -*- coding: utf-8 -*-
import streamlit as st
import math

st.set_page_config(page_title="Preanestesia", page_icon="🩺", layout="wide")
st.title("🩺 Asistente de Evaluación Preanestésica")

col_izq, col_der = st.columns([1, 1.2])

with col_izq:
    st.header("📋 Datos de Entrada")
    
    with st.expander("1. Datos Demográficos", expanded=True):
        c1, c2, c3 = st.columns(3)
        sexo = c1.radio("Sexo", ["Masculino", "Femenino"])
        edad = c2.number_input("Edad (años)", min_value=1, value=50)
        peso_real = c3.number_input("Peso (kg)", min_value=30.0, value=70.0)
        talla_cm = st.number_input("Talla (cm)", min_value=100, value=165)

    with st.expander("2. Seguridad y Fármacos", expanded=True):
        st.markdown("**🚨 Alergias**")
        alergias_med = st.multiselect("Meds:", ["Penicilina", "AINEs", "Sulfa", "Contraste", "Látex", "Relajantes", "Opioides", "Dipirona"])
        alergias_com = st.multiselect("Alimentos:", ["Mariscos", "Chocolate", "Soja", "Frutos Secos", "Huevo", "Lácteos", "Gluten", "Pescado"])
        otras_alergias = st.text_input("Otras alergias:", "")
        
        st.markdown("**💊 Fármacos y Antecedentes**")
        farmacos_criticos = st.multiselect("Fármacos:", ["Betabloqueantes", "IECA/ARA II", "Antiagregantes", "Anticoagulantes", "Insulina", "Antidiabéticos", "Corticoides", "Anticonvulsivantes"])
        otros_farmacos = st.text_input("Otros fármacos:", "")
        
        c_ant1, c_ant2 = st.columns(2)
        tiene_infarto = c_ant1.checkbox("Infarto (< 6 meses)")
        tiene_ic = c_ant1.checkbox("Insuficiencia Cardíaca")
        tiene_acv = c_ant1.checkbox("ACV o AIT")
        tiene_cancer = c_ant1.checkbox("Cáncer Activo")
        tiene_insulina = c_ant2.checkbox("Diabetes + Insulina")
        tiene_ev = c_ant2.checkbox("> 5 Extrasístoles/min")
        tiene_ritmo_no_s = c_ant2.checkbox("Ritmo no sinusal / FA")
        tiene_epoc = c_ant2.checkbox("EPOC")

    with st.expander("3. Vía Aérea y Ventilación"):
        mallampati = st.selectbox("Mallampati", ["Clase I", "Clase II", "Clase III", "Clase IV"])
        dtm = st.number_input("DTM (cm)", value=7.0)
        dem = st.number_input("DEM (cm)", value=13.0)
        cuello = st.number_input("Cuello (cm)", value=38)
        
        historia_vad = st.checkbox("Historia previa VAD")
        patologia_vad = st.checkbox("Patología VAD")
        apertura_bucal = st.checkbox("Apertura Bucal < 3.5 cm")
        movilidad_sel = st.selectbox("Movilidad (0=Normal, 1=Mod, 2=Sev):", [0, 1, 2])
        tiene_barba = st.checkbox("Barba densa")
        tiene_edentulia = st.checkbox("Edentulia")
        tiene_ronquido = st.checkbox("Ronquido / SAHOS")

    with st.expander("4. Laboratorios", expanded=True):
        dict_labs = {}
        hb, hto, creatinina = 13.0, 40.0, 0.9 
        
        if st.checkbox("Hb / Hto", value=True):
            hb = st.number_input("Hb", value=13.0)
            hto = st.number_input("Hto", value=40.0)
            dict_labs["Hemograma"] = f"Hb: {hb}, Hto: {hto}%"
        if st.checkbox("Plaquetas", value=True):
            plt = st.number_input("Plaquetas", value=250)
            dict_labs["Plaquetas"] = f"{plt} x10³"
        if st.checkbox("Coagulación", value=True):
            tp = st.number_input("TP", value=12.5)
            tpt = st.number_input("TPT", value=32.0)
            dict_labs["Tiempos"] = f"TP: {tp}s, TPT: {tpt}s"
        if st.checkbox("Renal", value=True):
            urea = st.number_input("Urea", value=30)
            creatinina = st.number_input("Creatinina", value=0.9)
            dict_labs["Renal"] = f"U: {urea}, Cr: {creatinina}"
        if st.checkbox("Albúmina", value=True):
            alb = st.number_input("Albúmina", value=4.0)
            dict_labs["Albúmina"] = f"{alb} g/dL"
        alteraciones_lab = st.text_input("Otros labs:", "Sin alteraciones")

    with st.expander("5. EKG", expanded=True):
        c_ekg1, c_ekg2 = st.columns(2)
        ekg_sinusal = c_ekg1.checkbox("Ritmo Sinusal Normal", value=True)
        ekg_fa = c_ekg1.checkbox("FA / Flutter")
        ekg_bav1 = c_ekg1.checkbox("BAV 1er Grado")
        ekg_bav2 = c_ekg1.checkbox("BAV 2do Grado")
        ekg_bav3 = c_ekg1.checkbox("BAV 3er Grado")
        ekg_bicia = c_ekg2.checkbox("Bloqueo de Rama")
        ekg_st_supra = c_ekg2.checkbox("ST Supradesnivel")
        ekg_st_infra = c_ekg2.checkbox("ST Infradesnivel / T Inv")
        ekg_hvi = c_ekg2.checkbox("HVI (Sokolow +)")
        ekg_qt_largo = c_ekg2.checkbox("QT Prolongado")
        otros_hallazgos_ekg = st.text_input("Otros EKG:", "Ninguno")

    with st.expander("6. Plan Quirúrgico y Anestésico", expanded=True):
        cx_comunes = {
            "Colecistectomía Lap.": "Intermedio",
            "Apendicectomía": "Intermedio",
            "Hernioplastia": "Bajo",
            "Histerectomía": "Intermedio",
            "Artroplastia": "Intermedio",
            "Cesárea": "Bajo",
            "Cataratas": "Bajo",
            "Prostatectomía": "Intermedio",
            "Mastectomía": "Bajo",
            "Bypass / CRM": "Alto",
            "Amputación Mayor": "Alto",
            "Laparotomía": "Alto",
            "Otra": "Intermedio"
        }
        cx_sel = st.selectbox("Cirugía Planeada:", list(cx_comunes.keys()))
        if cx_sel == "Otra":
            nombre_cx = st.text_input("Nombre Cx:", "Cirugía General")
            riesgo_cx_tipo = st.selectbox("Riesgo Quirúrgico:", ["Bajo", "Intermedio", "Alto"], index=1)
        else:
            nombre_cx = cx_sel
            riesgo_cx_tipo = cx_comunes[cx_sel]
        
        cirugia_emergencia = st.checkbox("Cirugía de Emergencia")
        
        st.markdown("---")
        plan_anestesico = st.selectbox("💉 Plan Anestésico Principal:", ["General", "Sedación", "Raquídea", "Epidural"])

    with st.expander("7. Riesgos Adicionales (Caprini/Apfel)"):
        no_fumador = st.checkbox("NO Fumador", value=True)
        historia_nvpo = st.checkbox("Historia NVPO")
        opioides_post = st.checkbox("Opioides post-op", value=True)
        varices = st.checkbox("Várices venosas")
        edema_mi = st.checkbox("Edema MMII")
        inmovilizacion = st.checkbox("Inmovilizado >72h")
        trombofilia = st.checkbox("Trombofilia")
        acceso_central = st.checkbox("Acceso central")

# --- LÓGICA MATEMÁTICA ---
talla_m = talla_cm / 100.0
imc = peso_real / (talla_m ** 2)
asc = math.sqrt((peso_real * talla_cm) / 3600)

if sexo == "Masculino":
    peso_ideal = 50.0 + 2.3 * ((talla_cm / 2.54) - 60.0)
    peso_predicho = 50.0 + 0.91 * (talla_cm - 152.4)
    cg_factor, ckd_kappa, ckd_alfa, ckd_const = 1.0, 0.9, -0.411, 141
else:
    peso_ideal = 45.5 + 2.3 * ((talla_cm / 2.54) - 60.0)
    peso_predicho = 45.5 + 0.91 * (talla_cm - 152.4)
    cg_factor, ckd_kappa, ckd_alfa, ckd_const = 0.85, 0.7, -0.329, 144

peso_ajust_20 = peso_ideal + 0.2 * (peso_real - peso_ideal) if imc >= 25 else peso_real
peso_ajust_40 = peso_ideal + 0.4 * (peso_real - peso_ideal) if imc >= 25 else peso_real

clcr_cg = ((140 - edad) * peso_real / (72 * max(creatinina, 0.1))) * cg_factor
tfg_ckd = ckd_const * (min(creatinina/ckd_kappa, 1)**ckd_alfa) * (max(creatinina/ckd_kappa, 1)**ckd_alfa) * (0.993**edad)

vt_min = peso_predicho * 6
vt_max = peso_predicho * 8
peep_ideal = 10 if imc >= 40 else 8 if imc >= 30 else 5
fluido_mantenimiento = peso_real + 40 
volemia_est = peso_real * (70 if sexo == "Masculino" else 65)
hto_meta = 30.0 if (tiene_ic or tiene_infarto) else 25.0
sangrado_permisible = volemia_est * (hto - hto_meta) / hto if hto > hto_meta else 0

p_arne = (5 if historia_vad else 0) + (5 if patologia_vad else 0) + (2 if mallampati=="Clase III" else 5 if mallampati=="Clase IV" else 0) + (4 if dtm<=6.5 else 0) + (4 if apertura_bucal else 0) + (2 if movilidad_sel==1 else 5 if movilidad_sel==2 else 0)
p_stop = (1 if tiene_ronquido else 0) + (1 if imc>35 else 0) + (1 if edad>50 else 0) + (1 if cuello>40 else 0) + (1 if sexo=="Masculino" else 0)
p_lee = (1 if riesgo_cx_tipo=="Alto" else 0) + (1 if tiene_infarto else 0) + (1 if tiene_ic else 0) + (1 if tiene_acv else 0) + (1 if tiene_insulina else 0) + (1 if creatinina>2.0 else 0)
p_goldman = (5 if edad>70 else 0) + (10 if tiene_infarto else 0) + (7 if tiene_ritmo_no_s else 0) + (7 if tiene_ev else 0) + (11 if tiene_ic else 0) + (4 if cirugia_emergencia else 0) + (3 if riesgo_cx_tipo in ["Intermedio", "Alto"] else 0)
p_caprini = (1 if 41<=edad<=60 else 2 if 61<=edad<=74 else 3 if edad>=75 else 0) + (1 if imc>25 else 0) + (1 if varices else 0) + (1 if edema_mi else 0) + (1 if tiene_ic else 0) + (1 if tiene_epoc else 0) + (1 if tiene_infarto else 0) + (2 if riesgo_cx_tipo!="Bajo" else 0) + (2 if inmovilizacion else 0) + (2 if tiene_cancer else 0) + (2 if acceso_central else 0) + (3 if trombofilia else 0)
p_apfel = (1 if sexo=="Femenino" else 0) + (1 if no_fumador else 0) + (1 if historia_nvpo else 0) + (1 if opioides_post else 0)

lista_ekg = []
if ekg_sinusal: lista_ekg.append("Sinusal")
if ekg_fa: lista_ekg.append("FA/Flutter")
if ekg_bav1: lista_ekg.append("BAV 1")
if ekg_bav2: lista_ekg.append("BAV 2")
if ekg_bav3: lista_ekg.append("BAV 3")
if ekg_bicia: lista_ekg.append("Bloqueo Rama")
if ekg_st_supra: lista_ekg.append("ST Supra")
if ekg_st_infra: lista_ekg.append("ST Infra")
if ekg_hvi: lista_ekg.append("HVI")
if ekg_qt_largo: lista_ekg.append("QT Largo")
if otros_hallazgos_ekg != "Ninguno": lista_ekg.append(otros_hallazgos_ekg)
diag_ekg = ", ".join(lista_ekg) if lista_ekg else "Normal"

str_almed = ", ".join(alergias_med) if alergias_med else "Negadas"
str_alcom = ", ".join(alergias_com) if alergias_com else "Negadas"
str_far = ", ".join(farmacos_criticos) if farmacos_criticos else "Ninguno"

# --- COLUMNA DE REPORTE CON PESTAÑAS (TABS) ---
with col_der:
    st.header("📊 Panel Clínico Integrado")
    
    # Creación de las dos pestañas nativas
    tab_preanestesia, tab_transquirurgico, tab_dosificacion, tab_gasometria = st.tabs(["📝 Reporte Preanestésico", "⚙️ Plan Transquirúrgico","🧪 Dosificación", "🩸 Gasometría"])
    
    # ----------------------------------------------------------------
    # PESTAÑA 1: EVALUACIÓN PREANESTÉSICA (El reporte clásico)
    # ----------------------------------------------------------------
    with tab_preanestesia:
            st.subheader("📝 Reporte Preanestésico en Tiempo Real")
            st.markdown("""<style>.reporte-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; } h4 { color: #1e3d59; }</style>""", unsafe_allow_html=True)
            
            st.markdown(f"### 🩺 Reporte de Evaluación Preanestésica Avanzada")
            st.markdown(f"**Paciente:** {sexo} | {edad} años | **Peso Real:** {peso_real:.1f} kg | **Talla:** {talla_cm} cm\n\n**Área de Superficie Corporal (Mosteller):** **{asc:.2f} m²**")
            
            st.markdown(f"---\n#### 🧮 Evaluación del IMC y Pesos Clínicos")
            st.markdown(f"* **IMC:** **{imc:.1f} kg/m²** → ({'Bajo Peso' if imc < 18.5 else 'Normal' if imc < 25 else 'Sobrepeso' if imc < 30 else 'Obesidad'})")
            st.markdown(f"* **Peso Ideal (Devine):** **{peso_ideal:.1f} kg**")
            st.markdown(f"* **Peso Predicho (ARDSNet):** **{peso_predicho:.1f} kg**")
            if imc >= 25:
                st.markdown(f"> ⚠️ **Pesos Ajustados:** TIVA/Lipofílicos: **{peso_ajust_20:.1f} kg** | RMM/Hidrofílicos: **{peso_ajust_40:.1f} kg**")
            
            st.markdown(f"---\n#### 🚨 Seguridad Perioperatoria y Fármacos")
            st.markdown(f"* **Alergias:** {str_alergias_med.upper()} (Meds) | {str_alergias_com.upper()} (Alimentos)")
            st.markdown(f"* **Fármacos Críticos:** {str_farmacos}")
            
            st.markdown(f"---\n#### 🫁 Evaluación de la Vía Aérea y Ventilación")
            st.markdown(f"* **Mallampati:** {mallampati} | **DTM:** {dtm} cm | **DEM:** {dem} cm | **Cuello:** {cuello} cm")
            st.markdown(f"* 📋 **Índice de Arné:** **{p_arne} puntos** → RIESGO INTUBACIÓN: **{'ALTO (≥11)' if p_arne >= 11 else 'BAJO'}**")
            st.markdown(f"* 💤 **STOP-BANG (SAHOS):** **{p_stop} / 8 puntos**")
            
            st.markdown(f"---\n#### 🧪 Laboratorios y Función Renal")
            str_labs_resumen = ""
            if not dict_labs:
                st.error("❌ No hay datos de laboratorios")
                str_labs_resumen = "No provistos"
            else:
                for item, valor in dict_labs.items():
                    st.markdown(f"• **{item}:** {valor}")
                    str_labs_resumen += f"{item}: {valor} | "
            st.markdown(f"* **TFG (CKD-EPI):** {tfg_ckd:.0f} mL/min | **Aclaramiento (C-G):** {clcr_cg:.0f} mL/min")
            
            st.markdown(f"---\n#### 🛡️ Estratificación de Riesgo Perioperatorio")
            st.markdown(f"* **Cirugía:** {nombre_cx} ({riesgo_cx_tipo.upper()}) {'⚠️ EMERGENCIA' if cirugia_emergencia else ''}")
            st.markdown(f"* **Riesgo Cardíaco (Lee RCRI):** Clase {('I' if p_lee==0 else 'II' if p_lee==1 else 'III' if p_lee==2 else 'IV')} ({p_lee} criterios)")
            st.markdown(f"* **Riesgo Cardíaco (Goldman):** Clase {('I (0-5)' if p_goldman<=5 else 'II (6-12)' if p_goldman<=12 else 'III (13-25)' if p_goldman<=25 else 'IV (≥26)')} ({p_goldman} pts)")
            st.markdown(f"* **Tromboembólico (Caprini):** {p_caprini} puntos")
            st.markdown(f"* **NVPO (Apfel):** {p_apfel} / 4")
            
            st.markdown(f"---\n#### 🫀 Interpretación EKG")
            st.markdown(f"* **Patología Principal:** {diagnostico_ekg_consolidado.upper()}")
            
            st.markdown("---")
            st.subheader("📋 Resumen para Copiar")
            
            ant_lista = []
            if tiene_infarto: ant_lista.append("Infarto <6m")
            if tiene_ic: ant_lista.append("ICC")
            if tiene_acv: ant_lista.append("ACV")
            if tiene_insulina: ant_lista.append("DM2+Insulina")
            if tiene_ev: ant_lista.append(">5 EV")
            if tiene_ritmo_no_s: ant_lista.append("Ritmo No Sinusal")
            if tiene_cancer: ant_lista.append("Cáncer")
            if tiene_epoc: ant_lista.append("EPOC")
            ant_texto = ", ".join(ant_lista) if ant_lista else "Negados"

            texto_hc = (
                f"NOTA PREANESTÉSICA\n"
                f"PACIENTE: {sexo} | Edad: {edad}a. IMC: {imc:.1f} kg/m2. ASC: {asc:.2f} m2.\n"
                f"ALERGIAS: {str_alergias_med.upper()} / {str_alergias_com.upper()}\n"
                f"MEDICACIÓN: {str_farmacos}\n"
                f"ANTECEDENTES: {ant_texto}\n"
                f"VÍA AÉREA: Mallampati {mallampati}, DTM {dtm}cm, DEM {dem}cm. Arné: {p_arne}pts. STOP-BANG: {p_stop}/8.\n"
                f"LABS: {str_labs_resumen} | TFG: {tfg_ckd:.0f} mL/min.\n"
                f"EKG: {diagnostico_ekg_consolidado.upper()}\n"
                f"RIESGOS: Cx: {nombre_cx}. Lee RCRI: Clase {'I' if p_lee==0 else 'II' if p_lee==1 else 'III' if p_lee==2 else 'IV'}. Goldman: {p_goldman}pts. Caprini: {p_caprini}pts. Apfel: {p_apfel}/4."
            )
            st.code(texto_hc, language="text")
# ----------------------------------------------------------------
    # PESTAÑA 2: PLAN TRANSQUIRÚRGICO (Módulo Interactivo)
    # ----------------------------------------------------------------
    with tab_transquirurgico:
      # 1. CÁLCULOS ANTROPOMÉTRICOS (Anclados a la derecha)
        st.subheader("📏 Perfil Antropométrico (Basal)")
        
        # Fórmulas de cálculo rápido
        sc = ((talla_cm * peso_real) / 3600) ** 0.5
        ibw = (50.0 if sexo == "Masculino" else 45.5) + 0.91 * (talla_cm - 152.4)
        imc = peso_real / ((talla_cm / 100) ** 2)
        abw_20 = ibw + 0.2 * (peso_real - ibw)
        abw_40 = ibw + 0.4 * (peso_real - ibw)
        pbw = (50.0 if sexo == "Masculino" else 45.5) + 0.91 * (talla_cm - 152.4)
        
        # Display de métricas en columnas (Layout Profesional)
        c_ant1, c_ant2 = st.columns(2)
        c_ant1.metric("Peso Ideal (IBW)", f"{ibw:.1f} kg")
        c_ant2.metric("Sup. Corporal", f"{sc:.2f} m²")
        
        c_ant3, c_ant4 = st.columns(2)
        c_ant3.metric("ABW 20%", f"{abw_20:.1f} kg")
        c_ant4.metric("ABW 40%", f"{abw_40:.1f} kg")
        
        st.info(f"**IMC Actual:** {imc:.1f} kg/m² | **Clasificación:** {'Obesidad' if imc >= 30 else 'Normopeso/Sobrepeso'}")
        
        st.markdown("---")
        st.subheader("🩸 Monitor de Sangrado & PSP")
        
        # Inputs de laboratorio y sangrado
        c_sang1, c_sang2, c_sang3 = st.columns(3)
        with c_sang1:
            st.metric("Hto Act (%)", f"{hto:.1f}")
        with c_sang2:
            hto_meta = st.number_input("Hto Mín (%)", value=30.0)
        with c_sang3:
            sangrado_ml = st.number_input("Sangrado Total (mL)", min_value=0.0, value=0.0, step=50.0)
            
        # Lógica PSP
        volemia = peso_real * (70 if sexo == "Masculino" else 65)
        psp_max = volemia * (hto - hto_meta) / hto
        
        c_res1, c_res2 = st.columns(2)
        c_res1.metric("PSP MÁXIMA", f"{max(0, psp_max):.0f} mL")
        c_res2.info(f"Estado: {'⚠️ ALERTA' if sangrado_ml >= psp_max else '✅ OK'}")
        
        # Cálculos de fluidos
        mant = peso_real + 40
        insensibles = 4 * peso_real # Asumiendo 4 mL/kg/h
        
        # Creamos la tabla
        import pandas as pd
        data = {
            "Componente (mL)": ["Mant. (4-2-1)", "Insensibles", "Rep. Ayuno"],
            "H1": [mant, insensibles, 320],
            "H2": [mant, insensibles, 160],
            "H3": [mant, insensibles, 160]
        }
        df = pd.DataFrame(data)
        st.table(df)
        
        # Cálculo del TOTAL DE LÍQUIDOS A PASAR
        total_h1 = mant + insensibles + 320
        total_h2 = mant + insensibles + 160
        total_h3 = mant + insensibles + 160
        total_global = total_h1 + total_h2 + total_h3
        
        # Mostramos los totales al final
        c_t1, c_t2, c_t3 = st.columns(3)
        c_t1.metric("Total H1", f"{total_h1:.0f} mL")
        c_t2.metric("Total H2/H3", f"{total_h2:.0f} mL")
        c_t3.metric("TOTAL GLOBAL", f"{total_global:.0f} mL")
    
        st.markdown("---")
        st.subheader("🫁 Monitor Respiratorio y Ajuste de Capnografía")
        
        # Inputs para el monitor
        c_vent1, c_vent2 = st.columns(2)
        fr_act = c_vent1.number_input("FR Act (rpm)", value=12, key="fr_monitor_act")
        vt_act = c_vent2.number_input("VT Act (mL)", value=500, key="vt_monitor_act")
        
        # Cálculos de monitorización
        vol_min = (fr_act * vt_act) / 1000
        rel_peso_ideal = vt_act / pbw # Usando pbw definido previamente
        
        c_resv1, c_resv2 = st.columns(2)
        c_resv1.metric("VOL. MINUTO", f"{vol_min:.2f} L/min")
        c_resv2.metric("REL. PESO IDEAL", f"{rel_peso_ideal:.1f} mL/kg")
        
        # Ajuste de Capnografía
        c_paco1, c_paco2 = st.columns(2)
        paco_act = c_paco1.number_input("PaCO2 Act (mmHg)", value=50, key="paco_monitor_act")
        paco_obj = c_paco2.number_input("PaCO2 Obj (mmHg)", value=40, key="paco_monitor_obj")
        
        # Lógica de ajuste sugerido (Ecuación simplificada)
        # FR_nueva = (FR_act * PaCO2_act) / PaCO2_obj
        fr_sugerida = (fr_act * paco_act) / paco_obj
        vt_sugerido = (vt_act * paco_act) / paco_obj
        
        st.markdown("### 📊 Ajuste Sugerido de Capnografía")
        c_sug1, c_sug2 = st.columns(2)
        c_sug1.metric("Modificar FR", f"{fr_sugerida:.0f} rpm")
        c_sug2.metric("Modificar VT", f"{vt_sugerido:.0f} mL")
        
        # Alerta de seguridad (Ventilación Protectora)
        if (vt_sugerido / pbw) > 8:
            st.warning("⚠️ Alerta: El VT sugerido excede los 8 mL/kg (Riesgo de volutrauma).")
        else:
            st.success("✅ Ajuste dentro de rangos protectores.")
    # ----------------------------------------------------------------
    # PESTAÑA 3: DOSIFICACIÓN (INTERACTIVA)
    # ----------------------------------------------------------------
    with tab_dosificacion:
        st.subheader(f"🧪 Dosificación: {plan_anestesico}")
        if plan_anestesico == "General":
            prop = st.slider("Propofol (mg/kg)", 1.0, 3.0, 2.0, 0.1)
            rocu = st.slider("Rocuronio (mg/kg)", 0.5, 1.2, 0.6, 0.1)
            st.write(f"• **Dosis Propofol:** {peso_real * prop:.1f} mg")
            st.write(f"• **Dosis Rocuronio:** {peso_real * rocu:.1f} mg")
        elif plan_anestesico == "Raquídea":
            bupi = st.slider("Bupivacaína Pesada (mg)", 7.5, 20.0, 12.5, 0.5)
            st.write(f"• **Dosis Bupivacaína:** {bupi:.1f} mg")
        elif plan_anestesico == "Sedación":
            midaz = st.slider("Midazolam (mg)", 1.0, 5.0, 2.0, 0.5)
            st.write(f"• **Dosis Midazolam:** {midaz:.1f} mg")
        else:
            st.write("Dosificación específica pendiente de configuración para esta técnica.")
 
# ----------------------------------------------------------------
    # PESTAÑA 4: GASOMETRÍA Y HOMEOSTASIS ÁCIDO-BASE (Unificada)
    # ----------------------------------------------------------------
    with tab_gasometria:
        st.subheader("🩸 Análisis Ácido-Base y Ajuste Ventilatorio")
        
        st.markdown("#### 1. Parámetros Medidos")
        col1, col2, col3 = st.columns(3)
        ph = col1.number_input("pH", value=7.40, format="%.2f", step=0.01, key="g_ph_main")
        pco2 = col2.number_input("PaCO2 (mmHg)", value=40.0, key="g_pco2_main")
        hco3 = col3.number_input("HCO3- (mEq/L)", value=24.0, key="g_hco3_main")

        col4, col5 = st.columns(2)
        na = col4.number_input("Sodio - Na+ (mEq/L)", value=140.0, key="g_na_main")
        cl = col5.number_input("Cloro - Cl- (mEq/L)", value=104.0, key="g_cl_main")

        # ----------------------------------------------------------------
        # MOTOR DE DIAGNÓSTICO
        # ----------------------------------------------------------------
        st.markdown("---")
        st.markdown("#### 2. Interpretación Diagnóstica")
        
        ph_min, ph_max = 7.35, 7.45
        pco2_min, pco2_max = 35.0, 45.0
        hco3_min, hco3_max = 22.0, 26.0
        diagnostico = "Normal"
        
        if ph < ph_min:  # ACIDEMIA
            if pco2 > pco2_max and hco3 < hco3_min: diagnostico = "Trastorno Mixto (Acidosis Metabólica + Respiratoria)"
            elif pco2 > pco2_max:
                if hco3 > hco3_max: diagnostico = "Acidosis Respiratoria Parcialmente Compensada"
                elif hco3_min <= hco3 <= hco3_max: diagnostico = "Acidosis Respiratoria No Compensada"
            elif hco3 < hco3_min:
                if pco2 < pco2_min: diagnostico = "Acidosis Metabólica Parcialmente Compensada"
                elif pco2_min <= pco2 <= pco2_max: diagnostico = "Acidosis Metabólica No Compensada"
            else: diagnostico = "⚠️ Valores discordantes (Revisar concordancia de gasometría)"
                    
        elif ph > ph_max:  # ALCALEMIA
            if pco2 < pco2_min and hco3 > hco3_max: diagnostico = "Trastorno Mixto (Alcalosis Metabólica + Respiratoria)"
            elif pco2 < pco2_min:
                if hco3 < hco3_min: diagnostico = "Alcalosis Respiratoria Parcialmente Compensada"
                elif hco3_min <= hco3 <= hco3_max: diagnostico = "Alcalosis Respiratoria No Compensada"
            elif hco3 > hco3_max:
                if pco2 > pco2_max: diagnostico = "Alcalosis Metabólica Parcialmente Compensada"
                elif pco2_min <= pco2 <= pco2_max: diagnostico = "Alcalosis Metabólica No Compensada"
            else: diagnostico = "⚠️ Valores discordantes (Revisar concordancia de gasometría)"
                    
        else:  # pH NORMAL
            if pco2 > pco2_max and hco3 > hco3_max: diagnostico = "Acidosis Respiratoria Compensada" if ph <= 7.40 else "Alcalosis Metabólica Compensada"
            elif pco2 < pco2_min and hco3 < hco3_min: diagnostico = "Acidosis Metabólica Compensada" if ph <= 7.40 else "Alcalosis Respiratoria Compensada"
            elif pco2_min <= pco2 <= pco2_max and hco3_min <= hco3 <= hco3_max: diagnostico = "Gasometría Normal"
            else: diagnostico = "⚠️ Valores discordantes (Revisar concordancia de gasometría)"

        anion_gap = na - (cl + hco3)
        st.info(f"🧬 **Diagnóstico:** {diagnostico}")
        
        c_diag1, c_diag2 = st.columns(2)
        c_diag1.metric("Anion Gap", f"{anion_gap:.1f} mEq/L", help="Rango normal: 8 - 12 mEq/L")
        if "Acidosis Metabólica" in diagnostico:
            pco2_esperada = (1.5 * hco3) + 8
            c_diag2.metric("PaCO2 Esperada (Winter)", f"{pco2_esperada:.1f} ± 2 mmHg")

        # ----------------------------------------------------------------
        # MÓDULO TERAPÉUTICO (Bicarbonato y Ventilador Consolidados)
        # ----------------------------------------------------------------
        st.markdown("---")
        st.markdown("#### 3. Parámetros de Ajuste Terapéutico")
        
        # A. REPOSICIÓN DE BICARBONATO
        st.markdown("##### 💊 Reposición Metabólica (HCO3)")
        if "Acidosis Metabólica" in diagnostico or "Mixto" in diagnostico or ph < 7.25:
            hco3_meta = st.slider("HCO3 Meta (mEq/L)", 15.0, 24.0, 20.0, step=1.0, key="slider_hco3")
            deficit_hco3 = (hco3_meta - hco3) * 0.4 * peso_real
            c_bic1, c_bic2 = st.columns(2)
            c_bic1.metric("Déficit Estimado", f"{max(0, deficit_hco3):.1f} mEq")
            if ph < 7.20:
                c_bic2.error("pH crítico. Sugerencia: Reponer 50% en infusión lenta.")
            else:
                c_bic2.warning("pH > 7.20. Evaluar si la corrección metabólica es estrictamente necesaria.")
        else:
            st.success("Sin indicación prioritaria de reposición de bicarbonato exógeno.")

        # B. AJUSTE VENTILATORIO UNIFICADO (Con fórmulas de la proyección)
        st.markdown("##### 🫁 Ajuste Ventilatorio en Máquina de Anestesia")
        
        # 1. Cálculos Base (SC, PBW, VM)
        sc = math.sqrt((talla_cm * peso_real) / 3600)
        pbw_gas = (50.0 if sexo == "Masculino" else 45.5) + 0.91 * (talla_cm - 152.4)
        vm_objetivo = sc * 4.0 if sexo == "Masculino" else sc * 3.5
        
        # 2. Inputs únicos para evitar repeticiones
        c_v1, c_v2, c_v3 = st.columns(3)
        fr_vent = c_v1.number_input("FR Actual (rpm)", value=12, key="fr_vent_unica")
        vt_vent = c_v2.number_input("VT Actual (mL)", value=500, key="vt_vent_unica")
        pco2_meta = c_v3.number_input("PaCO2 Meta (mmHg)", value=40.0, key="pco2_meta_unica")
        
        # 3. Muestra de límites protectores
        st.caption(f"**Límites Protectores (PBW {pbw_gas:.1f} kg):** VT Mín: {pbw_gas*6:.0f} mL | VT Máx: {pbw_gas*8:.0f} mL")
        
        # 4. Fórmulas de ajuste
        c_res1, c_res2 = st.columns(2)
        
        with c_res1:
            st.info("**Objetivo Basal (Protocolo DANI)**")
            fr_dani = vm_objetivo / (vt_vent / 1000) if vt_vent > 0 else 0
            st.metric("Vol. Minuto Ideal", f"{vm_objetivo:.2f} L/min")
            st.metric("FR Meta (VM/VT_Litros)", f"{fr_dani:.1f} rpm", help="Frecuencia necesaria para cumplir el Volumen Minuto ideal con el VT actual.")
            
        with c_res2:
            st.warning("**Corrección Gasométrica (PaCO2)**")
            fr_correccion = (fr_vent * pco2) / pco2_meta if pco2_meta > 0 else 0
            vt_correccion = (vt_vent * pco2) / pco2_meta if pco2_meta > 0 else 0
            st.metric("FR Sugerida", f"{fr_correccion:.1f} rpm", help="Modificación de FR manteniendo el VT actual.")
            st.metric("VT Sugerido", f"{vt_correccion:.0f} mL", help="Modificación de VT manteniendo la FR actual.")
            
            # Guardrail de seguridad para la corrección de VT
            if vt_correccion > (pbw_gas * 8):
                st.error("⚠️ El VT sugerido excede los 8 mL/kg. Ajuste la FR en su lugar.")
