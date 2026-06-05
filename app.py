import streamlit as st
import math
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Asistente Anestésico", page_icon="🩺")

# =============================================================================
# 🛠️ FUNCIONES UTILITARIAS GLOBALES
# =============================================================================
def formatear_lista(lista_original, texto_extra):
    lista = [x for x in lista_original if x != "Ninguno"] if len(lista_original) > 1 else list(lista_original)
    if "Otros (Especificar)" in lista:
        lista.remove("Otros (Especificar)")
        if texto_extra.strip() != "":
            lista.append(f"*{texto_extra.strip()}*")
    return lista

# --- MOTOR DE INTELIGENCIA ANTROPOMÉTRICA ---
def actualizar_antropometria():
    if 'mod1_edad' not in st.session_state or 'mod1_sexo' not in st.session_state:
        return
        
    e = st.session_state.mod1_edad
    s = st.session_state.mod1_sexo
    
    # Fórmulas de estimación pediátrica (APLS) y proyección adulta
    if e == 0: 
        p, t = 5.0, 60.0
    elif 1 <= e <= 5: 
        p, t = (e * 2.0) + 8.0, (e * 6.0) + 77.0
    elif 6 <= e <= 12: 
        p, t = (e * 3.0) + 7.0, (e * 6.0) + 77.0
    elif 13 <= e <= 17:
        if s == "Masculino": p, t = 50.0 + (e - 12.0) * 4.0, 155.0 + (e - 12.0) * 5.0
        else: p, t = 45.0 + (e - 12.0) * 3.0, 150.0 + (e - 12.0) * 2.0
    else: # Adultos
        if s == "Masculino": p, t = 70.0, 170.0
        else: p, t = 60.0, 158.0
            
    st.session_state.mod1_peso = float(p)
    st.session_state.mod1_talla = float(t)

# --- TÍTULO PRINCIPAL ---
st.title("🩺 Asistente de Evaluación Anestésica")
st.caption("Sistema de validación perioperatoria y seguridad del paciente.")
st.caption("**Autor:** Dr. Marcos Aviles")
st.markdown("---")

# --- BLOQUEO DE TECLADO MÓVIL PARA MENÚS DESPLEGABLES ---
components.html(
    """
    <script>
    const doc = window.parent.document;
    const observer = new MutationObserver(function(mutations) {
        const selectInputs = doc.querySelectorAll('div[data-baseweb="select"] input');
        selectInputs.forEach(function(input) {
            input.setAttribute('inputmode', 'none');
        });
    });
    observer.observe(doc, { childList: true, subtree: true });
    </script>
    """,
    height=0,
    width=0,
)

col_izquierda, col_derecha = st.columns([1.3, 1])

