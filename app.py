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

    # 2. Seguridad y Antecedentes
    with st.expander("2. Seguridad y Antecedentes Patológicos"):
        alergias = st.text_input("Alergias Conocidas", "Negadas")
        medicamentos = st.text_input("Medicamentos Críticos en Uso", "Ninguno")
        
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
        protrusion = st.selectbox("Protrusión Mandibular", ["Clase I (Incisivos inf. adelante)", "Clase II (Incisivos alineados)", "Clase III (No logra avanzar)"])
        
        st.markdown("**Índice Multivariable de Arné**")
        historia_vad = st.checkbox("Historia previa de VAD")
        patologia_vad = st.checkbox("Patología asociada a VAD (Tumores, micrognatia, etc.)")
        apertura_bucal = st.checkbox("Apertura Bucal < 3.5 cm")
        movilidad_cervical = st.selectbox("Movilidad Cabeza/Cuello", ["> 90° (Normal)", "90° ± 10° (Limitación moderada)", "< 80° (Limitación severa)"])

        st.markdown("**Ventilación con Mascarilla (VMD) y SAHOS**")
        tiene_barba = st.checkbox("Paciente tiene Barba densa")
        tiene_edentulia = st.checkbox("Edentulia total o parcial")
        tiene_ronquido = st.checkbox("Historia de Ronquido severo / SAHOS documentado")

    # 4. Laboratorios y Exámenes
    with st.expander("4. Laboratorios y Paraclínicos"):
        creatinina = st.number_input("Creatinina Sérica (mg/dL)", min_value=0.1, max_value=15.0, value=0.9, step=0.1)
        alteraciones_lab = st.text_area("Otras alteraciones de laboratorio (opcional)", "Sin alteraciones de importancia perioperatoria.")
        diagnostico_ekg = st.text_input("Patología / Diagnóstico Principal del EKG", "Ritmo sinusal normal, sin alteraciones agudas del ST.")

    # 5. Parámetros Quirúrgicos
    with st.expander("5. Datos Quirúrgicos"):
        nombre_cx = st.text_input("Procedimiento Planeado", "Colecistectomía Laparoscópica")
        riesgo_cx_tipo = st.selectbox("Riesgo Intrínseco de la Cirugía", ["Intermedio (1-5% - ej. Abdominal, Cadera)", "Bajo (<1% - ej. Superficial, Cataratas)", "Alto (>5% - ej. Vascular Mayor, Torácica)"])
        cirugia_emergencia = st.checkbox("Cirugía de Emergencia")

    # 6. Escala de Apfel y Caprini Adicionales
    with st.expander("6. Factores de Riesgo Adicionales (Caprini/Apfel)"):
        no_fumador = st.checkbox("Paciente es NO Fumador")
        historia_nvpo = st.checkbox("Historia previa de NVPO o Cinetosis")
        opioides_post = st.checkbox("Uso planeado de opioides postoperatorios")
        
        st.markdown("**Criterios Caprini Adicionales**")
        varices = st.checkbox("Presencia de Várices venosas")
        edema_mi = st.checkbox("Edema de miembros inferiores")
        inmovilizacion = st.checkbox("Inmovilización en cama > 72 horas reciente")
        trombofilia = st.checkbox("Trombofilia conocida")
        acceso_central = st.checkbox("Uso de acceso venoso central")

# --- LÓGICA DE CÁLCULO ---
talla_m = talla_cm / 100.0

# Antropometría
imc = peso_real / (talla_m ** 2)
asc = math.sqrt((peso_real * talla_cm) / 3600)

# Pesos ideales y predichos
if sexo == "Masculino":
    peso_ideal = 50.0 + 2.3 * ((talla_cm / 2.54) - 60.0)
    peso_predicho = 50.0 + 0.91 * (talla_cm - 152.4)
else:
    peso_ideal = 45.5 + 2.3 * ((talla_cm / 2.54) - 60.0)
    peso_predicho = 45.5 + 0.91 * (talla_cm - 152.4)

# Pesos Ajustados
if imc >= 25:
    peso_ajust_20 = peso_ideal + 0.2 * (peso_real - peso_ideal)
    peso_ajust_40 = peso_ideal + 0.4 * (peso_real - peso_ideal)
else:
    peso_ajust_20 = peso_real
    peso_ajust_40 = peso_real

# Función Renal (CKD-EPI simplificado y Cockcroft-Gault)
if sexo == "Masculino":
    cg_factor = 1.0
    ckd_kappa = 0.9
    ckd_alfa = -0.411
    ckd_const = 141
