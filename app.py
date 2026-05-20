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
        talla_cm = st.number_input("Talla (cm)", min_value=100, max_value=220, value=165)

    # 2. Seguridad, Alergias y Medicamentos
    with st.expander("2. Seguridad, Alergias y Medicamentos", expanded=True):
        st.markdown("**🚨 Alergias**")
        options_med = [
            "Penicilina / Betalactámicos", "AINEs (Aspirina, Ibuprofeno, etc.)", 
            "Sulfa / Sulfonamidas", "Medios de Contraste Yodados", 
            "Látex", "Relajantes Musculares (Succinilcolina, Rocuronio)", 
            "Opioides (Morfina, Fentanilo)", "Dipirona / Metamizol"
        ]
        alergias_med = st.multiselect("Medicamentosas / Sustancias:", options=options_med)
        
        options_com = [
            "Camarones / Mariscos", "Chocolate", "Soja", 
            "Maní / Frutos Secos", "Huevo", "Leche de Vaca (Lactosa/Caseína)", 
            "Trigo / Gluten", "Pescado"
        ]
        alergias_com = st.multiselect("Alimentarias:", options=options_com)
        otras_alergias = st.text_input("Otras alergias (Especificar):", value="")
        
        st.markdown("---")
        st.markdown("**💊 Medicamentos Críticos en Uso**")
        options_farmacos = [
            "Betabloqueantes (Metoprolol, Carvedilol)", 
            "IECA / ARA II (Enalapril, Losartán)", 
            "Antiagregantes (Aspirina, Clopidogrel)", 
            "Anticoagulantes Orales (Warfarina, Rivaroxabán)", 
            "Insulina", 
            "Antidiabéticos Orales (Metformina, Empagliflozina)", 
            "Corticoides Crónicos (Prednisona)", 
            "Anticonvulsivantes / Moduladores (Gabapentina, Fenitoína)"
        ]
        farmacos_criticos = st.multiselect("Seleccione los fármacos activos:", options=options_farmacos)
        otros_farmacos = st.text_input("Otros medicamentos (Especificar):", value="")
        
        st.markdown("---")
        st.markdown("**Antecedentes Clínicos (Marque los presentes):**")
        c_ant1, c_ant2 = st.columns(2)
        tiene_infarto = c_ant1.checkbox("Infarto de Miocardio (< 6 meses)")
        tiene_ic = c_ant1.checkbox("Insuficiencia Cardíaca Congestiva")
        tiene_acv = c_ant1.checkbox("Historia de ACV o AIT")
        tiene_insulina = c_ant2.checkbox("Diabetes bajo tratamiento con Insulina")
        tiene_ev = c_ant2.checkbox("> 5 Extrasístoles Ventriculares/min")
        tiene_ritmo_no_s = c_ant2.checkbox("Ritmo no sinusal / EAs en EKG")
        tiene_cancer = c_ant1.checkbox("Cáncer Activo o previo")
        tiene_epoc = c_ant2.checkbox("EPOC o Enfermedad Pulmonar Crónica")

    # 3. Exploración de Vía Aérea y Ventilación
    with st.expander("3. Valoración Estructural de la Vía Aérea"):
        c_va1, c_va2 = st.columns(2)
        mallampati = c_va1.selectbox("Clasificación Mallampati", ["Clase I", "Clase II", "Clase III", "Clase IV"])
        dtm = c_va1.number_input("Distancia Tiromentoniana (cm)", min_value=2.0, max_value=20.0, value=7.0)
        dem = c_va2.number_input("Distancia Esternomentoniana (cm)", min_value=5.0, max_value=25.0, value=13.0)
        cuello = c_va2.number_input("Circunferencia de Cuello (cm)", min_value=20, max_value=60, value=38)
        
        protrusion_opt = [1, 2, 3]
        protrusion_sel = st.selectbox("Protrusión Mandibular (Clase):", options=protrusion_opt)
        
        st.markdown("**Índice Multivariable de Arné**")
        historia_vad = st.checkbox("Historia previa de VAD")
        patologia_vad = st.checkbox("Patología asociada a VAD")
        apertura_bucal = st.checkbox("Apertura Bucal < 3.5 cm")
        
        movilidad_opt = [0, 1, 2]
        movilidad_sel = st.selectbox("Movilidad Cabeza/Cuello (0=Normal, 1=Moderada, 2=Severa):", options=movilidad_opt)

        st.markdown("**Ventilación con Mascarilla (VMD) y SAHOS**")
        tiene_barba = st.checkbox("Paciente tiene Barba densa")
        tiene_edentulia = st.checkbox("Edentulia total o parcial")
        tiene_ronquido = st.checkbox("Historia de Ronquido severo / SAHOS")

    # 4. Laboratorios y Exámenes
    with st.expander("4. Laboratorios (Módulo Transquirúrgico)", expanded=True):
        st.markdown("**🧪 Perfil de Laboratorio Analítico**")
        st.caption("Desmarque la casilla si el paciente no dispone del examen.")
        
        dict_labs = {}
        
        # Variables por defecto para cálculos seguros
        hb, hto, creatinina = 13.0, 40.0, 0.9 
        
        tiene_hb = st.checkbox("Hemoglobina / Hematocrito", value=True)
        if tiene_hb:
            c_hb1, c_hb2 = st.columns(2)
            hb = c_hb1.number_input("Hemoglobina (g/dL)", min_value=3.0, max_value=25.0, value=13.0)
            hto = c_hb2.number_input("Hematocrito (%)", min_value=10.0, max_value=75.0, value=40.0)
            dict_labs["Hemoglobina / Hematocrito"] = f"Hb: {hb} g/dL, Hto: {hto}%"
        
        tiene_plt = st.checkbox("Conteo de Plaquetas", value=True)
        if tiene_plt:
            plt = st.number_input("Plaquetas (x10³/µL)", min_value=10, max_value=1000, value=250)
            dict_labs["Plaquetas"] = f"{plt} x10³/µL"
            
        tiene_coag = st.checkbox("Tiempos (TP / TPT)", value=True)
        if tiene_coag:
            c_t1, c_t2 = st.columns(2)
            tp = c_t1.number_input("TP (Segundos)", min_value=5.0, max_value=60.0, value=12.5)
            tpt = c_t2.number_input("TPT (Segundos)", min_value=10.0, max_value=120.0, value=32.0)
            dict_labs["Tiempos de Coagulación"] = f"TP: {tp}s, TPT: {tpt}s"
            
        tiene_renal = st.checkbox("Función Renal (Urea / Creatinina)", value=True)
        if tiene_renal:
            c_r1, c_r2 = st.columns(2)
            urea = c_r1.number_input("Urea (mg/dL)", min_value=5, max_value=300, value=30)
            creatinina = c_r2.number_input("Creatinina Sérica (mg/dL)", min_value=0.1, max_value=15.0, value=0.9)
            dict_labs["Función Renal"] = f"Urea: {urea} mg/dL, Creatinina: {creatinina} mg/dL"
            
        tiene_alb = st.checkbox("Albúmina Sérica", value=True)
        if tiene_alb:
            alb = st.number_input("Albúmina (g/dL)", min_value=1.0, max_value=7.0, value=4.0)
            dict_labs["Albúmina"] = f"{alb} g/dL"

        st.markdown("---")
        alteraciones_lab = st.text_area("Otras alteraciones de laboratorio (opcional)", "Sin alteraciones")

    # 5. Hallazgos y Patologías del EKG
    with st.expander("5. Hallazgos y Patologías del EKG", expanded=True):
        st.markdown("**🫀 Selección de Hallazgos Electrocardiográficos**")
        st.caption("Marque las casillas correspondientes a las alteraciones observadas:")
        
        c_ekg1, c_ekg2 = st.columns(2)
        ekg_sinusal = c_ekg1.checkbox("Ritmo Sinusal Normal", value=True)
        ekg_fa = c_ekg1.checkbox("Fibrilación Auricular / Flutter")
        ekg_bav1 = c_ekg1.checkbox("Bloqueo AV de Primer Grado")
        ekg_bav2 = c_ekg1.checkbox("Bloqueo AV de Segundo Grado (Mobitz I/II)")
        ekg_bav3 = c_ekg1.checkbox("Bloqueo AV Completo (Tercer Grado)")
        
        ekg_bicia = c_ekg2.checkbox("Bloqueo de Rama Izquierda o Derecha (BRIHH/BRDHH)")
        ekg_st_supra = c_ekg2.checkbox("Supradesnivel del segmento ST (Lesión aguda)")
        ekg_st_infra = c_ekg2.checkbox("Infradesnivel del segmento ST / Inversión Onda T")
        ekg_hvi = c_ekg2.checkbox("Signos de Hipertrofia Ventricular (Sokolow-Lyon +)")
        ekg_qt_largo = c_ekg2.checkbox("Intervalo QT Prolongado (QTc > 470/480ms)")
        
        otros_hallazgos_ekg = st.text_input("Otros hallazgos electrocardiográficos específicos:", "Ninguno")

    # 6. Parámetros Quirúrgicos
    with st.expander("6. Datos Quirúrgicos", expanded=True):
        st.markdown("**📋 Selección de Procedimiento**")
        
        cx_comunes = {
            "Colecistectomía Laparoscópica": "Intermedio (1-5% - ej. Abdominal, Cadera)",
            "Apendicectomía Laparoscópica / Abierta": "Intermedio (1-5% - ej. Abdominal, Cadera)",
            "Hernioplastia Inguinal / Umbilical": "Bajo (<1% - ej. Superficial, Cataratas)",
            "Histerectomía Abdominal / Laparoscópica": "Intermedio (1-5% - ej. Abdominal, Cadera)",
            "Artroplastia Total de Cadera o Rodilla": "Intermedio (1-5% - ej. Abdominal, Cadera)",
            "Cesárea": "Bajo (<1% - ej. Superficial, Cataratas)",
            "Cirugía de Cataratas (Facoemulsificación)": "Bajo (<1% - ej. Superficial, Cataratas)",
            "Prostatectomía Transuretral (RTU) / Abierta": "Intermedio (1-5% - ej. Abdominal, Cadera)",
            "Mastectomía Parcial o Total": "Bajo (<1% - ej. Superficial, Cataratas)",
            "Cirugía Revascularización Miocárdica / Bypass (CRM)": "Alto (>5% - ej. Vascular Mayor, Torácica)",
            "Aneurismectomía de Aorta Abdominal / Torácica": "Alto (>5% - ej. Vascular Mayor, Torácica)",
            "Amputación de Miembro Inferior (Mayor)": "Alto (>5% - ej. Vascular Mayor, Torácica)",
            "Endoscopia / Colonoscopia Diagnóstica o Terapéutica": "Bajo (<1% - ej. Superficial, Cataratas)",
            "Laparotomía Exploradora": "Alto (>5% - ej. Vascular Mayor, Torácica)",
            "Tiroidectomía Total / Parcial": "Intermedio (1-5% - ej. Abdominal, Cadera)",
            "Otra (Especificar manualmente)": "Intermedio (1-5% - ej. Abdominal, Cadera)"
        }
        
        cx_seleccionada = st.selectbox("Procedimiento Planeado:", options=list(cx_comunes.keys()))
        
        if cx_seleccionada == "Otra (Especificar manualmente)":
            nombre_cx = st.text_input("Escriba el nombre del procedimiento:", value="Cirugía General")
            riesgo_cx_tipo = st.selectbox("Riesgo Intrínseco de la Cirugía", ["Intermedio (1-5% - ej. Abdominal, Cadera)", "Bajo (<1% - ej. Superficial, Cataratas)", "Alto (>5% - ej. Vascular Mayor, Torácica)"], index=0)
        else:
            nombre_cx = cx_seleccionada
            riesgo_predeterminado = cx_comunes[cx_seleccionada]
            lista_riesgos = ["Intermedio (1-5% - ej. Abdominal, Cadera)", "Bajo (<1% - ej. Superficial, Cataratas)", "Alto (>5% - ej. Vascular Mayor, Torácica)"]
            idx_riesgo = lista_riesgos.index(riesgo_predeterminado)
            riesgo_cx_tipo = st.selectbox("Riesgo Intrínseco de la Cirugía (Auto)", lista_riesgos, index=idx_riesgo)

        cirugia_emergencia = st.checkbox("Cirugía de Emergencia")
        plan_anestesico = st.selectbox("Plan Anestésico:", ["General", "Sedación", "Raquídea", "Epidural"])
    # 7. Escala de Apfel y Caprini Adicionales
    with st.expander("7. Factores de Riesgo Adicionales (Caprini/Apfel)"):
        no_fumador = st.checkbox("Paciente es NO Fumador", value=True)
        historia_nvpo = st.checkbox("Historia previa de NVPO o Cinetosis")
        opioides_post = st.checkbox("Uso planeado de opioides postoperatorios", value=True)
        
        st.markdown("**Criterios Caprini Adicionales**")
        varices = st.checkbox("Presencia de Várices venosas")
        edema_mi = st.checkbox("Edema de miembros inferiores")
        inmovilizacion = st.checkbox("Inmovilización en cama > 72 horas reciente")
        trombofilia = st.checkbox("Trombofilia conocida")
        acceso_central = st.checkbox("Uso de acceso venoso central")

