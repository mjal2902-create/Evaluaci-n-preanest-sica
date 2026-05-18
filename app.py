# -*- coding: utf-8 -*-
import streamlit as st
import math
import google.generativeai as genai
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Evaluador Preanestésico + IA", page_icon="🩺", layout="wide")

# Configuración de la IA (Gemini)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.sidebar.warning("⚠️ Configura tu GOOGLE_API_KEY en los Secrets para usar la IA.")

st.title("🩺 Asistente de Evaluación Preanestésica e IA")
st.write("Optimización clínica perioperatoria potenciada con visión artificial.")

col_izq, col_der = st.columns([1, 1.2])

with col_izq:
    st.header("📋 Datos de Entrada")
    
    with st.expander("1. Datos Demográficos", expanded=True):
        c1, c2, c3 = st.columns(3)
        sexo = c1.radio("Sexo", ["Masculino", "Femenino"])
        edad = c2.number_input("Edad", min_value=1, max_value=120, value=50)
        peso_real = c3.number_input("Peso Real (kg)", min_value=30.0, value=70.0)
        talla_cm = st.number_input("Talla (cm)", min_value=100, value=165)

    with st.expander("2. Seguridad, Alergias y Medicamentos"):
        st.markdown("**🚨 Alergias**")
        opciones_medicamentos = [
            "Penicilina / Betalactámicos", "AINEs (Aspirina, Ibuprofeno, etc.)", 
            "Sulfa / Sulfonamidas", "Medios de Contraste Yodados", 
            "Látex", "Relajantes Musculares (Succinilcolina, Rocuronio)", 
            "Opioides (Morfina, Fentanilo)", "Dipirona / Metamizol"
        ]
        alergias_med = st.multiselect("Medicamentosas / Sustancias:", options=opciones_medicamentos)
        
        opciones_comida = [
            "Camarones / Mariscos", "Chocolate", "Soja", 
            "Maní / Frutos Secos", "Huevo", "Leche de Vaca (Lactosa/Caseína)", 
            "Trigo / Gluten", "Pescado"
        ]
        alergias_com = st.multiselect("Alimentarias:", options=opciones_comida)
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

    with st.expander("3. Vía Aérea"):
        mallampati = st.selectbox("Mallampati", ["Clase I", "Clase II", "Clase III", "Clase IV"])
        dtm = st.number_input("Distancia Tiromentoniana (cm)", value=7.0)

    # NUEVO MÓDULO DE LABORATORIOS OPTIMIZADO
    with st.expander("4. Laboratorios y EKG (Módulo IA)", expanded=True):
        st.markdown("**🧪 Perfil de Laboratorio Perioperatorio**")
        st.caption("Desmarque la casilla si el paciente no dispone del examen.")
        
        dict_labs = {}
        
        # 1. Hemoglobina / Hematocrito
        tiene_hb = st.checkbox("Hemoglobina / Hematocrito", value=True)
        if tiene_hb:
            c_hb1, c_hb2 = st.columns(2)
            hb = c_hb1.number_input("Hemoglobina (g/dL)", min_value=3.0, max_value=25.0, value=13.0, step=0.1)
            hto = c_hb2.number_input("Hematocrito (%)", min_value=10.0, max_value=75.0, value=40.0, step=1.0)
            dict_labs["Hb/Hto"] = f"Hb: {hb} g/dL, Hto: {hto}%"
        
        # 2. Plaquetas
        tiene_plt = st.checkbox("Conteo de Plaquetas", value=True)
        if tiene_plt:
            plt = st.number_input("Plaquetas (x10³/µL)", min_value=10, max_value=1000, value=250, step=10)
            dict_labs["Plaquetas"] = f"{plt} x10³/µL"
            
        # 3. Tiempos de Coagulación
        tiene_coag = st.checkbox("Tiempos (TP / TPT / INR)", value=True)
        if tiene_coag:
            c_t1, c_t2 = st.columns(2)
            tp = c_t1.number_input("TP (Segundos)", min_value=5.0, max_value=60.0, value=12.5, step=0.1)
            tpt = c_t2.number_input("TPT (Segundos)", min_value=10.0, max_value=120.0, value=32.0, step=0.1)
            dict_labs["Tiempos"] = f"TP: {tp}s, TPT: {tpt}s"
            
        # 4. Función Renal (Urea / Creatinina)
        tiene_renal = st.checkbox("Función Renal (Urea / Creatinina)", value=True)
        if tiene_renal:
            c_r1, c_r2 = st.columns(2)
            urea = c_r1.number_input("Urea (mg/dL)", min_value=5, max_value=300, value=30, step=1)
            creatinina = c_r2.number_input("Creatinina (mg/dL)", min_value=0.1, max_value=15.0, value=0.9, step=0.1)
            dict_labs["Función Renal"] = f"Urea: {urea} mg/dL, Creatinina: {creatinina} mg/dL"
        else:
            creatinina = 0.9 # Valor de respaldo para cálculo de score de Lee si se desmarca
            
        # 5. Albúmina
        tiene_alb = st.checkbox("Albúmina Sérica", value=True)
        if tiene_alb:
            alb = st.number_input("Albúmina (g/dL)", min_value=1.0, max_value=7.0, value=4.0, step=0.1)
            dict_labs["Albúmina"] = f"{alb} g/dL"

        st.markdown("---")
        st.markdown("**📸 Análisis de EKG por Visión Artificial**")
        archivo_ekg = st.file_uploader("Cargar foto de EKG o Tira de Ritmo", type=["jpg", "jpeg", "png"])
        
        analisis_ia = ""
        if archivo_ekg:
            img = Image.open(archivo_ekg)
            st.image(img, caption="EKG cargado", use_container_width=True)
            
            if st.button("🧠 ANALIZAR EKG CON IA"):
                if "GOOGLE_API_KEY" in st.secrets:
                    try:
                        with st.spinner("La IA está interpretando la morfología del EKG..."):
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            
                            # Consolidación de datos clínicos para el prompt
                            texto_alergias_med = ", ".join(alergias_med) if alergias_med else "Ninguna"
                            texto_alergias_com = ", ".join(alergias_com) if alergias_com else "Ninguna"
                            if otras_alergias: texto_alergias_med += f", {otras_alergias}"
                            
                            texto_farmacos = ", ".join(farmacos_criticos) if farmacos_criticos else "Ninguno"
                            if otros_farmacos: texto_farmacos += f", {otros_farmacos}"
                            
                            texto_labs_ia = "; ".join([f"{k}: {v}" for k, v in dict_labs.items()]) if dict_labs else "No provistos"
                            
                            prompt = f"""
                            Actúa como un cardiólogo y anestesiólogo experto en medicina perioperatoria. 
                            Analiza esta imagen de EKG de un paciente de {edad} años, sexo {sexo}, 
                            con antecedentes de infarto: {tiene_infarto} e insuficiencia cardíaca: {tiene_ic}.
                            
                            Contexto Clínico del Paciente:
                            - Alergias: Medicamentosas ({texto_alergias_med}), Alimentarias ({texto_alergias_com})
                            - Medicación Crítica: {texto_farmacos}
                            - Laboratorios Reportados: {texto_labs_ia}
                            
                            1. Identifica el ritmo y frecuencia aproximada en la imagen.
                            2. Evalúa intervalos (PR, QRS, QT) si son visibles.
                            3. Busca signos de isquemia, lesión o sobrecarga.
                            4. Concluye la relevancia para el riesgo anestésico y transquirúrgico relacionando los hallazgos del EKG con los laboratorios y fármacos provistos.
                            
                            Responde en español, de forma breve y con viñetas.
                            IMPORTANTE: Agrega un descargo de responsabilidad al final indicando que esto es soporte educativo.
                            """
                            response = model.generate_content([prompt, img])
                            analisis_ia = response.text
                    except Exception as e:
                        st.error(f"Error de conexión con la IA: {e}")
                else:
                    st.error("Falta la API Key de Google en los Secrets.")

    with st.expander("5. Datos Quirúrgicos"):
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