# =============================================================================
# COLUMNA IZQUIERDA: MÓDULOS DE EVALUACIÓN CLÍNICA
# =============================================================================
with col_izquierda:
    st.header("📋 Datos de Entrada")
    
    st.markdown("### 🏥 Registro Institucional")
    tipo_institucion = st.selectbox("Clasificación Institucional", ["👈 Seleccione el Sector...", "Red Pública (MSP / IESS)", "Sector Privado / JBG", "Otro Centro / Práctica Privada"], key="mod_inst_tipo")
    hospital_final = ""; hospital_valido = False
    
    if tipo_institucion == "Red Pública (MSP / IESS)":
        lista_publicos = ["👈 Seleccione un hospital público...", "Hospital de Especialidades Abel Gilbert Pontón (MSP)", "Hospital General del Norte de Guayaquil Los Ceibos (IESS)", "Hospital de Especialidades Teodoro Maldonado Carbo (IESS)", "Hospital General del Guasmo Sur (MSP)", "Hospital General Dr. Enrique Ortega Moreira (MSP)", "Hospital General Monte Sinaí (MSP)", "Hospital Universitario de Guayaquil (MSP)", "Otro Hospital Público (Especificar)"]
        hosp_sel = st.selectbox("📍 Seleccione el Hospital Público", lista_publicos, key="mod_inst_pub")
        if hosp_sel != "👈 Seleccione un hospital público...":
            hospital_valido = True
            hospital_final = st.text_input("Nombre del hospital:", key="mod_inst_pub_txt") if hosp_sel == "Otro Hospital Público (Especificar)" else hosp_sel
            
    elif tipo_institucion == "Sector Privado / JBG":
        lista_privados = ["👈 Seleccione un centro...", "Hospital de Niños Dr. Roberto Gilbert Elizalde (JBG)", "Hospital Gineco-Obstétrico Alfredo G. Paulson (JBG)", "Omni Hospital", "Hospital Clínica Kennedy", "Hospital Alcívar", "Interhospital", "Hospital Clínica Panamericana", "Otro Centro Privado (Especificar)"]
        hosp_sel = st.selectbox("📍 Seleccione el Centro Privado", lista_privados, key="mod_inst_priv")
        if hosp_sel != "👈 Seleccione un centro...":
            hospital_valido = True
            hospital_final = st.text_input("Nombre del centro:", key="mod_inst_priv_txt") if hosp_sel == "Otro Centro Privado (Especificar)" else hosp_sel
            
    elif tipo_institucion == "Otro Centro / Práctica Privada":
        hospital_final = st.text_input("Escriba el nombre de la Clínica o Centro Médico:", key="mod_inst_otro_txt")
        if hospital_final.strip() != "": hospital_valido = True

    if not hospital_valido:
        st.info("🔒 Complete el registro institucional arriba para desbloquear la evaluación.")
    else: 
        st.success(f"✅ Centro registrado: **{hospital_final}**")
        st.divider()
        
        # ---------------------------------------------------------
        # MÓDULO 1: DEMOGRÁFICOS Y CONTEXTO QUIRÚRGICO
        # ---------------------------------------------------------
        with st.expander("1. Datos Demográficos y Contexto Quirúrgico", expanded=True):
            st.divider() 
            st.markdown("### 🏢 Ámbito de la Evaluación Anestésica")
            ambito_atencion = st.radio("Seleccione el entorno actual del paciente:", ["Quirófano / Emergencia 🏥", "Consulta Externa Preanestésica 📑"], horizontal=True, key="mod1_ambito_atencion")
            st.divider()

            # Precarga de variables en Session State para evitar errores en recargas
            if 'mod1_edad' not in st.session_state: st.session_state['mod1_edad'] = 50
            if 'mod1_peso' not in st.session_state: st.session_state['mod1_peso'] = 70.0
            if 'mod1_talla' not in st.session_state: st.session_state['mod1_talla'] = 170.0

            c_demo1, c_demo2, c_demo3 = st.columns(3)
            sexo = c_demo1.radio("Sexo", ["Masculino", "Femenino"], key="mod1_sexo", on_change=actualizar_antropometria)
            edad = c_demo2.number_input("Edad (años)", min_value=0, max_value=120, key="mod1_edad", on_change=actualizar_antropometria)
            grupo_sangre = c_demo3.selectbox("Grupo y Rh", ["Desconocido", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"], key="mod1_gs")
            
            st.caption("✨ *El peso y talla se autoajustan según percentil al cambiar la edad (pueden ser modificados manualmente).*")
            c_ant1, c_ant2 = st.columns(2)
            peso_real = c_ant1.number_input("Peso Real (kg)", min_value=1.0, max_value=300.0, step=0.1, key="mod1_peso")
            talla_cm = c_ant2.number_input("Talla (cm)", min_value=30.0, max_value=250.0, step=1.0, key="mod1_talla")
            
            imc = peso_real / ((talla_cm / 100) ** 2) if talla_cm > 0 else 0
            
            st.divider()
            
            def conmutar_modulo_obstetrico():
                if st.session_state.get("mod1_es_obstetrico"): st.session_state["mod1_especialidad"] = "Ginecología y Obstetricia"
                elif st.session_state.get("mod1_especialidad") == "Ginecología y Obstetricia": st.session_state["mod1_especialidad"] = "Cirugía General"

            es_obstetrico = False
            if sexo == "Femenino" and 10 <= edad <= 45:
                es_obstetrico = st.checkbox("🤰 Paciente Obstétrica (Cambia diagnósticos y procedimientos)", key="mod1_es_obstetrico", on_change=conmutar_modulo_obstetrico)

            st.markdown("**Contexto Quirúrgico y Clasificación**")

            semanas_eg = 0; horas_ayuno = 8; tipo_ayuno = "No aplica"; plan_suspension_meds = []; interconsultas_req = []

            if "Quirófano" in ambito_atencion:
                c_cx1, c_asa = st.columns(2)
                caracter_cx = c_cx1.selectbox("Carácter", ["Electiva", "Urgencia", "Emergencia"], key="mod1_caracter")
                asa_ps = c_asa.selectbox("Clasificación ASA", ["ASA I: Paciente sano normal", "ASA II: Enfermedad sistémica leve", "ASA III: Enfermedad sistémica grave", "ASA IV: Enf. sistémica grave con amenaza vital", "ASA V: Paciente moribundo", "ASA VI: Muerte cerebral (Donante)"], key="mod1_asa")

                if es_obstetrico:
                    st.markdown("🤰 **Datos Obstétricos de Emergencia**")
                    semanas_eg = st.number_input("Semanas de Gestación Actual (EG):", min_value=4, max_value=42, value=38, step=1, key="mod1_semanas_eg")

                st.markdown("⏱️ **Control de Ayuno Activo (Estatus NPO)**")
                c_npo1, c_npo2 = st.columns(2)
                tipo_ayuno = c_npo1.selectbox("Última ingesta de:", ["Sólidos pesados / Grasas", "Comida ligera / Leche de fórmula", "Leche materna", "Líquidos claros (Agua, té, café negro)"], key="mod1_tipo_ayuno")
                horas_ayuno = c_npo2.number_input("Horas de ayuno cumplidas:", min_value=0, max_value=48, value=8, step=1, key="mod1_horas_ayuno")
            else:
                caracter_cx = "Electiva"
                c_cx1, c_asa = st.columns(2)
                c_cx1.info("📋 **Carácter Quirúrgico:** Fijado automáticamente como **Electiva**.")
                asa_ps = c_asa.selectbox("Clasificación ASA Proyectada", ["ASA I: Paciente sano normal", "ASA II: Enfermedad sistémica leve", "ASA III: Enfermedad sistémica grave", "ASA IV: Enf. sistémica grave con amenaza vital"], key="mod1_asa")

                st.markdown("📑 **Planificación y Optimización de Consulta Externa**")
                c_ce1, c_ce2 = st.columns(2)
                plan_suspension_meds = c_ce1.multiselect("🛑 Plan de Suspensión de Fármacos Críticos:", ["Suspender Antiagregantes (Aspirina/Clopidogrel) 5-7 días antes", "Suspender Anticoagulantes Orales (Warfarina/DOACs) según protocolo", "Suspender Metformina 24 horas antes del procedimiento", "Continuar Beta-bloqueadores de forma habitual el día de la cirugía", "No requiere suspensiones de tratamiento continuo"], key="mod1_ce_suspensiones")
                interconsultas_req = c_ce2.multiselect("🩺 Interconsultas de Optimización Solicitadas:", ["Valoración por Cardiología (Riesgo Quirúrgico)", "Valoración por Neumología (Espirometría / EPOC)", "Valoración por Endocrinología (Control metabólico HbA1c)", "Ninguna interconsulta adicional requerida"], key="mod1_ce_interconsultas")

            riesgo_cx = st.selectbox("Riesgo Quirúrgico Intrínseco (AHA/ACC)", ["Bajo (<1%) - Ej: Superficial, Endoscópica, Catarata", "Intermedio (1-5%) - Ej: Intraperitoneal, Ortopédica mayor", "Alto (>5%) - Ej: Vascular mayor, Torácica, Aórtica"], key="mod1_riesgo")
            st.divider()

            lista_especialidades = ["Cirugía General", "Cirugía Oncológica"]
            if edad < 15: lista_especialidades.append("Cirugía Pediátrica")
            if sexo == "Femenino": lista_especialidades.append("Ginecología y Obstetricia")
            lista_especialidades.extend(["Traumatología y Ortopedia", "Cirugía Cardiovascular y Torácica", "Neurocirugía", "Urología", "Otorrinolaringología y Oftalmología", "Cirugía Plástica y Maxilofacial", "Otra Especialidad"])

            if "mod1_especialidad" in st.session_state:
                current_spec = st.session_state["mod1_especialidad"]
                if edad < 15 and current_spec == "Cirugía General": st.session_state["mod1_especialidad"] = "Cirugía Pediátrica"
                elif edad >= 15 and current_spec == "Cirugía Pediátrica": st.session_state["mod1_especialidad"] = "Cirugía General"
            else:
                st.session_state["mod1_especialidad"] = "Cirugía Pediátrica" if edad < 15 else "Cirugía General"

            especialidad_cx = st.selectbox("Especialidad Quirúrgica", lista_especialidades, key="mod1_especialidad")
            c_cx3, c_cx4 = st.columns(2)
            
            # --- MOTOR RELACIONAL: DIAGNÓSTICOS -> PROCEDIMIENTOS ---
            mapa_cx = {
                "Cirugía General": {
                    "Colelitiasis / Colecistitis Aguda": ["Colecistectomía Laparoscópica", "Colecistectomía Abierta"],
                    "Apendicitis Aguda": ["Apendicectomía Laparoscópica", "Apendicectomía Convencional"],
                    "Hernia Inguinal / Umbilical / Crural": ["Hernioplastia con Malla (Laparoscópica)", "Hernioplastia Abierta"],
                    "Obstrucción Intestinal / Abdomen Agudo": ["Laparotomía Exploradora", "Resección Intestinal + Anastomosis / Estoma"],
                    "Patología Orificial": ["Hemorroidectomía", "Fistulectomía / Drenaje de Absceso"],
                },
                "Cirugía Oncológica": {
                    "Neoplasia de Mama": ["Mastectomía Radical Modificada", "Cuadrantectomía + Ganglio Centinela", "Reconstrucción Mamaria Inmediata"],
                    "Neoplasia Gastrointestinal (Colon/Estómago)": ["Hemicolectomía Radical", "Gastrectomía Total/Subtotal con Linfadenectomía", "Resección Anterior de Recto"],
                    "Neoplasia Ginecológica (Cérvix/Ovario/Útero)": ["Histerectomía Radical (Wertheim-Meigs)", "Cirugía Citorreductora (Ovario) + Omentectomía"],
                    "Neoplasia Urológica (Próstata/Riñón)": ["Prostatectomía Radical", "Nefrectomía Radical / Parcial"],
                    "Neoplasia de Cabeza y Cuello": ["Tiroidectomía Total/Parcial + Vaciamiento Cervical", "Glosectomía", "Parotidectomía"],
                    "Neoplasia de Piel y Partes Blandas": ["Resección Amplia de Sarcoma / Melanoma", "Amputación Mayor Oncológica"]
                },
                "Cirugía Pediátrica": {
                    "Apendicitis Aguda Pediátrica": ["Apendicectomía Laparoscópica Pediátrica", "Apendicectomía Abierta"],
                    "Fimosis / Parafimosis": ["Circuncisión / Plastia de Prepucio"],
                    "Criptorquidia / Testículo No Descendido": ["Orquidopexia Unilateral / Bilateral"],
                    "Hernia Inguinal / Umbilical Congénita": ["Hernioplastia Pediátrica"],
                    "Estenosis Hipertrófica del Píloro": ["Piloromiotomía"]
                },
                "Ginecología y Obstetricia": {
                    "Embarazo a Término / Trabajo de Parto": ["Cesárea Segmentaria Transversa", "Parto Vaginal Dirigido"],
                    "Miomatosis Uterina Sintomática": ["Histerectomía Total Abdominal / Laparoscópica", "Miomectomía"],
                    "Quiste / Tumoración Benigna de Ovario": ["Quistectomía de Ovario", "Salpingooforectomía"],
                    "Embarazo Ectópico": ["Laparotomía Exploradora", "Salpingectomía Laparoscópica"],
                    "Hemorragia Uterina Anómala": ["Legrado Uterino Instrumental (LUI) / AMEU", "Histeroscopia"]
                },
                "Traumatología y Ortopedia": {
                    "Fractura de Cadera / Cuello Femoral": ["Reemplazo Articular (Prótesis)", "Fijación con Clavo Cefalomedular / DHS"],
                    "Fractura de Huesos Largos (Fémur/Tibia/Humero)": ["Reducción Abierta y Fijación Interna (RAFI) con Placa/Clavo"],
                    "Artrosis Severa de Rodilla / Cadera": ["Artroplastia Total (Reemplazo Articular)"],
                    "Lesión Ligamentaria / Meniscal de Rodilla": ["Artroscopia Terapéutica / Reconstrucción de Ligamentos"],
                    "Osteomielitis / Infección de Material": ["Retiro de Material de Osteosíntesis (RMO)", "Limpieza Quirúrgica + Secuestrectomía"]
                },
                "Neurocirugía": {
                    "Neoplasia / Tumor Cerebral": ["Craneotomía + Resección de Tumor"],
                    "Hematoma Subdural / Epidural": ["Evacuación de Hematoma", "Craniectomía Descompresiva"],
                    "Hernia Discal Lumbar / Cervical": ["Discectomía / Microdiscectomía", "Laminectomía"],
                    "Hidrocefalia": ["Colocación de Válvula de Derivación Ventriculoperitoneal (DVP)"],
                    "Aneurisma Cerebral": ["Clipaje de Aneurisma por Craneotomía"]
                },
                "Urología": {
                    "Hipertrofia Prostática Benigna (HPB)": ["Resección Transuretral de Próstata (RTU-P)", "Enucleación Prostática Láser / Abierta"],
                    "Litiasis Renoureteral Obstructiva": ["Ureterolitotripsia Láser", "Nefrolitotomía Percutánea"],
                    "Hidrocele / Varicocele Sintomático": ["Hidrocelectomía", "Varicocelectomía Unilateral/Bilateral"],
                    "Estenosis de Uretra": ["Uretrotomía Óptica Interna / Dilatación Uretral"]
                },
                "Cirugía Cardiovascular y Torácica": {
                    "Cardiopatía Isquémica": ["Revascularización Miocárdica (CABG / By-pass Coronario)"],
                    "Valvulopatía (Aórtica/Mitral)": ["Cambio Valvular Mecánico / Biológico", "Plastia Valvular"],
                    "Derrame Pleural / Neumotórax": ["Toracoscopia Asistida (VATS)", "Colocación de Tubo Torácico / Ventana Pericárdica"],
                    "Aneurisma de Aorta": ["Reemplazo Aórtico con Tubo Valvulado", "Reparación Endovascular (TEVAR/EVAR)"]
                },
                "Otorrinolaringología y Oftalmología": {
                    "Catarata Senil / Capsular": ["Facoemulsificación + Colocación de Lente Intraocular (LIO)"],
                    "Desviación Septal / Hipertrofia de Cornetes": ["Septoplastia / Turbinoplastia Endoscópica"],
                    "Otitis Media Crónica": ["Timpanoplastia / Mastoidectomía"],
                    "Hipertrofia de Amígdalas / Adenoides": ["Amigdalectomía / Adenoidectomía"]
                },
                "Cirugía Plástica y Maxilofacial": {
                    "Secuela de Quemadura / Cicatriz": ["Escarectomía + Injerto de Piel", "Colgajo Reconstructivo"],
                    "Fractura Maxilofacial": ["Reducción y Fijación Rígida Maxilofacial"],
                    "Lipodistrofia / Ptosis Mamaria": ["Abdominoplastia", "Mastopexia / Mamoplastia", "Liposucción"],
                    "Fisura Labiopalatina": ["Queiloplastia", "Palatoplastia"]
                }
            }

            diccionario_actual = mapa_cx.get(especialidad_cx, {})
            lista_diagnosticos = list(diccionario_actual.keys())
            
            # --- INYECCIÓN UNIVERSAL DE CÁNCER ---
            if especialidad_cx != "Cirugía Oncológica" and "Cáncer / Neoplasia Oncológica" not in lista_diagnosticos:
                lista_diagnosticos.append("Cáncer / Neoplasia Oncológica")
                diccionario_actual["Cáncer / Neoplasia Oncológica"] = ["Resección Tumoral Mayor", "Biopsia Escisional / Incisional", "Cirugía Paliativa / Derivativa"]
            
            lista_diagnosticos.append("Otro (Especificar)")
            diag_base = c_cx3.selectbox("Diagnóstico Principal", lista_diagnosticos, key="mod1_diag_base")
            diagnostico_final = c_cx3.text_input("Especifique el diagnóstico", key="mod1_diag_txt") if diag_base == "Otro (Especificar)" else diag_base
            
            lista_procedimientos = diccionario_actual.get(diag_base, ["Procedimiento Menor / Biopsia", "Procedimiento Mayor Especializado"])
            if "Otro (Especificar)" not in lista_procedimientos:
                lista_procedimientos.append("Otro (Especificar)")
            
            proc_base = c_cx4.selectbox("Procedimiento Propuesto", lista_procedimientos, key="mod1_proc_base")
            procedimiento_final = c_cx4.text_input("Especifique el procedimiento", key="mod1_proc_txt") if proc_base == "Otro (Especificar)" else proc_base
            
            tiempo_fractura_cx = "No aplica"
            tipo_fractura_cx = "No aplica"
            
            if "Fractura" in diagnostico_final:
                tiempo_fractura_cx = c_cx3.radio(
                    "⏱️ Tiempo de Evolución de la Fractura:",
                    ["Menor a un mes", "Mayor a un mes", "Mayor a un año"],
                    key="mod1_tiempo_fractura",
                    help="Clave para la estratificación de riesgo trombótico en la escala de Caprini."
                )
                
                # --- AUTO-CLASIFICACIÓN SILENCIOSA PARA CAPRINI ---
                if any(palabra in diagnostico_final.upper() for palabra in ["CADERA", "FEMORAL", "FÉMUR", "PELVIS", "TIBIA", "PERONÉ", "INFERIOR"]):
                    tipo_fractura_cx = "Riesgo Caprini Extremo"
                else:
                    tipo_fractura_cx = "Riesgo Caprini Standard"
                
            c_ane1, c_ane2 = st.columns(2)
            tipo_anestesia = c_ane1.selectbox("Técnica Anestésica Propuesta", ["Anestesia General (Balanceada / TIVA)", "Anestesia Regional (Neuroeje: Raquídea / Epidural)", "Bloqueo de Nervio Periférico + Sedación", "Cuidado Anestésico Monitorizado (MAC) / Sedación", "Anestesia Local"], key="mod1_tecnica")
            
            st.markdown("<br>", unsafe_allow_html=True) 
            req_sangre = c_ane2.checkbox("🩸 **Previsión de sangrado mayor (>500ml) / Requiere reserva de sangre cruzada**", key="mod1_sangre")

        # ---------------------------------------------------------
        # MÓDULO 2: SEGURIDAD Y ANTECEDENTES (Con Motor Predictivo)
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
            tipo_fractura_app = "No aplica"; tipo_fractura_ant = "No aplica"; child_ascitis = "Ausente"; child_encefalo = "Ausente"
            
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
                    lista_patologias.insert(idx, "Cáncer activo o en tratamiento")

                c_unif1, c_unif2 = st.columns(2)
                antecedentes_seleccionados = c_unif1.multiselect("Patologías Clínicas (APP)", options=lista_patologias, key="mod2_antecedentes")

                if "Cirrosis Hepática" in antecedentes_seleccionados:
                    st.caption("🟡 Evaluación de Severidad Hepática (Child-Pugh):")
                    c_hep1, c_hep2 = st.columns(2)
                    child_ascitis = c_hep1.selectbox("Ascitis", ["Ausente", "Leve / Moderada (Controlada)", "Tensa / Grave (Refractaria)"], key="mod2_ascitis")
                    child_encefalo = c_hep2.selectbox("Encefalopatía", ["Ausente", "Grado I - II (Leve)", "Grado III - IV (Grave)"], key="mod2_encefalo")

                if "Fractura / Traumatismo Mayor" in antecedentes_seleccionados:
                    tipo_fractura_app = c_unif1.selectbox("🛹 Tipo / Localización de la Fractura", ["Fractura de Cadera (Fémur Proximal) [Riesgo Caprini Alto]", "Fractura de Pelvis o Acetábulo [Riesgo Caprini Alto]", "Fractura de Miembro Inferior (Diáfisis de Fémur, Tibia, Peroné)", "Otro Traumatismo Mayor"])
                    tipo_fractura_ant = c_unif1.radio("⏱️ Tiempo desde el antecedente de la fractura:", ["Menor a un mes", "Mayor a un mes", "Mayor a un año"], key="mod2_tiempo_frac_ant")
                
                if "Otros (Especificar)" in antecedentes_seleccionados: 
                    otros_antecedentes_txt = c_unif1.text_input("🔍 Especifique otros antecedentes:", key="mod2_ant_otros_txt")
                
                # --- MOTOR PREDICTIVO DE MEDICACIÓN ---
                meds_dinamicos = set(["Analgésicos comunes (Paracetamol/AINEs)", "Protectores gástricos (IBP/Ranitidina)", "Vitaminas / Suplementos"])
                for app in antecedentes_seleccionados:
                    if any(x in app for x in ["Hipertensión", "HTA", "Preeclampsia"]): meds_dinamicos.update(["Antihipertensivos (IECA/ARA II/BCC)", "Beta-bloqueadores", "Diuréticos"])
                    if "Diabetes" in app: meds_dinamicos.update(["Metformina / Hipoglucemiantes orales", "Insulina"])
                    if "Hipotiroidismo" in app: meds_dinamicos.add("Levotiroxina")
                    if any(x in app for x in ["Asma", "EPOC", "Hiperreactividad", "Rinitis"]): meds_dinamicos.update(["Inhaladores (SABA/LAMA/Corticoides)", "Antihistamínicos"])
                    if any(x in app for x in ["Cardiopatía", "Arritmia", "ACV", "Isquemia", "IAM", "Insuficiencia"]): meds_dinamicos.update(["Antiagregantes (Aspirina/Clopidogrel)", "Anticoagulantes (Warfarina/DOACs)", "Estatinas", "Antiarrítmicos / Digoxina"])
                    if any(x in app for x in ["Epilepsia", "Convulsiones", "Psiquiátrico"]): meds_dinamicos.update(["Anticonvulsivantes", "Antidepresivos / Ansiolíticos"])
                    if "Cáncer" in app: meds_dinamicos.update(["Medicación Oncológica (Quimioterapia / Inmunoterapia)", "Corticoides sistémicos", "Analgésicos Opioides"])
                    if any(x in app for x in ["Autoinmune", "LES"]): meds_dinamicos.update(["Inmunosupresores / Biológicos", "Corticoides sistémicos"])
                    if "Dislipidemia" in app: meds_dinamicos.add("Estatinas / Fibratos")

                lista_medicamentos = sorted(list(meds_dinamicos))
                lista_medicamentos.insert(0, "Ninguno")
                lista_medicamentos.append("Otros (Especificar)")
                
                medicacion_actual = c_unif2.multiselect("Fármacos Predictivos", options=lista_medicamentos, key="mod2_medicacion")
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
                
                c_cafe1, c_cafe2 = st.columns([3, 1])
                hab_cafe = c_cafe1.checkbox("Consumo de Café", key="mod2_hab_caf")
                int_cafe = c_cafe2.selectbox("Intensidad Café", ["+", "++", "+++"], key="mod2_int_caf", disabled=not hab_cafe, label_visibility="collapsed")
                
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
            ped_estridor = False; ped_ivra = False; ped_vad_previo = False; ped_ronquido = False; ped_retrognatia = False; ped_macroglosia = False; ped_cuello_corto = False; ped_masas = False
            ariscat_enfermedad_pulmonar = False; ariscat_infeccion_reciente = False

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

                if not es_pediatrico_va:
                    st.divider()
                    st.markdown("#### 😷 Factores Físicos y Sintomatología (OBESE / STOP)")
                    vmd_barba = st.checkbox("🔸 Presencia de barba tupida (Dificulta el sello de la máscara)", key="mod3_barba")
                    vmd_edentulo = st.checkbox("🔸 Paciente edéntulo total o parcial", key="mod3_edentulo")
                    sb_s = st.checkbox("🔸 Historial de ronquido fuerte (Audible a través de puertas cerradas)", key="mod3_sb_s")
                    sb_t = st.checkbox("🔸 Cansancio, fatiga o somnolencia diurna frecuente", key="mod3_sb_t")
                    sb_o = st.checkbox("🔸 Apnea nocturna observada por terceros (Pausas al respirar)", key="mod3_sb_o")

            st.divider()
            st.markdown("#### 🫁 Evaluación Respiratoria Avanzada (ARISCAT)")
            c_aris1, c_aris2 = st.columns(2)
            with c_aris1: ariscat_enfermedad_pulmonar = st.checkbox("🔸 Patología respiratoria crónica activa (EPOC, Asma sintomática, Fibrosis)", key="mod3_ariscat_epoc")
            with c_aris2: ariscat_infeccion_reciente = st.checkbox("🔸 Infección de vías respiratorias (altas o bajas) en el último mes", key="mod3_ariscat_inf")

        # ---------------------------------------------------------
        # MÓDULO 4: EVALUACIÓN CARDIOVASCULAR
        # ---------------------------------------------------------
        with st.expander("4. Evaluación Cardiovascular y Capacidad Funcional", expanded=True):
            capacidad_funcional = "No aplica (Pediátrico)"; clase_nyha = "No aplica (Pediátrico)"; cardio_angina = False; cardio_disnea = False; cardio_palpitaciones = False; cardio_edema = False; cardio_soplo = False; ecg_hallazgo = "No disponible / No solicitado"; fevi_valor = 60.0; fevi_disponible = False
            clase_ross = "Clase I"; complejidad_cc = "Leve"; tiene_marcapasos = False
            mostrar_cardio_completo = True

            if es_pediatrico_va:
                sin_cardiopatia_ped = st.checkbox("✅ Paciente pediátrico sin patologías cardíacas conocidas", value=True, key="mod4_ped_sano")
                if sin_cardiopatia_ped:
                    mostrar_cardio_completo = False
                    st.info("👶 Evaluación cardiológica avanzada omitida por criterio de edad (Infante sano).")
                else:
                    mostrar_cardio_completo = False
                    st.markdown("#### 👶 Evaluación Cardiovascular Pediátrica Especializada")
                    c_ped1, c_ped2 = st.columns(2)
                    clase_ross = c_ped1.selectbox("Clase Funcional Pediátrica (Escala de Ross)", ["Clase I: Asintomático", "Clase II: Taquipnea o diaforesis leve en la alimentación. Disnea de esfuerzo en niños mayores.", "Clase III: Marcada taquipnea/diaforesis al alimentarse. Tiempo de toma prolongado. Retraso del crecimiento.", "Clase IV: Síntomas de insuficiencia cardíaca congestiva en reposo (retracciones, quejido)."], key="mod4_ross")
                    complejidad_cc = c_ped2.selectbox("Complejidad de la Cardiopatía Congénita (CC)", ["Leve (Bajo Riesgo): CC corregida sin shunts residuales o Estenosis Pulmonar leve.", "Moderada (Riesgo Intermedio): CC acianógena no corregida (CIV/CIA pequeñas), Fallot corregido, Coartación corregida.", "Severa (Alto Riesgo): Hipertensión Pulmonar (Eisenmenger), CC cianógenas, Ventrículo único, Miocardiopatías."], key="mod4_cc_complejidad")
                    capacidad_funcional = f"Complejidad CC: {complejidad_cc.split('(')[0].strip()}"
                    clase_nyha = f"Ross: {clase_ross.split(':')[0].strip()}"

            if mostrar_cardio_completo:
                st.markdown("#### 🏃 Capacidad Metabólica y Clase Funcional")
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
                
                st.divider()
                st.markdown("#### ⚡ Dispositivos Implantables")
                tiene_marcapasos = st.checkbox("⚙️ Paciente portador de Marcapasos o Desfibrilador Automático Implantable (DAI)", key="mod4_marcapasos")

        # ---------------------------------------------------------
        # MÓDULO 5: PRUEBAS DE LABORATORIO Y COAGULACIÓN
        # ---------------------------------------------------------
        with st.expander("5. Pruebas de Laboratorio y Coagulación", expanded=True):
            sin_laboratorios = st.checkbox("✅ No dispone o no requiere exámenes de laboratorio (Paciente sano)", value=True, key="mod5_sin_labs")

            hb_val = 14.0; hto_val = 42.0; plaquetas_val = 250000; urea_val = 30.0; creatinina_val = 0.8; albumina_serica = 3.5; sodio_serico = 140.0; potasio_serico = 4.0; cloro_serico = 102.0; bili_total = 1.0; tp_val = 12.0; ttpa_val = 30.0; inr_val = 1.0; tiene_gasometria = False
            ph_val = 7.40; paco2_val = 40.0; hco3_val = 24.0; pao2_val = 90.0; fio2_val = 21.0; be_val = 0.0; na_gas = 140.0; cl_gas = 102.0; lactato_val = 1.0
            glucosa_basal = 90.0; hba1c_val = 5.5; ver_metabolico = False
            cirrosis_activa = "Cirrosis Hepática" in antecedentes_seleccionados

            if not sin_laboratorios or cirrosis_activa:
                st.markdown("#### 🩸 Hemograma")
                c_lab1, c_lab2, c_lab3 = st.columns(3)
                hb_val = c_lab1.number_input("Hemoglobina (g/dL)", min_value=3.0, max_value=25.0, value=14.0, step=0.1, key="mod5_hb")
                hto_val = c_lab2.number_input("Hematocrito (%)", min_value=10.0, max_value=75.0, value=42.0, step=1.0, key="mod5_hto")
                plaquetas_val = c_lab3.number_input("Plaquetas (u/µL)", min_value=10000, max_value=1000000, value=250000, step=5000, key="mod5_plaq")
                st.divider()

                ver_metabolico = st.checkbox("🍬 Incluir Perfil Glucémico / Metabólico", value=True if "Diabetes" in str(antecedentes_seleccionados) else False, key="chk_grupo_metabolico")
                if ver_metabolico:
                    st.markdown("#### 🍬 Perfil Glucémico")
                    c_glu1, c_glu2 = st.columns(2)
                    glucosa_basal = c_glu1.number_input("Glucosa Basal (mg/dL)", min_value=20.0, max_value=800.0, value=90.0, step=1.0, key="mod5_glucosa")
                    hba1c_val = c_glu2.number_input("Hemoglobina Glicosilada (HbA1c %)", min_value=3.0, max_value=20.0, value=5.5, step=0.1, key="mod5_hba1c")
                    st.divider()

                ver_renal = st.checkbox("🧪 Incluir Función Renal y Proteínas", value=True, key="chk_grupo_renal")
                if ver_renal or cirrosis_activa:
                    st.markdown("#### 💾 Función Renal y Proteínas")
                    c_ren1, c_ren2, c_ren3 = st.columns(3)
                    urea_val = c_ren1.number_input("Urea (mg/dL)", min_value=5.0, max_value=300.0, value=30.0, step=1.0, key="mod5_urea")
                    creatinina_val = c_ren2.number_input("Creatinina Sérica (mg/dL)", min_value=0.1, max_value=20.0, value=0.8, step=0.1, key="mod5_creat")
                    albumina_serica = c_ren3.number_input("Albúmina Sérica (g/dL)", min_value=1.0, max_value=6.0, value=3.5, step=0.1, key="mod5_albu")
                    st.divider()

                ver_electrolitos = st.checkbox("⚡ Incluir Panel de Electrólitos Séricos", value=False, key="chk_grupo_elytes")
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

        # ---------------------------------------------------------
        # MÓDULO 6: RIESGO TROMBOEMBÓLICO Y EMETOGÉNICO
        # ---------------------------------------------------------
        titulo_mod6 = "6. Riesgo Emetogénico (Apfel)" if "Quirófano" in ambito_atencion else "6. Riesgo Tromboembólico (Caprini) y Emetogénico (Apfel)"
        with st.expander(titulo_mod6, expanded=True):
            st.markdown("#### 🤢 Riesgo de Náuseas y Vómitos Postoperatorios (Escala de Apfel)")
            apfel_historia = st.checkbox("🔸 Antecedente personal de NVPO o cinetosis (mareo por movimiento)", key="mod6_apfel_hist")
            apfel_opioides = st.checkbox("🔸 Previsión de uso de opioides potentes en el postoperatorio", key="mod6_apfel_op")

            caprini_clinicos = []
            caprini_quirurgicos = []
            caprini_altoriesgo = []

            if "Consulta Externa" in ambito_atencion:
                st.divider()
                st.markdown("#### 🧦 Prevención Cardiovascular: Riesgo Tromboembólico (Caprini)")
                caprini_clinicos = st.multiselect("Factores Médicos Particulares", options=["Venas varicosas superficiales sintomáticas (+1)", "Uso actual de anticonceptivos orales o terapia de reemplazo hormonal (+1)", "Sepsis o Infección médica aguda activa (< 1 mes) (+1)", "Cáncer activo o antecedente de malignidad sólida/hematológica (+2)"], key="mod6_cap_clin")
                caprini_quirurgicos = st.multiselect("Factores de Inmovilización y Procedimientos Especiales", options=["Cirugía artroscópica (+2)", "Inmovilización actual con yeso, férula o tracción (+2)", "Acceso venoso central permanente o catéter de diálisis (+2)", "Paciente encamado en reposo absoluto prolongado (> 72 horas) (+2)"], key="mod6_cap_cx")
                caprini_altoriesgo = st.multiselect("Antecedentes de Trombofilias y Eventos Graves", options=["Antecedente personal de TVP o Tromboembolismo Pulmonar (TEP) (+3)", "Historia familiar directa de trombosis u oclusión vascular (+3)", "Trombofilia congénita o adquirida confirmada por laboratorio (+3)", "ACV / Ictus isquémico reciente (< 1 mes) (+5)", "Fractura de cadera, pelvis o extremidad inferior (< 1 mes) (+5)", "Artroplastia electiva programada de cadera o rodilla (+5)", "Lesión medular aguda con paraplejía o cuadriplejía (< 1 mes) (+5)"], key="mod6_cap_alto")

# =============================================================================
# COLUMNA DERECHA: MONITOR METABÓLICO PERIOPERATORIO ESTÁTICO (STICKY)
# =============================================================================
with col_derecha:
    if hospital_valido:
        # Inyección de Insignias CSS y Sticky Block
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
                .badge {
                    padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85em; display: inline-block; margin-right: 8px; margin-bottom: 8px;
                }
                .badge-green { background-color: rgba(40, 167, 69, 0.15); color: #28a745; border: 1px solid #28a745; }
                .badge-yellow { background-color: rgba(255, 193, 7, 0.15); color: #ffc107; border: 1px solid #ffc107; }
                .badge-orange { background-color: rgba(253, 126, 20, 0.15); color: #fd7e14; border: 1px solid #fd7e14; }
                .badge-red { background-color: rgba(220, 53, 69, 0.15); color: #dc3545; border: 1px solid #dc3545; }
                .badge-dark { background-color: rgba(108, 117, 125, 0.15); color: #adb5bd; border: 1px solid #6c757d; }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 id='panel-de-control-perioperatorio'>📊 PANEL DE CONTROL PERIOPERATORIO</h3>", unsafe_allow_html=True)
        
        # ---------------------------------------------------------------------
        # 🧠 BLOQUE DE PROCESAMIENTO CENTRALIZADO (ESTABILIDAD DE VARIABLES)
        # ---------------------------------------------------------------------
        peso_calc = peso_real; talla_raw = talla_cm; talla_m = talla_raw / 100.0; imc_control = peso_calc / (talla_m ** 2) if talla_m > 0 else 0
        bsa_calc = math.sqrt((peso_calc * talla_raw) / 3600.0) if peso_calc > 0 and talla_raw > 0 else 0
        sexo_calc = sexo; edad_calc = edad; es_ped = edad_calc < 18; gs_calc = grupo_sangre; obs_calc = es_obstetrico
        caracter_calc = caracter_cx; riesgo_calc = riesgo_cx; asa_calc = asa_ps
        diag_calc = diagnostico_final; frac_calc = tiempo_fractura_cx; localizacion_frac_calc = tipo_fractura_cx
        proc_calc = procedimiento_final; anestesia_calc = tipo_anestesia; especialidad_calc = especialidad_cx; req_sangre_calc = req_sangre
        
        # --- ASA FINAL ---
        asa_final = asa_calc
        if caracter_calc in ["Urgencia", "Emergencia"] and "E" not in asa_final:
            asa_final += " - 'E' (Emergencia)"

        # --- SCORE CARDIOVASCULAR (LEE) ---
        desglose_lee = []
        lee_val = 0
        if "Alto" in riesgo_calc: desglose_lee.append("Cirugía de Alto Riesgo (+1 pt)"); lee_val += 1
        factor_cardiopatia_isq = 1 if (not sin_antecedentes and any("Isquémica" in p or "IAM" in p for p in antecedentes_seleccionados)) or cardio_angina else 0
        if factor_cardiopatia_isq > 0: desglose_lee.append("Cardiopatía Isquémica (+1 pt)"); lee_val += 1
        factor_insuf_cardiaca = 1 if (not sin_antecedentes and any(x in p for p in antecedentes_seleccionados for x in ["Insuficiencia", "Falla Cardíaca"])) or cardio_edema or cardio_disnea else 0
        if factor_insuf_cardiaca > 0: desglose_lee.append("Insuficiencia Cardíaca (+1 pt)"); lee_val += 1
        factor_acv = 1 if (not sin_antecedentes and any("ACV" in p or "Isquemia" in p for p in antecedentes_seleccionados)) else 0
        if factor_acv > 0: desglose_lee.append("Historia de ACV / AIT (+1 pt)"); lee_val += 1
        factor_insulina = 1 if (not sin_antecedentes and "Insulina" in medicacion_actual) else 0
        if factor_insulina > 0: desglose_lee.append("Diabetes insulinodependiente (+1 pt)"); lee_val += 1
        if creatinina_val > 2.0: desglose_lee.append("Creatinina > 2.0 mg/dL (+1 pt)"); lee_val += 1

        # --- SCORE VÍA AÉREA (ARNÉ) ---
        desglose_arne = []
        score_arne = 0
        if es_ped:
            if ped_vad_previo: desglose_arne.append("Intubación previa difícil (+12 pts)"); score_arne += 12
            if ped_retrognatia: desglose_arne.append("Micrognatia/Retrognatia (+6 pts)"); score_arne += 6
            if ped_macroglosia: desglose_arne.append("Macroglosia evidente (+6 pts)"); score_arne += 6
            if ped_cuello_corto: desglose_arne.append("Cuello corto/Inmóvil (+6 pts)"); score_arne += 6
        else:
            if arne_historia: desglose_arne.append("Antecedente Intubación Difícil (+10 pts)"); score_arne += 10
            if arne_patologia: desglose_arne.append("Patología de VAD (+5 pts)"); score_arne += 5
            if any(x in mallampati for x in ["Clase III", "Clase IV"]): desglose_arne.append(f"{mallampati.split(':')[0]} (+5 pts)"); score_arne += 5
            if "Clase III" in dtm: desglose_arne.append("DTM < 6.0 cm (+4 pts)"); score_arne += 4
            if "Clase III" in apertura_bucal: desglose_arne.append("Apertura Bucal Severa (+3 pts)"); score_arne += 3
            if "Normal" not in mov_cervical_arne: desglose_arne.append("Movilidad Limitada (+5 pts)"); score_arne += 5

        # --- SCORE VENTILACIÓN (OBESE) ---
        desglose_obese = []
        score_obese_total = 0
        if not es_ped:
            if imc_control > 26.0: desglose_obese.append("IMC > 26 kg/m² (+1 pt)"); score_obese_total += 1
            if vmd_barba: desglose_obese.append("Presencia de Barba (+1 pt)"); score_obese_total += 1
            if vmd_edentulo: desglose_obese.append("Edéntulo (+1 pt)"); score_obese_total += 1
            if sb_s: desglose_obese.append("Ronquido Fuerte (+1 pt)"); score_obese_total += 1
            if edad_calc > 55: desglose_obese.append("Edad > 55 años (+1 pt)"); score_obese_total += 1

        # --- SCORE AOS (STOP-BANG) ---
        desglose_sb = []
        score_stop_bang_total = 0
        if not es_ped:
            if sb_s: desglose_sb.append("Ronquido Fuerte (S) (+1 pt)"); score_stop_bang_total += 1
            if sb_t: desglose_sb.append("Cansancio/Fatiga (T) (+1 pt)"); score_stop_bang_total += 1
            if sb_o: desglose_sb.append("Apnea Observada (O) (+1 pt)"); score_stop_bang_total += 1
            if not sin_antecedentes and any(x in str(antecedentes_seleccionados) for x in ["Hipertensión", "HTA"]): desglose_sb.append("Hipertensión (P) (+1 pt)"); score_stop_bang_total += 1
            if imc_control > 35.0: desglose_sb.append("IMC > 35 kg/m² (B) (+1 pt)"); score_stop_bang_total += 1
            if edad_calc > 50: desglose_sb.append("Edad > 50 años (A) (+1 pt)"); score_stop_bang_total += 1
            if "Mayor a 40 cm" in cuello_cat: desglose_sb.append("Cuello > 40 cm (N) (+1 pt)"); score_stop_bang_total += 1
            if sexo_calc == "Masculino": desglose_sb.append("Sexo Masculino (G) (+1 pt)"); score_stop_bang_total += 1

        # --- SCORE PULMONAR POSTOPERATORIO (ARISCAT) ---
        desglose_ariscat = []
        score_ariscat_total = 0
        if not es_ped:
            if ariscat_infeccion_reciente: desglose_ariscat.append("Infección Respiratoria < 1 mes (+17 pts)"); score_ariscat_total += 17
            if ariscat_enfermedad_pulmonar: desglose_ariscat.append("EPOC / Asma / Neumopatía (+4 pts)"); score_ariscat_total += 4
            if 51 <= edad_calc <= 80: desglose_ariscat.append("Edad 51-80 años (+3 pts)"); score_ariscat_total += 3
            elif edad_calc > 80: desglose_ariscat.append("Edad > 80 años (+16 pts)"); score_ariscat_total += 16
            if hb_val <= 10.0: desglose_ariscat.append("Hemoglobina ≤ 10 g/dL (+11 pts)"); score_ariscat_total += 11
            if caracter_calc in ["Urgencia", "Emergencia"]: desglose_ariscat.append("Cirugía de Urgencia/Emergencia (+8 pts)"); score_ariscat_total += 8
            proc_upper = proc_calc.upper()
            if any(x in proc_upper for x in ["TORAC", "PULMON", "VATS", "LOBECTOMIA"]):
                desglose_ariscat.append("Incisión Torácica (+24 pts)"); score_ariscat_total += 24
            elif any(x in proc_upper for x in ["COLECIST", "GASTRO", "LAPAROTOM", "HEMICOLECTOMIA", "RESECCION INTESTINAL", "NEFRECTOMIA", "HISTERECTOM", "PROSTATECTOMIA"]):
                desglose_ariscat.append("Incisión Abdomen Superior (+15 pts)"); score_ariscat_total += 15
            if "Alto" in riesgo_calc: desglose_ariscat.append("Procedimiento de Alto Riesgo (+6 pts)"); score_ariscat_total += 6

        # --- SCORE NVPO (APFEL) ---
        desglose_apfel = []
        pts_apfel = 0
        if apfel_historia: desglose_apfel.append("Cinetosis / NVPO previa (+1 pt)"); pts_apfel += 1
        if apfel_opioides: desglose_apfel.append("Uso de opioides postop (+1 pt)"); pts_apfel += 1
        if sexo_calc == "Femenino": desglose_apfel.append("Sexo Femenino (+1 pt)"); pts_apfel += 1
        if sin_habitos or not hab_cigarrillo: desglose_apfel.append("No fumador (+1 pt)"); pts_apfel += 1

        # --- SCORE TROMBOEMBÓLICO (CAPRINI) ---
        desglose_caprini = []
        score_caprini = 0
        if "Consulta Externa" in ambito_atencion:
            if tipo_fractura_ant == "Menor a un mes" or frac_calc == "Menor a un mes": 
                desglose_caprini.append("Fractura / Trauma mayor < 1 mes (+5 pts)"); score_caprini += 5
            elif localizacion_frac_calc != "No aplica":
                pts = 5 if "Riesgo Caprini Extremo" in localizacion_frac_calc else 2
                desglose_caprini.append(f"Cirugía Ortopédica / Fractura (+{pts} pts)"); score_caprini += pts

            if 41 <= edad_calc <= 60: desglose_caprini.append("Edad 41-60 años (+1 pt)"); score_caprini += 1
            elif 61 <= edad_calc <= 74: desglose_caprini.append("Edad 61-74 años (+2 pts)"); score_caprini += 2
            elif edad_calc >= 75: desglose_caprini.append("Edad ≥ 75 años (+3 pts)"); score_caprini += 3

            if imc_control > 25.0: desglose_caprini.append("IMC > 25 kg/m² (+1 pt)"); score_caprini += 1
            if obs_calc: desglose_caprini.append("Embarazo o postparto (+1 pt)"); score_caprini += 1
            if "Alto" in riesgo_cx or "Intermedio" in riesgo_cx: desglose_caprini.append("Cirugía Mayor (>45min) (+2 pts)"); score_caprini += 2
            else: desglose_caprini.append("Cirugía Menor (<45min) (+1 pt)"); score_caprini += 1
            if cardio_edema: desglose_caprini.append("Edema de miembros inferiores (+1 pt)"); score_caprini += 1

            for f in caprini_clinicos: 
                v = 1 if "(+1)" in f else 2
                desglose_caprini.append(f"{f.rsplit('(', 1)[0].strip()} (+{v} pts)"); score_caprini += v
            for f in caprini_quirurgicos: 
                v = 2 if "(+2)" in f else 0
                if v > 0: desglose_caprini.append(f"{f.rsplit('(', 1)[0].strip()} (+{v} pts)"); score_caprini += v
            for f in caprini_altoriesgo: 
                v = 3 if "(+3)" in f else 5
                desglose_caprini.append(f"{f.rsplit('(', 1)[0].strip()} (+{v} pts)"); score_caprini += v

        # =====================================================================
        # 📈 RENDERIZADO VISUAL DEL MONITOR (Pestañas)
        # =====================================================================
        tab1, tab2 = st.tabs(["🔢 Cálculos y Escalas", "📄 Reporte Final"])
        
        with tab1:
            st.markdown("##### 🕸️ Vistazo de Riesgo Perioperatorio")
            r_cardio = min(lee_val + 1, 5)
            r_pulm = 1 if score_ariscat_total < 26 else (3 if score_ariscat_total < 45 else 5)
            
            r_tromb = 1
            if "Consulta Externa" in ambito_atencion:
                r_tromb = 1 if score_caprini == 0 else (2 if score_caprini <= 2 else (3 if score_caprini <= 4 else (4 if score_caprini <= 8 else 5)))
                
            r_nvpo = 1 if pts_apfel <= 1 else (3 if pts_apfel == 2 else 5)
            r_va = 1
            if score_arne > 10: r_va = 5
            elif score_stop_bang_total >= 5 or score_obese_total >= 2: r_va = 4
            elif score_stop_bang_total >= 3: r_va = 3

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[r_cardio, r_pulm, r_va, r_nvpo, r_tromb, r_cardio],
                theta=['Cardiovascular', 'Pulmonar', 'Vía Aérea', 'NVPO', 'Tromboembólico', 'Cardiovascular'],
                fill='toself',
                fillcolor='rgba(220, 53, 69, 0.2)' if any(v>=4 for v in [r_cardio, r_pulm, r_va, r_nvpo, r_tromb]) else 'rgba(40, 167, 69, 0.2)',
                line=dict(color='#dc3545' if any(v>=4 for v in [r_cardio, r_pulm, r_va, r_nvpo, r_tromb]) else '#28a745', width=2),
                hoverinfo="text",
                text=[f"Nivel de Riesgo: {v}/5" for v in [r_cardio, r_pulm, r_va, r_nvpo, r_tromb, r_cardio]]
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 5], tickvals=[1,2,3,4,5], ticktext=['Mín','Leve','Mod','Alto','Crítico'], gridcolor="rgba(255,255,255,0.1)"),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
                ),
                showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=40, r=40), height=300
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🧮 Espejo Clínico y Volúmenes")
            
            asa_base = asa_final.split(":")[0].strip()
            if "I" in asa_base and "II" not in asa_base and "V" not in asa_base: color_asa = "badge-green"
            elif "II" in asa_base and "III" not in asa_base: color_asa = "badge-yellow"
            elif "III" in asa_base: color_asa = "badge-orange"
            else: color_asa = "badge-red"

            badge_html = f"""
            <div style='display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 15px;'>
                <span class='badge {color_asa}'>🛡️ {asa_final}</span>
                <span class='badge {"badge-red" if not sin_alergias else "badge-green"}'>{'🚨 ALERGIAS' if not sin_alergias else '✅ SIN ALERGIAS'}</span>
                <span class='badge badge-dark'>🩸 Grupo {gs_calc}</span>
                <span class='badge {"badge-orange" if req_sangre_calc else "badge-dark"}'>{'🩸 RESERVAR SANGRE' if req_sangre_calc else '✅ SIN RESERVA SANGUÍNEA'}</span>
            </div>
            """
            st.markdown(badge_html, unsafe_allow_html=True)
            
            if peso_calc > 0 and talla_raw > 0:
                if es_ped:
                    if edad_calc == 0: peso_esperado = 7.5; talla_esperada = 65.0
                    elif 1 <= edad_calc <= 5: peso_esperado = (edad_calc * 2) + 8; talla_esperada = (edad_calc * 6) + 77
                    elif 6 <= edad_calc <= 12: peso_esperado = (edad_calc * 3) + 7; talla_esperada = (edad_calc * 6) + 77
                    else:  
                        if talla_raw >= 152.4:
                            peso_esperado = 50.0 + 2.3 * ((talla_raw / 2.54) - 60.0) if sexo_calc == "Masculino" else 45.5 + 2.3 * ((talla_raw / 2.54) - 60.0)
                        else: peso_esperado = (edad_calc * 3.3) + 5  
                        talla_esperada = 162.0 if sexo_calc == "Femenino" else 173.0

                    porcentaje_peso = (peso_calc / peso_esperado) * 100
                    if porcentaje_peso < 80: cat_ped = "Desnutrición Severa 🚨"
                    elif porcentaje_peso < 90: cat_ped = "Bajo Peso / Delgadez ⚠️"
                    elif porcentaje_peso <= 115: cat_ped = "Eutrófico (Normal) ✅"
                    elif porcentaje_peso <= 130: cat_ped = "Sobrepeso Pediátrico ⚠️"
                    else: cat_ped = "Obesidad Pediátrica 🚨"

                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.metric(label="BMI / IMC Pediátrico", value=f"{imc_control:.1f} kg/m²", delta=cat_ped, delta_color="normal")
                        st.metric(label="Peso Esperado p/Edad", value=f"{peso_esperado:.1f} kg")
                    with m_col2:
                        st.metric(label="Superficie Corporal (BSA)", value=f"{bsa_calc:.2f} m²")
                        st.metric(label="Talla Esperada p/Edad", value=f"{talla_esperada:.1f} cm")

                else:
                    if talla_raw < 152.4:
                        peso_ideal = peso_calc; peso_predicho = peso_calc
                        st.info("ℹ️ **Nota:** Talla < 152.4 cm. Fórmulas de peso ideal omitidas por margen de error matemático.")
                    else:
                        if sexo_calc == "Masculino":
                            peso_ideal = 50.0 + 2.3 * ((talla_raw / 2.54) - 60.0)
                            peso_predicho = 50.0 + 0.91 * (talla_raw - 152.4)
                        else:
                            peso_ideal = 45.5 + 2.3 * ((talla_raw / 2.54) - 60.0)
                            peso_predicho = 45.5 + 0.91 * (talla_raw - 152.4)
                    
                    if peso_calc > peso_ideal:
                        peso_ajustado_20 = peso_ideal + 0.20 * (peso_calc - peso_ideal)
                        peso_ajustado_40 = peso_ideal + 0.40 * (peso_calc - peso_ideal)
                    else:
                        peso_ajustado_20 = peso_calc; peso_ajustado_40 = peso_calc
                    
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
                        st.warning(f"⚠️ **Alerta Obesidad.** Ajuste volúmenes (ARDSNet) y calcule fármacos lipofílicos según peso ideal/ajustado.")
                
                st.divider()
                st.markdown("##### 🏥 Contexto Quirúrgico y Planificación")
                st.markdown(f"**Ámbito de Atención:** *{ambito_atencion}*")
                st.markdown(f"**Especialidad Quirúrgica:** *{especialidad_calc}*")
                st.markdown(f"**Carácter Quirúrgico:** *{caracter_calc}*")
                st.markdown(f"**Riesgo Quirúrgico (AHA/ACC):** *{riesgo_calc}*")
                
                if "Quirófano / Emergencia" in ambito_atencion:
                    st.markdown(f"**Estatus NPO:** {horas_ayuno} horas de ayuno para *{tipo_ayuno}*")
                    if obs_calc: st.markdown(f"**Edad Gestacional Activa:** **{semanas_eg} semanas**")
                    
                    ayuno_insuficiente = False
                    if "Sólidos" in tipo_ayuno and horas_ayuno < 8: ayuno_insuficiente = True
                    elif "formula" in tipo_ayuno and horas_ayuno < 6: ayuno_insuficiente = True
                    elif "materna" in tipo_ayuno and horas_ayuno < 4: ayuno_insuficiente = True
                    elif "Líquidos claros" in tipo_ayuno and horas_ayuno < 2: ayuno_insuficiente = True
                    
                    if ayuno_insuficiente or (obs_calc and semanas_eg > 12) or caracter_calc == "Emergencia":
                        st.error("🚨 **ALERTA: RIESGO DE ESTÓMAGO LLENO:** Alto riesgo de broncoaspiración activa. Se exige **Inducción de Secuencia Rápida (ISR)**.")
                    else: st.success("🟢 **Seguridad de Vía Aérea:** Tiempos de ayuno conformes a directrices formales ASA.")
                    if obs_calc and semanas_eg >= 20: st.warning(f"⚠️ **ALERTA COMPRESIÓN AORTOCAVA:** Desplazamiento uterino a la izquierda de 15°.")
                
                st.markdown(f"**Diagnóstico Principal:** **{diag_calc}**")
                if frac_calc != "No aplica": st.markdown(f"**Evolución del Trauma:** ⏱️ *{frac_calc}*")
                st.markdown(f"**Procedimiento Quirúrgico:** **{proc_calc}**")
                st.divider()
                st.success(f"💉 **Estrategia Anestésica:** **{anestesia_calc}**")
                
                if req_sangre_calc: st.error("🩸 **REQUERIMIENTO TRANSFUSIONAL ACTIVO:** Verificar pruebas cruzadas.")

                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 2: SEGURIDAD, ALERGIAS Y ANTECEDENTES
                # =====================================================================
                st.subheader("🛡️ Seguridad y Antecedentes (Módulo 2)")
                
                al_med_list = formatear_lista(alergias_med, otras_alergias_med_txt)
                al_ali_list = formatear_lista(alergias_alim, otras_alergias_ali_txt)
                app_list = formatear_lista(antecedentes_seleccionados, otros_antecedentes_txt)
                meds_list = formatear_lista(medicacion_actual, notas_medicacion_txt)
                
                if not sin_alergias:
                    if al_med_list: st.error(f"🚨 **Alergia Farmacológica:** {', '.join(al_med_list)}")
                    if al_ali_list: st.warning(f"⚠️ **Alergia Alimentaria:** {', '.join(al_ali_list)}")

                if sin_antecedentes: st.info("✅ **Historial Clínico:** Sin antecedentes patológicos ni medicación continua.")
                else:
                    if app_list and app_list != ["Ninguno"]:
                        st.markdown(f"**🩺 Patologías (APP):** {', '.join(app_list)}")
                        if "Cirrosis Hepática" in app_list: st.caption(f"🟡 *Child-Pugh Ascitis {child_ascitis} | Encefalopatía {child_encefalo}*")
                    else: st.markdown("**🩺 Patologías (APP):** Ninguna reportada.")

                    if meds_list and meds_list != ["Ninguno"]: st.markdown(f"**💊 Medicación Habitual:** {', '.join(meds_list)}")
                    else: st.markdown("**💊 Medicación Habitual:** Ninguna reportada.")
                        
                if not sin_habitos:
                    habitos_activos = []
                    if hab_cigarrillo: habitos_activos.append(f"🚬 Tabaco ({int_cigarrillo})")
                    if hab_alcohol: habitos_activos.append(f"🍷 Alcohol ({int_alcohol})")
                    if hab_cafe: habitos_activos.append(f"☕ Café ({int_cafe})")
                    if hab_drogas: 
                        habitos_activos.append(f"💊 Sustancias ({int_drogas})")
                        if txt_drogas.strip() != "": habitos_activos[-1] += f" *({txt_drogas.strip()})*"
                    if habitos_activos: st.markdown(f"**🚬 Hábitos:** {' | '.join(habitos_activos)}")
                else: st.success("✅ **Hábitos de Riesgo:** Negados / Estilo de vida saludable.")
                        
                st.divider()

                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 3: VÍA AÉREA Y RIESGO RESPIRATORIO
                # =====================================================================
                st.subheader("🫁 Vía Aérea y Predictores Dinámicos (Módulo 3)")
                
                if es_ped:
                    m3_col1, m3_col2 = st.columns(2)
                    with m3_col1: 
                        st.metric(label="Riesgo de VAD Estructural", value=f"{score_arne} pts")
                        if desglose_arne:
                            with st.expander("🔍 Ver desglose de puntos"):
                                for item in desglose_arne: st.markdown(f"- {item}")
                    with m3_col2:
                        score_pulmonar_ped = 0
                        if ped_ivra: score_pulmonar_ped += 1
                        if ped_estridor: score_pulmonar_ped += 1
                        if ariscat_infeccion_reciente: score_pulmonar_ped += 1

                        st.metric(label="Criterios de Hiperreactividad", value=f"{score_pulmonar_ped} / 3")
                        if score_pulmonar_ped > 0:
                            with st.expander("🔍 Ver desglose de puntos"):
                                if ped_ivra: st.markdown("- IVRA reciente (< 2 sem) (+1 pt)")
                                if ped_estridor: st.markdown("- Historia de estridor (+1 pt)")
                                if ariscat_infeccion_reciente: st.markdown("- Infección respiratoria activa (+1 pt)")
                    
                    if ped_vad_previo: st.error("🚨 **ALERTA CRÍTICA:** Antecedente de intubación fallida/difícil. Prepare algoritmo de VAD pediátrica.")
                    elif score_arne >= 6: st.error(f"🚨 **Riesgo de VAD Elevado ({score_arne} pts):** Malformación craneofacial activa.")
                    else: st.success("🟢 **Índice de Intubación Pediátrica:** Sin malformaciones anatómicas.")

                    if score_pulmonar_ped > 0:
                        st.error("🚨 **ALERTA DE RESPUESTA LARÍNGEA SEVERA:** Alto riesgo de laringoespasmo.")
                        st.info("💡 **Justificación de Tesis:** Uso recomendado de **Lidocaína Intravenosa (0.6 mg/kg/h)** para deprimir los reflejos de la vía aérea en la extubación.")
                    else: st.success("🟢 **Riesgo Resonador/Reflejo:** Vía aérea reactiva basal estable.")
                
                else:
                    estrato_obese = "Riesgo Alto de Ventilación 🚨" if score_obese_total >= 2 else "Riesgo Bajo de Ventilación"
                    estrato_sb = "Riesgo Alto para AOS 🚨" if score_stop_bang_total >= 5 else ("Riesgo Intermedio para AOS" if score_stop_bang_total >= 3 else "Riesgo Bajo para AOS")
                    estrato_ariscat = "Riesgo Alto (~42.1% RCP) 🚨" if score_ariscat_total >= 45 else ("Riesgo Moderado (~13.3% RCP)" if score_ariscat_total >= 26 else "Riesgo Bajo (~1.6% RCP)")

                    row1_col1, row1_col2 = st.columns(2)
                    with row1_col1: 
                        st.metric(label="Arné (Intubación)", value=f"{score_arne} pts")
                        if desglose_arne:
                            with st.expander("🔍 Ver desglose de puntos"):
                                for item in desglose_arne: st.markdown(f"- {item}")
                    with row1_col2: 
                        st.metric(label="OBESE (Ventilación)", value=f"{score_obese_total} pts")
                        if desglose_obese:
                            with st.expander("🔍 Ver desglose de puntos"):
                                for item in desglose_obese: st.markdown(f"- {item}")
                    
                    row2_col1, row2_col2 = st.columns(2)
                    with row2_col1: 
                        st.metric(label="STOP-Bang (Apnea)", value=f"{score_stop_bang_total} pts")
                        if desglose_sb:
                            with st.expander("🔍 Ver desglose de puntos"):
                                for item in desglose_sb: st.markdown(f"- {item}")
                    with row2_col2: 
                        st.metric(label="ARISCAT (Pulmonar)", value=f"{score_ariscat_total} pts")
                        if desglose_ariscat:
                            with st.expander("🔍 Ver desglose de puntos"):
                                for item in desglose_ariscat: st.markdown(f"- {item}")
                    
                    if score_arne <= 10: st.success(f"🟢 **Índice de Intubación:** Riesgo Bajo ({score_arne} pts).")
                    else: st.error(f"🚨 **ALERTA:** Índice de Intubación Difícil Elevado ({score_arne} pts).")

                    if score_obese_total >= 2: st.error(f"🚨 **Índice de Ventilación (OBESE):** {estrato_obese}.")
                    else: st.success("🟢 **Índice de Ventilación:** Riesgo Bajo con Máscara.")

                    if score_stop_bang_total >= 5: st.warning(f"⚠️ **STOP-Bang:** {estrato_sb}.")
                    if score_ariscat_total >= 45: st.error(f"🚨 **Riesgo Pulmonar (ARISCAT):** {estrato_ariscat}.")
                    
                    hallazgos_va = []
                    if any(x in mallampati for x in ["III", "IV"]): hallazgos_va.append("👅 Mallampati Alto")
                    if "Clase III" in dtm: hallazgos_va.append("📐 DTM Corta")
                    if "Clase III" in apertura_bucal: hallazgos_va.append("👄 Apertura Limitada")
                    if vad_retrognatia: hallazgos_va.append("🦷 Retrognatia")
                    if hallazgos_va: st.warning(f"⚠️ **Alertas Anatómicas:** {' | '.join(hallazgos_va)}")
                
                st.divider()

                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 4: EVALUACIÓN CARDIOVASCULAR (MÓDULO 4)
                # =====================================================================
                st.subheader("🫀 Monitor Cardiovascular y Riesgo (Módulo 4)")

                if es_ped:
                    if sin_cardiopatia_ped:
                        st.success("✅ **Cardiología Pediátrica:** Lactante / Infante sano sin cardiopatía conocida.")
                    else:
                        m4_col1, m4_col2 = st.columns(2)
                        with m4_col1: st.metric(label="Clase Funcional (Ross)", value=clase_nyha)
                        with m4_col2: st.metric(label="Complejidad de la CC", value=capacidad_funcional)
                        
                        if "Severa" in capacidad_funcional or "IV" in clase_nyha: st.error("🚨 **ALERTA CC COMPLEJA:** Alto riesgo de inestabilidad hemodinámica intraoperatoria.")
                        else: st.warning("⚠️ **Riesgo Intermedio Pediátrico:** Cardiopatía congénita moderada/leve.")
                
                else:
                    if lee_val == 0: clase_lee = "Clase I (Riesgo Bajo ~0.4%)"; color_lee = "normal"
                    elif lee_val == 1: clase_lee = "Clase II (Riesgo Moderado ~0.9%)"; color_lee = "normal"
                    elif lee_val == 2: clase_lee = "Clase III (Riesgo Alto ~6.6%) ⚠️"; color_lee = "inverse"
                    else: clase_lee = "Clase IV (Riesgo Muy Alto ~11%) 🚨"; color_lee = "inverse"
                        
                    m4_col1, m4_col2 = st.columns(2)
                    with m4_col1: 
                        st.metric(label="Índice de Lee (RCRI)", value=f"{lee_val} pts", delta=clase_lee, delta_color=color_lee)
                        if desglose_lee:
                            with st.expander("🔍 Ver desglose de puntos"):
                                for item in desglose_lee: st.markdown(f"- {item}")
                    with m4_col2:
                        if fevi_disponible:
                            delta_fevi = "Normal ✅" if fevi_valor >= 50.0 else ("Disfunción Moderada ⚠️" if fevi_valor >= 40.0 else "Disfunción Severa 🚨")
                            st.metric(label="FEVI (Ecocardiograma)", value=f"{fevi_valor:.0f}%", delta=delta_fevi)
                        else:
                            estrato_mets = "Limitada (<4 METs) ⚠️" if "Limitada" in capacidad_funcional or "Severamente" in capacidad_funcional else "Adecuada (≥4 METs) ✅"
                            st.metric(label="Reserva Metabólica", value=estrato_mets)

                    if lee_val >= 2 or "Limitada" in capacidad_funcional or "Severamente" in capacidad_funcional:
                        st.error(f"🚨 **ALERTA DE RIESGO CARDÍACO MAYOR:** Paciente en {clase_lee}. Evite taquicardia intraoperatoria.")
                    else: st.success("🟢 **Riesgo Cardiovascular Basal:** Adecuada reserva miocárdica.")
                        
                    sintomas_cardio = []
                    if cardio_angina: sintomas_cardio.append("💔 Angina Inestable")
                    if cardio_disnea: sintomas_cardio.append("🫁 Disnea de causa cardíaca")
                    if cardio_palpitaciones: sintomas_cardio.append("💓 Palpitaciones/Síncope")
                    if cardio_edema: sintomas_cardio.append("🦶 Edema maleolar reciente")
                    if cardio_soplo: sintomas_cardio.append("🩺 Soplo patológico")
                    
                    if sintomas_cardio: st.error(f"🚨 **SÍNTOMAS CARDIOVASCULARES ACTIVOS:** Inestabilidad clínica: {', '.join(sintomas_cardio)}.")
                    if "Normal" not in ecg_hallazgo and "No disponible" not in ecg_hallazgo: st.warning(f"⚠️ **Hallazgo ECG Crítico:** Se registra `{ecg_hallazgo}`. Monitorice DII y V5.")
                    if tiene_marcapasos: st.error("🚨 **ALERTA ELECTROQUIRÚRGICA:** Paciente portador de Marcapasos/DAI. Riesgo de inhibición. Solicite uso de electrobisturí BIPOLAR y tenga imán disponible.")

                st.divider()

                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 5: EXÁMENES DE LABORATORIO Y COAGULACIÓN
                # =====================================================================
                st.subheader("🧪 Laboratorio Clínico y Coagulación (Módulo 5)")
                
                if sin_laboratorios and not cirrosis_activa:
                    st.success("✅ **Laboratorios:** No solicitados / Paciente calificado clínicamente como sano.")
                else:
                    l_col1, l_col2 = st.columns(2)
                    with l_col1:
                        st.markdown("**🩸 Serie Roja y Plaquetas**")
                        st.markdown(f"* Hemoglobina: **{hb_val:.1f} g/dL**")
                        st.markdown(f"* Hematocrito: **{hto_val:.0f}%**")
                        st.markdown(f"* Plaquetas: **{plaquetas_val:,} u/µL**")
                    with l_col2:
                        st.markdown("**⏱️ Perfil de Hemostasia**")
                        st.markdown(f"* Tiempo de Protrombina (TP): **{tp_val:.1f} seg**")
                        st.markdown(f"* TTPa: **{ttpa_val:.1f} seg**")
                        st.markdown(f"* INR: **{inr_val:.2f}**")
                    
                    st.markdown("##### 🔍 Alertas de Seguridad Analítica:")
                    if plaquetas_val < 100000 and "Regional" in anestesia_calc: st.error(f"🚨 **CONTRAINDICACIÓN ABSOLUTA DE NEUROEJE:** Con solo **{plaquetas_val:,} u/µL** plaquetas, existe riesgo crítico de hematoma epidural/espinal. Cambie la estrategia a Anestesia General.")
                    elif plaquetas_val < 150000: st.warning(f"⚠️ **Trombocitopenia Moderada:** ({plaquetas_val:,} u/µL).")
                        
                    if hb_val < 10.0: st.error(f"🚨 **Anemia Significativa (Hb {hb_val:.1f} g/dL):** Asegure reserva de hematíes en banco de sangre.")
                    elif (sexo_calc == "Femenino" and hb_val < 12.0) or (sexo_calc == "Masculino" and hb_val < 13.0): st.caption(f"⚠️ *Anemia leve marginal ({hb_val:.1f} g/dL).*")

                    if inr_val > 1.5 or tp_val > 15.0: st.error(f"🚨 **COAGULOPATÍA ACTIVA:** INR elevado (**{inr_val:.2f}**). Alto riesgo de sangrado.")

                    if ver_metabolico or (not sin_antecedentes and "Diabetes" in str(antecedentes_seleccionados)):
                        if glucosa_basal > 180: st.warning(f"⚠️ **Hiperglucemia Preoperatoria ({glucosa_basal:.0f} mg/dL):** Riesgo de cetoacidosis e infección de herida. Considere corrección.")
                        elif glucosa_basal < 70: st.error(f"🚨 **HIPOGLUCEMIA CRÍTICA ({glucosa_basal:.0f} mg/dL):** Riesgo de daño neurológico. Administre Dextrosa IV inmediatamente.")
                        if hba1c_val >= 8.0: st.warning(f"⚠️ **Mal Control Metabólico Crónico (HbA1c {hba1c_val:.1f}%):** Aumento del riesgo de complicaciones cardiovasculares.")

                    detalles_organicos = []
                    if not sin_laboratorios or cirrosis_activa:
                        detalles_organicos.append(f"Creatinina: **{creatinina_val:.2f} mg/dL**")
                        detalles_organicos.append(f"Urea: **{urea_val:.0f} mg/dL**")
                        detalles_organicos.append(f"Albúmina: **{albumina_serica:.1f} g/dL**")
                    if cirrosis_activa: detalles_organicos.append(f"Bilirrubina: **{bili_total:.1f} mg/dL**")
                    if ver_metabolico or (not sin_antecedentes and "Diabetes" in str(antecedentes_seleccionados)):
                        detalles_organicos.append(f"Glucosa: **{glucosa_basal:.0f} mg/dL**")
                        detalles_organicos.append(f"HbA1c: **{hba1c_val:.1f}%**")
                        
                    if detalles_organicos:
                        st.markdown("**💾 Función Renal / Hepática / Metabólica:**")
                        st.markdown(" | ".join(detalles_organicos))

                    if tiene_gasometria:
                        st.markdown("---")
                        st.markdown("##### 🫁 Diagnóstico Ácido-Base (AGA)")
                        
                        estado_ab = "Normal"
                        if ph_val < 7.35:
                            if paco2_val > 45 and hco3_val <= 26: estado_ab = "Acidosis Respiratoria"
                            elif hco3_val < 22 and paco2_val <= 40: estado_ab = "Acidosis Metabólica"
                            elif paco2_val > 45 and hco3_val < 22: estado_ab = "Acidosis Mixta"
                            else: estado_ab = "Acidemia (Trastorno en compensación)"
                        elif ph_val > 7.45:
                            if paco2_val < 35 and hco3_val >= 22: estado_ab = "Alcalosis Respiratoria"
                            elif hco3_val > 26 and paco2_val >= 35: estado_ab = "Alcalosis Metabólica"
                            elif paco2_val < 35 and hco3_val > 26: estado_ab = "Alcalosis Mixta"
                            else: estado_ab = "Alcalemia (Trastorno en compensación)"
                        else:
                            if paco2_val > 45 and hco3_val > 26: estado_ab = "Trastorno Mixto (Acidosis Resp. + Alcalosis Met.) compensado"
                            elif paco2_val < 35 and hco3_val < 22: estado_ab = "Trastorno Mixto (Alcalosis Resp. + Acidosis Met.) compensado"
                        
                        color_ph = "normal" if "Normal" in estado_ab else ("inverse" if "Acid" in estado_ab else "off")
                        st.metric(label="Diagnóstico Ácido-Base Primario", value=estado_ab, delta=f"pH: {ph_val:.2f}", delta_color=color_ph)

                        pafi = pao2_val / (fio2_val / 100.0) if fio2_val >= 21.0 else pao2_val / 0.21
                        anion_gap = na_gas - (cl_gas + hco3_val)
                        ag_corregido = anion_gap + 2.5 * (4.5 - (albumina_serica if albumina_serica > 1.0 else 1.0))
                        
                        PB = 760; PH2O = 47
                        PIO2 = (fio2_val / 100.0) * (PB - PH2O)
                        PAO2 = PIO2 - (paco2_val / 0.8)
                        gradiente_Aa = PAO2 - pao2_val
                        
                        winters_paco2 = (1.5 * hco3_val) + 8
                        winters_min = winters_paco2 - 2
                        winters_max = winters_paco2 + 2

                        g_col1, g_col2 = st.columns(2)
                        with g_col1:
                            st.markdown(f"* PaCO2: **{paco2_val:.0f} mmHg**")
                            st.markdown(f"* HCO3- Actual: **{hco3_val:.1f} mEq/L**")
                            st.markdown(f"* Lactato Sérico: **{lactato_val:.1f} mmol/L**")
                            st.markdown(f"* Exceso de Base (BE): **{be_val:.1f}**")
                            
                            if "Acidosis Metabólica" in estado_ab:
                                if paco2_val < winters_min: comp_winters = "Sobrecompensación (Alcalosis Respiratoria agregada)"
                                elif paco2_val > winters_max: comp_winters = "Subcompensación (Acidosis Respiratoria agregada)"
                                else: comp_winters = "Compensación respiratoria adecuada"
                                st.caption(f"📏 **Winters (PaCO2 Esperada):** {winters_min:.1f} - {winters_max:.1f} mmHg. *{comp_winters}*")
                                
                        with g_col2:
                            st.metric(label="Anion Gap (Corregido p/ Albúmina)", value=f"{ag_corregido:.1f} mEq/L", help="Rango normal: 8 - 12 mEq/L.")
                            st.metric(label="Índice de Kirby (PaO2/FiO2)", value=f"{pafi:.0f} mmHg")
                            st.metric(label="Gradiente A-a de O2", value=f"{gradiente_Aa:.1f} mmHg")
                        
                        if pafi < 200: st.error(f"🚨 **INSUFICIENCIA RESPIRATORIA CRÍTICA:** Kirby gravemente comprometido (**{pafi:.0f} mmHg**).")
                        if ag_corregido > 12 and "Acidosis Metabólica" in estado_ab: st.warning(f"⚠️ **Acidosis Metabólica con Anion Gap Elevado ({ag_corregido:.1f}):** Considere Cetoacidosis, Uremia o Láctico.")

                st.divider()

                # =====================================================================
                # PESTAÑA 1 - SECCIÓN 6: EMETOGÉNESIS Y TROMBOFILIA
                # =====================================================================
                st.subheader("🤢 Emetogénesis y Trombofilia (Módulo 6)")

                if pts_apfel <= 1: estrato_apfel = "Riesgo Bajo (~10-20%)"; color_apfel = "normal"
                elif pts_apfel == 2: estrato_apfel = "Riesgo Moderado (~40%)"; color_apfel = "normal"
                else: estrato_apfel = "Riesgo Alto (~60-80%) 🚨"; color_apfel = "inverse"
                    
                if "Consulta Externa" in ambito_atencion:
                    if score_caprini == 0: estrato_caprini = "Riesgo Mínimo (<0.5%)"; color_caprini = "normal"
                    elif 1 <= score_caprini <= 2: estrato_caprini = "Riesgo Bajo (~1.5%)"; color_caprini = "normal"
                    elif 3 <= score_caprini <= 4: estrato_caprini = "Riesgo Moderado (~3.0%) ⚠️"; color_caprini = "off"
                    elif 5 <= score_caprini <= 8: estrato_caprini = "Riesgo Alto (~6.0%) 🚨"; color_caprini = "inverse"
                    else: estrato_caprini = "Riesgo Muy Alto (>11%) 🚨"; color_caprini = "inverse"
                else:
                    estrato_caprini = "No evaluado en Quirófano"; color_caprini = "off"
                    
                m6_col1, m6_col2 = st.columns(2)
                with m6_col1: 
                    st.metric(label="Escala de Apfel (NVPO)", value=f"{pts_apfel} / 4 pts", delta=estrato_apfel, delta_color=color_apfel)
                    if desglose_apfel:
                        with st.expander("🔍 Ver desglose de puntos"):
                            for item in desglose_apfel: st.markdown(f"- {item}")
                with m6_col2: 
                    if "Consulta Externa" in ambito_atencion:
                        st.metric(label="Score de Caprini (ETV)", value=f"{score_caprini} pts", delta=estrato_caprini, delta_color=color_caprini)
                        if desglose_caprini:
                            with st.expander("🔍 Ver desglose de puntos"):
                                for item in desglose_caprini: st.markdown(f"- {item}")
                    else:
                        st.metric(label="Score de Caprini (ETV)", value="No aplica", delta=estrato_caprini, delta_color=color_caprini, help="La profilaxis tromboembólica detallada se evalúa típicamente en Consulta Externa.")
                    
                st.markdown("##### 🔍 Directrices de Profilaxis Perioperatoria:")
                if pts_apfel >= 3:
                    st.error(f"🚨 **ALERTA NVPO CRÍTICA:** Exige **Estrategia Multimodal Profiláctica**: Dexametasona 4 mg IV + Ondansetrón 4 mg IV.")
                    st.info("💡 **Aporte de Tesis:** La infusión de Lidocaína IV reduce el consumo de opioides intraoperatorios, atacando la emetogénesis basal.")
                elif pts_apfel == 2: st.warning(f"⚠️ **Profilaxis Apfel Moderada:** Ondansetrón 4 mg IV previo a la emersión.")
                else: st.success("🟢 **Emetogénesis Controlada:** Riesgo bajo de NVPO.")
                    
                if "Consulta Externa" in ambito_atencion:
                    if score_caprini >= 5: st.error(f"🚨 **ALERTA RIESGO TROMBOEMBÓLICO ALTO/MUY ALTO ({score_caprini} pts):** Indicación mandatoria de **Profilaxis Combinada**: Medidas mecánicas + HBPM (Enoxaparina 40 mg SC cada 24h).")
                    elif 3 <= score_caprini <= 4: st.warning(f"⚠️ **Riesgo Caprini Moderado ({score_caprini} pts):** Se recomienda profilaxis farmacológica (HBPM) o medidas mecánicas.")
                    elif 1 <= score_caprini <= 2: st.info(f"🔹 **Riesgo Caprini Bajo ({score_caprini} pts):** Considere el uso de medias elásticas compresivas.")
                    else: st.success("🟢 **Riesgo Tromboembólico Mínimo:** Solo se aconseja deambulación temprana, activa y frecuente.")

        # =====================================================================
        # PESTAÑA 2: GENERACIÓN DE REPORTE Y HISTORIA CLÍNICA COPIABLE
        # =====================================================================
        with tab2:
            st.subheader("📄 Nota de Valoración Preanestésica")
            st.caption("Haga clic en el ícono de copiar para trasladar la nota estructurada a tu historial clínico:")
            
            txt_alergias_final = "NEGADAS."
            if not sin_alergias:
                componentes_al = []
                if al_med_list: componentes_al.append(f"Fármacos: {', '.join(al_med_list)}")
                if al_ali_list: componentes_al.append(f"Alimentarias: {', '.join(al_ali_list)}")
                if componentes_al: txt_alergias_final = " | ".join(componentes_al)

            txt_app_final = "NEGADOS."
            if not sin_antecedentes:
                if app_list and app_list != ["Ninguno"]: 
                    txt_app_final = ", ".join(app_list)
                    if "Cirrosis Hepática" in app_list:
                        txt_app_final += f" (Child-Pugh Ascitis: {child_ascitis} | Encefalopatía: {child_encefalo})"

            txt_meds_final = "NEGADA."
            if not sin_antecedentes:
                if meds_list and meds_list != ["Ninguno"]: txt_meds_final = ", ".join(meds_list)

            txt_habitos_final = "NEGADOS."
            if not sin_habitos:
                if habitos_activos: txt_habitos_final = " | ".join(habitos_activos)

            if sin_laboratorios:
                txt_labs_final = "No requeridos / Paciente clínicamente sano."
            else:
                txt_labs_final = f"Hb: {hb_val:.1f}g/dL | Hto: {hto_val:.0f}% | Plaq: {plaquetas_val:,}/uL | TP: {tp_val:.1f}s | TTPa: {ttpa_val:.1f}s | INR: {inr_val:.2f}"
                if ver_metabolico or (not sin_antecedentes and "Diabetes" in str(antecedentes_seleccionados)):
                    txt_labs_final += f"\n   [Metabólico] Glucosa: {glucosa_basal:.0f} mg/dL | HbA1c: {hba1c_val:.1f}%"
                if tiene_gasometria:
                    txt_labs_final += f"\n   [Gasometría] pH: {ph_val:.2f} | PaCO2: {paco2_val:.0f} mmHg | HCO3: {hco3_val:.1f} mEq/L | Lactato: {lactato_val:.1f} mmol/L | PaO2/FiO2: {pafi:.0f} mmHg"

            if "Consulta Externa" in ambito_atencion:
                txt_caprini_rep = "EXIGE Profilaxis Combinada: Mecánica + Farmacológica (HBPM Enoxaparina)." if score_caprini >= 5 else ("Profilaxis farmacológica o mecánica precoz." if score_caprini >= 2 else "Solo deambulación temprana activa.")
            else:
                txt_caprini_rep = "Manejo según protocolo estándar de Quirófano (Evaluación Caprini omitida)."

            reporte_medico_texto = f"""=====================================================================
🏥 NOTA DE EVALUACIÓN PREANESTÉSICA CONSOLIDADA
=====================================================================
Centro Institucional: {hospital_final}
Responsable: Dr. Marcos Aviles
Estatus de Validación: Certificado por Sistema Experto Perioperatorio

1. FILIACIÓN Y ANTROPOMETRÍA
---------------------------------------------------------------------
• Sexo Biológico: {sexo_calc}
• Edad Cronológica: {edad_calc} años
• Grupo Sanguíneo y Rh: {gs_calc}
• Peso Real: {peso_calc:.1f} kg | Talla: {talla_raw:.0f} cm
• IMC Calculado: {imc_control:.1f} kg/m²
• Superficie Corporal (BSA): {bsa_calc:.2f} m²
• Peso Ideal Estimado: {peso_ideal if 'peso_ideal' in locals() else peso_calc:.1f} kg

2. CONTEXTO QUIRÚRGICO Y PLANIFICACIÓN
---------------------------------------------------------------------
• Ámbito de Atención: {ambito_atencion}
• Diagnóstico Principal: {diag_calc} {f'(Evolución: {frac_calc})' if (frac_calc != "No aplica") else ''}
• Procedimiento Quirúrgico: {proc_calc}
• Carácter de la Cirugía: {caracter_calc}
• Riesgo Quirúrgico Intrínseco (AHA/ACC): {riesgo_calc}
• Clasificación del Estado Físico (ASA): {asa_final}
• Técnica Anestésica Propuesta: {anestesia_calc}
{f'• Reserva de Hemoderivados: REQUERIDA (Riesgo de sangrado mayor)' if req_sangre_calc else '• Reserva de Hemoderivados: No requerida de rutina'}
{f'• Estatus NPO en Quirófano: {horas_ayuno} horas de ayuno para {tipo_ayuno}' if "Quirófano" in ambito_atencion else ''}
{f'• Edad Gestacional: {semanas_eg} semanas de gestación (Prever ISR y desplazamiento lateral)' if (obs_calc and "Quirófano" in ambito_atencion) else ''}
{f'• Planificación CE - Suspensión de Fármacos: {", ".join(plan_suspension_meds) if plan_suspension_meds else "No requiere"}' if "Consulta Externa" in ambito_atencion else ''}
{f'• Planificación CE - Interconsultas Solicitadas: {", ".join(interconsultas_req) if interconsultas_req else "Ninguna"}' if "Consulta Externa" in ambito_atencion else ''}

3. SEGURIDAD, ALERGIAS Y ANTECEDENTES (APP)
---------------------------------------------------------------------
• Alergias y Sensibilidades: {txt_alergias_final}
• Antecedentes Patológicos Clínicos: {txt_app_final}
• Medicación de Uso Continuo: {txt_meds_final}
• Dispositivos Implantables: {'Marcapasos/DAI presente (Precaución con electrobisturí)' if tiene_marcapasos else 'No aplica'}
• Hábitos y Estilo de Vida: {txt_habitos_final}

4. SCREENING PREDICTIVO Y ESTRATIFICACIÓN DE RIESGO
---------------------------------------------------------------------
• Índice de Intubación Difícil (Arné): {score_arne if not es_ped else score_arne_ped} puntos
• Riesgo de Ventilación (OBESE): {score_obese_total if not es_ped else 'N/A'} puntos
• Tamizaje de Apnea del Sueño (STOP-Bang): {score_stop_bang_total if not es_ped else 'N/A'} puntos
• Riesgo Pulmonar Postoperatorio (ARISCAT): {score_ariscat_total if not es_ped else 'N/A'} puntos
• Índice de Riesgo Cardíaco Revisado (Lee / RCRI): {lee_val if not es_ped else 'N/A'} puntos
• Riesgo de Náuseas y Vómitos (Apfel): {pts_apfel} / 4 puntos

5. EXÁMENES COMPLEMENTARIOS DE BASE
---------------------------------------------------------------------
• Reporte de Laboratorio: {txt_labs_final}
• Electrocardiograma (ECG): {ecg_hallazgo}
• Ecocardiograma (FEVI %): {f"{fevi_valor:.0f}%" if fevi_disponible else 'No solicitado'}

6. PLAN DE ACCIÓN Y PROFILAXIS RECOMENDADA
---------------------------------------------------------------------
• Manejo Antiemético (Apfel): {'EXIGE Profilaxis Multimodal Combinada (Dexametasona + Ondansetrón).' if pts_apfel >= 3 else ('Profilaxis estándar (Ondansetrón IV).' if pts_apfel == 2 else 'Manejo sintomático según demanda.')}
• Manejo Antitrombótico (Caprini): {txt_caprini_rep}
• Consideraciones de Vía Aérea: {f'ALERTA: Vía Aérea Difícil Predictiva.' if (not es_ped and score_arne > 10) or (es_ped and ped_vad_previo) else 'Vía aérea con predictores anatómicos estables de intubación.'}
• Observación Especial Pediátrica: {f"Riesgo de Hiperreactividad Laríngea activo. CONSIDERAR ADICIÓN DE LIDOCAÍNA IV PROTOCOLO DE TESIS." if es_ped and (ped_ivra or ped_estridor) else ("Estable sin criterios especiales." if es_ped else "No aplica (Paciente adulto).")}

=====================================================================
FIN DEL REPORTE - FIRMA REGISTRADA ELECTRÓNICAMENTE
=====================================================================
"""
            st.code(reporte_medico_texto, language="text")