# --- LÓGICA DE CÁLCULO GENERAL ---
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

if imc >= 25:
    peso_ajust_20 = peso_ideal + 0.2 * (peso_real - peso_ideal)
    peso_ajust_40 = peso_ideal + 0.4 * (peso_real - peso_ideal)
else:
    peso_ajust_20 = peso_real
    peso_ajust_40 = peso_real

clcr_cg = ((140 - edad) * peso_real / (72 * max(creatinina, 0.1))) * cg_factor
creat_term = max(creatinina / ckd_kappa, 1) ** ckd_alfa
edad_term = 0.993 ** edad
tfg_ckd = ckd_const * (min(creatinina / ckd_kappa, 1) ** ckd_alfa) * creat_term * edad_term

# --- LÓGICA DE CÁLCULO TRANSQUIRÚRGICO (NUEVO) ---
# 1. Ventilación
vt_min = peso_predicho * 6
vt_max = peso_predicho * 8
peep_ideal = 5 if imc < 30 else 8 if imc < 40 else 10

# 2. Fluidoterapia (Regla Holliday-Segar 4-2-1 para adultos)
# Para adultos >20kg la fórmula simplificada es Peso + 40
fluido_mantenimiento = peso_real + 40 

# 3. Volemia y Sangrado Permisible
volemia_est = peso_real * (70 if sexo == "Masculino" else 65)
hto_meta = 30.0 if (tiene_ic or tiene_infarto) else 25.0
sangrado_permisible = volemia_est * (hto - hto_meta) / hto if hto > hto_meta else 0

