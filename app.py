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
        # MÓDULO 2: SEGURIDAD, ALERGIAS Y ANTECEDENTES (DINAMIZADO Y UNIFICADO)
        # ---------------------------------------------------------
        with st.expander("2. Seguridad, Alergias y Antecedentes Patológicos", expanded=True):
            
            # --- 1. SECCIÓN DE ALERGIAS (Dinamizada) ---
            st.markdown("#### 🚨 Alergias y Sensibilidades")
            
            sin_alergias = st.checkbox("✅ No refiere alergias", value=True, key="mod2_sin_alergias")
            
            # Inicialización de seguridad (Evita colapsos cuando la sección está oculta)
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

            # --- 2. SECCIÓN UNIFICADA: ANTECEDENTES Y MEDICACIÓN (Dinamizada) ---
            st.markdown("#### 📋 Antecedentes Patológicos y Medicación Habitual")
            
            sin_antecedentes = st.checkbox("✅ No refiere antecedentes patológicos ni medicación de uso continuo", value=True, key="mod2_sin_antecedentes")
            
            # Inicialización de seguridad (Esencial para que el Módulo 3 de Vía Aérea no falle)
            antecedentes_seleccionados = ["Ninguno"]
            otros_antecedentes_txt = ""
            medicacion_actual = ["Ninguno"]
            notas_medicacion_txt = ""
            
            if not sin_antecedentes:
                # Motor epidemiológico dinámico (Heredado del Módulo 1)
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

                lista_medicamentos = ["Antihipertensivos (IECA/ARA II/BCC)", "Beta-bloqueadores", "Diuréticos", "Metformina / Hipoglucemiantes orales", "Insulina", "Antiagregantes (Aspirina/Clopidogrel)", "Anticoagulantes (Warfarina/DOACs)", "Levotiroxina", "Inhaladores (SABA/Corticoides)", "Anticonvulsivantes", "Ninguno", "Otros (Especificar)"]
                
                # Renderizado en paralelo para correlación clínica inmediata
                c_unif1, c_unif2 = st.columns(2)
                
                antecedentes_seleccionados = c_unif1.multiselect(
                    "Patologías Clínicas (APP)", 
                    options=lista_patologias, 
                    key="mod2_antecedentes"
                )
                if "Otros (Especificar)" in antecedentes_seleccionados:
                    otros_antecedentes_txt = c_unif1.text_input("🔍 Especifique otros antecedentes:", key="mod2_ant_otros_txt")

                medicacion_actual = c_unif2.multiselect(
                    "Fármacos de Uso Continuo", 
                    options=lista_medicamentos, 
                    key="mod2_medicacion"
                )
                if "Otros (Especificar)" in medicacion_actual:
                    notas_medicacion_txt = c_unif2.text_input("📝 Especifique dosis o frecuencias:", key="mod2_med_notas_txt")

            st.divider()

            # --- 3. SECCIÓN DE HÁBITOS (Dinamizada) ---
            st.markdown("#### 🚬 Hábitos y Estilo de Vida")
            sin_habitos = st.checkbox("✅ No refiere hábitos dañinos", value=True, key="mod2_sin_habitos")

            hab_alcohol = False
            int_alcohol = "+"
            hab_cigarrillo = False
            int_cigarrillo = "+"
            hab_cafe = False
            int_cafe = "+"
            hab_drogas = False
            int_drogas = "+"
            txt_drogas = ""

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
                    txt_drogas = st.text_input("Especifique la sustancia (Ej. Cannabis, Cocaína):", key="mod2_txt_dro")

