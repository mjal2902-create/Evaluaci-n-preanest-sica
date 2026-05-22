import streamlit as st
import math

st.set_page_config(layout="wide", page_title="Asistente Anestésico", page_icon="🩺")
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
    # GATEKEEPER: REGISTRO INSTITUCIONAL (Bloqueo Estricto)
    # ---------------------------------------------------------
    st.markdown("### 🏥 Registro Institucional")
    
    tipo_institucion = st.selectbox(
        "Clasificación Institucional",
        ["👈 Seleccione el Sector...", "Red Pública (MSP / IESS / JBG)", "Sector Privado", "Otro Centro / Práctica Privada"],
        key="mod_inst_tipo"
    )
    
    hospital_final = ""
    hospital_valido = False
    
    if tipo_institucion == "Red Pública (MSP / IESS / JBG)":
        lista_publicos = [
            "👈 Seleccione un hospital público...", 
            "Hospital de Especialidades Abel Gilbert Pontón (MSP)",
            "Hospital General del Norte de Guayaquil Los Ceibos (IESS)",
            "Hospital de Especialidades Teodoro Maldonado Carbo (IESS)",
            "Hospital General Monte Sinaí (MSP)",
            "Hospital Universitario de Guayaquil (MSP)",
            "Hospital de Niños Dr. Roberto Gilbert Elizalde (JBG)",
            "Hospital Gineco-Obstétrico Alfredo G. Paulson (JBG)",
            "Otro Hospital Público (Especificar)"
        ]
        hosp_sel = st.selectbox("📍 Seleccione el Hospital Público", lista_publicos, key="mod_inst_pub")
        
        # Lógica estricta de validación
        if hosp_sel == "👈 Seleccione un hospital público...":
            hospital_valido = False
        elif hosp_sel == "Otro Hospital Público (Especificar)":
            hospital_final = st.text_input("Escriba el nombre del hospital público:", key="mod_inst_pub_txt")
            if hospital_final.strip() != "": hospital_valido = True
        else:
            hospital_final = hosp_sel
            hospital_valido = True
            
    elif tipo_institucion == "Sector Privado":
        lista_privados = [
            "👈 Seleccione un centro privado...", 
            "Omni Hospital",
            "Hospital Clínica Kennedy (Policentro / Alborada / Samborondón)",
            "Hospital Alcívar",
            "Interhospital",
            "Hospital Clínica Panamericana",
            "Otro Centro Privado (Especificar)"
        ]
        hosp_sel = st.selectbox("📍 Seleccione el Centro Privado", lista_privados, key="mod_inst_priv")
        
        # Lógica estricta de validación
        if hosp_sel == "👈 Seleccione un centro privado...":
            hospital_valido = False
        elif hosp_sel == "Otro Centro Privado (Especificar)":
            hospital_final = st.text_input("Escriba el nombre del centro privado:", key="mod_inst_priv_txt")
            if hospital_final.strip() != "": hospital_valido = True
        else:
            hospital_final = hosp_sel
            hospital_valido = True
            
    elif tipo_institucion == "Otro Centro / Práctica Privada":
        hospital_final = st.text_input("Escriba el nombre de la Clínica o Centro Médico:", key="mod_inst_otro_txt")
        if hospital_final.strip() != "": hospital_valido = True

    # =========================================================
    # LÓGICA DE BLOQUEO (CANDADO)
    # =========================================================
    if not hospital_valido:
        st.info("🔒 Por favor, complete la selección de la institución arriba para desbloquear la evaluación.")
        
    else: # SI EL HOSPITAL ES VÁLIDO, ENTONCES DIBUJA LO DEMÁS
        st.success(f"✅ Centro registrado: **{hospital_final}**")
        st.divider()
        
        # ---------------------------------------------------------
        # MÓDULO 1: DATOS DEMOGRÁFICOS Y QUIRÚRGICOS (Con IMC)
        # ---------------------------------------------------------
        with st.expander("1. Datos Demográficos y Contexto Quirúrgico", expanded=True):
            st.divider() 
            # Fila 1: Demografía y Sangre
            c_demo1, c_demo2, c_demo3 = st.columns(3)
            sexo = c_demo1.radio("Sexo", ["Masculino", "Femenino"], key="mod1_sexo")
            edad_default = 30 if sexo == "Femenino" else 50
            edad = c_demo2.number_input("Edad (años)", min_value=0, max_value=120, value=edad_default, key="mod1_edad")
            grupo_sangre = c_demo3.selectbox("Grupo y Rh", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-", "Desconocido"], key="mod1_gs")
            
            # Fila 2: Antropometría e IMC Automatizado
            c_ant1, c_ant2, c_ant3 = st.columns(3)
            peso_real = c_ant1.number_input("Peso Real (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1, key="mod1_peso")
            talla_cm = c_ant2.number_input("Talla (cm)", min_value=30.0, max_value=250.0, value=165.0, step=1.0, key="mod1_talla")
            
            # Cálculo matemático e interpretación del IMC
            imc = 0.0
            cat_imc = "No calculado"
            if talla_cm > 0:
                imc = peso_real / ((talla_cm / 100) ** 2)
                if imc < 18.5:
                    cat_imc = "Bajo Peso ⚠️"
                elif imc < 25.0:
                    cat_imc = "Normal ✅"
                elif imc < 30.0:
                    cat_imc = "Sobrepeso ⚠️"
                else:
                    cat_imc = "Obesidad 🚨"
            
            # Despliegue visual del IMC como métrica destacada
            c_ant3.metric(label="IMC Calculado", value=f"{imc:.1f} kg/m²", delta=cat_imc, delta_color="normal")
            
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

            # Selectores
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

        # ---------------------------------------------------------
        # MÓDULO 2: SEGURIDAD, ALERGIAS Y ANTECEDENTES (Interactivos)
        # ---------------------------------------------------------
        with st.expander("2. Seguridad, Alergias y Antecedentes Patológicos", expanded=True):
            
            # --- 1. SECCIÓN DE ALERGIAS ---
            st.markdown("#### 🚨 Alergias y Sensibilidades")
            c_al1, c_al2 = st.columns(2)
            
            alergias_med = c_al1.multiselect(
                "Farmacológicas / Sustancias",
                options=["Penicilinas / Betalactámicos", "AINEs", "Látex", "Opioides", "Relajantes Musculares", "Anestésicos Locales", "Medios de Contraste", "Otros (Especificar)"],
                key="mod2_al_med"
            )
            # Cuadro dinámico para alergias medicamentosas
            if "Otros (Especificar)" in alergias_med:
                otras_alergias_med_txt = st.text_input("💊 Especifique otras alergias farmacológicas:", key="mod2_al_med_txt")
            else:
                otras_alergias_med_txt = ""

            alergias_alim = c_al2.multiselect(
                "Alimentarias",
                options=["Huevo", "Soya", "Mariscos / Yodo", "Frutos secos", "Lácteos", "Gluten", "Otros (Especificar)"],
                key="mod2_al_ali"
            )
            # Cuadro dinámico para alergias alimentarias
            if "Otros (Especificar)" in alergias_alim:
                otras_alergias_ali_txt = st.text_input("🥚 Especifique otras alergias alimentarias:", key="mod2_al_ali_txt")
            else:
                otras_alergias_ali_txt = ""

            st.divider()

            # --- 2. SECCIÓN DE ANTECEDENTES PATOLÓGICOS ---
            st.markdown("#### 📋 Antecedentes Patológicos Personales (APP)")
            
            if es_obstetrico:
                lista_patologias = ["Ninguno", "Trastornos Hipertensivos (Preeclampsia/HTA)", "Diabetes Gestacional", "Anemia", "Hipotiroidismo", "Asma", "Cardiopatía", "Obesidad", "Otros (Especificar)"]
            elif edad < 18:
                lista_patologias = ["Ninguno", "Asma / Hiperreactividad Bronquial", "Cardiopatía Congénita", "Epilepsia / Convulsiones", "Prematuridad / Ingreso a UCIN", "Trastorno Hematológico (Hemofilia/Drepanocitosis)", "Atopia / Rinitis", "Otros (Especificar)"]
            elif edad >= 60:
                if sexo == "Masculino":
                    lista_patologias = ["Ninguno", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Cardiopatía Isquémica (IAM/Angina)", "EPOC / Fumador", "Hipertrofia Prostática Benigna", "Arritmia (Fibrilación Auricular)", "Enfermedad Renal Crónica (ERC)", "ACV / Isquemia Transitoria", "Otros (Especificar)"]
                else:
                    lista_patologias = ["Ninguno", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Hipotiroidismo", "Osteoporosis / Osteoartritis", "Insuficiencia Cardíaca", "Arritmia (Fibrilación Auricular)", "Enfermedad Renal Crónica (ERC)", "ACV", "Otros (Especificar)"]
            else:
                if sexo == "Masculino":
                    lista_patologias = ["Ninguno", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Dislipidemia", "Asma / EPOC", "Reflujo Gastroesofágico (ERGE)", "Esteatosis Hepática / Hepatopatía", "Trastorno Psiquiátrico", "Otros (Especificar)"]
                else:
                    lista_patologias = ["Ninguno", "Hipotiroidismo", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Asma", "Enfermedad Autoinmune (LES/AR)", "Migraña / Cefalea Crónica", "Anemia", "Trastorno Psiquiátrico", "Otros (Especificar)"]

            antecedentes_seleccionados = st.multiselect(
                "Seleccione las patologías presentes", 
                options=lista_patologias, 
                key="mod2_antecedentes"
            )
            # Cuadro dinámico para antecedentes patológicos
            if "Otros (Especificar)" in antecedentes_seleccionados:
                otros_antecedentes_txt = st.text_input("🔍 Especifique otros antecedentes clínicos:", key="mod2_ant_otros_txt")
            else:
                otros_antecedentes_txt = ""

            st.divider()

            # --- 3. MEDICACIÓN HABITUAL ---
            st.markdown("#### 💊 Medicación de Uso Continuo")
            
            lista_medicamentos = ["Antihipertensivos (IECA/ARA II/BCC)", "Beta-bloqueadores", "Diuréticos", "Metformina / Hipoglucemiantes orales", "Insulina", "Antiagregantes (Aspirina/Clopidogrel)", "Anticoagulantes (Warfarina/DOACs)", "Levotiroxina", "Inhaladores (SABA/Corticoides)", "Anticonvulsivantes", "Ninguno", "Otros (Especificar)"]
            
            medicacion_actual = st.multiselect(
                "Fármacos activos", 
                options=lista_medicamentos, 
                key="mod2_medicacion"
            )
            # Cuadro dinámico para medicación habitual
            if "Otros (Especificar)" in medicacion_actual:
                notas_medicacion_txt = st.text_input("📝 Especifique fármacos adicionales, dosis o frecuencias:", key="mod2_med_notas_txt")
            else:
                notas_medicacion_txt = ""

            st.divider()

            # --- 4. SECCIÓN DE HÁBITOS ---
            st.markdown("#### 🚬 Hábitos y Estilo de Vida")
            st.caption("Nota: `+` Bajo | `++` Moderado | `+++` Severo/Grave")
            
            # Fila 1: Alcohol
            c_alc1, c_alc2 = st.columns([3, 1])
            hab_alcohol = c_alc1.checkbox("Consumo de Alcohol", key="mod2_hab_alc")
            int_alcohol = c_alc2.selectbox("Intensidad Alcohol", ["+", "++", "+++"], key="mod2_int_alc", disabled=not hab_alcohol, label_visibility="collapsed")
            
            # Fila 2: Cigarrillos
            c_cig1, c_cig2 = st.columns([3, 1])
            hab_cigarrillo = c_cig1.checkbox("Tabaquismo (Cigarrillos)", key="mod2_hab_cig")
            int_cigarrillo = c_cig2.selectbox("Intensidad Cigarrillo", ["+", "++", "+++"], key="mod2_int_cig", disabled=not hab_cigarrillo, label_visibility="collapsed")
            
            # Fila 3: Café
            c_caf1, c_caf2 = st.columns([3, 1])
            hab_cafe = c_caf1.checkbox("Consumo de Café", key="mod2_hab_caf")
            int_cafe = c_caf2.selectbox("Intensidad Café", ["+", "++", "+++"], key="mod2_int_caf", disabled=not hab_cafe, label_visibility="collapsed")
            
            # Fila 4: Drogas
            c_dro1, c_dro2 = st.columns([3, 1])
            hab_drogas = c_dro1.checkbox("Sustancias / Drogas de Abuso", key="mod2_hab_dro")
            int_drogas = c_dro2.selectbox("Intensidad Drogas", ["+", "++", "+++"], key="mod2_int_dro", disabled=not hab_drogas, label_visibility="collapsed")
            
            if hab_drogas:
                txt_drogas = st.text_input("Especifique la sustancia (Ej. Cannabis, Cocaína):", key="mod2_txt_dro")

# ---------------------------------------------------------
        # MÓDULO 3: VÍA AÉREA Y PARÁMETROS RESPIRATORIOS (SINCRO TOTAL)
        # ---------------------------------------------------------
        with st.expander("3. Vía Aérea y Parámetros Respiratorios", expanded=True):
            
            # --- 1. ESTADO RESPIRATORIO BASAL ---
            st.markdown("#### 🫁 Estado Respiratorio Basal")
            c_resp1, c_resp2 = st.columns(2)
            
            spo2_basal = c_resp1.number_input("SpO2 Basal (%)", min_value=10, max_value=100, value=98, key="mod3_spo2")
            fr_basal = c_resp2.number_input("FR Basal (rpm)", min_value=0, max_value=60, value=16, key="mod3_fr")
            
            auscultacion = st.selectbox(
                "Auscultación Pulmonar",
                ["Murmullo Vesicular Conservado", "Sibilancias Bilaterales", "Estertores / Crepitantes", "Disminución de MV unilateral", "Roncus"],
                key="mod3_ausc"
            )
            
            st.divider()

            # --- 2. PREDICTORES DE INTUBACIÓN DIFÍCIL (ASA TASKFORCE ACTUALIZADO) ---
            st.markdown("#### 👅 Predictores de Vía Aérea de Difícil Manejo (ASA Taskforce)")
            
            c_vad1, c_vad2 = st.columns(2)
            
            mallampati = c_vad1.selectbox(
                "Clasificación de Mallampati",
                [
                    "Clase I: Visibilidad de paladar blando, úvula, fauces y pilares",
                    "Clase II: Visibilidad de paladar blando, úvula y fauces",
                    "Clase III: Visibilidad de paladar blando y base de la úvula (Mallampati >2)",
                    "Clase IV: Solo es visible el paladar duro (Mallampati >2)"
                ],
                key="mod3_mallampati"
            )
            
            dtm = c_vad2.selectbox(
                "Distancia Tiromentoniana (Patil-Aldreti)",
                [
                    "Clase I (> 6.5 cm): Sin dificultad predictiva",
                    "Clase II (6.0 - 6.5 cm): Dificultad moderada",
                    "Clase III (< 6.0 cm): VAD predictiva"
                ],
                key="mod3_dtm"
            )
            
            c_vad3, c_vad4 = st.columns(2)
            
            apertura_bucal = c_vad3.selectbox(
                "Apertura Bucal (Distancia Interincisivos)",
                [
                    "Clase I (> 3.5 cm): Normal",
                    "Clase II (3.0 - 3.5 cm): Limitación leve",
                    "Clase III (< 3.0 cm): Limitación severa / Riesgo VAD"
                ],
                key="mod3_ab"
            )
            
            # NUEVO: Distancia Esternomentoniana (Escala de Savva)
            dem = c_vad4.selectbox(
                "Distancia Esternomentoniana (Savva)",
                [
                    "Clase I (> 12.5 cm): Sin dificultad predictiva",
                    "Clase II (11.5 - 12.5 cm): Dificultad moderada",
                    "Clase III (< 11.5 cm): Gran dificultad / VAD predictiva"
                ],
                key="mod3_dem"
            )

            c_vad5 = st.columns(1)[0]
            # NUEVO: Circunferencia de cuello movida aquí con los rangos solicitados
            cuello_cat = c_vad5.selectbox(
                "Circunferencia de Cuello",
                ["Menor a 35 cm (< 35 cm)", "Mayor a 35 cm (> 35 cm)"],
                key="mod3_cuello_categoria"
            )

            st.markdown("**Hallazgos Anatómicos Particulares:**")
            
            # Al eliminar st.columns, el texto respira y las casillas se alinean perfectamente
            vad_incisivos = st.checkbox("🔹 Incisivos largos y prominentes", key="mod3_incisivos")
            vad_paladar = st.checkbox("🔹 Paladar alto / Ojival", key="mod3_paladar")
            vad_lengua = st.checkbox("🔹 Gran tamaño de lengua (Macroglosia)", key="mod3_lengua")
            vad_cuello_ancho = st.checkbox("🔹 Cuello corto y ancho", value=(cuello_cat == "Mayor a 35 cm (> 35 cm)"), key="mod3_cuello_ancho")
            vad_movilidad = st.checkbox("🔹 Paciente incapaz de tocar la mandíbula con el pecho o extender la cabeza", key="mod3_mov_cervical")

            # Conteo analítico actualizado con los nuevos parámetros de intubación difícil
            criterios_asa_positivos = sum([
                vad_incisivos, vad_paladar, vad_lengua, vad_cuello_ancho, vad_movilidad,
                "Mallampati >2" in mallampati,
                "Clase III" in dtm,
                "Clase III" in apertura_bucal,
                "Clase III" in dem,
                cuello_cat == "Mayor a 35 cm (> 35 cm)"
            ])

            # Conteo analítico actualizado con los nuevos parámetros de intubación difícil
            criterios_asa_positivos = sum([
                vad_incisivos, vad_paladar, vad_lengua, vad_cuello_ancho, vad_movilidad,
                "Mallampati >2" in mallampati,
                "Clase III" in dtm,
                "Clase III" in apertura_bucal,
                "Clase III" in dem,
                cuello_cat == "Mayor a 35 cm (> 35 cm)"
            ])

            if criterios_asa_positivos >= 3:
                st.error(f"⚠️ Alerta: El paciente presenta {criterios_asa_positivos} factores de predicción de VAD (Criterios ASA Taskforce).")

            st.divider()

            # --- 3. PREDICTORES DE VENTILACIÓN DIFÍCIL CON MÁSCARA (OBESE CON SINCRO FORZADA) ---
            st.markdown("#### 😷 Predictores de Ventilación Difícil (Criterios OBESE)")
            st.caption("Nota: Las casillas de Edad y Obesidad están estrictamente concatenadas con los datos del Módulo 1.")
            
            # Lógica matemática de evaluación
            check_edad_obese = edad > 55
            check_imc_obese = imc >= 30.0 if 'imc' in locals() else False
            
            # SOLUCIÓN AL BUG DE STREAMLIT: Forzar la memoria de los widgets antes de renderizarlos
            st.session_state["mod3_vmd_edad"] = check_edad_obese
            st.session_state["mod3_vmd_ob"] = check_imc_obese
            
            c_vmd1, c_vmd2 = st.columns(2)
            
            # Renderizado reactivo absoluto
            vmd_edad = c_vmd1.checkbox("O - Edad > 55 años", key="mod3_vmd_edad")
            vmd_obesidad = c_vmd2.checkbox("O - Obesidad (IMC ≥ 30 kg/m²)", key="mod3_vmd_ob")
            
            c_vmd3, c_vmd4 = st.columns(2)
            vmd_barba = c_vmd3.checkbox("B - Presencia de Barba tupida", key="mod3_barba")
            vmd_edentulo = c_vmd4.checkbox("E - Paciente Edéntulo (Total o Parcial)", key="mod3_edentulo")
            
            # Sincronización automática de SAHOS con el Módulo 2
            check_sahos = any("SAHOS" in p or "Apnea" in p for p in antecedentes_seleccionados) if 'antecedentes_seleccionados' in locals() else False
            st.session_state["mod3_sahos"] = check_sahos
            
            vmd_sahos = st.checkbox("S - Historia de Ronquido Severo / Apnea del Sueño (SAHOS)", key="mod3_sahos")

            puntos_vmd = sum([vmd_edad, vmd_obesidad, vmd_barba, vmd_edentulo, vmd_sahos])
            if puntos_vmd >= 2:
                st.warning(f"⚠️ Riesgo de Ventilación Difícil con Máscara Facial: Elevado ({puntos_vmd}/5 criterios OBESE positivos).")