# --- PUNTUACIÓN DE ESCALAS ---
p_arne = 0
if historia_vad: p_arne += 5
if patologia_vad: p_arne += 5
if mallampati == "Clase III": p_arne += 2
elif mallampati == "Clase IV": p_arne += 5
if dtm <= 6.5: p_arne += 4
if apertura_bucal: p_arne += 4
if movilidad_sel == 1: p_arne += 2
elif movilidad_sel == 2: p_arne += 5

p_stop = 0
if tiene_ronquido: p_stop += 1
if imc > 35: p_stop += 1
if edad > 50: p_stop += 1
if cuello > 40: p_stop += 1
if sexo == "Masculino": p_stop += 1

p_lee = 0
if "Alto" in riesgo_cx_tipo: p_lee += 1
if tiene_infarto: p_lee += 1
if tiene_ic: p_lee += 1
if tiene_acv: p_lee += 1
if tiene_insulina: p_lee += 1
if tiene_renal and creatinina > 2.0: p_lee += 1

p_goldman = 0
if edad > 70: p_goldman += 5
if tiene_infarto: p_goldman += 10
if tiene_ritmo_no_s: p_goldman += 7
if tiene_ev: p_goldman += 7
if tiene_ic: p_goldman += 11
if cirugia_emergencia: p_goldman += 4
if riesgo_cx_tipo in ["Intermedio (1-5% - ej. Abdominal, Cadera)", "Alto (>5% - ej. Vascular Mayor, Torácica)"]: p_goldman += 3

