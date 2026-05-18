# -*- coding: utf-8 -*-
import streamlit as st
import math

# Configuración básica
st.set_page_config(page_title="Evaluador Preanestésico", page_icon="🩺", layout="wide")

st.title("🩺 Asistente de Evaluación Preanestésica")
st.write("Optimización clínica perioperatoria y analítica transquirúrgica.")

col_izq, col_der = st.columns([1, 1.2])

with col_izq:
    st.header("📋 Datos de Entrada")
    
    with st.expander("1. Datos Demográficos", expanded=True):
        c1, c2, c3 = st.columns(3)
        sexo = c1.radio("Sexo", ["Masculino", "Femenino"])
        edad = c2.number_input("Edad (años)", min_value=1, max_value=120, value=50)
        peso_real = c3.number_input("Peso Real (kg)", min_value=30.0, value=70.0)
        talla_cm = st.number_input("Talla (cm)", min_value=100, value=165)

    with st.expander("2. Seguridad, Alergias y Medicamentos", expanded=True):
        st.markdown("**🚨 Alergias**")
        opciones_med = [
            "Penicilina / Betalactámicos", "AINEs (Aspirina, Ibuprofeno, etc.)", 
            "Sulfa / Sulfonamidas", "Medios de Contraste Yodados", 
            "Látex", "Relajantes Musculares (Succinilcolina, Rocuronio)", 
            "Opioides (Morfina, Fentanilo)", "Dipirona / Metamizol"
        ]
        alergias_med = st.multiselect("Medicamentosas / Sustancias:", options=opciones_med)
        
        opciones_com = [
            "Camarones / Mariscos", "Chocolate", "Soja", 
            "Maní / Frutos Secos", "Huevo", "Leche de Vaca (Lactosa/Caseína)", 
            "Trigo / Gluten", "Pescado"
        ]
        alergias_com = st.multiselect("Alimentarias:", options=opciones_com)
        otras_alergias = st.text_input("Otras alergias (Especificar):", value="")
        
        st.markdown("---")
        st.markdown("**💊 Medicamentos Críticos en Uso**")
        opciones_farmacos = [
            "Betabloqueantes (Metoprolol, Carvedilol)", 
            "IECA / ARA II (Enalapril, Losartán)", 
            "Antiagregantes (Aspirina, Clopidogrel)", 
            "Anticoagulantes Orales (Warfarina, Rivaroxabán)", 
            "Insulina", 
            "Antidiabéticos Orales (Metformina, Empagliflozina)", 
            "Corticoides Crónicos (Prednisona)", 
            "Anticonvulsivantes / Moduladores (Gabapentina, Fenitoína)"
        ]
        farmacos_criticos = st.multiselect("Seleccione los fármacos activos:", options=opciones_farmacos)
        otros_farmacos = st.text_input("Otros medicamentos (Especificar):", value="")
        
        st.markdown("---")
        st.markdown("**🩺 Antecedentes Patológicos**")
        tiene_infarto = st.checkbox("Infarto de Miocardio (< 6 meses)")
        tiene_ic = st.checkbox("Insuficiencia Cardíaca")
        tiene_acv = st.checkbox("Historia de ACV")
        tiene_insulina = st.checkbox("Diabetes con Insulina")
        tiene_cancer = st.checkbox("Cáncer Activo")

    with st.expander("3. Vía Aérea e Intubación Potencial"):
        mallampati = st.selectbox("Mallampati", ["Clase I", "Clase II", "Clase III", "Clase IV"])
        dtm = st.number_input("Distancia Tiromentoniana (cm)", value=7.0)
        
        st.markdown("**Escala de Arné (VAD)**")
        # Quitamos los textos largos y dejamos números puros para burlar al traductor
        arne_mallampati = st.selectbox("Arné - Mallampati (Puntos):", [0, 1, 2, 4])
        arne_dtm = st.selectbox("Arné - Distancia Tiromentoniana (Puntos):", [0, 4])
        arne_apertura = st.selectbox("Arné - Apertura bucal (Puntos):", [0, 2, 6])
        arne_movilidad = st.selectbox("Arné - Movilidad cervical (Puntos):", [0, 2, 5])
        arne_protrusion = st.selectbox("Arné - Protrusión mandibular (Puntos):", [0, 2, 4])
        arne_antecedente = st.checkbox("Arné - Antecedente de VAD confirmada (+6)")

    with st.expander("4. Laboratorios (Módulo Transquirúrgico)", expanded=True):
        st.markdown("**🧪 Perfil de Laboratorio Perioperatorio**")
        st.caption("Desmarque la casilla si el paciente no dispone del examen.")
        
        dict_labs = {}
        
        tiene_hb = st.checkbox("Hemoglobina / Hematocrito", value=True)
        if tiene_hb:
            c_hb1, c_hb2 = st.columns(2)
            hb = c_hb1.number_input("Hemoglobina (g/dL)", min_value=3.0, value=13.0)
            hto = c_hb2.number_input("Hematocrito (%)", min_value=10.0, value=40.0)
            dict_labs["Hemoglobina / Hematocrito"] = f"Hb: {hb} g/dL, Hto: {hto}%"
        
        tiene_plt = st.checkbox("Conteo de Plaquetas", value=True)
        if tiene_plt:
            plt = st.number_input("Plaquetas (x10³/µL)", min_value=10, value=250)
            dict_labs["Plaquetas"] = f"{plt} x10³/µL"
            
        tiene_coag = st.checkbox("Tiempos (TP / TPT / INR)", value=True)
        if tiene_coag:
            c_t1, c_t2 = st.columns(2)
            tp = c_t1.number_input("TP (Segundos)", min_value=5.0, value=12.5)
            tpt = c_t2.number_input("TPT (Segundos)", min_value=10.0, value=32.0)
            dict_labs["Tiempos de Coagulación"] = f"TP: {tp}s, TPT: {tpt}s"
            
        tiene_renal = st.checkbox("Función Renal (Urea / Creatinina)", value=True)
        if tiene_renal:
            c_r1, c_r2 = st.columns(2)
            urea = c_r1.number_input("Urea (mg/dL)", min_value=5, value=30)
            creatinina = c_r2.number_input("Creatinina (mg/dL)", min_value=0.1, value=0.9)
            dict_labs["Función Renal"] = f"Urea: {urea} mg/dL, Creatinina: {creatinina} mg/dL"
        else:
            creatinina = 0.9
            
        tiene_alb = st.checkbox("Albúmina Sérica", value=True)
        if tiene_alb:
            alb = st.number_input("Albúmina (g/dL)", min_value=1.0, value=4.0)
            dict_labs["Albúmina"] = f"{alb} g/dL"

    with st.expander("5. Escalas de Riesgo Adicionales"):
        st.markdown("**🤢 Riesgo de Náuseas y Vómitos (Apfel)**")
        apfel_mujer = st.checkbox("Paciente de sexo Femenino", value=(sexo == "Femenino"))
        apfel_no_fumador = st.checkbox("No fumador", value=True)
        apfel_antecedente = st.checkbox("Antecedente de NVPO o cinetosis")
        apfel_opioides = st.checkbox("Uso previsto de opioides postoperatorios", value=True)
        
        st.markdown("---")
        st.markdown("**💤 Evaluación de Apnea (STOP-BANG)**")
        sb_ronca = st.checkbox("S - ¿Ronca fuerte?")
        sb_cansado = st.checkbox("T - ¿Se siente cansado?")
        sb_observado = st.checkbox("O - ¿Deja de respirar al dormir?")
        sb_presion = st.checkbox("P - ¿Tiene hipertensión?")
        sb_cuello = st.checkbox("Cuello - ¿Circunferencia cuello > 40 cm?")
        
        st.markdown("---")
        st.markdown("**🩸 Riesgo Tromboembólico (Caprini Corto)**")
        cap_cx_mayor = st.checkbox("Cirugía mayor (> 45 min)")
        cap_movilidad = st.checkbox("Paciente confinado a cama (> 72 horas)")
        cap_vte = st.checkbox("Antecedente personal o familiar de TEV/TVP")

    with st.expander("6. Datos Quirúrgicos"):
        nombre_cx = st.text_input("Procedimiento", "Colecistectomía")
        riesgo_cx_tipo = st.selectbox("Riesgo Quirúrgico", ["Intermedio", "Bajo", "Alto"])

