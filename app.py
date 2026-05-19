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

    # 4. Laboratorios y Exámenes (Módulo de Laboratorios)
    with st.expander("4. Laboratorios (Módulo Transquirúrgico)", expanded=True):
        st.markdown("**🧪 Perfil de Laboratorio Analítico**")
        st.caption("Desmarque la casilla si el paciente no dispone del examen.")
        
        dict_labs = {}
        
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
        else:
            creatinina = 0.9
            
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
        
        ekg_bricia = c_ekg2.checkbox("Bloqueo de Rama Izquierda (BRDHH/BRIHH)")
        ekg_st_supra = c_ekg2.checkbox("Supradesnivel del segmento ST (Lesión aguda)")
        ekg_st_infra = c_ekg2.checkbox("Infradesnivel del segmento ST / Inversión Onda T")
        ekg_hvi = c_ekg2.checkbox("Signos de Hipertrofia Ventricular (Sokolow-Lyon +)")
        ekg_qt_largo = c_ekg2.checkbox("Intervalo QT Prolongado (QTc > 470/480ms)")
        
        otros_hallazgos_ekg = st.text_input("Otros hallazgos electrocardiográficos específicos:", "Ninguno")

    # 6. Parámetros Quirúrgicos (MÓDULO DE CIRUGÍAS MÁS COMUNES)
    with st.expander("6. Datos Quirúrgicos", expanded=True):
        st.markdown("**📋 Selección de Procedimiento**")
        
        # Diccionario con Cx comunes organizadas por riesgo intrínseco estimado (Guías AHA/ESC)
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
        
        # Si selecciona "Otra", permite escribirla, sino adopta el nombre del diccionario
        if cx_seleccionada == "Otra (Especificar manualmente)":
            nombre_cx = st.text_input("Escriba el nombre del procedimiento:", value="Cirugía General")
            # En caso de manual, el usuario asigna el riesgo
            riesgo_cx_tipo = st.selectbox("Riesgo Intrínseco de la Cirugía", ["Intermedio (1-5% - ej. Abdominal, Cadera)", "Bajo (<1% - ej. Superficial, Cataratas)", "Alto (>5% - ej. Vascular Mayor, Torácica)"], index=0)
        else:
            nombre_cx = cx_seleccionada
            # Indexación automática del riesgo predeterminado
            riesgo_predeterminado = cx_comunes[cx_seleccionada]
            lista_riesgos = ["Intermedio (1-5% - ej. Abdominal, Cadera)", "Bajo (<1% - ej. Superficial, Cataratas)", "Alto (>5% - ej. Vascular Mayor, Torácica)"]
            idx_riesgo = lista_riesgos.index(riesgo_predeterminado)
            riesgo_cx_tipo = st.selectbox("Riesgo Intrínseco de la Cirugía (Auto)", list_riesgos, index=idx_riesgo)

        cirugia_emergencia = st.checkbox("Cirugía de Emergencia")

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

# --- LÓGICA DE CÁLCULO ---
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
if acceso_central: p_caprini +=