# ---------------------------------------------------------
        # MÓDULO 3: VÍA AÉREA Y PREDICTORES (DISEÑO DE RECOLECCIÓN PURO)
        # ---------------------------------------------------------
        with st.expander("3. Vía Aérea y Predictores de Dificultad", expanded=True):
            
            # --- 1. CRITERIOS CLÍNICOS PREVIOS (ÍNDICE DE ARNÉ) ---
            st.markdown("#### 📜 Historia Clínica de Vía Aérea")
            c_arne1, c_arne2 = st.columns(2)
            
            arne_historia = c_arne1.checkbox("🚨 Antecedente personal de Intubación Difícil", key="mod3_arne_hist")
            arne_patologia = c_arne2.checkbox("🏥 Patología clínica asociada a VAD (Ej: Tumores, Angioedema)", key="mod3_arne_pat")
            
            st.divider()

            # --- 2. PREDICTORES ANATÓMICOS (ASA TASKFORCE & ARNÉ) ---
            st.markdown("#### 👅 Evaluación Anatómica y Movilidad")
            
            c_vad1, c_vad2 = st.columns(2)
            
            mallampati = c_vad1.selectbox(
                "Clasificación de Mallampati",
                [
                    "Clase I: Visibilidad de paladar blando, úvula, fauces y pilares",
                    "Clase II: Visibilidad de paladar blando, úvula y fauces",
                    "Clase III: Visibilidad de paladar blando y base de la úvula",
                    "Clase IV: Solo es visible el paladar duro"
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
                    "Clase III (< 3.0 cm): Limitación severa"
                ],
                key="mod3_ab"
            )
            
            dem = c_vad4.selectbox(
                "Distancia Esternomentoniana (Savva)",
                [
                    "Clase I (> 12.5 cm): Sin dificultad predictiva",
                    "Clase II (11.5 - 12.5 cm): Dificultad moderada",
                    "Clase III (< 11.5 cm): Gran dificultad / VAD predictiva"
                ],
                key="mod3_dem"
            )

            c_vad5, c_vad6 = st.columns(2)
            
            # Rangos de cuello actualizados incluyendo la opción mayor a 40 cm
            cuello_cat = c_vad5.selectbox(
                "Circunferencia de Cuello",
                ["Menor a 35 cm (< 35 cm)", "Entre 35 y 40 cm (35 - 40 cm)", "Mayor a 40 cm (> 40 cm)"],
                key="mod3_cuello_categoria"
            )
            
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

            # Conteo analítico complementario de criterios ASA presentes
            cuello_aumentado = cuello_cat in ["Entre 35 y 40 cm (35 - 40 cm)", "Mayor a 40 cm (> 40 cm)"]
            criterios_asa_positivos = sum([
                vad_incisivos, vad_paladar, vad_lengua, vad_retrognatia,
                "Clase III" in mallampati or "Clase IV" in mallampati,
                "Clase III" in dtm, "Clase III" in apertura_bucal, "Clase III" in dem,
                cuello_aumentado, "Clase III" in ulbt, "Limitación Severa" in mov_cervical_arne
            ])

            st.divider()

            # --- 3. SECCIÓN UNIFICADA: FACTORES FÍSICOS Y SÍNTOMAS (OBESE / STOP) ---
            st.markdown("#### 😷 Factores Físicos y Sintomatología (OBESE / STOP)")
            st.caption("Marque las características particulares identificadas en la evaluación:")

            # Lista vertical pura: sin columnas, el texto no se rompe y se alinea perfectamente
            vmd_barba = st.checkbox("🔸 Presencia de barba tupida (Dificulta el sello de la máscara)", key="mod3_barba")
            vmd_edentulo = st.checkbox("🔸 Paciente edéntulo total o parcial", key="mod3_edentulo")
            sb_s = st.checkbox("🔸 Historial de ronquido fuerte (Audible a través de puertas cerradas)", key="mod3_sb_s")
            sb_t = st.checkbox("🔸 Cansancio, fatiga o somnolencia diurna frecuente", key="mod3_sb_t")
            sb_o = st.checkbox("🔸 Apnea nocturna observada por terceros (Pausas al respirar)", key="mod3_sb_o")

            # --- PROCESAMIENTO SILENCIOSO (Mantiene tus bases de datos y reportes intactos) ---
            puntos_vmd = sum([vmd_barba, vmd_edentulo])
            puntos_stop_bang = sum([sb_s, sb_t, sb_o])
# ---------------------------------------------------------
        # MÓDULO 4: EVALUACIÓN CARDIOVASCULAR Y CAPACIDAD FUNCIONAL
        # ---------------------------------------------------------
        with st.expander("4. Evaluación Cardiovascular y Capacidad Funcional", expanded=True):
            
            # --- 1. CAPACIDAD METABÓLICA Y CLASE FUNCIONAL ---
            st.markdown("#### 🏃 Capacidad Metabólica y Clase Funcional")
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
            
            # --- 2. SINTOMATOLOGÍA CARDIOVASCULAR ACTUAL (Lista Vertical Limpia) ---
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
            
            # Dinamismo de la FEVI: El casillero numérico aparece solo si se activa el check
            fevi_disponible = c_card4.checkbox("¿Cuenta con reporte de Ecocardiograma?", key="mod4_check_fevi")
            fevi_valor = 60.0  # Valor predeterminado por defecto
            
            if fevi_disponible:
                fevi_valor = c_card4.number_input(
                    "Fracción de Eyección (FEVI %)",
                    min_value=10.0, max_value=85.0, value=60.0, step=1.0,
                    key="mod4_fevi_val"
                )
            
            st.divider()
            
            # --- 4. CONDICIÓN RENAL / COMPLEMENTO DE RIESGO ---
            st.markdown("#### 🧪 Parámetro Metabólico Adicional")
            # Factor de Lee independiente (Creatinina > 2 mg/dl), no duplicado en el módulo 2
            creatinina_alta = st.checkbox("🔹 Creatinina sérica preoperatoria > 2.0 mg/dL (177 µmol/L)", key="mod4_creat")

            # --- PROCESAMIENTO SILENCIOSO DE RIESGO DE LEE (Para tu matriz de tesis) ---
            # Extracción limpia de factores de riesgo del Índice de Lee Modificado (RCRI)
            factor_cirugia_riesgo = 1 if (riesgo_cx and "Alto" in riesgo_cx) else 0
            factor_cardiopatia_isq = 1 if (not sin_antecedentes and any("Isquémica" in p or "IAM" in p for p in antecedentes_seleccionados)) or cardio_angina else 0
            factor_insuf_cardiaca = 1 if (not sin_antecedentes and "Insuficiencia Cardíaca" in lista_patologias) or cardio_edema or cardio_disnea else 0
            factor_acv = 1 if (not sin_antecedentes and any("ACV" in p or "Isquemia" in p for p in antecedentes_seleccionados)) else 0
            factor_insulina = 1 if (not sin_antecedentes and "Insulina" in medicacion_actual) else 0
            factor_creatinina = 1 if creatinina_alta else 0
            
            # Sumatoria interna almacenada en variable
            score_lee = factor_cirugia_riesgo + factor_cardiopatia_isq + factor_insuf_cardiaca + factor_acv + factor_insulina + factor_creatinina
