import streamlit as st

# --- TÍTULO PRINCIPAL ---
st.title("🩺 Asistente de Evaluación Anestésica")
st.caption("Desarrollado para optimización clínica intraoperatoria y seguridad del paciente.")
st.caption("**Autor:** Dr. Marcos Aviles")
st.markdown("---")

# --- COLUMNAS PRINCIPALES ---
col_izq, col_der = st.columns([1, 1.2])

with col_izq:
    st.header("📋 Datos de Entrada")
    
    # ---------------------------------------------------------
    # MÓDULO 1: DATOS DEMOGRÁFICOS Y QUIRÚRGICOS
    # ---------------------------------------------------------
    with st.expander("1. Datos Demográficos y Contexto Quirúrgico", expanded=True):

        # --- SECCIÓN HOSPITALARIA (Para Contexto de Tesis) ---
        st.markdown("**🏥 Centro Hospitalario de Registro**")
        
        # El carácter general no es obligatorio ("No especificado" por defecto)
        tipo_institucion = st.selectbox(
            "Clasificación Institucional (Opcional)",
            ["No especificado", "Red Pública (MSP / IESS / JBG)", "Sector Privado", "Otro Centro / Práctica Privada"],
            key="mod1_tipo_inst"
        )
        
        hospital_final = "No especificado"
        
        # Viñeta especial: Si se selecciona una categoría, se vuelve obligatoria la selección del hospital
        if tipo_institucion == "Red Pública (MSP / IESS / JBG)":
            lista_publicos = [
                "Hospital de Especialidades Abel Gilbert Pontón (MSP)",
                "Hospital General del Norte de Guayaquil Los Ceibos (IESS)",
                "Hospital de Especialidades Teodoro Maldonado Carbo (IESS)",
                "Hospital General Monte Sinaí (MSP)",
                "Hospital Universitario de Guayaquil (MSP)",
                "Hospital de Niños Dr. Roberto Gilbert Elizalde (JBG)",
                "Hospital Gineco-Obstétrico Alfredo G. Paulson (JBG)",
                "Otro Hospital Público (Especificar)"
            ]
            hosp_sel = st.selectbox("📍 Seleccione el Hospital Público (Obligatorio para el registro)", lista_publicos, key="mod1_hosp_pub")
            if hosp_sel == "Otro Hospital Público (Especificar)":
                hospital_final = st.text_input("Escriba el nombre del hospital público:", key="mod1_hosp_pub_txt")
            else:
                hospital_final = hosp_sel
                
        elif tipo_institucion == "Sector Privado":
            lista_privados = [
                "Omni Hospital",
                "Hospital Clínica Kennedy (Policentro / Alborada / Samborondón)",
                "Hospital Alcívar",
                "Interhospital",
                "Hospital Clínica Panamericana",
                "Otro Centro Privado (Especificar)"
            ]
            hosp_sel = st.selectbox("📍 Seleccione el Centro Privado (Obligatorio para el registro)", lista_privados, key="mod1_hosp_priv")
            if hosp_sel == "Otro Centro Privado (Especificar)":
                hospital_final = st.text_input("Escriba el nombre del centro privado:", key="mod1_hosp_priv_txt")
            else:
                hospital_final = hosp_sel
                
        elif tipo_institucion == "Otro Centro / Práctica Privada":
            hospital_final = st.text_input("Escriba el nombre de la Clínica o Centro Médico (Obligatorio):", key="mod1_hosp_otro_txt")

        st.divider() 
        # Fila 1: Demografía y Sangre
        c_demo1, c_demo2, c_demo3 = st.columns(3)
        sexo = c_demo1.radio("Sexo", ["Masculino", "Femenino"], key="mod1_sexo")
        # Sugerencia inteligente de edad
        edad_default = 30 if sexo == "Femenino" else 50
        edad = c_demo2.number_input("Edad (años)", min_value=0, max_value=120, value=edad_default, key="mod1_edad")
        grupo_sangre = c_demo3.selectbox("Grupo y Rh", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-", "Desconocido"], key="mod1_gs")
        
        # Fila 2: Antropometría
        c_ant1, c_ant2 = st.columns(2)
        peso_real = c_ant1.number_input("Peso Real (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1, key="mod1_peso")
        talla_cm = c_ant2.number_input("Talla (cm)", min_value=30.0, max_value=250.0, value=165.0, step=1.0, key="mod1_talla")
        
        st.divider() 
        
        # Fila 3: Contexto Quirúrgico Base
        st.markdown("**Contexto Quirúrgico y Plan Anestésico**")
        
        # Lógica inteligente: Casilla obstétrica solo en mujeres en edad reproductiva o mayor
        es_obstetrico = False
        if sexo == "Femenino" and edad >= 10:
            es_obstetrico = st.checkbox("🤰 Paciente Obstétrica (Cambia diagnósticos y procedimientos)", key="mod1_obstetrico")

        c_cx1, c_cx2 = st.columns(2)
        caracter_cx = c_cx1.selectbox("Carácter", ["Electiva", "Urgencia", "Emergencia"], key="mod1_caracter")
        
        # Riesgo Quirúrgico
        riesgo_cx = c_cx2.selectbox("Riesgo Quirúrgico (AHA/ACC)", [
            "Bajo (<1%) - Ej: Superficial, Endoscópica, Catarata", 
            "Intermedio (1-5%) - Ej: Intraperitoneal, Ortopédica mayor", 
            "Alto (>5%) - Ej: Vascular mayor, Torácica, Aórtica"
        ], key="mod1_riesgo")
        
                # Fila 4: Diagnóstico y Procedimiento Dinámico (Motor Epidemiológico)
        c_cx3, c_cx4 = st.columns(2)
        
        # 1. Escenario Obstétrico (Precedencia más alta)
        if es_obstetrico:
            lista_diagnosticos = [
                "Embarazo a Término", "Trabajo de Parto Fase Activa", "Pre-eclampsia / Eclampsia", 
                "Sufrimiento Fetal Agudo", "Ruptura Prematura de Membranas", "Placenta Previa", 
                "Embarazo Ectópico", "Aborto Incompleto", "Otro (Especificar)"
            ]
            lista_procedimientos = [
                "Cesárea Segmentaria", "Legrado Uterino Instrumental (LUI)", 
                "Aspiración Manual Endouterina (AMEU)", "Cerclaje Cervical", 
                "Laparotomía Exploradora", "Salpingectomía", "Otro (Especificar)"
            ]
            
        # 2. Escenario Pediátrico (< 18 años)
        elif edad < 18:
            if sexo == "Masculino":
                lista_diagnosticos = ["Fimosis / Parafimosis", "Criptorquidia", "Apendicitis Aguda", "Hernia Inguinal", "Hipertrofia Amigdalina", "Fractura / Traumatismo", "Otro (Especificar)"]
                lista_procedimientos = ["Circuncisión", "Orquidopexia", "Apendicectomía", "Hernioplastia", "Amigdalectomía", "Reducción y Fijación (RAFI)", "Otro (Especificar)"]
            else:
                lista_diagnosticos = ["Apendicitis Aguda", "Hernia Umbilical / Inguinal", "Hipertrofia Amigdalina", "Cuerpo Extraño", "Fractura / Traumatismo", "Otro (Especificar)"]
                lista_procedimientos = ["Apendicectomía", "Hernioplastia", "Amigdalectomía", "Extracción de Cuerpo Extraño", "Reducción y Fijación (RAFI)", "Otro (Especificar)"]

        # 3. Escenario Geriátrico (≥ 60 años)
        elif edad >= 60:
            if sexo == "Masculino":
                lista_diagnosticos = ["Hipertrofia Prostática Benigna (HPB)", "Hernia Inguinal", "Artrosis Severa (Cadera/Rodilla)", "Cataratas", "Neoplasia (Urológica/Digestiva)", "Colelitiasis", "Otro (Especificar)"]
                lista_procedimientos = ["Resección Transuretral de Próstata (RTUP)", "Hernioplastia", "Artroplastia (Reemplazo Articular)", "Facoemulsificación", "Resección Oncológica", "Colecistectomía Laparoscópica", "Otro (Especificar)"]
            else:
                lista_diagnosticos = ["Fractura de Cadera / Fémur", "Colelitiasis / Colecistitis", "Artrosis Severa (Cadera/Rodilla)", "Prolapso de Órganos Pélvicos", "Cataratas", "Neoplasia", "Otro (Especificar)"]
                lista_procedimientos = ["Osteosíntesis / Artroplastia", "Colecistectomía Laparoscópica", "Reemplazo Articular", "Colporrafia / Histerectomía Vaginal", "Facoemulsificación", "Resección Oncológica", "Otro (Especificar)"]

        # 4. Escenario Adulto (18 - 59 años)
        else:
            if sexo == "Masculino":
                lista_diagnosticos = ["Colelitiasis / Colecistitis", "Hernia Inguinal / Umbilical", "Apendicitis Aguda", "Fractura / Traumatismo", "Enfermedad Hemorroidal", "Varicocele", "Otro (Especificar)"]
                lista_procedimientos = ["Colecistectomía Laparoscópica", "Hernioplastia", "Apendicectomía", "Reducción Abierta y Fijación Interna (RAFI)", "Hemorroidectomía", "Varicocelectomía", "Otro (Especificar)"]
            else:
                lista_diagnosticos = ["Colelitiasis / Colecistitis", "Miomatosis Uterina", "Quiste Ovárico", "Apendicitis Aguda", "Patología Mamaria", "Hernia Umbilical", "Otro (Especificar)"]
                lista_procedimientos = ["Colecistectomía Laparoscópica", "Histerectomía (Lap/Abierta)", "Quistectomía / Ooforectomía", "Apendicectomía", "Mastectomía / Resección Local", "Hernioplastia", "Otro (Especificar)"]

        # ---------------------------------------------------------
        # Renderizado de los Selectores
        # ---------------------------------------------------------
        diag_base = c_cx3.selectbox("Diagnóstico Principal", lista_diagnosticos, key="mod1_diag_base")
        if diag_base == "Otro (Especificar)":
            diagnostico_final = c_cx3.text_input("Especifique el diagnóstico", key="mod1_diag_txt")
        else:
            diagnostico_final = diag_base

        proc_base = c_cx4.selectbox("Procedimiento Propuesto", lista_procedimientos, key="mod1_proc_base")
        if proc_base == "Otro (Especificar)":
            procedimiento_final = c_cx4.text_input("Especifique el procedimiento", key="mod1_proc_txt")
        else:
            procedimiento_final = proc_base

            
        # Fila 5: Plan Anestésico
        tipo_anestesia = st.selectbox("Técnica Anestésica Propuesta", [
            "Anestesia General (Balanceada / TIVA)",
            "Anestesia Regional (Neuroeje: Raquídea / Epidural)",
            "Bloqueo de Nervio Periférico + Sedación",
            "Cuidado Anestésico Monitorizado (MAC) / Sedación",
            "Anestesia Local"
        ], key="mod1_tecnica")
        