else:
    cg_factor = 0.85
    ckd_kappa = 0.7
    ckd_alfa = -0.329
    ckd_const = 144

clcr_cg = ((140 - edad) * peso_real / (72 * creatinina)) * cg_factor

# Cálculo aproximado CKD-EPI
creat_term = max(creatinina / ckd_kappa, 1) ** ckd_alfa
edad_term = 0.993 ** edad
tfg_ckd = ckd_const * (min(creatinina / ckd_kappa, 1) ** ckd_alfa) * creat_term * edad_term

# --- PUNTUACIÓN DE ESCALAS ---

# 1. Índice de Arné
p_arne = 0
if historia_vad: p_arne += 5
if patologia_vad: p_arne += 5
if mallampati == "Clase III": p_arne += 2
elif mallampati == "Clase IV": p_arne += 5
if dtm <= 6.5: p_arne += 4
if apertura_bucal: p_arne += 4
if movilidad_cervical == "90° ± 10° (Limitación moderada)": p_arne += 2
elif movilidad_cervical == "< 80° (Limitación severa)": p_arne += 5

# 2. STOP-BANG
p_stop = 0
if tiene_ronquido: p_stop += 1
if imc > 35: p_stop += 1
if edad > 50: p_stop += 1
if cuello > 40: p_stop += 1
if sexo == "Masculino": p_stop += 1

# 3. Índice de Lee (RCRI)
p_lee = 0
if riesgo_cx_tipo == "Alto (>5% - ej. Vascular Mayor, Torácica)": p_lee += 1
if tiene_infarto: p_lee += 1
if tiene_ic: p_lee += 1
if tiene_acv: p_lee += 1
if tiene_insulina: p_lee += 1
if creatinina > 2.0: p_lee += 1

# 4. Índice de Goldman Modificado
p_goldman = 0
if edad > 70: p_goldman += 5
if tiene_infarto: p_goldman += 10
if tiene_ritmo_no_s: p_goldman += 7
if tiene_ev: p_goldman += 7
if tiene_ic: p_goldman += 11
if cirugia_emergencia: p_goldman += 4
if riesgo_cx_tipo in ["Intermedio (1-5% - ej. Abdominal, Cadera)", "Alto (>5% - ej. Vascular Mayor, Torácica)"]: p_goldman += 3

# 5. Escala de Caprini
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
if riesgo_cx_tipo != "Bajo (<1% - ej. Superficial, Cataratas)": p_caprini += 2  # Asumiendo cx mayor >45 min
if inmovilizacion: p_caprini += 2
if tiene_cancer: p_caprini += 2
if acceso_central: p_caprini += 2
if trombofilia: p_caprini += 3

# 6. Escala de Apfel
p_apfel = 0
if sexo == "Femenino": p_apfel += 1
if no_fumador: p_apfel += 1
if historia_nvpo: p_apfel += 1
if opioides_post: p_apfel += 1

