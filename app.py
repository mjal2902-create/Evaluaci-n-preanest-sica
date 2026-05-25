import streamlit as st
import math

st.set_page_config(layout="wide", page_title="Asistente Anestésico", page_icon="🩺")

# --- TÍTULO PRINCIPAL ---
st.title("🩺 Asistente de Evaluación Anestésica")
st.caption("Desarrollado para optimización clínica intraoperatoria y seguridad del paciente.")
st.caption("**Autor:** Dr. Marcos Aviles")
st.markdown("---")

# =============================================================================
# 1. INICIALIZACIÓN UNIFICADA DE LAS COLUMNAS PRINCIPALES
# =============================================================================
col_izquierda, col_derecha = st.columns([1.3, 1])

# =============================================================================
# COLUMNA IZQUIERDA: MÓDULOS DE EVALUACIÓN CLÍNICA (ENTRADA DE DATOS)
# =============================================================================
with col_izquierda:
    st.header("📋 Datos de Entrada")
    # ---------------------------------------------------------
    # GATEKEEPER: REGISTRO INSTITUCIONAL (Bloqueo Estricto)
    # ---------------------------------------------------------
    st.markdown("### 🏥 Registro Institucional")
    
    tipo_institucion = st.selectbox(
        "Clasificación Institucional",
        ["👈 Seleccione el Sector...", "Red Pública (MSP / IESS)", "Sector Privado / JBG", "Otro Centro / Práctica Privada"],
        key="mod_inst_tipo"
    )
    
    hospital_final = ""
    hospital_valido = False
    
    if tipo_institucion == "Red Pública (MSP / IESS)":
        lista_publicos = [
            "👈 Seleccione un hospital público...", 
            "Hospital de Especialidades Abel Gilbert Pontón (MSP)",
            "Hospital General del Norte de Guayaquil Los Ceibos (IESS)",
            "Hospital de Especialidades Teodoro Maldonado Carbo (IESS)",
            "Hospital Generl Gusmo Sur (MSP)",
            "Hospital Generl DR. Enrique Ortega Moreira (MSP)",
            "Hospital General Monte Sinaí (MSP)",
            "Hospital Universitario de Guayaquil (MSP)",
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
            
    elif tipo_institucion == "Sector Privado / JBG":
        lista_privados = [
            "👈 Seleccione un centro...", 
            "Hospital de Niños Dr. Roberto Gilbert Elizalde (JBG)",
            "Hospital Gineco-Obstétrico Alfredo G. Paulson (JBG)",
            "Omni Hospital",
            "Hospital Clínica Kennedy (Policentro / Alborada / Samborondón)",
            "Hospital Alcívar",
            "Interhospital",
            "Hospital Clínica Panamericana",
            "Otro Centro Privado (Especificar)"
        ]
        hosp_sel = st.selectbox("📍 Seleccione el Centro Privado / JBG", lista_privados, key="mod_inst_priv")
        
        # Lógica estricta de validación
        if hosp_sel == "👈 Seleccione un centro...":
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
    

    # --- APLICACIÓN DEL CANDADO DE SEGURIDAD ---
    if not hospital_valido:
        st.info("🔒 Por favor, complete la selección de la institución arriba para desbloquear la evaluación.")
        
    else: 
        st.success(f"✅ Centro registrado: **{hospital_final}**")
        st.divider()
        
        # ---------------------------------------------------------
        # MÓDULO 1: DATOS DEMOGRÁFICOS Y QUIRÚRGICOS
        # ---------------------------------------------------------
        with st.expander("1. Datos Demográficos y Contexto Quirúrgico", expanded=True):
            st.divider() 
            c_demo1, c_demo2, c_demo3 = st.columns(3)
            sexo = c_demo1.radio("Sexo", ["Masculino", "Femenino"], key="mod1_sexo")
            edad_default = 30 if sexo == "Femenino" else 50
            edad = c_demo2.number_input("Edad (años)", min_value=0, max_value=120, value=edad_default, key="mod1_edad")
            grupo_sangre = c_demo3.selectbox("Grupo y Rh", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-", "Desconocido"], key="mod1_gs")

            # Fila 2: Antropometría (Optimizado a 2 columnas, sin visualización de IMC)
            c_ant1, c_ant2 = st.columns(2)
            peso_real = c_ant1.number_input("Peso Real (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1, key="mod1_peso")
            talla_cm = c_ant2.number_input("Talla (cm)", min_value=30.0, max_value=250.0, value=165.0, step=1.0, key="mod1_talla")
            
            # --- PROCESAMIENTO SILENCIOSO DEL IMC ---
            # Se calcula bajo el hood para alimentar el Score de Caprini y el Monitor Derecho
            imc = 0.0
            cat_imc = "No calculado"
            if talla_cm > 0:
                imc = peso_real / ((talla_cm / 100) ** 2)
                if imc < 18.5: cat_imc = "Bajo Peso ⚠️"
                elif imc < 25.0: cat_imc = "Normal ✅"
                elif imc < 30.0: cat_imc = "Sobrepeso ⚠️"
                else: cat_imc = "Obesidad 🚨"
            
            st.divider()
            
# Fila 3: Contexto Quirúrgico Base
            st.markdown("**Contexto Quirúrgico y Clasificación**")
            
            # Lógica inteligente: Casilla obstétrica solo en mujeres en edad reproductiva o mayor
            es_obstetrico = False
            if sexo == "Femenino" and edad >= 10:
                es_obstetrico = st.checkbox("🤰 Paciente Obstétrica (Cambia diagnósticos y procedimientos)", key="mod1_obstetrico")

            # Fila A: Carácter y ASA (2 columnas amplias para no apiñar el texto)
            c_cx1, c_asa = st.columns(2)
            caracter_cx = c_cx1.selectbox("Carácter de la Intervención", ["Electiva", "Urgencia", "Emergencia"], key="mod1_caracter")
            
            asa_ps = c_asa.selectbox("Clasificación ASA", [
                "ASA I: Paciente sano normal",
                "ASA II: Enfermedad sistémica leve",
                "ASA III: Enfermedad sistémica grave",
                "ASA IV: Enf. sistémica grave con amenaza vital",
                "ASA V: Paciente moribundo",
                "ASA VI: Muerte cerebral (Donante)"
            ], key="mod1_asa")
            
            # Fila B: Riesgo Quirúrgico (A todo lo ancho para que el texto largo encaje perfecto)
            riesgo_cx = st.selectbox("Riesgo Quirúrgico (AHA/ACC)", [
                "Bajo (<1%) - Ej: Superficial, Endoscópica, Catarata", 
                "Intermedio (1-5%) - Ej: Intraperitoneal, Ortopédica mayor", 
                "Alto (>5%) - Ej: Vascular mayor, Torácica, Aórtica"
            ], key="mod1_riesgo")
            
            st.divider()
            
            # Fila 4: Diagnóstico y Procedimiento Dinámico
            c_cx3, c_cx4 = st.columns(2)
            
            if es_obstetrico:
                lista_diagnosticos = ["Embarazo a Término", "Trabajo de Parto Fase Activa", "Pre-eclampsia / Eclampsia", "Sufrimiento Fetal Agudo", "Ruptura Prematura de Membranas", "Placenta Previa", "Embarazo Ectópico", "Aborto Incompleto", "Otro (Especificar)"]
                lista_procedimientos = ["Cesárea Segmentaria", "Legrado Uterino Instrumental (LUI)", "Aspiración Manual Endouterina (AMEU)", "Cerclaje Cervical", "Laparotomía Exploradora", "Salpingectomía", "Otro (Especificar)"]
            elif edad < 18:
                if sexo == "Masculino":
                    lista_diagnosticos = ["Fimosis / Parafimosis", "Criptorquidia", "Apendicitis Aguda", "Hernia Inguinal", "Hipertrofia Amigdalina", "Fractura / Traumatismo", "Otro (Especificar)"]
                    lista_procedimientos = ["Circuncisión", "Orquidopexia", "Apendicectomía", "Hernioplastia", "Amigdalectomía", "Reducción y Fijación (RAFI)", "Otro (Especificar)"]
                else:
                    lista_diagnosticos = ["Apendicitis Aguda", "Hernia Umbilical / Inguinal", "Hipertrofia Amigdalina", "Cuerpo Extraño", "Fractura / Traumatismo", "Otro (Especificar)"]
                    lista_procedimientos = ["Apendicectomía", "Hernioplastia", "Amigdalectomía", "Extracción de Cuerpo Extraño", "Reducción y Fijación (RAFI)", "Otro (Especificar)"]
            elif edad >= 60:
                if sexo == "Masculino":
                    lista_diagnosticos = ["Hipertrofia Prostática Benigna (HPB)", "Hernia Inguinal", "Artrosis Severa (Cadera/Rodilla)", "Cataratas", "Neoplasia (Urológica/Digestiva)", "Colelitiasis", "Otro (Especificar)"]
                    lista_procedimientos = ["Resección Transuretral de Próstata (RTUP)", "Hernioplastia", "Artroplastia (Reemplazo Articular)", "Facoemulsificación", "Resección Oncológica", "Colecistectomía Laparoscópica", "Otro (Especificar)"]
                else:
                    lista_diagnosticos = ["Fractura de Cadera / Fémur", "Colelitiasis / Colecistitis", "Artrosis Severa (Cadera/Rodilla)", "Prolapso de Órganos Pélvicos", "Cataratas", "Neoplasia", "Otro (Especificar)"]
                    lista_procedimientos = ["Osteosíntesis / Artroplastia", "Colecistectomía Laparoscópica", "Reemplazo Articular", "Colporrafia / Histerectomía Vaginal", "Facoemulsificación", "Resección Oncológica", "Otro (Especificar)"]
            else:
                if sexo == "Masculino":
                    lista_diagnosticos = ["Colelitiasis / Colecistitis", "Hernia Inguinal / Umbilical", "Apendicitis Aguda", "Fractura / Traumatismo", "Enfermedad Hemorroidal", "Varicocele", "Otro (Especificar)"]
                    lista_procedimientos = ["Colecistectomía Laparoscópica", "Hernioplastia", "Apendicectomía", "Reducción Abierta y Fijación Interna (RAFI)", "Hemorroidectomía", "Varicocelectomía", "Otro (Especificar)"]
                else:
                    lista_diagnosticos = ["Colelitiasis / Colecistitis", "Miomatosis Uterina", "Quiste Ovárico", "Apendicitis Aguda", "Patología Mamaria", "Hernia Umbilical", "Otro (Especificar)"]
                    lista_procedimientos = ["Colecistectomía Laparoscópica", "Histerectomía (Lap/Abierta)", "Quistectomía / Ooforectomía", "Apendicectomía", "Mastectomía / Resección Local", "Hernioplastia", "Otro (Especificar)"]

            diag_base = c_cx3.selectbox("Diagnóstico Principal", lista_diagnosticos, key="mod1_diag_base")
            diagnostico_final = c_cx3.text_input("Especifique el diagnóstico", key="mod1_diag_txt") if diag_base == "Otro (Especificar)" else diag_base
            
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
                    ], key="mod1_tipo_fractura"
                )
            proc_base = c_cx4.selectbox("Procedimiento Propuesto", lista_procedimientos, key="mod1_proc_base")
            procedimiento_final = c_cx4.text_input("Especifique el procedimiento", key="mod1_proc_txt") if proc_base == "Otro (Especificar)" else proc_base
                
            tipo_anestesia = st.selectbox("Técnica Anestésica Propuesta", ["Anestesia General (Balanceada / TIVA)", "Anestesia Regional (Neuroeje: Raquídea / Epidural)", "Bloqueo de Nervio Periférico + Sedación", "Cuidado Anestésico Monitorizado (MAC) / Sedación", "Anestesia Local"], key="mod1_tecnica")

        # ---------------------------------------------------------
        # MÓDULO 2: SEGURIDAD, ALERGIAS Y ANTECEDENTES
        # ---------------------------------------------------------
        with st.expander("2. Seguridad, Alergias y Antecedentes Patológicos", expanded=True):
            st.markdown("#### 🚨 Alergias y Sensibilidades")
            sin_alergias = st.checkbox("✅ No refiere alergias", value=True, key="mod2_sin_alergias")
            
            alergias_med = []; otras_alergias_med_txt = ""; alergias_alim = []; otras_alergias_ali_txt = ""
            if not sin_alergias:
                c_al1, c_al2 = st.columns(2)
                alergias_med = c_al1.multiselect("Farmacológicas / Sustancias", options=["Penicilinas / Betalactámicos", "AINEs", "Látex", "Opioides", "Relajantes Musculares", "Anestésicos Locales", "Medios de Contraste", "Otros (Especificar)"], key="mod2_al_med")
                if "Otros (Especificar)" in alergias_med: otras_alergias_med_txt = c_al1.text_input("💊 Especifique otras alergias farmacológicas:", key="mod2_al_med_txt")
                alergias_alim = c_al2.multiselect("Alimentarias", options=["Huevo", "Soya", "Mariscos / Yodo", "Frutos secos", "Lácteos", "Gluten", "Otros (Especificar)"], key="mod2_al_ali")
                if "Otros (Especificar)" in alergias_alim: otras_alergias_ali_txt = c_al2.text_input("🥚 Especifique otras alergias alimentarias:", key="mod2_al_ali_txt")

            st.divider()
            st.markdown("#### 📋 Antecedentes Patológicos y Medicación Habitual")
            sin_antecedentes = st.checkbox("✅ No refiere antecedentes patológicos ni medicación de uso continuo", value=True, key="mod2_sin_antecedentes")
            
            antecedentes_seleccionados = ["Ninguno"]; otros_antecedentes_txt = ""; medicacion_actual = ["Ninguno"]; notas_medicacion_txt = ""
            tipo_fractura_app = "No aplica"; child_ascitis = "Ausente"; child_encefalo = "Ausente"
            
            if not sin_antecedentes:
                if es_obstetrico: lista_patologias = ["Ninguno", "Trastornos Hipertensivos (Preeclampsia/HTA)", "Diabetes Gestacional", "Anemia", "Hipotiroidismo", "Asma", "Cardiopatía", "Obesidad", "Otros (Especificar)"]
                elif edad < 18: lista_patologias = ["Ninguno", "Asma / Hiperreactividad Bronquial", "Cardiopatía Congénita", "Epilepsia / Convulsiones", "Prematuridad / Ingreso a UCIN", "Trastorno Hematológico", "Atopia / Rinitis", "Otros (Especificar)"]
                elif edad >= 60:
                    lista_patologias = ["Ninguno", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Cardiopatía Isquémica (IAM/Angina)", "EPOC / Fumador", "Hipertrofia Prostática Benigna", "Arritmia (FA)", "Enfermedad Renal Crónica (ERC)", "ACV / Isquemia Transitoria", "Otros (Especificar)"] if sexo == "Masculino" else ["Ninguno", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Hipotiroidismo", "Osteoporosis / Osteoartritis", "Insuficiencia Cardíaca", "Arritmia (FA)", "Enfermedad Renal Crónica (ERC)", "ACV", "Otros (Especificar)"]
                else:
                    lista_patologias = ["Ninguno", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Dislipidemia", "Asma / EPOC", "Reflujo Gastroesofágico (ERGE)", "Hepatopatía", "Trastorno Psiquiátrico", "Otros (Especificar)"] if sexo == "Masculino" else ["Ninguno", "Hipotiroidismo", "Hipertensión Arterial (HTA)", "Diabetes Mellitus Tipo 2", "Asma", "Enfermedad Autoinmune (LES/AR)", "Migraña", "Anemia", "Trastorno Psiquiátrico", "Otros (Especificar)"]

                if "Otros (Especificar)" in lista_patologias:
                    idx = lista_patologias.index("Otros (Especificar)")
                    lista_patologias.insert(idx, "Fractura / Traumatismo Mayor")
                    lista_patologias.insert(idx, "Cirrosis Hepática")

                lista_medicamentos = ["Antihipertensivos (IECA/ARA II/BCC)", "Beta-bloqueadores", "Diuréticos", "Metformina / Hipoglucemiantes orales", "Insulina", "Antiagregantes (Aspirina/Clopidogrel)", "Anticoagulantes (Warfarina/DOACs)", "Levotiroxina", "Inhaladores (SABA/Corticoides)", "Anticonvulsivantes", "Ninguno", "Otros (Especificar)"]
                
                c_unif1, c_unif2 = st.columns(2)
                antecedentes_seleccionados = c_unif1.multiselect("Patologías Clínicas (APP)", options=lista_patologias, key="mod2_antecedentes")

                if "Cirrosis Hepática" in antecedentes_seleccionados:
                    st.caption("🟡 Evaluación de Severidad Hepática (Child-Pugh):")
                    c_hep1, c_hep2 = st.columns(2)
                    child_ascitis = c_hep1.selectbox("Ascitis", ["Ausente", "Leve / Moderada (Controlada)", "Tensa / Grave (Refractaria)"], key="mod2_ascitis")
                    child_encefalo = c_hep2.selectbox("Encefalopatía", ["Ausente", "Grado I - II (Leve)", "Grado III - IV (Grave)"], key="mod2_encefalo")
                
                if "Fractura / Traumatismo Mayor" in antecedentes_seleccionados:
                    tipo_fractura_app = c_unif1.selectbox("🦴 Tipo / Localización de la Fractura", ["Fractura de Cadera (Fémur Proximal) [Riesgo Caprini Alto]", "Fractura de Pelvis o Acetábulo [Riesgo Caprini Alto]", "Fractura de Miembro Inferior (Diáfisis de Fémur, Tibia, Peroné) [Riesgo Caprini Alto]", "Fractura de Miembro Superior (Húmero, Radio, Cúbito, Clavícula)", "Fractura Vertebral / Columna (Torácica / Lumbar)", "Fractura Craneofacial / Mandibular"], key="mod2_tipo_fractura")
                
                if "Otros (Especificar)" in antecedentes_seleccionados: otros_antecedentes_txt = c_unif1.text_input("🔍 Especifique otros antecedentes:", key="mod2_ant_otros_txt")
                medicacion_actual = c_unif2.multiselect("Fármacos de Uso Continuo", options=lista_medicamentos, key="mod2_medicacion")
                if "Otros (Especificar)" in medicacion_actual: notas_medicacion_txt = c_unif2.text_input("📝 Especifique dosis o frecuencias:", key="mod2_med_notas_txt")

            st.divider()
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
                if hab_drogas: txt_drogas = st.text_input("Especifique la sustancia:", key="mod2_txt_dro")

        # ---------------------------------------------------------
        # MÓDULO 3: VÍA AÉREA Y PREDICTORES RESPIRATORIOS
        # ---------------------------------------------------------
        with st.expander("3. Vía Aérea y Predictores de Dificultad", expanded=True):
            arne_historia = False; arne_patologia = False; mallampati = "No aplica (Pediátrico)"; dtm = "No aplica (Pediátrico)"; apertura_bucal = "No aplica (Pediátrico)"; dem = "No aplica (Pediátrico)"; cuello_cat = "No aplica (Pediátrico)"; ulbt = "No aplica (Pediátrico)"; mov_cervical_arne = "Normal: Extensión completa (> 90°)"
            vad_incisivos = False; vad_paladar = False; vad_lengua = False; vad_retrognatia = False; vmd_barba = False; vmd_edentulo = False; sb_s = False; sb_t = False; sb_o = False
            score_arne = 0; puntos_vmd = 0; puntos_stop_bang = 0

            es_pediatrico_va = edad < 18
            mostrar_va_adultos = True

            if es_pediatrico_va:
                colabora_ped = st.checkbox("👦 Paciente pediátrico colaborador (Permite examen físico con rangos indexados)", value=False, key="mod3_ped_colabora")
                if not colabora_ped:
                    mostrar_va_adultos = False
                    st.markdown("#### 👶 Evaluación de Vía Aérea Pediátrica (Lactantes / Infantes)")
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

            if mostrar_va_adultos:
                if es_pediatrico_va:
                    opciones_mallampati = ["Clase I: Visibilidad de paladar blando, úvula y pilares", "Clase II: Visibilidad de paladar blando y úvula", "Clase III: Visibilidad de paladar blando y base de la úvula", "Clase IV: Solo es visible el paladar duro"]
                    opciones_dtm = ["Clase I (Normal): > 3 dedos del propio paciente (Distancia conservada)", "Clase II (Moderada): 2 - 3 dedos del propio paciente (Acortamiento leve)", "Clase III (VAD Predictiva): < 2 dedos del propio paciente (Acortamiento severo)"]
                    opciones_ab = ["Clase I (Normal): > 2 dedos del propio paciente (Apertura conservada)", "Clase II (Moderada): 1.5 - 2 dedos del propio paciente (Limitación leve)", "Clase III (Severa): < 1.5 dedos del propio paciente (Limitación crítica)"]
                    opciones_dem = ["Clase I (Normal): Extensión esternomentoniana conservada para la edad", "Clase II (Moderada): Restricción parcial de la extensión cefálica", "Clase III (Severa): Extensión críticamente limitada / VAD predictiva"]
                    opciones_cuello = ["Normal y proporcional para la edad cronológica", "Aumentado / Cuello grueso u obeso para la edad (Riesgo obstructivo)"]
                else:
                    opciones_mallampati = ["Clase I: Visibilidad de paladar blando, úvula, fauces y pilares", "Clase II: Visibilidad de paladar blando, úvula y fauces", "Clase III: Visibilidad de paladar blando y base de la úvula", "Clase IV: Solo es visible el paladar duro"]
                    opciones_dtm = ["Clase I (> 6.5 cm): Sin dificultad predictiva", "Clase II (6.0 - 6.5 cm): Dificultad moderada", "Clase III (< 6.0 cm): VAD predictiva"]
                    opciones_ab = ["Clase I (> 3.5 cm): Normal", "Clase II (3.0 - 3.5 cm): Limitación leve", "Clase III (< 3.0 cm): Limitación severa"]
                    opciones_dem = ["Clase I (> 12.5 cm): Sin dificultad predictiva", "Clase II (11.5 - 12.5 cm): Dificultad moderada", "Clase III (< 11.5 cm): Gran dificultad / VAD predictiva"]
                    opciones_cuello = ["Menor a 35 cm (< 35 cm)", "Entre 35 y 40 cm (35 - 40 cm)", "Mayor a 40 cm (> 40 cm)"]

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
                ulbt = c_vad6.selectbox("Test de Mordida de Labio Superior (ULBT / Subluxación)", ["Clase I: Incisivos inferiores cubren la línea bermellón", "Clase II: Incisivos muerden el labio pero no cubren la línea", "Clase III: Incisivos no pueden morder el labio superior"], key="mod3_ulbt")

                mov_cervical_arne = st.selectbox("Movilidad de Cabeza y Cuello (Extensión cervical)", ["Normal: Extensión completa (> 90°)", "Limitación Moderada: Extensión parcialmente reducida (80° - 90°)", "Limitación Severa: Rigidez extrema o fijación estructural (< 80°)"], key="mod3_mov_arne")

                st.markdown("**Hallazgos Anatómicos Particulares adicionales:**")
                vad_incisivos = st.checkbox("🔹 Incisivos largos y prominentes", key="mod3_incisivos")
                vad_paladar = st.checkbox("🔹 Paladar alto / Ojival", key="mod3_paladar")
                vad_lengua = st.checkbox("🔹 Gran tamaño de lengua (Macroglosia)", key="mod3_lengua")
                vad_retrognatia = st.checkbox("🔹 Retrognatia / Micrognatia (Mentón retraído)", key="mod3_retrognatia")

                pts_historia = 10 if arne_historia else 0
                pts_patologia = 5 if arne_patologia else 0
                pts_mallampati = 0 if "Clase I" in mallampati else (1 if "Clase II" in mallampati else (2 if "Clase III" in mallampati else 5))
                pts_dtm = 0 if "Clase I" in dtm else (2 if "Clase II" in dtm else 4)
                pts_ab = 0 if "Clase I" in apertura_bucal else (2 if "Clase II" in apertura_bucal else 4)
                pts_mov = 0 if "Normal" in mov_cervical_arne else (2 if "Moderada" in mov_cervical_arne else 5)
                score_arne = pts_historia + pts_patologia + pts_mallampati + pts_dtm + pts_ab + pts_mov

                if not es_pediatrico_va:
                    st.divider()
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

            # --- SUBSECCIÓN GENERAL: RIESGO PULMONAR (ARISCAT) ---
            st.divider()
            st.markdown("#### 🫁 Evaluación Respiratoria Avanzada (ARISCAT)")
            st.caption("Complete los hallazgos clínicos para la predicción de complicaciones pulmonares postoperatorias:")
            c_aris1, c_aris2 = st.columns(2)
            with c_aris1: ariscat_enfermedad_pulmonar = st.checkbox("🔸 Patología respiratoria crónica activa (EPOC, Asma sintomática, Fibrosis)", key="mod3_ariscat_epoc")
            with c_aris2: ariscat_infeccion_reciente = st.checkbox("🔸 Infección de vías respiratorias (altas o bajas) en el último mes", key="mod3_ariscat_inf")

        # ---------------------------------------------------------
        # MÓDULO 4: EVALUACIÓN CARDIOVASCULAR Y CAPACIDAD FUNCIONAL
        # ---------------------------------------------------------
        with st.expander("4. Evaluación Cardiovascular y Capacidad Funcional", expanded=True):
            capacidad_funcional = "No aplica (Pediátrico)"; clase_nyha = "No aplica (Pediátrico)"; cardio_angina = False; cardio_disnea = False; cardio_palpitaciones = False; cardio_edema = False; cardio_soplo = False; ecg_hallazgo = "No disponible / No solicitado"; fevi_valor = 60.0; score_lee = 0
            es_pediatrico = edad < 18
            mostrar_cardio_completo = True

            if es_pediatrico:
                sin_cardiopatia_ped = st.checkbox("✅ Paciente pediátrico sin patologías cardíacas conocidas", value=True, key="mod4_ped_sano")
                if sin_cardiopatia_ped:
                    mostrar_cardio_completo = False
                    st.info("👶 Evaluación cardiológica avanzada omitida por criterio de edad (Infante sano).")
                else:
                    mostrar_cardio_completo = False
                    st.markdown("#### 👶 Evaluación Cardiovascular Pediátrica Especializada")
                    c_ped1, c_ped2 = st.columns(2)
                    clase_ross = c_ped1.selectbox("Clase Funcional Pediátrica (Escala de Ross)", ["Clase I: Asintomático", "Clase II: Taquipnea o diaforesis leve en la alimentación. Disnea de esfuerzo en niños mayores.", "Clase III: Marcada taquipnea/diaforesis al alimentarse. Tiempo de toma prolongado. Retraso del crecimiento.", "Clase IV: Síntomas de insuficiencia cardíaca congestiva en repos (retracciones, quejido)."], key="mod4_ross")
                    complejidad_cc = c_ped2.selectbox("Complejidad de la Cardiopatía Congénita (CC)", ["Leve (Bajo Riesgo): CC corregida sin shunts residuales o Estenosis Pulmonar leve.", "Moderada (Riesgo Intermedio): CC acianógena no corregida (CIV/CIA pequeñas), Fallot corregido, Coartación corregida.", "Severa (Alto Riesgo): Hipertensión Pulmonar (Eisenmenger), CC cianógenas, Ventrículo único, Miocardiopatías."], key="mod4_cc_complejidad")
                    capacidad_funcional = f"Complejidad CC: {complejidad_cc.split('(')[0].strip()}"
                    clase_nyha = f"Ross: {clase_ross.split(':')[0].strip()}"

            if mostrar_cardio_completo:
                st.markdown("#### 🏃 Capacidad Métabolica y Clase Funcional")
                c_card1, c_card2 = st.columns(2)
                capacidad_funcional = c_card1.selectbox("Capacidad Funcional (Mets)", ["Excelente (≥ 10 METs) - Ej: Deportes de alta intensidad", "Buena (4 - 10 METs) - Ej: Sube dos pisos de escaleras sin detenerse", "Limitada (< 4 METs) - Ej: Camina 1 o 2 cuadras / Trabajo doméstico ligero", "Severamente Limitada (< 1 MET) - Ej: Disnea en reposo o actividades de autocuidado"], key="mod4_mets")
                clase_nyha = c_card2.selectbox("Clasificación Funcional NYHA", ["Clase I: Sin limitación de la actividad física ordinaria", "Clase II: Limitación ligera. Confortable en reposo", "Clase III: Limitación marcada. Actividad menor a la ordinaria causa síntomas", "Clase IV: Incapacidad de realizar cualquier actividad sin malestar / Síntomas en reposo"], key="mod4_nyha")
                
                st.divider()
                st.markdown("#### 🫀 Sintomatología y Signos Clínicos Activos")
                cardio_angina = st.checkbox("🔹 Angina inestable o de reciente comienzo", key="mod4_angina")
                cardio_disnea = st.checkbox("🔹 Disnea de causa cardíaca no filiada / Ortopnea", key="mod4_disnea")
                cardio_palpitaciones = st.checkbox("🔹 Palpitaciones clínicas, síncope o arritmia sintomática", key="mod4_palpitaciones")
                cardio_edema = st.checkbox("🔹 Edema maleolar bilateral reciente o signos de congestión", key="mod4_edema")
                cardio_soplo = st.checkbox("🔹 Soplo cardíaco patológico relevante (Ej: Sugestivo de Estenosis Aórtica)", key="mod4_soplo")
                
                st.divider()
                st.markdown("#### 📊 Hallazgos en Exámenes Complementarios")
                c_card3, c_card4 = st.columns(2)
                ecg_hallazgo = c_card3.selectbox("Hallazgo en Electrocardiograma (ECG)", ["Ritmo Sinusal Normal", "Fibrilación Auricular / Flutter / Extrasistolia frecuente", "Bloqueo de Rama (Izquierda / Derecha / Bifascicular)", "Bloqueo AV (Primer, Segundo o Tercer grado)", "Trastornos de la Repolarización / Isquemia subendocárdica", "Hipertrofia Ventricular / Signos de sobrecarga", "No disponible / No solicitado"], key="mod4_ecg")
                fevi_disponible = c_card4.checkbox("¿Cuenta con reporte de Ecocardiograma?", key="mod4_check_fevi")
                if fevi_disponible: fevi_valor = c_card4.number_input("Fracción de Eyección (FEVI %)", min_value=10.0, max_value=85.0, value=60.0, step=1.0, key="mod4_fevi_val")

                factor_cirugia_riesgo = 1 if (riesgo_cx and "Alto" in riesgo_cx) else 0
                factor_cardiopatia_isq = 1 if (not sin_antecedentes and any("Isquémica" in p or "IAM" in p for p in antecedentes_seleccionados)) or cardio_angina else 0
                factor_insuf_cardiaca = 1 if (not sin_antecedentes and "Insuficiencia Cardíaca" in lista_patologias) or cardio_edema or cardio_disnea else 0
                factor_acv = 1 if (not sin_antecedentes and any("ACV" in p or "Isquemia" in p for p in antecedentes_seleccionados)) else 0
                factor_insulina = 1 if (not sin_antecedentes and "Insulina" in medicacion_actual) else 0
                score_lee = factor_cirugia_riesgo + factor_cardiopatia_isq + factor_insuf_cardiaca + factor_acv + factor_insulina

        # ---------------------------------------------------------
        # MÓDULO 5: PRUEBAS DE LABORATORIO Y COAGULACIÓN
        # ---------------------------------------------------------
        with st.expander("5. Pruebas de Laboratorio y Coagulación", expanded=True):
            sin_laboratorios = st.checkbox("✅ No dispone o no requiere exámenes de laboratorio (Paciente sano)", value=True, key="mod5_sin_labs")

            hb_val = 14.0; hto_val = 42.0; plaquetas_val = 250000; urea_val = 30.0; creatinina_val = 0.8; albumina_serica = 3.5; sodio_serico = 140.0; potasio_serico = 4.0; cloro_serico = 102.0; bili_total = 1.0; tp_val = 12.0; ttpa_val = 30.0; inr_val = 1.0; tiene_gasometria = False
            cirrosis_activa = "Cirrosis Hepática" in antecedentes_seleccionados

            if not sin_laboratorios or cirrosis_activa:
                st.markdown("#### 🩸 Hemograma")
                c_lab1, c_lab2, c_lab3 = st.columns(3)
                hb_val = c_lab1.number_input("Hemoglobina (g/dL)", min_value=3.0, max_value=25.0, value=14.0, step=0.1, key="mod5_hb")
                hto_val = c_lab2.number_input("Hematocrito (%)", min_value=10.0, max_value=75.0, value=42.0, step=1.0, key="mod5_hto")
                plaquetas_val = c_lab3.number_input("Plaquetas (u/µL)", min_value=10000, max_value=1000000, value=250000, step=5000, key="mod5_plaq")
                st.divider()

                ver_renal = st.checkbox("🧪 Incluir Función Renal y Proteínas", value=True, key="chk_grupo_renal")
                if ver_renal or cirrosis_activa:
                    st.markdown("#### 💾 Función Renal y Proteínas")
                    c_ren1, c_ren2, c_ren3 = st.columns(3)
                    urea_val = c_ren1.number_input("Urea (mg/dL)", min_value=5.0, max_value=300.0, value=30.0, step=1.0, key="mod5_urea")
                    creatinina_val = c_ren2.number_input("Creatinina Sérica (mg/dL)", min_value=0.1, max_value=20.0, value=0.8, step=0.1, key="mod5_creat")
                    albumina_serica = c_ren3.number_input("Albúmina Sérica (g/dL)", min_value=1.0, max_value=6.0, value=3.5, step=0.1, key="mod5_albu")
                    st.divider()

                ver_electrolitos = st.checkbox("🧪 Incluir Panel de Electrólitos Séricos", value=False, key="chk_grupo_elytes")
                if ver_electrolitos:
                    st.markdown("#### ⚡ Electrólitos Séricos")
                    c_el1, c_el2, c_el3 = st.columns(3)
                    sodio_serico = c_el1.number_input("Sodio Sérico (Na+ mEq/L)", min_value=100.0, max_value=180.0, value=140.0, step=1.0, key="mod5_na_serico")
                    potasio_serico = c_el2.number_input("Potasio Sérico (K+ mEq/L)", min_value=1.5, max_value=8.0, value=4.0, step=0.1, key="mod5_k_serico")
                    cloro_serico = c_el3.number_input("Cloro Sérico (Cl- mEq/L)", min_value=70.0, max_value=130.0, value=102.0, step=1.0, key="mod5_cl_serico")
                    st.divider()

                if cirrosis_activa:
                    st.markdown("#### 🧬 Perfil Hepático Crítico")
                    bili_total = st.number_input("Bilirrubina Total (mg/dL)", min_value=0.1, max_value=50.0, value=1.0, step=0.1, key="mod5_bili")
                    st.divider()

                ver_coagulacion = st.checkbox("🫀 Incluir Tiempos de Coagulación", value=True, key="chk_grupo_coag")
                if ver_coagulacion or cirrosis_activa:
                    st.markdown("#### ⏱️ Coagulación")
                    c_lab6, c_lab7, c_lab8 = st.columns(3)
                    tp_val = c_lab6.number_input("Tiempo de Protrombina TP (seg)", min_value=5.0, max_value=60.0, value=12.0, step=0.1, key="mod5_tp")
                    ttpa_val = c_lab7.number_input("TTPa (seg)", min_value=10.0, max_value=120.0, value=30.0, step=0.1, key="mod5_ttpa")
                    inr_val = c_lab8.number_input("INR", min_value=0.5, max_value=10.0, value=1.0, step=0.1, key="mod5_inr")
                    st.divider()

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
                    pafi = pao2_val / (fio2_val / 100.0) if fio2_val > 0 else 0
                    anion_gap = na_gas - (cl_gas + hco3_val)
                    
                    gc_col1, gc_col2 = st.columns(2)
                    gc_col1.metric("Índice de Kirby (PaO2/FiO2)", f"{pafi:.1f} mmHg", help="Normal > 300.")
                    gc_col2.metric("Anion Gap (Brecha Aniónica)", f"{anion_gap:.1f} mEq/L", help="Normal entre 8 y 12 mEq/L.")
                    st.divider()

        # ---------------------------------------------------------
        # MÓDULO 6: RIESGO TROMBOEMBÓLICO Y EMETOGÉNICO
        # ---------------------------------------------------------
        with st.expander("6. Riesgo Tromboembólico (Caprini) y Emetogénico (Apfel)", expanded=True):
            st.markdown("#### 🤢 Riesgo de Náuseas y Vómitos Postoperatorios (Escala de Apfel)")
            apfel_historia = st.checkbox("🔸 Antecedente personal de NVPO o cinetosis (mareo por movimiento)", key="mod6_apfel_hist")
            apfel_opioides = st.checkbox("🔸 Previsión de uso de opioides potentes en el postoperatorio", key="mod6_apfel_op")

            st.divider()
            st.markdown("#### 🧦 Prevención Cardiovascular: Riesgo Tromboembólico (Caprini)")
            caprini_clinicos = st.multiselect("Factores Médicos Particulares", options=["Venas varicosas superficiales sintomáticas (+1)", "Uso actual de anticonceptivos orales o terapia de reemplazo hormonal (+1)", "Sepsis o Infección médica aguda activa (< 1 mes) (+1)", "Cáncer activo o antecedente de malignidad sólida/hematológica (+2)"], key="mod6_cap_clin")
            caprini_quirurgicos = st.multiselect("Factores de Inmovilización y Procedimientos Especiales", options=["Cirugía artroscópica (+2)", "Inmovilización actual con yeso, férula o tracción (+2)", "Acceso venoso central permanente o catéter de diálisis (+2)", "Paciente encamado en reposo absoluto prolongado (> 72 horas) (+2)"], key="mod6_cap_cx")
            caprini_altoriesgo = st.multiselect("Antecedentes de Trombofilias y Eventos Graves", options=["Antecedente personal de TVP o Tromboembolismo Pulmonar (TEP) (+3)", "Historia familiar directa de trombosis u oclusión vascular (+3)", "Trombofilia congénita o adquirida confirmada por laboratorio (+3)", "ACV / Ictus isquémico reciente (< 1 mes) (+5)", "Fractura de cadera, pelvis o extremidad inferior (< 1 mes) (+5)", "Artroplastia electiva programada de cadera o rodilla (+5)", "Lesión medular aguda con paraplejía o cuadriplejía (< 1 mes) (+5)"], key="mod6_cap_alto")

            # --- MOTORES DE SEGUNDO PLANO ---
            pts_apfel = sum([apfel_historia, apfel_opioides])
            if 'sexo' in locals() and sexo == "Femenino": pts_apfel += 1
            if 'sin_habitos' in locals() and (sin_habitos or not hab_cigarrillo): pts_apfel += 1

            score_caprini = 0
            if 'tipo_fractura_cx' in locals() and tipo_fractura_cx != "No aplica":
                score_caprini += 5 if "Riesgo Caprini Extremo" in tipo_fractura_cx else 2
                
            if 'edad' in locals():
                if 41 <= edad <= 60: score_caprini += 1
                elif 61 <= edad <= 74: score_caprini += 2
                elif edad >= 75: score_caprini += 3
                
            if 'imc' in locals() and imc > 25.0: score_caprini += 1
            if 'es_obstetrico' in locals() and es_obstetrico: score_caprini += 1
            if 'riesgo_cx' in locals(): score_caprini += 2 if ("Alto" in riesgo_cx or "Intermedio" in riesgo_cx) else 1
            if 'cardio_edema' in locals() and cardio_edema: score_caprini += 1

            for f in caprini_clinicos: score_caprini += 1 if "(+1)" in f else 2
            for f in caprini_quirurgicos: score_caprini += 2 if "(+2)" in f else 0
            for f in caprini_altoriesgo: score_caprini += 3 if "(+3)" in f else 5

# =============================================================================
# COLUMNA DERECHA: MONITOR METABÓLICO PERIOPERATORIO ESTÁTICO (STICKY)
# =============================================================================
with col_derecha:
    if hospital_valido:
        # Inyección CSS para congelar el panel derecho y dejarlo estático con el scroll
        st.markdown("""
            <style>
                div[data-testid="stColumn"]:has(#panel-de-control-perioperatorio) > div[data-testid="stVerticalBlock"] {
                    position: -webkit-sticky;
                    position: sticky;
                    top: 1.5rem;
                    background-color: rgba(128, 128, 128, 0.05);
                    padding: 20px;
                    border-radius: 12px;
                    border: 1px solid rgba(128, 128, 128, 0.15);
                }
            </style>
        """, unsafe_allow_html=True)
            unsafe_allow_html=True
        )
            unsafe_allow_html=True
        )
            unsafe_allow_html=True
        )
        
        st.markdown("### 📊 PANEL DE CONTROL PERIOPERATORIO")
        tab1, tab2 = st.tabs(["🔢 Cálculos y Escalas", "📄 Reporte Final"])
        
        with tab1:
            # ---------------------------------------------------------------------
            # PESTAÑA 1 - SECCIÓN 1: DUPLICACIÓN COMPLETA - ANTROPOMETRÍA Y CONTEXTO
            # ---------------------------------------------------------------------
            st.subheader("🧮 Espejo Clínico y Volúmenes (Módulo 1)")
            
            # Recolección analítica y segura de variables nativas del Módulo 1
            peso_calc = peso_real if 'peso_real' in locals() else 0.0
            talla_raw = talla_cm if 'talla_cm' in locals() else 0.0
            talla_m = talla_raw / 100.0
            sexo_calc = sexo if 'sexo' in locals() else "Masculino"
            edad_calc = edad if 'edad' in locals() else 35
            gs_calc = grupo_sangre if 'grupo_sangre' in locals() else "Desconocido"
            obs_calc = es_obstetrico if 'es_obstetrico' in locals() else False
            
            caracter_calc = caracter_cx if 'caracter_cx' in locals() else "Electiva"
            riesgo_calc = riesgo_cx if 'riesgo_cx' in locals() else "No definido"
            asa_calc = asa_ps if 'asa_ps' in locals() else "No definido"
            diag_calc = diagnostico_final if 'diagnostico_final' in locals() else "No definido"
            frac_calc = tipo_fractura_cx if 'tipo_fractura_cx' in locals() else "No aplica"
            proc_calc = procedimiento_final if 'procedimiento_final' in locals() else "No definido"
            anestesia_calc = tipo_anestesia if 'tipo_anestesia' in locals() else "No definido"

            if peso_calc > 0 and talla_raw > 0:
                # --- SUBSECCIÓN A: METABOLISMO Y VOLÚMENES (BIFURCACIÓN PEDIATRÍA/ADULTO) ---
                st.markdown("##### 📏 Índices Fisiológicos y Somatometría")
                imc_control = peso_calc / (talla_m ** 2)
                bsa_calc = math.sqrt((peso_calc * talla_raw) / 3600.0)
                
                # =====================================================================
                # ENTORNO PEDIÁTRICO (< 18 AÑOS) - FÓRMULAS DE ESTIMACIÓN CLÍNICA
                # =====================================================================
                if edad_calc < 18:
                    # 1. Algoritmo de Peso y Talla esperados según la edad (Estándar APLS / OMS)
                    if edad_calc == 0:
                        peso_esperado = 7.5  # Lactante promedio estándar (6 meses)
                        talla_esperada = 65.0
                    elif 1 <= edad_calc <= 5:
                        peso_esperado = (edad_calc * 2) + 8
                        talla_esperada = (edad_calc * 6) + 77
                    elif 6 <= edad_calc <= 12:
                        peso_esperado = (edad_calc * 3) + 7
                        talla_esperada = (edad_calc * 6) + 77
                    else:  # Adolescentes (13 a 17 años)
                        # Si alcanzan la talla base adulta (>152.4 cm), Devine es metodológicamente aceptable
                        if talla_raw >= 152.4:
                            if sexo_calc == "Masculino":
                                peso_esperado = 50.0 + 2.3 * ((talla_raw / 2.54) - 60.0)
                            else:
                                peso_esperado = 45.5 + 2.3 * ((talla_raw / 2.54) - 60.0)
                        else:
                            peso_esperado = (edad_calc * 3.3) + 5  # Estimación lineal puberal alternativa
                        talla_esperada = 162.0 if sexo_calc == "Femenino" else 173.0

                    # 2. Estratificación del Estado Nutricional Pediátrico (% de Desvío Ponderal)
                    porcentaje_peso = (peso_calc / peso_esperado) * 100
                    if porcentaje_peso < 80: cat_ped = "Desnutrición Severa 🚨"
                    elif porcentaje_peso < 90: cat_ped = "Bajo Peso / Delgadez ⚠️"
                    elif porcentaje_peso <= 115: cat_ped = "Eutrófico (Normal) ✅"
                    elif porcentaje_peso <= 130: cat_ped = "Sobrepeso Pediátrico ⚠️"
                    else: cat_ped = "Obesidad Pediátrica 🚨"

                    # 3. Renderizado de Tarjetas Métricas Pediátricas
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.metric(label="BMI / IMC Pediátrico", value=f"{imc_control:.1f} kg/m²", delta=cat_ped, delta_color="normal")
                        st.metric(label="Peso Esperado p/Edad", value=f"{peso_esperado:.1f} kg", help="Calculado mediante fórmulas oficiales APLS (Advanced Pediatric Life Support).")
                    with m_col2:
                        st.metric(label="Superficie Corporal (BSA)", value=f"{bsa_calc:.2f} m²", help="Parámetro de oro en pediatría para calcular tasas de fluidoterapia de mantenimiento, reposición de pérdidas y dosificación de inductores.")
                        if edad_calc <= 12:
                            st.metric(label="Talla Esperada p/Edad", value=f"{talla_esperada:.1f} cm", help="Fórmula de crecimiento lineal teórico: (Edad en años x 6) + 77 cm.")
                        else:
                            st.metric(label="Talla Objetivo Est.", value=f"{talla_esperada:.0f} cm", help="Estatura promedio proyectada para el sexo biológico al finalizar el desarrollo.")
                            
                    if edad_calc < 2:
                        st.info("👶 **Nota clínica:** En lactantes menores de 2 años, el IMC aislado tiene baja correlación diagnóstica; se sugiere cotejar con las curvas de Peso para la Longitud de la OMS.")

                # =====================================================================
                # ENTORNO ADULTO (≥ 18 AÑOS) - FÓRMULAS CONVENCIONALES
                # =====================================================================
                else:
                    if sexo_calc == "Masculino":
                        peso_ideal = 50.0 + 2.3 * ((talla_raw / 2.54) - 60.0)
                        peso_predicho = 50.0 + 0.91 * (talla_raw - 152.4)
                    else:
                        peso_ideal = 45.5 + 2.3 * ((talla_raw / 2.54) - 60.0)
                        peso_predicho = 45.5 + 0.91 * (talla_raw - 152.4)
                    
                    if peso_ideal < 0: peso_ideal = peso_calc
                    if peso_predicho < 0: peso_predicho = peso_calc
                    
                    if peso_calc > peso_ideal:
                        peso_ajustado_20 = peso_ideal + 0.20 * (peso_calc - peso_ideal)
                        peso_ajustado_40 = peso_ideal + 0.40 * (peso_calc - peso_ideal)
                    else:
                        peso_ajustado_20 = peso_calc
                        peso_ajustado_40 = peso_calc
                    
                    # Renderizado de Tarjetas Métricas Adultos
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.metric(label="BMI / IMC Real", value=f"{imc_control:.1f} kg/m²")
                        st.metric(label="Peso Ideal (Devine)", value=f"{peso_ideal:.1f} kg")
                        st.metric(label="Peso Ajustado (20%)", value=f"{peso_ajustado_20:.1f} kg")
                    with m_col2:
                        st.metric(label="Superficie Corporal (BSA)", value=f"{bsa_calc:.2f} m²")
                        st.metric(label="Peso Predicho (ARDSNet)", value=f"{peso_predicho:.1f} kg")
                        st.metric(label="Peso Ajustado (40%)", value=f"{peso_ajustado_40:.1f} kg")
                    
                    if imc_control >= 30.0:
                        grado_obesidad = 1 if imc_control < 35 else (2 if imc_control < 40 else 3)
                        st.warning(f"⚠️ **Alerta:** Obesidad Grado {grado_obesidad}. Ajuste volúmenes y fármacos.")
                
                # --- SUBSECCIÓN B: DUPLICACIÓN DE DATOS DEMOGRÁFICOS ---
                st.markdown("##### 👤 Perfil Demográfico del Paciente")
                c_der_demo1, c_der_demo2 = st.columns(2)
                with c_der_demo1:
                    st.markdown(f"**Sexo Biológico:** {sexo_calc}")
                    st.markdown(f"**Edad Cronológica:** {edad_calc} años")
                with c_der_demo2:
                    st.markdown(f"**Grupo Sanguíneo y Rh:** {gs_calc}")
                    st.markdown(f"**Estado Obstétrico:** {'Paciente Obstétrica 🤰' if obs_calc else 'No aplica / No gestante'}")
                
                st.divider()
                