p_caprini = 0
if 41 <= edad <= 60: p_caprini += 1
elif 61 <= edad <= 74: p_caprini += 2
elif edad >= 75: p_caprini += 3
if imc > 25: p_caprini += 1
if varices: p_caprini += 1
if edema_mi: p_caprini += 1
if tiene_ic: p_caprini += 1
if tiene_epoc: p_caprini += 1
if tiene_infarto: p_caprini += 1
if "Bajo" not in riesgo_cx_tipo: p_caprini += 2
if inmovilizacion: p_caprini += 2
if tiene_cancer: p_caprini += 2
if acceso_central: p_caprini += 2
if trombofilia: p_caprini += 3

p_apfel = 0
if sexo == "Femenino": p_apfel += 1
if no_fumador: p_apfel += 1
if historia_nvpo: p_apfel += 1
if opioides_post: p_apfel += 1

lista_ekg = []
if ekg_sinusal: lista_ekg.append("Ritmo Sinusal Normal")
if ekg_fa: lista_ekg.append("Fibrilación Auricular/Flutter")
if ekg_bav1: lista_ekg.append("Bloqueo AV 1er Grado")
if ekg_bav2: lista_ekg.append("Bloqueo AV 2do Grado")
if ekg_bav3: lista_ekg.append("Bloqueo AV Completo (3er Grado)")
if ekg_bicia: lista_ekg.append("Bloqueo de Rama (BRIHH/BRDHH)")
if ekg_st_supra: lista_ekg.append("Supradesnivel del ST (Lesión)")
if ekg_st_infra: lista_ekg.append("Infradesnivel ST / Inv. Onda T")
if ekg_hvi: lista_ekg.append("Hipertrofia Ventricular Izquierda")
if ekg_qt_largo: lista_ekg.append("QTc Prolongado")
if otros_hallazgos_ekg != "Ninguno" and otros_hallazgos_ekg != "":
    lista_ekg.append(otros_hallazgos_ekg)