# --- LÓGICA DE CÁLCULO ---
talla_m = talla_cm / 100.0
imc = peso_real / (talla_m ** 2)
peso_predicho = (50.0 if sexo == "Masculino" else 45.5) + 0.91 * (talla_cm - 152.4)

p_lee = 0
if riesgo_cx_tipo == "Alto": p_lee += 1
if tiene_infarto: p_lee += 1
if tiene_ic: p_lee += 1
if tiene_acv: p_lee += 1
if tiene_insulina: p_lee += 1
if tiene_renal and creatinina > 2.0: p_lee += 1

p_arne = arne_mallampati + arne_dtm + arne_apertura + arne_movilidad + arne_protrusion
if arne_antecedente: p_arne += 6

p_apfel = 0
if apfel_mujer: p_apfel += 1
if apfel_no_fumador: p_apfel += 1
if apfel_antecedente: p_apfel += 1
if apfel_opioides: p_apfel += 1

p_sb = 0
if sb_ronca: p_sb += 1
if sb_cansado: p_sb += 1
if sb_observado: p_sb += 1
if sb_presion: p_sb += 1
if imc > 35: p_sb += 1
if edad > 50: p_sb += 1
if sb_cuello: p_sb += 1
if sexo == "Masculino": p_sb += 1

cap_edad = 1 if (41 <= edad <= 60) else 2 if (61 <= edad <= 74) else 3 if (edad >= 75) else 0
p_caprini = cap_edad
if cap_cx_mayor: p_caprini += 2
if cap_movilidad: p_caprini += 1
if cap_vte: p_caprini += 3
if tiene_cancer: p_caprini += 2

