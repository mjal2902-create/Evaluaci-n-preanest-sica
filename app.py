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

# --- COLUMNA DERECHA: PESTAÑAS ---
with col_der:
    st.header("📊 Panel Clínico Integrado")
    tab_pre, tab_trans = st.tabs(["📝 Reporte Preanestésico", "⚙️ Plan Transquirúrgico"])
    
    with tab_pre:
        if st.button("🔄 ACTUALIZAR REPORTE", type="primary"):
            st.subheader("🩺 Evaluación Preanestésica")
            st.write(f"**Paciente:** {sexo} | {edad} años")
            st.write(f"**Antropometría:** {peso_real} kg | {talla_cm} cm | IMC: {imc:.1f}")
            st.write(f"**Pesos:** Ideal {peso_ideal:.1f} kg | Predicho {peso_predicho:.1f} kg")
            
            st.markdown("---")
            st.write(f"**Alergias:** {str_almed} / {str_alcom}")
            st.write(f"**Fármacos:** {str_far}")
            
            st.markdown("---")
            st.write(f"**Vía Aérea:** Mallampati {mallampati} | DTM: {dtm}cm")
            st.write(f"**Riesgo Intubación (Arné):** {p_arne} pts")
            st.write(f"**Riesgo SAHOS (STOP-BANG):** {p_stop}/8")
            
            st.markdown("---")
            st.write("**Laboratorios:**")
            if dict_labs:
                for k, v in dict_labs.items(): st.write(f"- {k}: {v}")
            else:
                st.write("- Sin laboratorios")
            st.write(f"**TFG:** {tfg_ckd:.0f} mL/min | **ClCr:** {clcr_cg:.0f} mL/min")
            
            st.markdown("---")
            st.write(f"**Cirugía Planeada:** {nombre_cx} ({riesgo_cx_tipo})")
            st.write(f"**Plan Anestésico:** {plan_anestesico}")
            st.write(f"**Riesgo Lee:** Clase {('I' if p_lee==0 else 'II' if p_lee==1 else 'III' if p_lee==2 else 'IV')} ({p_lee} criterios) | **Goldman:** {p_goldman} pts")
            st.write(f"**Riesgo Caprini:** {p_caprini} pts | **Apfel:** {p_apfel}/4 pts")
            st.write(f"**EKG:** {diag_ekg}")
            
            st.subheader("📋 Resumen para Copiar")
            texto_hc = f"PREANESTESIA: {sexo}, {edad}a. IMC {imc:.1f}. Cx: {nombre_cx}. Anestesia: {plan_anestesico.upper()}. Lee: {p_lee}. Goldman: {p_goldman}. EKG: {diag_ekg}. Alergias: {str_almed}. Arné {p_arne} pts. Caprini: {p_caprini}. Apfel: {p_apfel}/4."
            st.code(texto_hc, language="text")

    with tab_trans:
        if st.button("⚙️ GENERAR PLAN", type="primary"):
            st.subheader("⚙️ Plan Intraoperatorio")
            st.write(f"**Técnica:** {plan_anestesico.upper()}")
            
            if plan_anestesico == "General":
                st.info("Recomendación: Asegurar estrategia protectora y relajación neuromuscular profunda si la Cx lo amerita.")
            elif plan_anestesico in ["Raquídea", "Epidural"]:
                st.info("Recomendación: Prevención de hipotensión por bloqueo simpático. Tener vasopresores preparados.")
            elif plan_anestesico == "Sedación":
                st.info("Recomendación: Capnografía continua y oxígeno suplementario. Equipo de vía aérea preparado.")

            st.markdown("---")
            st.write("🫁 **Ventilación (Si precisa):**")
            st.write(f"• **Volumen Corriente:** {vt_min:.0f} a {vt_max:.0f} mL")
            st.write(f"• **PEEP Sugerido:** {peep_ideal} cmH2O")
            
            st.markdown("---")
            st.write("💧 **Fluidos y Sangre:**")
            st.success(f"🚰 **Mantenimiento Basal (4-2-1):** {fluido_mantenimiento:.0f} mL/hr")
            st.write(f"• **Volemia Estimada:** {volemia_est:.0f} mL")
            st.error(f"🩸 **Sangrado Permisible:** {sangrado_permisible:.0f} mL (Meta Hto {hto_meta}%)")
            
            st.markdown("---")
            st.write("🛡️ **Profilaxis:**")
            st.write(f"• **NVPO:** {'Doble/Triple terapia' if p_apfel>=2 else 'Simple/Rescate'} (Apfel {p_apfel})")
            st.write(f"• **TVP:** {'Farmacológica/Mecánica' if p_caprini>=5 else 'Mecánica'} (Caprini {p_caprini})")
            
            st.subheader("📋 Copiar Plan Quirúrgico")
            texto_trans = f"PLAN {plan_anestesico.upper()}: Vt {vt_min:.0f}-{vt_max:.0f}mL. PEEP {peep_ideal}. Fluidos {fluido_mantenimiento:.0f}mL/hr. Sangrado Permisible: {sangrado_permisible:.0f}mL. Profilaxis NVPO y TVP según protocolos."
            st.code(texto_trans, language="text")
