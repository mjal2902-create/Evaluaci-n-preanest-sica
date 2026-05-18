# -*- coding: utf-8 -*-
import streamlit as st
import math

# Configuración de la página
st.set_page_config(page_title="Evaluador Preanestésico", page_icon="🩺", layout="wide")

st.title("🩺 Asistente de Evaluación Preanestésica")
st.write("Optimización clínica perioperatoria, escalas avanzadas y analítica transquirúrgica.")

col_izq, col_der = st.columns([1, 1.2])

with col_izq:
    st.header("📋 Datos de Entrada")
    
    with st.expander("1. Datos Demográficos", expanded=True):
        c1, c2, c3 = st.columns(3)
        sexo = c1.radio("Sexo", ["Masculino", "Femenino"])
        edad = c2.number_input("Edad", min_value=1, max_value=120, value=50)
        peso_real = c3.number_input("Peso Real (kg)", min_value=30.0, value=70.0)
        talla_cm = st.number_input("Talla (cm)", min_value=100, value=165)

    with st.expander("2. Seguridad, Alergias y Medicamentos", expanded=True):
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

    with st.expander("3. Vía Aérea e Intubación Potencial"):
        mallampati = st.selectbox("Mallampati", ["Clase I", "Clase II", "Clase III", "Clase IV"])
        dtm = st.number_input("Distancia Tiromentoniana (cm)", value=7.0)
        
        st.markdown("**Escala de Arné (Predicción de Vía Aérea Difícil)**")
        arne_mallampati = st.selectbox("Arné - Mallampati:", [0, 1, 2, 4], format_func=lambda x: f"Clase I/II (0 pts)" if x==0 else f"Clase III (1 pt)" if x==1 else f"Clase IV (2 pts)" if x==2 else f"No evaluable (4 pts)")
        arne_dtm = st.selectbox("Arné - Distancia Tiromentoniana:", [0, 4], format_func=lambda x: f"> 6.5 cm (0 pts)" if x==0 else f"≤ 6.5 cm (4 pts)")
        arne_apertura = st.selectbox("Arné - Apertura bucal:", [0, 2, 6], format_func=lambda x: f"> 3.5 cm (0 pts)" if x==0 else f"2.5 a 3.5 cm (2 pts)" if x==2 else f"< 2.5 cm (6 pts)")
        arne_movilidad = st.selectbox("Arné - Movilidad cervical:", [0, 2, 5], format_func=lambda x: f"> 90° (0 pts)" if x==0 else f"80° a 90° (2 pts)" if x==2 else f"< 80° (5 pts)")
        arne_protrusion = st.selectbox("Arné - Protrusión mandibular:", [0, 2, 4], format_func=lambda x: f"Incisivos sup. superados (0 pts)" if x==0 else f"A tope / No superados (2 pts)" if x==2 else f"Imposible (4 pts)")
        arne_antecedente = st.checkbox("Arné - Antecedente de VAD confirmada (+6 pts)")

    with st.expander("4. Laboratorios (Módulo Transquirúrgico)", expanded=True):
        st.markdown("**🧪 Perfil de Laboratorio Perioperatorio**")
        st.caption("Desmarque la casilla si el paciente no dispone del examen.")
        
        dict_labs = {}
        
        tiene_hb = st.checkbox("Hemoglobina / Hematocrito", value=True)
        if tiene_hb:
            c_hb1, c_hb2 = st.columns(2)
            hb = c_hb1.number_input("Hemoglobina (g/dL)", min_value=3.0, max_value=25.0, value=13.0, step=0.1)
            hto = c_hb2.number_input("Hematocrito (%)", min_value=10.0, max_value=75.0, value=40.0, step=1.0)
            dict_labs["Hemoglobina / Hematocrito"] = f"Hb: {hb} g/dL, Hto: {hto}%"
        
        tiene_plt = st.checkbox("Conteo de Plaquetas", value=True)
        if tiene_plt:
            plt = st.number_input("Plaquetas (x10³/µL)", min_value=10, max
                                  