str_alergias_med = ", ".join(alergias_med) if alergias_med else "Negadas"
str_alergias_com = ", ".join(alergias_com) if alergias_com else "Negadas"
if otras_alergias:
    str_alergias_med = f"{str_alergias_med}, Otras: {otras_alergias}" if str_alergias_med != "Negadas" else otras_alergias

str_farmacos = ", ".join(farmacos_criticos) if farmacos_criticos else "Ninguno"
if otros_farmacos:
    str_farmacos = f"{str_farmacos}, Otros: {otros_farmacos}" if str_farmacos != "Ninguno" else otros_farmacos

with col_der:
    st.header("📊 Reporte Clínico Consolidado")
    
    if analisis_ia:
        st.subheader("🤖 Interpretación sugerida por IA")
        st.info(analisis_ia)
        st.markdown("---")

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
        
        # Si el diccionario de laboratorios seleccionados está vacío, muestra el recuadro "No hay datos"
        if not dict_labs:
            st.error("❌ No hay datos de laboratorios registrados")
        else:
            # Si hay laboratorios, los imprime de manera ordenada y elegante
            for item, valor in dict_labs.items():
                st.markdown(f"• **{item}:** {valor}")
        
        st.markdown(f"""
        ---
        #### 🫀 Riesgo Cardiovascular (Lee - RCRI)
        * **Criterios presentes:** {p_lee}
        * **Clase:** {'I' if p_lee==0 else 'II' if p_lee==1 else 'III' if p_lee==2 else 'IV'}
        * **Riesgo MACE:** {"0.4%" if p_lee==0 else "0.9%" if p_lee==1 else "6.6%" if p_lee==2 else "11%"}
        
        ---
        #### 🫁 Vía Aérea
        * **Mallampati:** {mallampati}
        * **Alerta:** {'VAD Potencial' if mallampati in ['Clase III', 'Clase IV'] else 'Aparentemente normal'}
        """)
        