# --- SUBSECCIÓN C: DUPLICACIÓN DE CONTEXTO QUIRÚRGICO Y PLAN ---
                st.markdown("##### 🏥 Contexto Quirúrgico y Planificación")
                st.markdown(f"**Clasificación ASA:** **{asa_calc}**")
                st.markdown(f"**Carácter Quirúrgico:** *{caracter_calc}*")
                st.markdown(f"**Riesgo Quirúrgico (AHA/ACC):** *{riesgo_calc}*")
                
                # Bloque de Diagnóstico y Procedimientos destacados
                st.markdown(f"**Diagnóstico Principal:** **{diag_calc}**")
                if frac_calc != "No aplica":
                    st.markdown(f"**Detalle de Traumatología:** 🦴 *{frac_calc}*")
                st.markdown(f"**Procedimiento Quirúrgico:** **{proc_calc}**")
                st.markdown("---")
                st.success(f"💉 **Estrategia Anestésica:** **{anestesia_calc}**")
                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 2: SEGURIDAD, ALERGIAS Y ANTECEDENTES (MÓDULO 2)
                # =====================================================================
                st.subheader("🛡️ Seguridad y Antecedentes (Módulo 2)")
                
                # --- FUNCIÓN DE LIMPIEZA INTELIGENTE ---
                # Reemplaza "Otros (Especificar)" con el texto real y elimina "Ninguno" si hay más cosas
                def formatear_lista(lista_original, texto_extra):
                    lista = [x for x in lista_original if x != "Ninguno"] if len(lista_original) > 1 else list(lista_original)
                    if "Otros (Especificar)" in lista:
                        lista.remove("Otros (Especificar)")
                        if texto_extra.strip() != "":
                            lista.append(f"*{texto_extra.strip()}*")
                    return lista

                # --- LECTURA SEGURA DE VARIABLES DEL MÓDULO 2 ---
                alergias_negadas = sin_alergias if 'sin_alergias' in locals() else True
                al_med_raw = alergias_med if 'alergias_med' in locals() else []
                al_ali_raw = alergias_alim if 'alergias_alim' in locals() else []
                txt_al_med = otras_alergias_med_txt if 'otras_alergias_med_txt' in locals() else ""
                txt_al_ali = otras_alergias_ali_txt if 'otras_alergias_ali_txt' in locals() else ""
                
                app_negados = sin_antecedentes if 'sin_antecedentes' in locals() else True
                app_raw = antecedentes_seleccionados if 'antecedentes_seleccionados' in locals() else []
                txt_app = otros_antecedentes_txt if 'otros_antecedentes_txt' in locals() else ""
                
                meds_raw = medicacion_actual if 'medicacion_actual' in locals() else []
                txt_meds = notas_medicacion_txt if 'notas_medicacion_txt' in locals() else ""
                
                habitos_negados = sin_habitos if 'sin_habitos' in locals() else True
                
                # Aplicamos la limpieza a todas las listas
                al_med_list = formatear_lista(al_med_raw, txt_al_med)
                al_ali_list = formatear_lista(al_ali_raw, txt_al_ali)
                app_list = formatear_lista(app_raw, txt_app)
                meds_list = formatear_lista(meds_raw, txt_meds)
                
                # --- SUBSECCIÓN A: ALERTAS DE ALERGIAS ---
                if alergias_negadas:
                    st.success("✅ **Alergias:** Negadas por el paciente.")
                else:
                    if al_med_list:
                        st.error(f"🚨 **Alergia Farmacológica:** {', '.join(al_med_list)}")
                    if al_ali_list:
                        st.warning(f"⚠️ **Alergia Alimentaria/Ambiental:** {', '.join(al_ali_list)}")

                # --- SUBSECCIÓN B: ANTECEDENTES Y MEDICACIÓN ---
                if app_negados:
                    st.info("✅ **Historial Clínico:** Sin antecedentes patológicos ni medicación continua.")
                else:
                    if app_list and app_list != ["Ninguno"]:
                        st.markdown(f"**🩺 Patologías (APP):** {', '.join(app_list)}")
                        
                        if "Cirrosis Hepática" in app_list or "Cirrosis Hepática" in app_raw:
                            asc_calc = child_ascitis if 'child_ascitis' in locals() else "Ausente"
                            enc_calc = child_encefalo if 'child_encefalo' in locals() else "Ausente"
                            st.caption(f"🟡 *Parámetros Hepáticos activos: Ascitis {asc_calc} | Encefalopatía {enc_calc}*")
                    else:
                        st.markdown("**🩺 Patologías (APP):** Ninguna reportada.")

                    if meds_list and meds_list != ["Ninguno"]:
                        st.markdown(f"**💊 Medicación Habitual:** {', '.join(meds_list)}")
                    else:
                        st.markdown("**💊 Medicación Habitual:** Ninguna reportada.")
                        # --- SUBSECCIÓN C: HÁBITOS Y ESTILO DE VIDA ---
                if not habitos_negados:
                    habitos_activos = []
                    if 'hab_cigarrillo' in locals() and hab_cigarrillo: 
                        habitos_activos.append(f"🚬 Tabaco ({int_cigarrillo if 'int_cigarrillo' in locals() else '+'})")
                    if 'hab_alcohol' in locals() and hab_alcohol: 
                        habitos_activos.append(f"🍷 Alcohol ({int_alcohol if 'int_alcohol' in locals() else '+'})")
                    if 'hab_cafe' in locals() and hab_cafe: 
                        habitos_activos.append(f"☕ Café ({int_cafe if 'int_cafe' in locals() else '+'})")
                    if 'hab_drogas' in locals() and hab_drogas: 
                        habitos_activos.append(f"💊 Sustancias ({int_drogas if 'int_drogas' in locals() else '+'})")
                        if 'txt_drogas' in locals() and txt_drogas.strip() != "":
                            habitos_activos[-1] += f" *({txt_drogas.strip()})*"
                    
                    if habitos_activos:
                        st.markdown(f"**🚬 Hábitos y Estilo de Vida:** {' | '.join(habitos_activos)}")
                else:
                    st.success("✅ **Hábitos de Riesgo:** Negados / Estilo de vida saludable.")
                        
                st.divider()
                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 3: VÍA AÉREA Y RIESGO RESPIRATORIO ADAPTATIVO
                # =====================================================================
                st.subheader("🫁 Vía Aérea y Predictores Dinámicos (Módulo 3)")
                
                # --- DETECCIÓN DE ENTORNO ETARIO ---
                es_ped = edad_calc < 18 if 'edad_calc' in locals() else False
                
                # --- LECTURA SEGURA DE VARIABLES CLÍNICAS (ADULTOS) ---
                sb_s_calc = sb_s if 'sb_s' in locals() else False
                sb_t_calc = sb_t if 'sb_t' in locals() else False
                sb_o_calc = sb_o if 'sb_o' in locals() else False
                vmd_barba_calc = vmd_barba if 'vmd_barba' in locals() else False
                vmd_edentulo_calc = vmd_edentulo if 'vmd_edentulo' in locals() else False
                
                # --- LECTURA SEGURA DE VARIABLES CLÍNICAS (PEDIÁTRICAS) ---
                p_estridor = ped_estridor if 'ped_estridor' in locals() else False
                p_ivra = ped_ivra if 'ped_ivra' in locals() else False
                p_vad_previo = ped_vad_previo if 'ped_vad_previo' in locals() else False
                p_ronquido = ped_ronquido if 'ped_ronquido' in locals() else False
                p_retrognatia = ped_retrognatia if 'ped_retrognatia' in locals() else False
                p_macroglosia = ped_macroglosia if 'ped_macroglosia' in locals() else False
                p_cuello_corto = ped_cuello_corto if 'ped_cuello_corto' in locals() else False
                p_masas = ped_masas if 'ped_masas' in locals() else False

                # =====================================================================
                # ESCENARIO PACIENTE PEDIÁTRICO (< 18 AÑOS)
                # =====================================================================
                if es_ped:
                    # Score de Arné Pediátrico / Riesgo Estructural Estreado
                    arne_val = score_arne if 'score_arne' in locals() else 0
                    
                    # Despliegue de Métricas Pediátricas
                    m3_col1, m3_col2 = st.columns(2)
                    with m3_col1:
                        st.metric(label="Riesgo de VAD Estructural", value=f"{arne_val} pts", help="Score indexado para pediatría por malformaciones anatómicas.")
                    with m3_col2:
                        # Indexamos ARISCAT o riesgo pulmonar adaptado
                        aris_inf = ariscat_infeccion_reciente if 'ariscat_infeccion_reciente' in locals() else False
                        score_pulmonar_ped = sum([p_ivra, p_estridor, aris_inf])
                        st.metric(label="Criterios de Hiperreactividad", value=f"{score_pulmonar_ped} / 3", help="Suma de factores predictores de laringoespasmo/broncoespasmo perioperatorio.")
                    
                    st.markdown("##### 🔍 Diagnóstico Predictivo Pediátrico:")
                    
                    # 1. Alerta de Vía Aérea Difícil Pediátrica
                    if p_vad_previo:
                        st.error("🚨 **ALERTA CRÍTICA:** Antecedente documentado de laringoscopia difícil o intubación fallida. Prepare algoritmo de VAD pediátrica, palas rectas (Miller) y estiletes/guías.")
                    elif arne_val >= 6:
                        st.error(f"🚨 **Riesgo de VAD Anatómico Elevado ({arne_val} pts):** Malformación craneofacial activa detectada (Micrognatia/Macroglosia/Cuello Corto). Riesgo severo de pérdida de vía aérea tras la inducción.")
                    else:
                        st.success("🟢 **Índice de Intubación Pediátrica:** Sin malformaciones anatómicas evidentes reportadas.")

                    # 2. Alerta de Hiperreactividad de Vía Aérea (¡EL NÚCLEO DE TU TESIS!)
                    if p_ivra or p_estridor:
                        st.error("🚨 **ALERTA DE RESPUESTA LARÍNGEA SEVERA (Reflejo Extubación):** Paciente con IVRA activa/reciente o historia de estridor. Riesgo crítico de laringoespasmo y broncoespasmo durante la manipulación de la vía aérea o la emergencia anestésica.")
                        st.info("💡 **Justificación de Protocolo de Tesis:** Altamente recomendado el uso de **Lidocaína Intravenosa (0.6 mg/kg/h)** como coadyuvante obligatorio para deprimir los reflejos de la vía aérea y asegurar una emergencia lisa y segura sin tos ni laringoespasmo.")
                    else:
                        st.success("🟢 **Riesgo Resonador/Reflejo:** Vía aérea reactiva basal estable.")
                        
                    # Espejo de Hallazgos Anatómicos Pediátricos marcados
                    hallazgos_ped = []
                    if p_retrognatia: hallazgos_ped.append("🦴 Micrognatia/Retrognatia (Pierre Robin/Treacher Collins)")
                    if p_macroglosia: hallazgos_ped.append("👅 Macroglosia (Down/Beckwith-Wiedemann)")
                    if p_cuello_corto: hallazgos_ped.append("🦒 Cuello corto / Movilidad limitada")
                    if p_masas: hallazgos_ped.append("🎈 Masa cervical compresiva")
                    if p_ronquido: hallazgos_ped.append("💤 Ronquido nocturno severo (SAOS pediátrico)")
                    
                    if hallazgos_ped:
                        st.warning(f"⚠️ **Factores Anatómicos Visibles:**\n" + "\n".join([f"* {x}" for x in hallazgos_ped]))

                # =====================================================================
                # ESCENARIO PACIENTE ADULTO (≥ 18 AÑOS) - TU CÓDIGO ORIGINAL CON OBESE
                # =====================================================================
                else:
                    # --- 1. MOTOR OBESE AUTOMATIZADO ---
                    score_obese_total = 0
                    if 'imc_control' in locals() and imc_control >= 30.0: score_obese_total += 1
                    if vmd_barba_calc: score_obese_total += 1
                    if vmd_edentulo_calc: score_obese_total += 1
                    if sb_s_calc: score_obese_total += 1
                    if 'edad_calc' in locals() and edad_calc > 55: score_obese_total += 1
                    
                    estrato_obese = "Riesgo Alto de Ventilación Difícil 🚨" if score_obese_total >= 2 else "Riesgo Bajo de Ventilación Difícil"

                    # --- 2. MOTOR STOP-BANG AUTOMATIZADO ---
                    score_stop_bang_total = sum([sb_s_calc, sb_t_calc, sb_o_calc])
                    if 'edad_calc' in locals() and edad_calc > 50: score_stop_bang_total += 1
                    if 'sexo_calc' in locals() and sexo_calc == "Masculino": score_stop_bang_total += 1
                    if 'imc_control' in locals() and imc_control > 35.0: score_stop_bang_total += 1
                    if vmd_barba_calc: score_stop_bang_total += 1
                    if 'app_raw' in locals() and "Hipertensión Arterial (HTA)" in app_raw: score_stop_bang_total += 1
                    
                    estrato_sb = "Riesgo Alto para AOS 🚨" if score_stop_bang_total >= 5 else ("Riesgo Intermedio para AOS" if score_stop_bang_total >= 3 else "Riesgo Bajo para AOS")

                    # --- 3. MOTOR ARISCAT AUTOMATIZADO ---
                    score_ariscat_total = 0
                    aris_epoc = ariscat_enfermedad_pulmonar if 'ariscat_enfermedad_pulmonar' in locals() else False
                    aris_inf = ariscat_infeccion_reciente if 'ariscat_infeccion_reciente' in locals() else False
                    
                    if aris_inf: score_ariscat_total += 17
                    if aris_epoc: score_ariscat_total += 4
                    if 'edad_calc' in locals():
                        if 51 <= edad_calc <= 80: score_ariscat_total += 3
                        elif edad_calc > 80: score_ariscat_total += 16
                    if 'hb_val' in locals() and hb_val <= 10.0: score_ariscat_total += 11
                    
                    if 'proc_calc' in locals():
                        proc_upper = proc_calc.upper()
                        if any(x in proc_upper for x in ["COLECIST", "GASTRO", "LAPAROTOM", "TORAC", "RESECCION ONCOLOGICA"]):
                            score_ariscat_total += 24
                        elif any(x in proc_upper for x in ["HERNIA", "HISTERECTOM", "APENDIC"]):
                            score_ariscat_total += 15
                            
                    if 'riesgo_calc' in locals() and "Alto" in riesgo_calc: score_ariscat_total += 6
                    estrato_ariscat = "Riesgo Alto (~42.1% RCP) 🚨" if score_ariscat_total >= 45 else ("Riesgo Moderado (~13.3% RCP)" if score_ariscat_total >= 26 else "Riesgo Bajo (~1.6% RCP)")

                    # --- DESPLIEGUE ADULTOS EN MATRIZ DE 2X2 ---
                    arne_val = score_arne if 'score_arne' in locals() else 0
                    
                    row1_col1, row1_col2 = st.columns(2)
                    with row1_col1: st.metric(label="Arné (Intubación)", value=f"{arne_val} pts")
                    with row1_col2: st.metric(label="OBESE (Ventilación)", value=f"{score_obese_total} pts")
                    
                    row2_col1, row2_col2 = st.columns(2)
                    with row2_col1: st.metric(label="STOP-Bang (Apnea)", value=f"{score_stop_bang_total} pts")
                    with row2_col2: st.metric(label="ARISCAT (Pulmonar)", value=f"{score_ariscat_total} pts")
                    
                    st.markdown("##### 🔍 Diagnóstico Predictivo de Vía Aérea:")
                    
                    if arne_val <= 10:
                        st.success(f"🟢 **Índice de Intubación:** Riesgo Bajo de Intubación Difícil ({arne_val} pts).")
                    else:
                        st.error(f"🚨 **ALERTA: Índice de Intubación Difícil Elevado** ({arne_val} pts). Alto riesgo de laringoscopia dificultosa.")

                    if score_obese_total >= 2:
                        st.error(f"🚨 **Índice de Ventilación (OBESE):** {estrato_obese} ({score_obese_total} pts). Riesgo de sello inadecuado. Asegure cánula de Guedel.")
                    else:
                        st.success(f"🟢 **Índice de Ventilación:** Riesgo Bajo de Ventilación con Máscara Facial.")

                    if score_stop_bang_total >= 5:
                        st.warning(f"⚠️ **STOP-Bang:** {estrato_sb}. Alta probabilidad de obstrucción de vía aérea.")
                    
                    if score_ariscat_total >= 45:
                        st.error(f"🚨 **Riesgo Pulmonar (ARISCAT):** {estrato_ariscat}.")
                    
                    # Espejo anatómico rápido adultos
                    hallazgos_va = []
                    if 'mallampati' in locals() and any(x in mallampati for x in ["III", "IV"]): hallazgos_va.append("👅 Mallampati Alto")
                    if 'dtm' in locals() and "Clase III" in dtm: hallazgos_va.append("📐 DTM Corta")
                    if 'apertura_bucal' in locals() and "Clase III" in apertura_bucal: hallazgos_va.append("👄 Apertura Limitada")
                    if 'vad_retrognatia' in locals() and vad_retrognatia: hallazgos_va.append("🦷 Retrognatia")
                    
                    if hallazgos_va:
                        st.warning(f"⚠️ **Alertas Anatómicas Detectadas:** {' | '.join(hallazgos_va)}")
                
                st.divider()
                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 4: EVALUACIÓN CARDIOVASCULAR (MÓDULO 4)
                # =====================================================================
                st.subheader("🫀 Monitor Cardiovascular y Riesgo (Módulo 4)")
                
                # --- LECTURA SEGURA DE VARIABLES NATIVAS ---
                mets_calc = capacidad_funcional if 'capacidad_funcional' in locals() else "No definido"
                nyha_calc = clase_nyha if 'clase_nyha' in locals() else "No definido"
                ecg_calc = ecg_hallazgo if 'ecg_hallazgo' in locals() else "No disponible / No solicitado"
                fevi_check = fevi_disponible if 'fevi_disponible' in locals() else False
                fevi_val_calc = fevi_valor if 'fevi_valor' in locals() else 60.0
                
                # Síntomas y signos clínicos activos
                angina_activa = cardio_angina if 'cardio_angina' in locals() else False
                disnea_activa = cardio_disnea if 'cardio_disnea' in locals() else False
                palp_activa = cardio_palpitaciones if 'cardio_palpitaciones' in locals() else False
                edema_activo = cardio_edema if 'cardio_edema' in locals() else False
                soplo_activo = cardio_soplo if 'cardio_soplo' in locals() else False

                # =====================================================================
                # ESCENARIO PACIENTE PEDIÁTRICO (< 18 AÑOS)
                # =====================================================================
                if es_ped:
                    ped_sano = sin_cardiopatia_ped if 'sin_cardiopatia_ped' in locals() else True
                    
                    if ped_sano:
                        st.success("✅ **Cardiología Pediátrica:** Lactante / Infante sano sin patologías cardíacas conocidas.")
                    else:
                        m4_col1, m4_col2 = st.columns(2)
                        with m4_col1:
                            st.metric(label="Clase Funcional (Ross)", value=nyha_calc)
                        with m4_col2:
                            st.metric(label="Complejidad de la CC", value=mets_calc)
                            
                        st.markdown("##### 🔍 Alertas Cardiológicas Pediátricas:")
                        if "Severa" in mets_calc or "Class IV" in nyha_calc or "IV" in nyha_calc:
                            st.error("🚨 **ALERTA CC COMPLEJA / ALTO RIESGO:** Paciente pediátrico con cardiopatía severa o insuficiencia cardíaca en reposo (Ross IV). Alto riesgo de inestabilidad hemodinámica intraoperatoria. Asegure monitorización invasiva de presión arterial, optimice estrictamente la precarga y evite caídas de la resistencia vascular sistémica.")
                        else:
                            st.warning("⚠️ **Riesgo Intermedio Pediátrico:** Cardiopatía congénita moderada o leve en seguimiento. Mantenga estabilidad hemodinámica basal y evite fluctuaciones severas del plano anestésico.")
                
                # =====================================================================
                # ESCENARIO PACIENTE ADULTO (≥ 18 AÑOS)
                # =====================================================================
                else:
                    # Ajuste dinámico del Score de Lee (RCRI) incorporando la creatinina de laboratorios (Módulo 5)
                    lee_val = score_lee if 'score_lee' in locals() else 0
                    if 'creatinina_val' in locals() and creatinina_val > 2.0:
                        lee_val += 1
                        
                    # Estratificación clínica del Score de Lee
                    if lee_val == 0:
                        clase_lee = "Clase I (Riesgo Bajo ~0.4%)"
                        color_lee = "normal"
                    elif lee_val == 1:
                        clase_lee = "Clase II (Riesgo Moderado ~0.9%)"
                        color_lee = "normal"
                    elif lee_val == 2:
                        clase_lee = "Clase III (Riesgo Alto ~6.6%) ⚠️"
                        color_lee = "inverse"
                    else:
                        clase_lee = "Clase IV (Riesgo Muy Alto ~11%) 🚨"
                        color_lee = "inverse"
                        
                    # Renderizado de Tarjetas Métricas
                    m4_col1, m4_col2 = st.columns(2)
                    with m4_col1:
                        st.metric(label="Índice de Lee (RCRI)", value=f"{lee_val} pts", delta=clase_lee, delta_color=color_lee)
                    with m4_col2:
                        if fevi_check:
                            delta_fevi = "Normal ✅" if fevi_val_calc >= 50.0 else ("Disfunción Moderada ⚠️" if fevi_val_calc >= 40.0 else "Disfunción Severa 🚨")
                            st.metric(label="FEVI (Ecocardiograma)", value=f"{fevi_val_calc:.0f}%", delta=delta_fevi)
                        else:
                            # Si no hay eco, mostramos una métrica de tamizaje rápido basado en METs
                            estrato_mets = "Limitada (<4 METs) ⚠️" if "Limitada" in mets_calc or "Severamente" in mets_calc else "Adecuada (≥4 METs) ✅"
                            st.metric(label="Reserva Metabólica", value=estrato_mets, help=mets_calc)

                    st.markdown("##### 🔍 Estatus Hemodinámico y Riesgo Isquémico:")
                    
                    # 1. Alertas por Score de Lee y Reserva Metabólica
                    if lee_val >= 2 or "Limitada" in mets_calc or "Severamente" in mets_calc:
                        st.error(f"🚨 **ALERTA DE RIESGO CARDÍACO MAYOR:** Paciente en {clase_lee} o con capacidad funcional comprometida. Alto riesgo perioperatorio de infarto agudo de miocardio, arritmias o paro cardíaco. Mantenga terapia con beta-bloqueadores si la recibe habitualmente y evite la taquicardia intraoperatoria.")
                    else:
                        st.success("🟢 **Riesgo Cardiovascular Basal:** Paciente calificado en rangos estables de bajo riesgo con adecuada reserva miocárdica.")
                        
                    # 2. Alertas por Sintomatología Cardiovascular Activa
                    sintomas_cardio = []
                    if angina_activa: sintomas_cardio.append("💔 Angina Inestable o de reciente comienzo")
                    if disnea_activa: sintomas_cardio.append("🫁 Disnea de causa cardíaca / Ortopnea")
                    if palp_activa: sintomas_cardio.append("💓 Palpitaciones clínicas o Síncope")
                    if edema_activo: sintomas_cardio.append("🦶 Edema maleolar reciente")
                    if soplo_activo: sintomas_cardio.append("🩺 Soplo cardíaco patológico relevante")
                    
                    if sintomas_cardio:
                        st.error(f"🚨 **SÍNTOMAS CARDIOVASCULARES ACTIVOS:** Alerta de sospecha clínica inestable. Presencia de: {', '.join(sintomas_cardio)}. Alto riesgo de descompensación intraoperatoria inmediata. Requiere optimización y valoración mandatoria por Especialidad antes del procedimiento.")
                    
                    # 3. Monitoreo Electrocardiográfico (ECG)
                    if "Normal" not in ecg_calc and "No disponible" not in ecg_calc:
                        st.warning(f"⚠️ **Hallazgo ECG Crítico:** Se registra `{ecg_calc}`. Correlacione estrechamente con el estado hemodinámico en vivo y mantenga monitorización continua del segmento ST en derivaciones DII y V5 en sala.")

                st.divider()
                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 5: EXÁMENES DE LABORATORIO Y COAGULACIÓN (MÓDULO 5)
                # =====================================================================
                st.subheader("🧪 Laboratorio Clínico y Coagulación (Módulo 5)")
                
                # --- LECTURA SEGURA DE VARIABLES NATIVAS ---
                labs_negados = sin_laboratorios if 'sin_laboratorios' in locals() else True
                cirrosis_presencia = cirrosis_activa if 'cirrosis_activa' in locals() else False
                
                # Hemograma
                hb_calc = hb_val if 'hb_val' in locals() else 14.0
                hto_calc = hto_val if 'hto_val' in locals() else 42.0
                plaq_calc = plaquetas_val if 'plaquetas_val' in locals() else 250000
                
                # Renal / Hepático
                creat_calc = creatinina_val if 'creatinina_val' in locals() else 0.8
                urea_calc = urea_val if 'urea_val' in locals() else 30.0
                albu_calc = albumina_serica if 'albumina_serica' in locals() else 3.5
                bili_calc = bili_total if 'bili_total' in locals() else 1.0
                
                # Coagulación
                tp_calc = tp_val if 'tp_val' in locals() else 12.0
                ttpa_calc = ttpa_val if 'ttpa_val' in locals() else 30.0
                inr_calc = inr_val if 'inr_val' in locals() else 1.0
                
                # Gasometría
                gas_check = tiene_gasometria if 'tiene_gasometria' in locals() else False

                # --- CASO A: PACIENTE SANO SIN REQUERIMIENTO DE LABS ---
                if labs_negados and not cirrosis_presencia:
                    st.success("✅ **Laboratorios:** No solicitados / Paciente calificado clínicamente como sano.")
                else:
                    # --- DESPLIEGUE EN MATRIZ DE HEMATOLOGÍA Y COAGULACIÓN ---
                    l_col1, l_col2 = st.columns(2)
                    
                    with l_col1:
                        st.markdown("**🩸 Serie Roja y Plaquetas**")
                        st.markdown(f"* Hemoglobina: **{hb_calc:.1f} g/dL**")
                        st.markdown(f"* Hematocrito: **{hto_calc:.0f}%**")
                        st.markdown(f"* Plaquetas: **{plaq_calc:,} u/µL**")
                        
                    with l_col2:
                        st.markdown("**⏱️ Perfil de Hemostasia**")
                        st.markdown(f"* Tiempo de Protrombina (TP): **{tp_calc:.1f} seg**")
                        st.markdown(f"* TTPa: **{ttpa_calc:.1f} seg**")
                        st.markdown(f"* INR: **{inr_calc:.2f}**")
                    
                    st.markdown("##### 🔍 Alertas de Seguridad Analítica:")
                    
                    # 1. CRUCE MAESTRO: Contraindicación de Bloqueo Central por Plaquetopenia
                    tecnica_anestesica = tipo_anestesia if 'tipo_anestesia' in locals() else ""
                    if plaq_calc < 100000 and "Regional" in tecnica_anestesica:
                        st.error(f"🚨 **CONTRAINDICACIÓN ABSOLUTA DE NEUROEJE:** Se registra un recuadro plaquetario crítico de **{plaq_calc:,} u/µL**. Existe un riesgo severo de hematoma epidural o espinal compresivo irreversible si se ejecuta la técnica propuesta (*{anestesia_calc}*). Recomiende firmemente cambiar la estrategia a Anestesia General.")
                    elif plaq_calc < 150000:
                        st.warning(f"⚠️ **Trombocitopenia Moderada:** ({plaq_calc:,} u/µL). Monitoree hemostasia quirúrgica y evite traumas innecesarios en la vía aérea.")
                        
                    # 2. Alerta de Anemia o Requerimiento de Hemoderivados
                    if hb_calc < 10.0:
                        st.error(f"🚨 **Anemia Significativa (Hb {hb_calc:.1f} g/dL):** Capacidad de transporte de oxígeno disminuida. Asegure la disponibilidad de concentrados de glóbulos rojos en banco de sangre, optimice la fracción inspirada de oxígeno intraoperatoria y aplique estrategias de ahorro de sangre (Patient Blood Management).")
                    elif (sexo_calc == "Femenino" and hb_calc < 12.0) or (sexo_calc == "Masculino" and hb_calc < 13.0):
                        st.caption(f"⚠️ *Anemia leve o marginal para el sexo biológico ({hb_calc:.1f} g/dL).*")

                    # 3. Alerta de Coagulación Prolongada
                    if inr_calc > 1.5 or tp_calc > 15.0:
                        st.error(f"🚨 **COAGULOPATÍA ACTIVA / RIESGO DEFICITARIO:** INR elevado (**{inr_calc:.2f}**). Alto riesgo de sangrado en napa o microvascular intraoperatorio. Prevea la necesidad de plasma fresco congelado si el sangrado quirúrgico se activa.")

                    # --- DETALLES DE FUNCIÓN RENAL Y HEPÁTICA (Consolidado de Texto) ---
                    detalles_organicos = []
                    if ('ver_renal' in locals() and ver_renal) or cirrosis_presencia:
                        detalles_organicos.append(f"Creatinina: **{creat_calc:.2f} mg/dL** ({'Elevada ⚠️' if creat_calc > 1.2 else 'Normal'})")
                        detalles_organicos.append(f"Urea: **{urea_calc:.0f} mg/dL**")
                        detalles_organicos.append(f"Albúmina Sérica: **{albu_calc:.1f} g/dL**")
                    if cirrosis_presencia:
                        detalles_organicos.append(f"Bilirrubina Total: **{bili_calc:.1f} mg/dL**")
                        
                    if detalles_organicos:
                        st.markdown("**💾 Función Renal / Hepática Consolidada:**")
                        st.markdown(" | ".join(detalles_organicos))

                    # --- SUBSECCIÓN: MONITOR GASOMÉTRICO (Si aplica) ---
                    if gas_check:
                        st.markdown("---")
                        st.markdown("##### 🫁 Estado Ácido-Base (Gasometría Arterial)")
                        ph_calc = ph_val if 'ph_val' in locals() else 7.40
                        paco2_calc = paco2_val if 'paco2_val' in locals() else 40.0
                        hco3_calc = hco3_val if 'hco3_val' in locals() else 24.0
                        lactato_calc = lactato_val if 'lactato_val' in locals() else 1.0
                        pafi_calc = pafi if 'pafi' in locals() else 300.0
                        
                        # Interpretación básica del pH
                        if ph_calc < 7.35: estado_ph = "Acidemia 🚨"
                        elif ph_calc > 7.45: estado_ph = "Alcalemia 🚨"
                        else: estado_ph = "Normal ✅"
                        
                        g_col1, g_col2 = st.columns(2)
                        with g_col1:
                            st.markdown(f"* pH Arterial: **{ph_calc:.2f}** ({estado_ph})")
                            st.markdown(f"* PaCO2: **{paco2_calc:.0f} mmHg**")
                            st.markdown(f"* HCO3- Actual: **{hco3_calc:.1f} mEq/L**")
                        with g_col2:
                            st.markdown(f"* Lactato Sérico: **{lactato_calc:.1f} mmol/L** ({'Hiperlactatemia ⚠️' if lactato_calc > 2.0 else 'Normal'})")
                            st.markdown(f"* Índice de Kirby (PaO2/FiO2): **{pafi_calc:.0f} mmHg**")
                            
                        if pafi_calc < 200:
                            st.error(f"🚨 **INSUFICIENCIA RESPIRATORIA CRÍTICA:** PAFI severamente comprometida (**{pafi_calc:.0f} mmHg**). Alto riesgo de hipoxemia refractaria inmediata durante la apnea de inducción. Maximice preoxigenación e instrumente con estrategia protectora rígida.")
                        elif pafi_calc < 300:
                            st.warning(f"⚠️ **Trastorno de Oxigenación Moderado:** Índice de Kirby en **{pafi_calc:.0f} mmHg**.")

                st.divider()
                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 6: EMETOGÉNESIS Y TROMBOFILIA (MÓDULO 6)
                # =====================================================================
                st.subheader("🤢 Emetogénesis y Trombofilia (Módulo 6)")
                
                # --- LECTURA SEGURA DE SCORES PROCESADOS ---
                apfel_final = pts_apfel if 'pts_apfel' in locals() else 0
                caprini_final = score_caprini if 'score_caprini' in locals() else 0
                
                # 1. Estratificación de la Escala de Apfel (Riesgo de NVPO)
                if apfel_final <= 1:
                    estrato_apfel = "Riesgo Bajo (~10-20%)"
                    color_apfel = "normal"
                elif apfel_final == 2:
                    estrato_apfel = "Riesgo Moderado (~40%)"
                    color_apfel = "normal"
                else:
                    estrato_apfel = "Riesgo Alto (~60-80%) 🚨"
                    color_apfel = "inverse"
                    
                # 2. Estratificación de la Escala de Caprini (Riesgo de TVP/TEP)
                if caprini_final <= 1:
                    estrato_caprini = "Riesgo Bajo"
                    color_caprini = "normal"
                elif caprini_final == 2:
                    estrato_caprini = "Riesgo Moderado"
                    color_caprini = "normal"
                elif 3 <= caprini_final <= 4:
                    estrato_caprini = "Riesgo Alto ⚠️"
                    color_caprini = "inverse"
                else:
                    estrato_caprini = "Riesgo Muy Alto / Extremo 🚨"
                    color_caprini = "inverse"
                    
                # --- DESPLIEGUE EN MATRIZ SIMÉTRICA ---
                m6_col1, m6_col2 = st.columns(2)
                with m6_col1:
                    st.metric(label="Escala de Apfel (NVPO)", value=f"{apfel_final} / 4 pts", delta=estrato_apfel, delta_color=color_apfel)
                with m6_col2:
                    st.metric(label="Score de Caprini (ETV)", value=f"{caprini_final} pts", delta=estrato_caprini, delta_color=color_caprini)
                    
                st.markdown("##### 🔍 Directrices de Profilaxis Perioperatoria:")
                
                # --- ALERTA CLÍNICA: ESTRATEGIA ANTIEMÉTICA (APFEL) ---
                if apfel_final >= 3:
                    st.error(f"🚨 **ALERTA NVPO CRÍTICA:** Puntuación de Apfel Elevada ({apfel_final} pts). Se exige **Estrategia Multimodal Profiláctica**: Administre Dexametasona 4 mg IV tras la inducción + Ondansetrón 4 mg IV 30 minutos antes de la extubación. Considere rescate con Metoclopramida o Alizaprida si es necesario.")
                    st.info("💡 **Aporte de Tesis:** El uso de Lidocaína IV en infusión reduce los requerimientos de opioides intraoperatorios, atacando directamente uno de los desencadenantes principales de NVPO en este paciente de alto riesgo.")
                elif apfel_final == 2:
                    st.warning(f"⚠️ **Profilaxis Apfel Moderada:** ({apfel_final} pts). Se sugiere monoterapia preventiva con Ondansetrón 4 mg IV previo a la emersión anestésica.")
                else:
                    st.success("🟢 **Emetogénesis Controlada:** Riesgo bajo. No se requiere terapia combinada de rutina.")
                    
                # --- ALERTA CLÍNICA: ANTICOAGULACIÓN Y PROFILAXIS (CAPRINI) ---
                if caprini_final >= 5:
                    st.error(f"🚨 **ALERTA DE RIESGO TROMBOEMBÓLICO MUY ALTO ({caprini_final} pts):** Indicación mandatoria de **Profilaxis Combinada**. Implemente medidas mecánicas inmediatas (medias de compresión graduada o compresión neumática intermitente) + Profilaxis Farmacológica con HBPM (Enoxaparina 40 mg SC cada 24 horas), iniciando entre 12 y 24 horas postquirúrgicas, siempre que se verifique la hemostasia quirúrgica.")
                elif 3 <= caprini_final <= 4:
                    st.warning(f"⚠️ **Riesgo Caprini Alto ({caprini_final} pts):** Indicación de profilaxis farmacológica con HBPM o heparina no fraccionada SC, asociada a deambulación temprana obligatoria.")
                elif caprini_final == 2:
                    st.info(f"🔹 **Riesgo Caprini Moderado ({caprini_final} pts):** Considere el uso de medias elásticas compresivas o deambulación activa precoz como pauta preventiva.")
                else:
                    st.success("🟢 **Riesgo Tromboembólico Mínimo:** Solo se aconseja deambulación temprana y precoz.")
                    
                st.markdown("---")
                st.caption("✨ **Monitorización de Pestaña 1 Completada.** Todos los cálculos basales e índices de seguridad han sido procesados y sincronizados.")
                # =====================================================================
        # PESTAÑA 2: GENERACIÓN DE REPORTE Y HISTORIA CLÍNICA COPIABLE
        # =====================================================================
        with tab2:
            st.subheader("📄 Nota de Valoración Preanestésica")
            st.caption("Haga clic en el ícono de copiar de la esquina derecha para pegar la nota directamente en el historial clínico electrónico.")
            
            # --- EXTRACTORES DE SEGURIDAD PARA TEXTO PLANO ---
            # Filtros de Alergias
            txt_alergias_final = "NEGADAS."
            if not (sin_alergias if 'sin_alergias' in locals() else True):
                componentes_al = []
                if 'al_med_list' in locals() and al_med_list: componentes_al.append(f"Fármacos: {', '.join(al_med_list)}")
                if 'al_ali_list' in locals() and al_ali_list: componentes_al.append(f"Alimentarias/Otras: {', '.join(al_ali_list)}")
                if componentes_al: txt_alergias_final = " | ".join(componentes_al)

            # Filtros de APP
            txt_app_final = "NEGADOS."
            if not (sin_antecedentes if 'sin_antecedentes' in locals() else True):
                if 'app_list' in locals() and app_list and app_list != ["Ninguno"]: 
                    txt_app_final = ", ".join(app_list)
                    if "Cirrosis Hepática" in app_list:
                        txt_app_final += f" (Child-Pugh Ascitis: {child_ascitis if 'child_ascitis' in locals() else 'Ausente'} | Encefalopatía: {child_encefalo if 'child_encefalo' in locals() else 'Ausente'})"

            # Filtros de Medicación
            txt_meds_final = "NEGADA."
            if not (sin_antecedentes if 'sin_antecedentes' in locals() else True):
                if 'meds_list' in locals() and meds_list and meds_list != ["Ninguno"]: txt_meds_final = ", ".join(meds_list)

            # Filtros de Hábitos
            txt_habitos_final = "NEGADOS."
            if not (sin_habitos if 'sin_habitos' in locals() else True):
                if 'habitos_activos' in locals() and habitos_activos: txt_habitos_final = " | ".join(habitos_activos)

            # Filtros de Laboratorios
            if sin_laboratorios if 'sin_laboratorios' in locals() else True:
                txt_labs_final = "No requeridos / Paciente clínicamente sano."
            else:
                txt_labs_final = f"Hb: {hb_calc:.1f}g/dL | Hto: {hto_calc:.0f}% | Plaq: {plaq_calc:,}/uL | TP: {tp_calc:.1f}s | TTPa: {ttpa_calc:.1f}s | INR: {inr_calc:.2f}"
                if 'gas_check' in locals() and gas_check:
                    txt_labs_final += f"\n   [Gasometría] pH: {ph_val:.2f} | PaCO2: {paco2_val:.0f} mmHg | HCO3: {hco3_val:.1f} mEq/L | Lactato: {lactato_val:.1f} mmol/L | PaO2/FiO2: {pafi_calc:.0f} mmHg"

            # --- CONSTRUCCIÓN DE LA PLANTILLA MÉDICA (TEXTO PLANO MULTILÍNEA) ---
            reporte_medico_texto = f"""=====================================================================
🏥 NOTA DE EVALUACIÓN PREANESTÉSICA CONSOLIDADA
=====================================================================
Centro Institucional: {hospital_final if 'hospital_final' in locals() else 'No registrado'}
Responsable: Dr. Marcos Aviles
Estatus de Validación: Certificado por Sistema Experto Perioperatorio

1. FILIACIÓN Y ANTROPOMETRÍA
---------------------------------------------------------------------
• Sexo Biológico: {sexo_calc if 'sexo_calc' in locals() else 'Masculino'}
• Edad Cronológica: {edad_calc if 'edad_calc' in locals() else '35'} años
• Grupo Sanguíneo y Rh: {gs_calc if 'gs_calc' in locals() else 'Desconocido'}
• Peso Real: {peso_calc:.1f} kg | Talla: {talla_raw:.0f} cm
• IMC Calculado: {imc_control:.1f} kg/m²
• Superficie Corporal (BSA): {bsa_calc:.2f} m²
• Peso Ideal Estimado: {peso_ideal:.1f} kg
• Pesos Ajustados: Al 20%: {peso_ajustado_20:.1f} kg | Al 40%: {peso_ajustado_40:.1f} kg

2. CONTEXTO QUIRÚRGICO Y PLANIFICACIÓN
---------------------------------------------------------------------
• Diagnóstico Principal: {diag_calc if 'diag_calc' in locals() else 'No definido'}
• Procedimiento Quirúrgico: {proc_calc if 'proc_calc' in locals() else 'No definido'}
• Carácter de la Cirugía: {caracter_calc if 'caracter_calc' in locals() else 'Electiva'}
• Riesgo Quirúrgico Intrínseco (AHA/ACC): {riesgo_calc if 'riesgo_calc' in locals() else 'Bajo'}
• Clasificación del Estado Físico (ASA): {asa_calc if 'asa_calc' in locals() else 'ASA I'}
• Técnica Anestésica Propuesta: {anestesia_calc if 'anestesia_calc' in locals() else 'Anestesia General'}

3. SEGURIDAD, ALERGIAS Y ANTECEDENTES (APP)
---------------------------------------------------------------------
• Alergias y Sensibilidades: {txt_alergias_final}
• Antecedentes Patológicos Clínicos: {txt_app_final}
• Medicación de Uso Continuo: {txt_meds_final}
• Hábitos y Estilo de Vida: {txt_habitos_final}

4. SCREENING PREDICTIVO Y ESTRATIFICACIÓN DE RIESGO
---------------------------------------------------------------------
• Índice de Intubación Difícil (Arné): {arne_val if 'arne_val' in locals() else 0} puntos
• Riesgo de Ventilación con Máscara (OBESE): {score_obese_total if ('score_obese_total' in locals() and not es_ped) else 'N/A'} puntos ({estrato_obese if ('estrato_obese' in locals() and not es_ped) else 'N/A'})
• Tamizaje de Apnea del Sueño (STOP-Bang): {score_stop_bang_total if ('score_stop_bang_total' in locals() and not es_ped) else 'N/A'} puntos
• Riesgo Pulmonar Postoperatorio (ARISCAT): {score_ariscat_total if 'score_ariscat_total' in locals() else 0} puntos ({estrato_ariscat if 'estrato_ariscat' in locals() else 'Bajo'})
• Índice de Riesgo Cardíaco Revisado (Lee / RCRI): {lee_val if ('lee_val' in locals() and not es_ped) else 'N/A'} puntos ({clase_lee if ('clase_lee' in locals() and not es_ped) else 'N/A'})
• Riesgo de Náuseas y Vómitos (Apfel): {apfel_final if 'apfel_final' in locals() else 0} / 4 puntos ({estrato_apfel if 'estrato_apfel' in locals() else 'Bajo'})

5. EXÁMENES COMPLEMENTARIOS DE BASE
---------------------------------------------------------------------
• Reporte de Laboratorio: {txt_labs_final}
• Electrocardiograma (ECG): {ecg_calc if 'ecg_calc' in locals() else 'No disponible'}
• Ecocardiograma (FEVI %): {f"{fevi_val_calc:.0f}%" if (fevi_check if 'fevi_check' in locals() else False) else 'No solicitado'}

6. PLAN DE ACCIÓN Y PROFILAXIS RECOMENDADA
---------------------------------------------------------------------
• Manejo Antiemético (Apfel): {'EXIGE Profilaxis Multimodal Combinada (Dexametasona + Ondansetrón).' if apfel_final >= 3 else ('Profilaxis estándar (Ondansetrón IV).' if apfel_final == 2 else 'Manejo sintomático según demanda.')}
• Manejo Antitrombótico (Caprini): {'EXIGE Profilaxis Combinada: Mecánica + Farmacológica (HBPM Enoxaparina).' if caprini_final >= 5 else ('Profilaxis farmacológica o mecánica precoz.' if caprini_final >= 2 else 'Solo deambulación temprana activa.')}
• Consideraciones de Vía Aérea: {'ALERTA: Vía Aérea Difícil Predictiva. Disponer de videolaringoscopio y/o dispositivo supraglótico en sala.' if (arne_val if 'arne_val' in locals() else 0) > 10 or (p_vad_previo if 'p_vad_previo' in locals() else False) else 'Vía aérea con predictores anatómicos estables de intubación.'}
• Observación Especial Pediátrica: {f"Riesgo de Hiperreactividad Laríngea activo. {'CONSIDERAR ADICIÓN DE LIDOCAÍNA IV PROTOCOLO DE TESIS.' if (p_ivra or p_estridor) else 'Control de reflejos estándar.'}" if es_ped else "Paciente en entorno fisiológico adulto."}

=====================================================================
FIN DEL REPORTE - FIRMA REGISTRADA ELECTRÓNICAMENTE
=====================================================================
"""
            
            # Despliegue del bloque copiable con el botón nativo de Streamlit
            st.code(reporte_medico_texto, language="text")