str_alergias_med = ", ".join(alergias_med) if alergias_med else "Negadas"
str_alergias_com = ", ".join(alergias_com) if alergias_com else "Negadas"
if otras_alergias:
    str_alergias_med = f"{str_alergias_med}, Otras: {otras_alergias}" if str_alergias_med != "Negadas" else otras_alergias

str_farmacos = ", ".join(farmacos_criticos) if farmacos_criticos else "Ninguno"
if otros_farmacos:
    str_farmacos = f"{str_farmacos}, Otros: {otros_farmacos}" if str_farmacos != "Ninguno" else otros_farmacos

with col_der:
    st.header("📊 Reporte Clínico Consolidado")
    
    if st.button("🔄 GENERAR REPORTE PERIOPERATORIO COMPLETO", type="primary"):
        st.markdown(f"""
        ### 🩺 Informe de Evaluación
        * **IMC:** {imc:.1f} kg/m²
        * 🎯 **Volumen Corriente Protector:** {peso_predicho*6:.0f} - {peso_predicho*8:.0f} mL
        
        ---
        #### 🚨 Seguridad, Alergias y Medicación
        * **Medicamentosas / Látex:** {str_alergias_med}
        * **Alimentarias:** {str_alergias_com}
        * **Medicación Crítica Activa:** {str_farmacos}
        """)
        
        st.markdown("---")
        st.markdown("#### 🧪 Analítica de Laboratorio (Transquirúrgico)")
        if not dict_labs:
            st.error("❌ No hay datos de laboratorios registrados")
        else:
            for item, valor in dict_labs.items():
                st.markdown(f"• **{item}:** {valor}")
        
        st.markdown(f"""
        ---
        #### 𫡢 Evaluación de la Vía Aérea
        * **Mallampati Clínico:** {mallampati} | **DTM:** {dtm} cm
        * **Puntaje Escala de Arné:** {p_arne} puntos
        * **Clasificación de Riesgo VAD:** {"Bajo Riesgo" if p_arne < 11 else "Riesgo Intermedio" if p_arne <= 14 else "Alto Riesgo de VAD"}
        
        ---
        #### 🫀 Riesgo Cardiovascular (Lee - RCRI)
        * **Criterios presentes:** {p_lee}
        * **Clase:** {'I' if p_lee==0 else 'II' if p_lee==1 else 'III' if p_lee==2 else 'IV'}
        * **Riesgo MACE:** {"0.4%" if p_lee==0 else "0.9%" if p_lee==1 else "6.6%" if p_lee==2 else "11%"}
        
        ---
        #### 🤢 Riesgo de NVPO (Apfel)
        * **Puntaje Apfel:** {p_apfel} / 4
        * **Incidencia estimada:** {"10%" if p_apfel==0 else "21%" if p_apfel==1 else "39%" if p_apfel==2 else "61%" if p_apfel==3 else "79%"}
        
        ---
        #### 💤 Tamizaje de SAHOS (STOP-BANG)
        * **Puntaje STOP-BANG:** {p_sb} / 8
        * **Riesgo:** {"Bajo Riesgo" if p_sb <= 2 else "Riesgo Intermedio" if p_sb <= 4 else "Alto Riesgo de SAHOS"}
        
        ---
        #### 🩸 Riesgo Tromboembólico (Caprini)
        * **Puntaje Caprini:** {p_caprini} puntos
        * **Nivel de Riesgo:** {"Muy Bajo" if p_caprini <= 1 else "Bajo" if p_caprini == 2 else "Moderado" if (p_caprini == 3 or p_caprini == 4) else "Alto Riesgo"}
        """)
        
