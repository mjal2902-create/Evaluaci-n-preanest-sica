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
# --- APARTADO DINÁMICO DE FRACTURAS (MÓDULO 1) ---
            tipo_fractura_cx = "No aplica"
            if "Fractura" in diagnostico_final:
                st.caption("⚠️ Detalle de Traumatología Quirúrgica detectado:")
                tipo_fractura_cx = st.selectbox(
                    "🦴 Tipo / Localización de la Fractura a intervenir",
                    [
                        "Fractura de Cadera (Fémur Proximal) [Riesgo Caprini Extremo]",
                        "Fractura de Pelvis o Acetábulo [Riesgo Caprini Extremo]",
                        "Fractura de Miembro Inferior (Diáfisis de Fémur, Tibia, Peroné) [Riesgo Caprini Extremo]",
                        "Fractura de Miembro Superior (Húmero, Radio, Cúbito, Clavícula)",
                        "Fractura Vertebral / Columna (Compromiso medular / Estabilización)",
                        "Fractura Conminuta de Tobillo / Retropié",
                        "Fractura Maxilofacial / Mandibular Compleja"
                    ],
                    key="mod1_tipo_fractura"
                )
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
        # MÓDULO 2: SEGURIDAD, ALERGIAS Y ANTECEDENTES (DINAMIZADO Y UNIFICADO)
        # ---------------------------------------------------------
        with st.expander("2. Seguridad, Alergias y Antecedentes Patológicos", expanded=True):
            
            # --- 1. SECCIÓN DE ALERGIAS ---
            st.markdown("#### 🚨 Alergias y Sensibilidades")
            sin_alergias = st.checkbox("✅ No refiere alergias", value=True, key="mod2_sin_alergias")
            
            alergias_med = []
            otras_alergias_med_txt = ""
            alergias_alim = []
            otras_alergias_ali_txt = ""
            
            if not sin_alergias:
                c_al1, c_al2 = st.columns(2)
                alergias_med = c_al1.multiselect(
                    "Farmacológicas / Sustancias",
                    options=["Penicilinas / Betalactámicos", "AINEs", "Látex", "Opioides", "Relajantes Musculares", "Anestésicos Locales", "Medios de Contraste", "Otros (Especificar)"],
                    key="mod2_al_med"
                )
                if "Otros (Especificar)" in alergias_med:
                    otras_alergias_med_txt = c_al1.text_input("💊 Especifique otras alergias farmacológicas:", key="mod2_al_med_txt")

                alergias_alim = c_al2.multiselect(
                    "Alimentarias",
                    options=["Huevo", "Soya", "Mariscos / Yodo", "Frutos secos", "Lácteos", "Gluten", "Otros (Especificar)"],
                    key="mod2_al_ali"
                )
                if "Otros (Especificar)" in alergias_alim:
                    otras_alergias_ali_txt = c_al2.text_input("🥚 Especifique otras alergias alimentarias:", key="mod2_al_ali_txt")

            st.divider()

            # --- 2. SECCIÓN UNIFICADA: ANTECEDENTES Y MEDICACIÓN ---
            st.markdown("#### 📋 Antecedentes Patológicos y Medicación Habitual")
            sin_antecedentes = st.checkbox("✅ No refiere antecedentes patológicos ni medicación de uso continuo", value=True, key="mod2_sin_antecedentes")
            
            antecedentes_seleccionados = ["Ninguno"]
            otros_antecedentes_txt = ""
            medicacion_actual = ["Ninguno"]
            notas_medicacion_txt = ""
            tipo_fractura_app = "No aplica" # Inicialización de seguridad
            child_ascitis = "Ausente"
            child_encefalo = "Ausente"
            
            if not sin_antecedentes:
                # Motor de listas epidemiológicas por edad/sexo
                if es_obstetrico:
                    lista_patologias = ["Ninguno", "Trastornos Hipertensivos (Preeclampsia/HTA)", "Diabetes Gestacional", "Anemia", "Hipotiroidismo", "Asma", "Cardiopatía", "Obesidad", "Otros (Especificar)"]
                elif edad < 18:
                    lista_patologias = ["Ninguno", "Asma / Hiperreactividad Bronquial", "Cardiopatía Congénita", "Epilepsia / Convulsiones", "Prematuridad / Ingreso a UCIN", "Trastorno Hematológico", "Atopia / Rinitis", "Otros (Especificar)"]
                elif edad >= 60:
                    if sexo == "Masculino":
                        lista_patologias = ["Ninguno", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Cardiopatía Isquémica (IAM/Angina)", "EPOC / Fumador", "Hipertrofia Prostática Benigna", "Arritmia (FA)", "Enfermedad Renal Crónica (ERC)", "ACV / Isquemia Transitoria", "Otros (Especificar)"]
                    else:
                        lista_patologias = ["Ninguno", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Hipotiroidismo", "Osteoporosis / Osteoartritis", "Insuficiencia Cardíaca", "Arritmia (FA)", "Enfermedad Renal Crónica (ERC)", "ACV", "Otros (Especificar)"]
                else:
                    if sexo == "Masculino":
                        lista_patologias = ["Ninguno", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Dislipidemia", "Asma / EPOC", "Reflujo Gastroesofágico (ERGE)", "Hepatopatía", "Trastorno Psiquiátrico", "Otros (Especificar)"]
                    else:
                        lista_patologias = ["Ninguno", "Hipotiroidismo", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Asma", "Enfermedad Autoinmune (LES/AR)", "Migraña", "Anemia", "Trastorno Psiquiátrico", "Otros (Especificar)"]

                # Inyección global de la opción de Fractura
               # Inyección global de opciones específicas
                if "Otros (Especificar)" in lista_patologias:
                    idx = lista_patologias.index("Otros (Especificar)")
                    lista_patologias.insert(idx, "Fractura / Traumatismo Mayor")
                    lista_patologias.insert(idx, "Cirrosis Hepática")

                lista_medicamentos = ["Antihipertensivos (IECA/ARA II/BCC)", "Beta-bloqueadores", "Diuréticos", "Metformina / Hipoglucemiantes orales", "Insulina", "Antiagregantes (Aspirina/Clopidogrel)", "Anticoagulantes (Warfarina/DOACs)", "Levotiroxina", "Inhaladores (SABA/Corticoides)", "Anticonvulsivantes", "Ninguno", "Otros (Especificar)"]
                
                c_unif1, c_unif2 = st.columns(2)
                
                antecedentes_seleccionados = c_unif1.multiselect("Patologías Clínicas (APP)", options=lista_patologias, key="mod2_antecedentes")

                # APARTADO DINÁMICO: CHILD-PUGH (PARÁMETROS CLÍNICOS)
                if "Cirrosis Hepática" in antecedentes_seleccionados:
                    st.caption("🟡 Evaluación de Severidad Hepática (Child-Pugh):")
                    c_hep1, c_hep2 = st.columns(2)
                    child_ascitis = c_hep1.selectbox("Ascitis", ["Ausente", "Leve / Moderada (Controlada)", "Tensa / Grave (Refractaria)"], key="mod2_ascitis")
                    child_encefalo = c_hep2.selectbox("Encefalopatía", ["Ausente", "Grado I - II (Leve)", "Grado III - IV (Grave)"], key="mod2_encefalo")
                # APARTADO DINÁMICO: TIPOS DE FRACTURA MÁS COMUNES
                if "Fractura / Traumatismo Mayor" in antecedentes_seleccionados:
                    tipo_fractura_app = c_unif1.selectbox(
                        "🦴 Tipo / Localización de la Fractura",
                        [
                            "Fractura de Cadera (Fémur Proximal) [Riesgo Caprini Alto]",
                            "Fractura de Pelvis o Acetábulo [Riesgo Caprini Alto]",
                            "Fractura de Miembro Inferior (Diáfisis de Fémur, Tibia, Peroné) [Riesgo Caprini Alto]",
                            "Fractura de Miembro Superior (Húmero, Radio, Cúbito, Clavícula)",
                            "Fractura Vertebral / Columna (Torácica / Lumbar)",
                            "Fractura Craneofacial / Mandibular"
                        ],
                        key="mod2_tipo_fractura"
                    )
                
                if "Otros (Especificar)" in antecedentes_seleccionados:
                    otros_antecedentes_txt = c_unif1.text_input("🔍 Especifique otros antecedentes:", key="mod2_ant_otros_txt")

                medicacion_actual = c_unif2.multiselect("Fármacos de Uso Continuo", options=lista_medicamentos, key="mod2_medicacion")
                if "Otros (Especificar)" in medicacion_actual:
                    notas_medicacion_txt = c_unif2.text_input("📝 Especifique dosis o frecuencias:", key="mod2_med_notas_txt")

            st.divider()
            
            # --- 3. SECCIÓN DE HÁBITOS ---
            st.markdown("#### 🚬 Hábitos y Estilo de Vida")
            sin_habitos = st.checkbox("✅ No refiere hábitos dañinos", value=True, key="mod2_sin_habitos")
            hab_alcohol = False; int_alcohol = "+"; hab_cigarrillo = False; int_cigarrillo = "+"; hab_cafe = False; int_cafe = "+"; hab_drogas = False; int_drogas = "+"; txt_drogas = ""

            if not sin_habitos:
                st.caption("Nota: `+` Bajo | `++` Moderado | `+++` Severo/Grave")
                c_alc1, c_alc2 = st.columns([3, 1])
                hab_alcohol = c_alc1.checkbox("Consumo de Alcohol", key="mod2_hab_alc")
                int_alcohol = c_alc2.selectbox("Intensidad Alcohol", ["+", "++", "+++"], key="mod2_int_alc", disabled=not hab_alcohol, label_visibility="collapsed")
                
                c_cig1, c_cig2 = st.columns([3, 1])
                hab_cigarrillo = c_cig1.checkbox("Tabaquismo (Cigarrillos)", key="mod2_hab_cig")
                int_cigarrillo = c_cig2.selectbox("Intensidad Cigarrillo", ["+", "++", "+++"], key="mod2_int_cig", disabled=not hab_cigarrillo, label_visibility="collapsed")
                
                c_caf1, c_caf2 = st.columns([3, 1])
                hab_cafe = c_caf1.checkbox("Consumo de Café", key="mod2_hab_caf")
                int_cafe = c_caf2.selectbox("Intensidad Café", ["+", "++", "+++"], key="mod2_int_caf", disabled=not hab_cafe, label_visibility="collapsed")
                
                c_dro1, c_dro2 = st.columns([3, 1])
                hab_drogas = c_dro1.checkbox("Sustancias / Drogas de Abuso", key="mod2_hab_dro")
                int_drogas = c_dro2.selectbox("Intensidad Drogas", ["+", "++", "+++"], key="mod2_int_dro", disabled=not hab_drogas, label_visibility="collapsed")
                if hab_drogas:
                    txt_drogas = st.text_input("Especifique la sustancia:", key="mod2_txt_dro")

# ---------------------------------------------------------
        # MÓDULO 3: VÍA AÉREA Y PREDICTORES (ANTROPOMETRÍA ADAPTATIVA)
        # ---------------------------------------------------------
        with st.expander("3. Vía Aérea y Predictores de Dificultad", expanded=True):
            
            # Inicialización global de variables de seguridad
            arne_historia = False
            arne_patologia = False
            mallampati = "No aplica (Pediátrico)"
            dtm = "No aplica (Pediátrico)"
            apertura_bucal = "No aplica (Pediátrico)"
            dem = "No aplica (Pediátrico)"
            cuello_cat = "No aplica (Pediátrico)"
            ulbt = "No aplica (Pediátrico)"
            mov_cervical_arne = "Normal: Extensión completa (> 90°)"
            
            vad_incisivos = False
            vad_paladar = False
            vad_lengua = False
            vad_retrognatia = False
            
            vmd_barba = False
            vmd_edentulo = False
            sb_s = False
            sb_t = False
            sb_o = False
            
            score_arne = 0
            puntos_vmd = 0
            puntos_stop_bang = 0

            es_pediatrico_va = edad < 18 if 'edad' in locals() else False
            mostrar_va_adultos = True

            if es_pediatrico_va:
                colabora_ped = st.checkbox(
                    "👦 Paciente pediátrico colaborador (Permite examen físico con rangos indexados)", 
                    value=False, 
                    key="mod3_ped_colabora"
                )
                
                if not colabora_ped:
                    mostrar_va_adultos = False
                    st.markdown("#### 👶 Evaluación de Vía Aérea Pediátrica (Lactantes / Infantes)")
                    st.caption("Escalas anatómicas estándar no valorables por falta de cooperación o desarrollo estructural:")
                    
                    ped_estridor = st.checkbox("🔹 Historia de estridor laríngeo, crup recurrente o laringomalacia", key="mod3_ped_estridor")
                    ped_ivra = st.checkbox("🔹 Infección de Vías Respiratorias Altas (IVRA) activa o reciente (< 2 semanas)", key="mod3_ped_ivra")
                    ped_vad_previo = st.checkbox("🔹 Antecedente documentado de laringoscopia difícil o intubación fallida", key="mod3_ped_vad_prev")
                    ped_ronquido = st.checkbox("🔹 Ronquido nocturno severo o Apnea obstructiva pediátrica conocida", key="mod3_ped_ronq")

                    st.divider()
                    
                    st.markdown("**Malformaciones Anatómicas y Complejidad Sindrómica:**")
                    ped_retrognatia = st.checkbox("🔹 Micrognatia / Retrognatia severa (Ej: Pierre Robin, Treacher Collins)", key="mod3_ped_retro")
                    ped_macroglosia = st.checkbox("🔹 Macroglosia evidente o sospecha (Ej: Síndrome de Down)", key="mod3_ped_macro")
                    ped_cuello_corto = st.checkbox("🔹 Limitación de la movilidad cervical o cuello corto (Ej: Klippel-Feil)", key="mod3_ped_ccorto")
                    ped_masas = st.checkbox("🔹 Presencia de masas cervicales o maxilofaciales compresivas", key="mod3_ped_masas")

                    score_arne = 12 if ped_vad_previo else 0
                    if ped_retrognatia or ped_macroglosia or ped_cuello_corto: score_arne += 6
                    puntos_vmd = sum([ped_ronquido, ped_macroglosia])
                    puntos_stop_bang = sum([ped_ronquido, ped_estridor, ped_ivra])

            # Si el paciente es Adulto O es un Niño Colaborador, adaptamos los rangos métricos
            if mostrar_va_adultos:
                
                # --- DEFINICIÓN DINÁMICA DE OPCIONES SEGÚN EL GRUPO ETARIO ---
                if es_pediatrico_va:
                    # Eliminamos centímetros fijos para evitar sesgos por diferencias de edad (2 vs 16 años)
                    opciones_mallampati = [
                        "Clase I: Visibilidad de paladar blando, úvula y pilares",
                        "Clase II: Visibilidad de paladar blando y úvula",
                        "Clase III: Visibilidad de paladar blando y base de la úvula",
                        "Clase IV: Solo es visible el paladar duro"
                    ]
                    opciones_dtm = [
                        "Clase I (Normal): > 3 dedos del propio paciente (Distancia conservada)",
                        "Clase II (Moderada): 2 - 3 dedos del propio paciente (Acortamiento leve)",
                        "Clase III (VAD Predictiva): < 2 dedos del propio paciente (Acortamiento severo)"
                    ]
                    opciones_ab = [
                        "Clase I (Normal): > 2 dedos del propio paciente (Apertura conservada)",
                        "Clase II (Moderada): 1.5 - 2 dedos del propio paciente (Limitación leve)",
                        "Clase III (Severa): < 1.5 dedos del propio paciente (Limitación crítica)"
                    ]
                    opciones_dem = [
                        "Clase I (Normal): Extensión esternomentoniana conservada para la edad",
                        "Clase II (Moderada): Restricción parcial de la extensión cefálica",
                        "Clase III (Severa): Extensión críticamente limitada / VAD predictiva"
                    ]
                    opciones_cuello = [
                        "Normal y proporcional para la edad cronológica", 
                        "Aumentado / Cuello grueso u obeso para la edad (Riesgo obstructivo)"
                    ]
                else:
                    # Rangos estándar internacionales para pacientes adultos
                    opciones_mallampati = [
                        "Clase I: Visibilidad de paladar blando, úvula, fauces y pilares",
                        "Clase II: Visibilidad de paladar blando, úvula y fauces",
                        "Clase III: Visibilidad de paladar blando y base de la úvula",
                        "Clase IV: Solo es visible el paladar duro"
                    ]
                    opciones_dtm = [
                        "Clase I (> 6.5 cm): Sin dificultad predictiva",
                        "Clase II (6.0 - 6.5 cm): Dificultad moderada",
                        "Clase III (< 6.0 cm): VAD predictiva"
                    ]
                    opciones_ab = [
                        "Clase I (> 3.5 cm): Normal",
                        "Clase II (3.0 - 3.5 cm): Limitación leve",
                        "Clase III (< 3.0 cm): Limitación severa"
                    ]
                    opciones_dem = [
                        "Clase I (> 12.5 cm): Sin dificultad predictiva",
                        "Clase II (11.5 - 12.5 cm): Dificultad moderada",
                        "Clase III (< 11.5 cm): Gran dificultad / VAD predictiva"
                    ]
                    opciones_cuello = [
                        "Menor a 35 cm (< 35 cm)", 
                        "Entre 35 y 40 cm (35 - 40 cm)", 
                        "Mayor a 40 cm (> 40 cm)"
                    ]

                # --- RENDERIZADO DE CONTROLES ADAPTATIVOS ---
                st.markdown("#### 📜 Historia Clínica de Vía Aérea")
                c_arne1, c_arne2 = st.columns(2)
                arne_historia = c_arne1.checkbox("🚨 Antecedente personal de Intubación Difícil", key="mod3_arne_hist")
                arne_patologia = c_arne2.checkbox("🏥 Patología clínica asociada a VAD (Ej: Tumores, Angioedema)", key="mod3_arne_pat")
                
                st.divider()
                st.markdown("#### 👅 Evaluación Anatómica y Movilidad")
                
                c_vad1, c_vad2 = st.columns(2)
                mallampati = c_vad1.selectbox("Clasificación de Mallampati", opciones_mallampati, key="mod3_mallampati")
                dtm = c_vad2.selectbox("Distancia Tiromentoniana (Patil-Aldreti)", opciones_dtm, key="mod3_dtm")
                
                c_vad3, c_vad4 = st.columns(2)
                apertura_bucal = c_vad3.selectbox("Apertura Bucal (Distancia Interincisivos)", opciones_ab, key="mod3_ab")
                dem = c_vad4.selectbox("Distancia Esternomentoniana (Savva)", opciones_dem, key="mod3_dem")

                c_vad5, c_vad6 = st.columns(2)
                cuello_cat = c_vad5.selectbox("Circunferencia de Cuello", opciones_cuello, key="mod3_cuello_categoria")
                ulbt = c_vad6.selectbox(
                    "Test de Mordida de Labio Superior (ULBT / Subluxación)",
                    [
                        "Clase I: Incisivos inferiores cubren la línea bermellón",
                        "Clase II: Incisivos muerden el labio pero no cubren la línea",
                        "Clase III: Incisivos no pueden morder el labio superior"
                    ],
                    key="mod3_ulbt"
                )

                mov_cervical_arne = st.selectbox(
                    "Movilidad de Cabeza y Cuello (Extensión cervical)",
                    [
                        "Normal: Extensión completa (> 90°)",
                        "Limitación Moderada: Extensión parcialmente reducida (80° - 90°)",
                        "Limitación Severa: Rigidez extrema o fijación estructural (< 80°)"
                    ],
                    key="mod3_mov_arne"
                )

                st.markdown("**Hallazgos Anatómicos Particulares adicionales:**")
                vad_incisivos = st.checkbox("🔹 Incisivos largos y prominentes", key="mod3_incisivos")
                vad_paladar = st.checkbox("🔹 Paladar alto / Ojival", key="mod3_paladar")
                vad_lengua = st.checkbox("🔹 Gran tamaño de lengua (Macroglosia)", key="mod3_lengua")
                vad_retrognatia = st.checkbox("🔹 Retrognatia / Micrognatia (Mentón retraído)", key="mod3_retrognatia")

                # --- PROCESAMIENTO SILENCIOSO DE ARNÉ ---
                pts_historia = 10 if arne_historia else 0
                pts_patologia = 5 if arne_patologia else 0
                pts_mallampati = 0 if "Clase I" in mallampati else (1 if "Clase II" in mallampati else (2 if "Clase III" in mallampati else 5))
                pts_dtm = 0 if "Clase I" in dtm else (2 if "Clase II" in dtm else 4)
                pts_ab = 0 if "Clase I" in apertura_bucal else (2 if "Clase II" in apertura_bucal else 4)
                pts_mov = 0 if "Normal" in mov_cervical_arne else (2 if "Moderada" in mov_cervical_arne else 5)
                score_arne = pts_historia + pts_patologia + pts_mallampati + pts_dtm + pts_ab + pts_mov

                st.divider()

                # --- PROCESAMIENTO SILENCIOSO DE ARNÉ ---
                pts_historia = 10 if arne_historia else 0
                pts_patologia = 5 if arne_patologia else 0
                pts_mallampati = 0 if "Clase I" in mallampati else (1 if "Clase II" in mallampati else (2 if "Clase III" in mallampati else 5))
                pts_dtm = 0 if "Clase I" in dtm else (2 if "Clase II" in dtm else 4)
                pts_ab = 0 if "Clase I" in apertura_bucal else (2 if "Clase II" in apertura_bucal else 4)
                pts_mov = 0 if "Normal" in mov_cervical_arne else (2 if "Moderada" in mov_cervical_arne else 5)
                score_arne = pts_historia + pts_patologia + pts_mallampati + pts_dtm + pts_ab + pts_mov

                # ---------------------------------------------------------
                # CONTROL PEDIÁTRICO ABSOLUTO PARA OBESE / STOP-BANG
                # ---------------------------------------------------------
                if not es_pediatrico_va:
                    st.divider()
                    # --- 3. SECCIÓN UNIFICADA SÓLO PARA ADULTOS ---
                    st.markdown("#### 😷 Factores Físicos y Sintomatología (OBESE / STOP)")
                    st.caption("Marque las características particulares identificadas en la evaluación:")

                    vmd_barba = st.checkbox("🔸 Presencia de barba tupida (Dificulta el sello de la máscara)", key="mod3_barba")
                    vmd_edentulo = st.checkbox("🔸 Paciente edéntulo total o parcial", key="mod3_edentulo")
                    sb_s = st.checkbox("🔸 Historial de ronquido fuerte (Audible a través de puertas cerradas)", key="mod3_sb_s")
                    sb_t = st.checkbox("🔸 Cansancio, fatiga o somnolencia diurna frecuente", key="mod3_sb_t")
                    sb_o = st.checkbox("🔸 Apnea nocturna observada por terceros (Pausas al respirar)", key="mod3_sb_o")

        puntos_vmd = sum([vmd_barba, vmd_edentulo])
            puntos_stop_bang = sum([sb_s, sb_t, sb_o])
        else:
            st.info("⚠️ **Nota metodológica:** Las herramientas OBESE y STOP-BANG están validadas exclusivamente para la población adulta, por lo que han sido omitidas de la evaluación de este paciente.")

        # --- SUBSECCIÓN GENERAL: RIESGO PULMONAR (MÓDULO 3) ---
        st.divider()
        st.markdown("#### 🫁 Evaluación Respiratoria Avanzada (ARISCAT)")
        st.caption("Complete los hallazgos clínicos para la predicción de complicaciones pulmonares postoperatorias:")
        
        c_aris1, c_aris2 = st.columns(2)
        with c_aris1:
            ariscat_enfermedad_pulmonar = st.checkbox("🔸 Patología respiratoria crónica activa (EPOC, Asma sintomática, Fibrosis)", key="mod3_ariscat_epoc")
        with c_aris2:
            ariscat_infeccion_reciente = st.checkbox("🔸 Infección de vías respiratorias (altas o bajas) en el último mes", key="mod3_ariscat_inf")
# ---------------------------------------------------------
        # MÓDULO 4: EVALUACIÓN CARDIOVASCULAR Y CAPACIDAD FUNCIONAL
        # ---------------------------------------------------------
        with st.expander("4. Evaluación Cardiovascular y Capacidad Funcional", expanded=True):
            
            # Inicialización basal de seguridad (Evita NameError)
            capacidad_funcional = "No aplica (Pediátrico)"
            clase_nyha = "No aplica (Pediátrico)"
            cardio_angina = False
            cardio_disnea = False
            cardio_palpitaciones = False
            cardio_edema = False
            cardio_soplo = False
            ecg_hallazgo = "No disponible / No solicitado"
            fevi_valor = 60.0
            score_lee = 0

            # Evaluación interactiva de edad desde el Módulo 1
            es_pediatrico = edad < 18 if 'edad' in locals() else False
            mostrar_cardio_completo = True

            # Condicional dinámico para etapas infantiles
            if es_pediatrico:
                sin_cardiopatia_ped = st.checkbox(
                    "✅ Paciente pediátrico sin patologías cardíacas conocidas", 
                    value=True, 
                    key="mod4_ped_sano"
                )
                if sin_cardiopatia_ped:
                    mostrar_cardio_completo = False
                    st.info("👶 Evaluación cardiológica avanzada omitida por criterio de edad (Infante sano).")
                else:
                    mostrar_cardio_completo = False
                    st.markdown("#### 👶 Evaluación Cardiovascular Pediátrica Especializada")
                    c_ped1, c_ped2 = st.columns(2)
                    
                    clase_ross = c_ped1.selectbox(
                        "Clase Funcional Pediátrica (Escala de Ross)",
                        [
                            "Clase I: Asintomático",
                            "Clase II: Taquipnea o diaforesis leve en la alimentación. Disnea de esfuerzo en niños mayores.",
                            "Clase III: Marcada taquipnea/diaforesis al alimentarse. Tiempo de toma prolongado. Retraso del crecimiento.",
                            "Clase IV: Síntomas de insuficiencia cardíaca congestiva en reposo (retracciones, quejido)."
                        ],
                        key="mod4_ross"
                    )
                    
                    complejidad_cc = c_ped2.selectbox(
                        "Complejidad de la Cardiopatía Congénita (CC)",
                        [
                            "Leve (Bajo Riesgo): CC corregida sin shunts residuales o Estenosis Pulmonar leve.",
                            "Moderada (Riesgo Intermedio): CC acianógena no corregida (CIV/CIA pequeñas), Fallot corregido, Coartación corregida.",
                            "Severa (Alto Riesgo): Hipertensión Pulmonar (Eisenmenger), CC cianógenas, Ventrículo único, Miocardiopatías."
                        ],
                        key="mod4_cc_complejidad"
                    )
                    
                    capacidad_funcional = f"Complejidad CC: {complejidad_cc.split('(')[0].strip()}"
                    clase_nyha = f"Ross: {clase_ross.split(':')[0].strip()}"

            # Si el paciente es adulto o es un infante con cardiopatía, se despliega todo
            if mostrar_cardio_completo:
                # --- 1. CAPACIDAD METABÓLICA Y CLASE FUNCIONAL ---
                st.markdown("#### 🏃 Capacidad Metabolicay Clase Funcional")
                c_card1, c_card2 = st.columns(2)
                
                capacidad_funcional = c_card1.selectbox(
                    "Capacidad Funcional (Mets)",
                    [
                        "Excelente (≥ 10 METs) - Ej: Deportes de alta intensidad",
                        "Buena (4 - 10 METs) - Ej: Sube dos pisos de escaleras sin detenerse",
                        "Limitada (< 4 METs) - Ej: Camina 1 o 2 cuadras / Trabajo doméstico ligero",
                        "Severamente Limitada (< 1 MET) - Ej: Disnea en reposo o actividades de autocuidado"
                    ],
                    key="mod4_mets"
                )
                
                clase_nyha = c_card2.selectbox(
                    "Clasificación Funcional NYHA",
                    [
                        "Clase I: Sin limitación de la actividad física ordinaria",
                        "Clase II: Limitación ligera. Confortable en reposo",
                        "Clase III: Limitación marcada. Actividad menor a la ordinaria causa síntomas",
                        "Clase IV: Incapacidad de realizar cualquier actividad sin malestar / Síntomas en reposo"
                    ],
                    key="mod4_nyha"
                )
                
                st.divider()
                
                # --- 2. SINTOMATOLOGÍA CARDIOVASCULAR ACTUAL ---
                st.markdown("#### 🫀 Sintomatología y Signos Clínicos Activos")
                st.caption("Marque los hallazgos de riesgo identificados en la evaluación actual:")
                
                cardio_angina = st.checkbox("🔹 Angina inestable o de reciente comienzo", key="mod4_angina")
                cardio_disnea = st.checkbox("🔹 Disnea de causa cardíaca no filiada / Ortopnea", key="mod4_disnea")
                cardio_palpitaciones = st.checkbox("🔹 Palpitaciones clínicas, síncope o arritmia sintomática", key="mod4_palpitaciones")
                cardio_edema = st.checkbox("🔹 Edema maleolar bilateral reciente o signos de congestión", key="mod4_edema")
                cardio_soplo = st.checkbox("🔹 Soplo cardíaco patológico relevante (Ej: Sugestivo de Estenosis Aórtica)", key="mod4_soplo")
                
                st.divider()
                
                # --- 3. PARÁMETROS ELECTRO Y ECOCARDIOGRÁFICOS ---
                st.markdown("#### 📊 Hallazgos en Exámenes Complementarios")
                c_card3, c_card4 = st.columns(2)
                
                ecg_hallazgo = c_card3.selectbox(
                    "Hallazgo en Electrocardiograma (ECG)",
                    [
                        "Ritmo Sinusal Normal",
                        "Fibrilación Auricular / Flutter / Extrasistolia frecuente",
                        "Bloqueo de Rama (Izquierda / Derecha / Bifascicular)",
                        "Bloqueo AV (Primer, Segundo o Tercer grado)",
                        "Trastornos de la Repolarización / Isquemia subendocárdica",
                        "Hipertrofia Ventricular / Signos de sobrecarga",
                        "No disponible / No solicitado"
                    ],
                    key="mod4_ecg"
                )
                
                fevi_disponible = c_card4.checkbox("¿Cuenta con reporte de Ecocardiograma?", key="mod4_check_fevi")
                
                if fevi_disponible:
                    fevi_valor = c_card4.number_input(
                        "Fracción de Eyección (FEVI %)",
                        min_value=10.0, max_value=85.0, value=60.0, step=1.0,
                        key="mod4_fevi_val"
                    )

                # --- PROCESAMIENTO SILENCIOSO DE RIESGO DE LEE (RCRI) ---
                factor_cirugia_riesgo = 1 if (riesgo_cx and "Alto" in riesgo_cx) else 0
                factor_cardiopatia_isq = 1 if (not sin_antecedentes and any("Isquémica" in p or "IAM" in p for p in antecedentes_seleccionados)) or cardio_angina else 0
                factor_insuf_cardiaca = 1 if (not sin_antecedentes and "Insuficiencia Cardíaca" in lista_patologias) or cardio_edema or cardio_disnea else 0
                factor_acv = 1 if (not sin_antecedentes and any("ACV" in p or "Isquemia" in p for p in antecedentes_seleccionados)) else 0
                factor_insulina = 1 if (not sin_antecedentes and "Insulina" in medicacion_actual) else 0
                
                # Nota: El factor_creatinina se sumará en el módulo de laboratorios posteriormente
                score_lee = factor_cirugia_riesgo + factor_cardiopatia_isq + factor_insuf_cardiaca + factor_acv + factor_insulina
# ---------------------------------------------------------
        # MÓDULO 5: PRUEBAS DE LABORATORIO Y COAGULACIÓN (SINCRO ESCALAS)
        # ---------------------------------------------------------
        with st.expander("5. Pruebas de Laboratorio y Coagulación", expanded=True):
            
            # 1. ESTA LÍNEA DEBE IR PRIMERO SIEMPRE (Crea la variable para el sistema)
            sin_laboratorios = st.checkbox("✅ No dispone o no requiere exámenes de laboratorio (Paciente sano)", value=True, key="mod5_sin_labs")

            # 2. VALORES BASALES DE SEGURIDAD (Garantizan estabilidad en el backend)
            hb_val = 14.0
            hto_val = 42.0
            plaquetas_val = 250000
            urea_val = 30.0
            creatinina_val = 0.8
            albumina_serica = 3.5
            sodio_serico = 140.0
            potasio_serico = 4.0
            cloro_serico = 102.0
            bili_total = 1.0
            tp_val = 12.0
            ttpa_val = 30.0
            inr_val = 1.0
            tiene_gasometria = False

            # Detectamos el antecedente del Módulo 2
            cirrosis_activa = "Cirrosis Hepática" in antecedentes_seleccionados

            # 3. CONTROL DE RENDERIZADO INTERACTIVO (Ahora sí leerá las variables sin NameError)
            if not sin_laboratorios or cirrosis_activa:
                
                # --- 1. HEMATOLOGÍA COMPLETA (Siempre visible si se piden laboratorios) ---
                st.markdown("#### 🩸 Hemograma")
                c_lab1, c_lab2, c_lab3 = st.columns(3)
                hb_val = c_lab1.number_input("Hemoglobina (g/dL)", min_value=3.0, max_value=25.0, value=14.0, step=0.1, key="mod5_hb")
                hto_val = c_lab2.number_input("Hematocrito (%)", min_value=10.0, max_value=75.0, value=42.0, step=1.0, key="mod5_hto")
                plaquetas_val = c_lab3.number_input("Plaquetas (u/µL)", min_value=10000, max_value=1000000, value=250000, step=5000, key="mod5_plaq")
                
                st.divider()

                # --- 2. APARTADO GENERAL: FUNCIÓN RENAL Y PROTEÍNAS ---
                ver_renal = st.checkbox("🧪 Incluir Función Renal y Proteínas", value=True, key="chk_grupo_renal")
                
                if ver_renal or cirrosis_activa:
                    st.markdown("#### 💾 Función Renal y Proteínas")
                    c_ren1, c_ren2, c_ren3 = st.columns(3)
                    urea_val = c_ren1.number_input("Urea (mg/dL)", min_value=5.0, max_value=300.0, value=30.0, step=1.0, key="mod5_urea")
                    creatinina_val = c_ren2.number_input("Creatinina Sérica (mg/dL)", min_value=0.1, max_value=20.0, value=0.8, step=0.1, key="mod5_creat")
                    albumina_serica = c_ren3.number_input("Albúmina Sérica (g/dL)", min_value=1.0, max_value=6.0, value=3.5, step=0.1, key="mod5_albu")
                    st.divider()

                # --- 3. APARTADO GENERAL: ELECTRÓLITOS SÉRICOS ---
                ver_electrolitos = st.checkbox("🧪 Incluir Panel de Electrólitos Séricos", value=False, key="chk_grupo_elytes")
                
                if ver_electrolitos:
                    st.markdown("#### ⚡ Electrólitos Séricos")
                    c_el1, c_el2, c_el3 = st.columns(3)
                    sodio_serico = c_el1.number_input("Sodio Sérico (Na+ mEq/L)", min_value=100.0, max_value=180.0, value=140.0, step=1.0, key="mod5_na_serico")
                    potasio_serico = c_el2.number_input("Potasio Sérico (K+ mEq/L)", min_value=1.5, max_value=8.0, value=4.0, step=0.1, key="mod5_k_serico")
                    cloro_serico = c_el3.number_input("Cloro Sérico (Cl- mEq/L)", min_value=70.0, max_value=130.0, value=102.0, step=1.0, key="mod5_cl_serico")
                    st.divider()

                # --- 4. PERFIL HEPÁTICO ESPECÍFICO (Solo Bilirrubina por Cirrosis) ---
                if cirrosis_activa:
                    st.markdown("#### 🧬 Perfil Hepático Crítico")
                    bili_total = st.number_input("Bilirrubina Total (mg/dL)", min_value=0.1, max_value=50.0, value=1.0, step=0.1, key="mod5_bili")
                    st.divider()

                # --- 5. APARTADO GENERAL: TIEMPOS DE COAGULACIÓN ---
                # Se muestra si el usuario lo marca O si el paciente es cirrótico de forma mandatoria
                ver_coagulacion = st.checkbox("🫀 Incluir Tiempos de Coagulación", value=True, key="chk_grupo_coag")
                
                if ver_coagulacion or cirrosis_activa:
                    st.markdown("#### ⏱️ Coagulación")
                    c_lab6, c_lab7, c_lab8 = st.columns(3)
                    tp_val = c_lab6.number_input("Tiempo de Protrombina TP (seg)", min_value=5.0, max_value=60.0, value=12.0, step=0.1, key="mod5_tp")
                    ttpa_val = c_lab7.number_input("TTPa (seg)", min_value=10.0, max_value=120.0, value=30.0, step=0.1, key="mod5_ttpa")
                    inr_val = c_lab8.number_input("INR", min_value=0.5, max_value=10.0, value=1.0, step=0.1, key="mod5_inr")
                    st.divider()

                # --- 6. GASOMETRÍA ARTERIAL INTEGRAL Y CRÍTICA ---
                tiene_gasometria = st.checkbox("🫁 ¿Cuenta con reporte de Gasometría Arterial?", value=False, key="mod5_check_gases")
                
                if tiene_gasometria:
                    st.markdown("#### 🩺 Gasometría Arterial Ampliada")
                    
                    c_gas1, c_gas2, c_gas3 = st.columns(3)
                    ph_val = c_gas1.number_input("pH Arterial", min_value=6.5, max_value=8.0, value=7.40, step=0.01, key="mod5_ph")
                    paco2_val = c_gas2.number_input("PaCO2 (mmHg)", min_value=10.0, max_value=150.0, value=40.0, step=1.0, key="mod5_paco2")
                    hco3_val = c_gas3.number_input("HCO3- Actual (mEq/L)", min_value=5.0, max_value=60.0, value=24.0, step=0.1, key="mod5_hco3")
                    
                    c_gas4, c_gas5, c_gas6 = st.columns(3)
                    pao2_val = c_gas4.number_input("PaO2 (mmHg)", min_value=30.0, max_value=600.0, value=90.0, step=1.0, key="mod5_pao2")
                    fio2_val = c_gas5.number_input("FiO2 Suministrada (%)", min_value=21.0, max_value=100.0, value=21.0, step=1.0, key="mod5_fio2")
                    be_val = c_gas6.number_input("Exceso de Base (BE)", min_value=-30.0, max_value=30.0, value=0.0, step=0.1, key="mod5_be")
                    
                    c_gas7, c_gas8, c_gas9 = st.columns(3)
                    na_gas = c_gas7.number_input("Sodio en Gasometría (Na+)", min_value=100.0, max_value=180.0, value=140.0, step=1.0, key="mod5_na_gas")
                    cl_gas = c_gas8.number_input("Cloro en Gasometría (Cl-)", min_value=70.0, max_value=130.0, value=102.0, step=1.0, key="mod5_cl_gas")
                    lactato_val = c_gas9.number_input("Lactato Sérico (mmol/L)", min_value=0.0, max_value=25.0, value=1.0, step=0.1, key="mod5_lactato")
                    
                    st.caption("📊 Índices Derivados en Tiempo Real:")
                    pafi = pao2_val / (fio2_val / 100.0)
                    anion_gap = na_gas - (cl_gas + hco3_val)
                    
                    gc_col1, gc_col2 = st.columns(2)
                    gc_col1.metric("Índice de Kirby (PaO2/FiO2)", f"{pafi:.1f} mmHg", help="Normal > 300.")
                    gc_col2.metric("Anion Gap (Brecha Aniónica)", f"{anion_gap:.1f} mEq/L", help="Normal entre 8 y 12 mEq/L.")
                    
                    st.divider()
# ---------------------------------------------------------
        # MÓDULO 6: RIESGO TROMBOEMBÓLICO Y EMETOGÉNICO (CÓDIGO DEPURADO)
        # ---------------------------------------------------------
        with st.expander("6. Riesgo Tromboembólico (Caprini) y Emetogénico (Apfel)", expanded=True):
            
            # --- 1. ESCALA DE APFEL (SÓLO VARIABLES NO CONCATENADAS) ---
            st.markdown("#### 🤢 Riesgo de Náuseas y Vómitos Postoperatorios (Escala de Apfel)")
            st.caption("Marque los factores clínicos específicos del entorno quirúrgico:")
            
            apfel_historia = st.checkbox("🔸 Antecedente personal de NVPO o cinetosis (mareo por movimiento)", key="mod6_apfel_hist")
            apfel_opioides = st.checkbox("🔸 Previsión de uso de opioides potentes en el postoperatorio", key="mod6_apfel_op")

            # --- 2. ESCALA DE CAPRINI (SÓLO VARIABLES NO CONCATENADAS) ---
            st.divider()
            st.markdown("#### 🧦 Prevención Cardiovascular: Riesgo Tromboembólico (Caprini)")
            st.caption("Seleccione únicamente las condiciones particulares que no han sido registradas previamente:")

            # Categoría A: Médicos Generales Restantes
            caprini_clinicos = st.multiselect(
                "Factores Médicos Particulares",
                options=[
                    "Venas varicosas superficiales sintomáticas (+1)",
                    "Uso actual de anticonceptivos orales o terapia de reemplazo hormonal (+1)",
                    "Sepsis o Infección médica aguda activa (< 1 mes) (+1)",
                    "Cáncer activo o antecedente de malignidad sólida/hematológica (+2)"
                ],
                key="mod6_cap_clin"
            )

            # Categoría B: Quirúrgicos y de Inmovilidad Restantes
            caprini_quirurgicos = st.multiselect(
                "Factores de Inmovilización y Procedimientos Especiales",
                options=[
                    "Cirugía artroscópica (+2)",
                    "Inmovilización actual con yeso, férula o tracción (+2)",
                    "Acceso venoso central permanente o catéter de diálisis (+2)",
                    "Paciente encamado en reposo absoluto prolongado (> 72 horas) (+2)"
                ],
                key="mod6_cap_cx"
            )

 # Categoría C: Trombosis de Alto Riesgo y Trombofilias
            caprini_altoriesgo = st.multiselect(
                "Antecedentes de Trombofilias y Eventos Graves",
                options=[
                    "Antecedente personal de TVP o Tromboembolismo Pulmonar (TEP) (+3)",
                    "Historia familiar directa de trombosis u oclusión vascular (+3)",
                    "Trombofilia congénita o adquirida confirmada por laboratorio (+3)",
                    "ACV / Ictus isquémico reciente (< 1 mes) (+5)",
                    "Fractura de cadera, pelvis o extremidad inferior (< 1 mes) (+5)",
                    "Artroplastia electiva programada de cadera o rodilla (+5)",
                    "Lesión medular aguda con paraplejía o cuadriplejía (< 1 mes) (+5)"
                ],
                key="mod6_cap_alto"
            )

            # =========================================================
            # PROCESAMIENTO AUTOMÁTICO SINCRO-TOTAL EN SEGUNDO PLANO
            # =========================================================
            
            # --- MOTOR DE APFEL AUTOMATIZADO ---
            pts_apfel = sum([apfel_historia, apfel_opioides])
            if 'sexo' in locals() and sexo == "Femenino": 
                pts_apfel += 1
            if 'sin_habitos' in locals() and (sin_habitos or not hab_cigarrillo): 
                pts_apfel += 1

# --- MOTOR DE CAPRINI AUTOMATIZADO ---
            score_caprini = 0
            
            # (Aquí van tus inferencias de Edad, IMC, etc., si ya las tienes)

            # SINCRO INTELIGENTE DE FRACTURA AGUDA DESDE EL MÓDULO 1
            if 'tipo_fractura_cx' in locals() and tipo_fractura_cx != "No aplica":
                if "Riesgo Caprini Extremo" in tipo_fractura_cx:
                    score_caprini += 5  # Suma 5 puntos si es Cadera, Pelvis o Miembro Inferior
                else:
                    score_caprini += 2  # Suma 2 puntos si es Miembro Superior u otra región
            
            # 1. Inferencia automática por Edad (Módulo 1)
            if 'edad' in locals():
                if 41 <= edad <= 60: score_caprini += 1
                elif 61 <= edad <= 74: score_caprini += 2
                elif edad >= 75: score_caprini += 3
                
            # 2. Inferencia automática por IMC (Módulo 1)
            if 'imc' in locals() and imc > 25.0:
                score_caprini += 1
                
            # 3. Inferencia automática por Embarazo (Módulo 1)
            if 'es_obstetrico' in locals() and es_obstetrico:
                score_caprini += 1
                
            # 4. Inferencia automática por Complejidad Quirúrgica (Módulo 1)
            if 'riesgo_cx' in locals():
                if "Alto" in riesgo_cx or "Moderado" in riesgo_cx:
                    score_caprini += 2  # Cirugía mayor (> 45 min)
                else:
                    score_caprini += 1  # Cirugía menor
                    
            # 5. Inferencia automática por Edema Clínico (Módulo 4)
            if 'cardio_edema' in locals() and cardio_edema:
                score_caprini += 1

            # 6. Sumatoria de los multiselects manuales depurados
            for f in caprini_clinicos:
                if "(+1)" in f: score_caprini += 1
                elif "(+2)" in f: score_caprini += 2
                    
            for f in caprini_quirurgicos:
                if "(+2)" in f: score_caprini += 2
                    
            for f in caprini_altoriesgo:
                if "(+3)" in f: score_caprini += 3
                elif "(+5)" in f: score_caprini += 5
