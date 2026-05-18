# -*- coding: utf-8 -*-
import streamlit as st
import math

st.set_page_config(page_title="Preanestesia", layout="wide")
st.title("🩺 Asistente de Evaluación Preanestésica")

col_izq, col_der = st.columns([1, 1.2])

with col_izq:
    st.header("📋 Datos de Entrada")
    
    with st.expander("1. Datos Demográficos", expanded=True):
        c1, c2, c3 = st.columns(3)
        sexo = c1.radio("Sexo", ["Masculino", "Femenino"])
        edad = c2.number_input("Edad (años)", value=50)
        peso_real = c3.number_input("Peso Real (kg)", value=70.0)
        talla_cm = st.number_input("Talla (cm)", value=165)

    with st.expander("2. Seguridad, Alergias y Medicamentos", expanded=True):
        st.markdown("**🚨 Alergias**")
        opciones_med = ["Penicilina / Betalactámicos", "AINEs", "Sulfa", "Medios de Contraste", "Látex", "Relajantes Musculares", "Opioides", "Dipirona"]
        alergias_med = st.multiselect("Medicamentosas:", options=opciones_med)
        
        opciones_com = ["Camarones / Mariscos", "Chocolate", "Soja", "Maní / Frutos Secos", "Huevo", "Leche de Vaca", "Trigo / Gluten", "Pescado"]
        alergias_com = st.multiselect("Alimentarias:", options=opciones_com)
        otras_alergias = st.text_input("Otras alergias:", value="")
        
        st.markdown("**💊 Medicamentos Críticos**")
        opciones_farmacos = ["Betabloqueantes", "IECA / ARA II", "Antiagregantes", "Anticoagulantes Orales", "Insulina", "Antidiabéticos Orales", "Corticoides Crónicos", "Anticonvulsivantes"]
        farmacos_criticos = st.multiselect("Fármacos activos:", options=opciones_farmacos)
        otros_farmacos = st.text_input("Otros medicamentos:", value="")
        
        st.markdown("**Antecedentes**")
        tiene_infarto = st.checkbox("Infarto de Miocardio (< 6 meses)")
        tiene_ic = st.checkbox("Insuficiencia Cardíaca Congestiva")
        tiene_acv = st.checkbox("Historia de ACV o AIT")
        tiene_insulina = st.checkbox("Diabetes con Insulina")
        tiene_ev = st.checkbox("> 5 Extrasístoles Ventriculares/min")
        tiene_ritmo_no_s = st.checkbox("Ritmo no sinusal / EAs")
        tiene_cancer = st.checkbox("Cáncer Activo")
        tiene_epoc = st.checkbox("EPOC / Neumopatía")

    with st.expander("3. Valoración de Vía Aérea"):
        mallampati = st.selectbox("Mallampati", ["Clase I", "Clase II", "Clase III", "Clase IV"])
        dtm = st.number_input("Distancia Tiromentoniana (cm)", value=7.0)
        dem = st.number_input("Distancia Esternomentoniana (cm)", value=13.0)
        cuello = st.number_input("Circunferencia de Cuello (cm)", value=38)
        protrusion_sel = st.selectbox("Protrusión Mandibular (Clase):", options=[1, 2, 3])
        
        st.markdown("**Índice de Arné**")
        historia_vad = st.checkbox("Historia previa de VAD")
        patologia_vad = st.checkbox("Patología asociada a VAD")
        apertura_bucal = st.checkbox("Apertura Bucal < 3.5 cm")
        movilidad_sel = st.selectbox("Movilidad Cervical (0=Normal, 1=Mod, 2=Sev):", options=[0, 1, 2])

        st.markdown("**VMD y SAHOS**")
        tiene_barba = st.checkbox("Barba densa")
        tiene_edentulia = st.checkbox("Edentulia")
        tiene_ronquido = st.checkbox("Historia de Ronquido / SAHOS")

    with st.expander("4. Laboratorios", expanded=True):
        dict_labs = {}
        if st.checkbox("Hemoglobina / Hematocrito", value=True):
            hb = st.number_input("Hemoglobina (g/dL)", value=13.0)
            hto = st.number_input("Hematocrito (%)", value=40.0)
            dict_labs["Hb/Hto"] = f"Hb: {hb} g/dL, Hto: {hto}%"
        if st.checkbox("Conteo de Plaquetas", value=True):
            plt = st.number_input("Plaquetas (x10³/µL)", value=250)
            dict_labs["Plaquetas"] = f"{plt} x10³"
        if st.checkbox("Tiempos (TP / TPT)", value=True):
            tp = st.number_input("TP (seg)", value=12.5)
            tpt = st.number_input("TPT (seg)", value=32.0)
            dict_labs["Tiempos"] = f"TP: {tp}s, TPT: {tpt}s"
        if st.checkbox("Función Renal", value=True):
            urea = st.number_input("Urea (mg/dL)", value=30)
            creatinina = st.number_input("Creatinina (mg/dL)", value=0.9)
            dict_labs["Renal"] = f"Urea: {urea}, Cr: {creatinina}"
        else:
            creatinina = 0.9
        if st.checkbox("Albúmina Sérica", value=True):
            alb = st.number_input("Albúmina (g/dL)", value=4.0)
            dict_labs["Albúmina"] = f"{alb} g/dL"
        alteraciones_lab = st.text_input("Otros laboratorios", "Sin alteraciones")
        diagnostico_ekg = st.text_input("Diagnóstico EKG", "Ritmo sinusal normal")

    with st.expander("5. Datos Quirúrgicos y Riesgos"):
        nombre_cx = st.text_input("Procedimiento", "Colecistectomía")
        riesgo_cx_tipo = st.selectbox("Riesgo Quirúrgico", ["Intermedio", "Bajo", "Alto"])
        cirugia_emergencia = st.checkbox("Cirugía de Emergencia")
        no_fumador = st.checkbox("NO Fumador", value=True)
        historia_nvpo = st.checkbox("Antecedente NVPO")
        opioides_post = st.checkbox("Opioides postoperatorios", value=True)
        varices = st.checkbox("Várices venosas")
        edema_mi = st.checkbox("Edema MMII")
        inmovilizacion = st.checkbox("Inmovilización > 72h")
        trombofilia = st.checkbox("Trombofilia")
        acceso_central = st.checkbox("Acceso central")