diagnostico_ekg_consolidado = ", ".join(lista_ekg) if lista_ekg else "Sin hallazgos registrados"

str_alergias_med = ", ".join(alergias_med) if alergias_med else "Negadas"
str_alergias_com = ", ".join(alergias_com) if alergias_com else "Negadas"
if otras_alergias:
    str_alergias_med = f"{str_alergias_med}, Otras: {otras_alergias}" if str_alergias_med != "Negadas" else otras_alergias

str_farmacos = ", ".join(farmacos_criticos) if farmacos_criticos else "Ninguno"
if otros_farmacos:
    str_farmacos = f"{str_farmacos}, Otros: {otros_farmacos}" if str_farmacos != "Ninguno" else otros_farmacos

# --- COLUMNA DE REPORTE CON PESTAÑAS (TABS) ---
with col_der:
    st.header("📊 Panel Clínico Integrado")
    
    # Creación de las dos pestañas nativas
    tab_preanestesia, tab_transquirurgico, tab_dosificacion = st.tabs(["📝 Reporte Preanestésico", "⚙️ Plan Transquirúrgico","🧪 Dosificación"])
    
    # ----------------------------------------------------------------
    # PESTAÑA 1: EVALUACIÓN PREANESTÉSICA (El reporte clásico)
    # ----------------------------------------------------------------
    with tab_preanestesia:
        if st.button("🔄 ACTUALIZAR EVALUACIÓN PREANESTÉSICA", type="primary"):
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
    # PESTAÑA 2: PLAN TRANSQUIRÚRGICO (Módulo Experto)
    # ----------------------------------------------------------------
    with tab_transquirurgico:
        st.subheader("🩸 Monitor de Sangrado & PSP")
        
        # Fila de inputs de sangrado
        c_sang1, c_sang2, c_sang3 = st.columns(3)
        hto_act = c_sang1.number_input("Hto Act (%)", value=40.0)
        hto_min = c_sang2.number_input("Hto Mín (%)", value=30.0)
        sangrado_ml = c_sang3.number_input("Sangrado (mL)", value=0)
        
        # Lógica de cálculo PSP (Pérdida Sanguínea Permisible)
        volemia = peso_real * (70 if sexo == "Masculino" else 65)
        psp_max = volemia * (hto_act - hto_min) / hto_act
        
        # Display dinámico de PSP
        c_res1, c_res2 = st.columns(2)
        c_res1.metric("PSP MÁXIMA", f"{psp_max:.0f} mL")
        c_res2.info(f"Estado: {'⚠️ ALERTA: Sangrado crítico' if sangrado_ml >= psp_max else '✅ Sin Sangrado Crítico'}")

        st.markdown("---")
        st.subheader("💧 Plan Transoperatorio (Regla 4-2-1)")
        
        # Tabla dinámica de componentes
        mant = peso_real + 40
        insensibles = 4 # Valor estándar por kg/h
        repos_ayuno = 960 / 3 # Ejemplo de déficit distribuido en 3 horas
        
        # Datos para la tabla
        data = {
            "Componente": ["Mant. (4-2-1)", "Insensibles", "Repos. Ayuno"],
            "H1": [mant, insensibles*peso_real, repos_ayuno],
            "H2": [mant, insensibles*peso_real, repos_ayuno/2],
            "H3": [mant, insensibles*peso_real, repos_ayuno/2]
        }
        
        # Renderizado de tabla interactiva
        import pandas as pd
        df = pd.DataFrame(data)
        st.table(df)
        
        # Totales inferiores
        c_t1, c_t2 = st.columns(2)
        c_t1.metric("Mant. Total", f"{mant*3:.0f}")
        c_t2.metric("TOTAL LÍQUIDOS", f"{(mant*3) + (insensibles*peso_real*3) + 960:.0f} mL")
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