# --- COLUMNA DE REPORTE (PROCESADO) ---
with col_der:
    st.header("📊 Reporte Clínico Consolidado")
    
    # Botón ejecutor de actualización visual
    if st.button("🔄 ACTUALIZAR Y RECALCULAR VARIABLES PERIOPERATORIAS", type="primary"):
        
        # Estilo CSS para simular informe impreso
        st.markdown("""
        <style>
        .reporte-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; }
        h4 { color: #1e3d59; }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown(f"""
            ### 🩺 Reporte de Evaluación Preanestésica Avanzada
            **Paciente:** {sexo} | {edad} años | **Peso Real:** {peso_real:.1f} kg | **Talla:** {talla_cm} cm
            **Área de Superficie Corporal (Mosteller):** **{asc:.2f} m²**
            
            ---
            #### 🧮 Evaluación del IMC y Pesos Clínicos
            * **IMC:** **{imc:.1f} kg/m²** → ({'Bajo Peso' if imc < 18.5 else 'Normal' if imc < 25 else 'Sobrepeso' if imc < 30 else 'Obesidad'})
            * **Peso Ideal (Devine):** **{peso_ideal:.1f} kg** *(Referencia para volumen central / bolo inicial)*
            * **Peso Predicho (ARDSNet):** **{peso_predicho:.1f} kg**
            * 🎯 **Volumen Corriente Protector (6-8 mL/kg):** **{peso_predicho*6:.0f} mL - {peso_predicho*8:.0f} mL**
            """)
            
            if imc >= 25:
                st.markdown(f"""
                > ⚠️ **Pesos Ajustados por Sobrepeso/Obesidad:**
                > * **Peso Ajustado al 20% (TIVA/Lipofílicos):** **{peso_ajust_20:.1f} kg**
                > * **Peso Ajustado al 40% (RMM/Hidrofílicos):** **{peso_ajust_40:.1f} kg**
                """)
                
            st.markdown(f"""
            ---
            #### 🚨 Seguridad Perioperatoria y Alergias
            * **Alergias:** **{alergias.upper()}**
            * **Fármacos en Uso Crítico:** {medicamentos}
            
            ---
            #### 🫁 Evaluación de la Vía Aérea y Ventilación
            * **Mallampati:** {mallampati} | **DTM:** {dtm} cm | **DEM:** {dem} cm | **Cuello:** {cuello} cm
            * 📋 **Índice Multivariable de Arné:** **{p_arne} puntos** → RIESGO DE INTUBACIÓN: **{"ALTO (≥11)" if p_arne >= 11 else "BAJO (<11)"}**
            * **Predictores de Ventilación Difícil (VMD):** {'SÍ' if (tiene_barba or imc > 30 or edad > 55 or tiene_edentulia or tiene_ronquido) else 'NO'}
            * 💤 **STOP-BANG (Riesgo SAHOS):** **{p_stop} / 8 puntos** → Riesgo **{"Alto (≥5)" if p_stop >= 5 else "Intermedio (3-4)" if p_stop >= 3 else "Bajo (0-2)"}**
            
            ---
            #### 🧪 Módulo de Laboratorios y Función Renal
            * **Otras Alteraciones Analíticas:** {alteraciones_lab}
            * **Creatinina Sérica:** {creatinina:.2f} mg/dL
            * 🔮 **TFG (CKD-EPI):** **{tfg_ckd:.0f} mL/min/1.73m²** 
            * 🔮 **Aclaramiento (Cockcroft-Gault):** **{clcr_cg:.0f} mL/min** *(Aclaramiento absoluto fármacos)*
            
            ---
            #### 🛡️ Módulo de Estratificación de Riesgo Perioperatorio Total
            
            ##### 🏗️ 1. Riesgo Quirúrgico Intrínseco
            * **Cirugía:** {nombre_cx}
            * **Clasificación Quirúrgica:** **{riesgo_cx_tipo.upper()}**
            
            ##### 🫀 2. Riesgo Cardiológico Perioperatorio Total
            * **Índice de Lee (RCRI):** Clase **{'I' if p_lee==0 else 'II' if p_lee==1 else 'III' if p_lee==2 else 'IV'}** ({p_lee} criterios, Riesgo MACE: {"0.4%" if p_lee==0 else "0.9%" if p_lee==1 else "6.6%" if p_lee==2 else "11.0%"})
            * **Índice de Goldman Modificado:** Clase **{'I (0-5)' if p_goldman<=5 else 'II (6-12)' if p_goldman<=12 else 'III (13-25)' if p_goldman<=25 else 'IV (≥26)'}** ({p_goldman} pts)
            * 🎯 **Riesgo Cardiológico Global Asignado:** **{"RIESGO BAJO" if p_lee <= 1 and p_goldman <= 12 else "RIESGO MODERADO" if p_lee == 2 else "RIESGO ALTO"}**
            
            ##### 🩸 3. Riesgo Tromboembólico (Caprini)
            * **Puntaje Caprini:** **{p_caprini} puntos** → Riesgo: **{"ALTO (≥5)" if p_caprini >= 5 else "Moderado (3-4)" if p_caprini >= 3 else "Bajo (1-2)" if p_caprini >= 1 else "Muy Bajo (0)"}**
            
            ##### 🤢 4. Riesgo de Náuseas y Vómitos (Apfel)
            * **Puntaje Apfel:** **{p_apfel} / 4** → Incidencia estimada de NVPO: **{"60-80%" if p_apfel >= 3 else "20-40%" if p_apfel >= 2 else "10%"}**
            
            ---
            #### ⚡ Interpretación Electrocardiográfica Directa (EKG)
            * **Patología Principal:** **{diagnostico_ekg.upper()}**
            """)
    else:
        st.info("💡 Complete o modifique los datos clínicos en el panel de la izquierda y presione el botón de arriba para generar el reporte unificado.")