# --- LÓGICA DE CÁLCULO ---
talla_m = talla_cm / 100.0
imc = peso_real / (talla_m ** 2)
asc = math.sqrt((peso_real * talla_cm) / 3600)
peso_ideal = (50.0 if sexo == "Masculino" else 45.5) + 2.3 * ((talla_cm / 2.54) - 60.0)
peso_predicho = (50.0 if sexo == "Masculino" else 45.5) + 0.91 * (talla_cm - 152.4)
clcr_cg = ((140 - edad) * peso_real / (72 * max(creatinina, 0.1))) * (1.0 if sexo == "Masculino" else 0.85)

p_arne = (5 if historia_vad else 0) + (5 if patologia_vad else 0) + (2 if mallampati=="Clase III" else 5 if mallampati=="Clase IV" else 0) + (4 if dtm<=6.5 else 0) + (4 if apertura_bucal else 0) + (2 if movilidad_sel==1 else 5 if movilidad_sel==2 else 0)
p_stop = (1 if tiene_ronquido else 0) + (1 if imc>35 else 0) + (1 if edad>50 else 0) + (1 if cuello>40 else 0) + (1 if sexo=="Masculino" else 0)
p_lee = (1 if riesgo_cx_tipo=="Alto" else 0) + (1 if tiene_infarto else 0) + (1 if tiene_ic else 0) + (1 if tiene_acv else 0) + (1 if tiene_insulina else 0) + (1 if creatinina>2.0 else 0)
p_goldman = (5 if edad>70 else 0) + (10 if tiene_infarto else 0) + (7 if tiene_ritmo_no_s else 0) + (7 if tiene_ev else 0) + (11 if tiene_ic else 0) + (4 if cirugia_emergencia else 0) + (3 if riesgo_cx_tipo in ["Intermedio", "Alto"] else 0)
p_caprini = (1 if 41<=edad<=60 else 2 if 61<=edad<=74 else 3 if edad>=75 else 0) + (1 if imc>25 else 0) + (1 if varices else 0) + (1 if edema_mi else 0) + (1 if tiene_ic else 0) + (1 if tiene_epoc else 0) + (1 if tiene_infarto else 0) + (2 if riesgo_cx_tipo!="Bajo" else 0) + (2 if inmovilizacion else 0) + (2 if tiene_cancer else 0) + (2 if acceso_central else 0) + (3 if trombofilia else 0)
p_apfel = (1 if sexo=="Femenino" else 0) + (1 if no_fumador else 0) + (1 if historia_nvpo else 0) + (1 if opioides_post else 0)

str_alergias_med = ", ".join(alergias_med) if alergias_med else "Negadas"
str_alergias_com = ", ".join(alergias_com) if alergias_com else "Negadas"
str_farmacos = ", ".join(farmacos_criticos) if farmacos_criticos else "Ninguno"

with col_der:
    st.header("📊 Reporte Clínico Consolidado")
    if st.button("🔄 RECALCULAR VARIABLES", type="primary"):
        st.subheader("🩺 Resultados de la Evaluación")
        st.write(f"**Paciente:** {sexo} | {edad} años | IMC: {imc:.1f} kg/m² | ASC: {asc:.2f} m²")
        st.write(f"**Pesos:** Ideal: {peso_ideal:.1f} kg | Predicho: {peso_predicho:.1f} kg")
        st.info(f"🎯 **Volumen Corriente Protector:** {peso_predicho*6:.0f} mL a {peso_predicho*8:.0f} mL")
        
        st.markdown("---")
        st.write(f"**Alergias Medicamentos:** {str_alergias_med.upper()}")
        st.write(f"**Alergias Alimentos:** {str_alergias_com.upper()}")
        st.write(f"**Fármacos Críticos:** {str_farmacos}")
        
        st.markdown("---")
        st.write(f"**Vía Aérea:** Mallampati {mallampati} | DTM: {dtm} cm | Cuello: {cuello} cm")
        st.write(f"• **Escala Arné (VAD):** {p_arne} pts ({'ALTO RIESGO' if p_arne>=11 else 'BAJO RIESGO'})")
        st.write(f"• **STOP-BANG (SAHOS):** {p_stop}/8 pts")
        
        st.markdown("---")
        st.write("**🧪 Laboratorios Transquirúrgicos:**")
        if not dict_labs:
            st.error("❌ No hay datos de laboratorios registrados")
        else:
            for k, v in dict_labs.items():
                st.write(f"• **{k}:** {v}")
        st.write(f"• **Aclaramiento (Cockcroft-Gault):** {clcr_cg:.0f} mL/min")
        st.write(f"• **Otros analíticos:** {alteraciones_lab}")
        
        st.markdown("---")
        st.write("**🛡️ Estratificación de Riesgo Perioperatorio:**")
        st.write(f"• **Procedimiento:** {nombre_cx} (Riesgo: {riesgo_cx_tipo})")
        st.write(f"• **Cardiovascular (Lee RCRI):** Clase {('I' if p_lee==0 else 'II' if p_lee==1 else 'III' if p_lee==2 else 'IV')} ({p_lee} criterios)")
        st.write(f"• **Cardiovascular (Goldman):** {p_goldman} puntos")
        st.write(f"• **Tromboembólico (Caprini):** {p_caprini} puntos")
        st.write(f"• **Náuseas y Vómitos (Apfel):** {p_apfel}/4 puntos")
        st.write(f"• **EKG:** {diagnostico_ekg.upper()}")
        
        st.markdown("---")
        st.subheader("📋 Bloque de Texto para Historia Clínica")
        
        ant_lista = [k for k, v in [("Infarto", tiene_infarto), ("ICC", tiene_ic), ("ACV", tiene_acv), ("Insulina", tiene_insulina), ("EV", tiene_ev), ("Ritmo no S", tiene_ritmo_no_s), ("Cáncer", tiene_cancer), ("EPOC", tiene_epoc)] if v]
        ant_texto = ", ".join(ant_lista) if ant_lista else "Negados"
        str_labs_txt = " | ".join([f"{k}: {v}" for k, v in dict_labs.items()]) if dict_labs else "No provistos"

        texto_hc = (
            f"EVALUACIÓN PREANESTÉSICA\n"
            f"PACIENTE: {sexo} | Edad: {edad}a. IMC: {imc:.1f}kg/m2. ASC: {asc:.2f}m2.\n"
            f"Vt protector: {peso_predicho*6:.0f}-{peso_predicho*8:.0f}mL.\n"
            f"ALERGIAS: Meds: {str_alergias_med.upper()} | Alimentos: {str_alergias_com.upper()}\n"
            f"MEDICACIÓN: {str_farmacos} | ANTECEDENTES: {ant_texto}\n"
            f"VÍA AÉREA: Mallampati {mallampati}, DTM {dtm}cm, Arné: {p_arne} pts, STOP-BANG: {p_stop}/8.\n"
            f"LABORATORIOS: {str_labs_txt} | ClCr: {clcr_cg:.0f}mL/min | EKG: {diagnostico_ekg.upper()}\n"
            f"RIESGOS: Lee: Clase {('I' if p_lee==0 else 'II' if p_lee==1 else 'III' if p_lee==2 else 'IV')} | Goldman: {p_goldman}pts | Caprini: {p_caprini}pts | Apfel: {p_apfel}/4."
        )
        st.text_area(label="Copiar evolución:", value=texto_hc, height=200)
    else:
        st.info("💡 Complete los datos a la izquierda y presione el botón.")
        
