import streamlit as st
import math
import matplotlib.pyplot as plt
import pickle
import numpy as np

# ======================================
# CONFIGURACIÓN
# ======================================

st.set_page_config(page_title="Calculadora MINOCA", layout="centered")

# ======================================
# ESTILO
# ======================================

st.markdown("""
<style>
.stApp { background-color: #F5F2EA; }
.block-container {
    background-color: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.title("Calculadora clínica de probabilidad de MINOCA")
st.markdown("Introduce los datos clínicos iniciales del paciente con infarto.")
st.divider()

# ======================================
# CARGAR SCALER (CLAVE)
# ======================================

scaler = pickle.load(open("scaler.pkl", "rb"))

# ======================================
# FUNCIONES
# ======================================

def parse_float(x):
    if x == "" or x is None:
        return 0.0
    try:
        return float(str(x).replace(",", "."))
    except:
        return 0.0

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

# ======================================
# INPUTS
# ======================================

st.header("Datos clínicos")

edad = parse_float(st.text_input("Edad (años)"))
sexo = st.selectbox("Sexo", ["Hombre", "Mujer"])
tabaco = st.selectbox("Tabaco", ["No fumador", "Fumador"])
diabetes = st.selectbox("Diabetes", ["No", "Sí"])
hta = st.selectbox("Hipertensión arterial", ["No", "Sí"])
dislipemia = st.selectbox("Dislipemia", ["No", "Sí"])
irc_previo = st.selectbox("Insuficiencia renal crónica previa", ["No", "Sí"])
ictus_final = st.selectbox("Ictus previo", ["No", "Sí"])

troponina_ths = parse_float(st.text_input("Troponina T hs"))
hb = parse_float(st.text_input("Hemoglobina"))
ck = parse_float(st.text_input("Creatina quinasa (CK)"))
frecuencia_cardiaca = parse_float(st.text_input("Frecuencia cardíaca (bpm)"))
tas = parse_float(st.text_input("Tensión arterial sistólica"))
colesterol_total = parse_float(st.text_input("Colesterol total"))
pcr_normal = parse_float(st.text_input("PCR normal"))
pcrus_al_ingreso = parse_float(st.text_input("PCR ultrasensible al ingreso"))
il_6_a = parse_float(st.text_input("IL-6"))

ritmo_en_ecg = float(st.selectbox("Ritmo en ECG", [1, 2, 3, 4]))
fevi_cat = float(st.selectbox("FEVI categorizada", [1, 2, 3]))

# ======================================
# CODIFICACIÓN
# ======================================

sexo_val = 1 if sexo == "Hombre" else 2
tabaco_val = 1 if tabaco == "Fumador" else 0
diabetes_val = 1 if diabetes == "Sí" else 0
hta_val = 1 if hta == "Sí" else 0
dislipemia_val = 1 if dislipemia == "Sí" else 0
irc_previo_val = 1 if irc_previo == "Sí" else 0
ictus_final_val = 1 if ictus_final == "Sí" else 0

# ======================================
# VECTOR DE INPUT (ORDEN CRÍTICO)
# ======================================

X_input = np.array([[
    edad,
    sexo_val,
    tabaco_val,
    diabetes_val,
    hta_val,
    dislipemia_val,
    irc_previo_val,
    ictus_final_val,
    troponina_ths,
    hb,
    ck,
    frecuencia_cardiaca,
    tas,
    ritmo_en_ecg,
    colesterol_total,
    pcr_normal,
    pcrus_al_ingreso,
    il_6_a,
    fevi_cat
]])

# ======================================
# ESCALADO (CLAVE)
# ======================================

X_scaled = scaler.transform(X_input)[0]

# ======================================
# COEFICIENTES
# ======================================

COEF = [
    0.198357, 1.0, 0.231265, 0.471615, 0.218579,
    0.395783, 0.070659, 0.038478, 0.405527,
    0.134931, 0.208151, 0.149204, 0.132517,
    0.163148, 0.193213, 0.098491, 0.130386,
    0.052608, 0.301552
]

# ======================================
# SCORE CORRECTO
# ======================================

score = sum([x * c for x, c in zip(X_scaled, COEF)])

# ======================================
# MODELO
# ======================================

a = 0.6233327289350132
b = -0.0009401927501036586

prob_model = sigmoid(a + b * score)

pi_real = 0.10
odds_model = prob_model / (1 - prob_model)
odds_corrected = odds_model * (pi_real / (1 - pi_real))
prob_minoca = odds_corrected / (1 + odds_corrected)

# ======================================
# RESULTADOS
# ======================================

prob_minoca = max(0, min(1, prob_minoca))
prob_obstructivo = 1 - prob_minoca

st.divider()
st.header("Resultado")

st.metric("Probabilidad MINOCA", f"{prob_minoca*100:.1f} %")
st.metric("Probabilidad IAM obstructivo", f"{prob_obstructivo*100:.1f} %")

st.subheader("Score total")
st.metric("Valor del score", f"{score:.2f}")

# ======================================
# TERMÓMETRO
# ======================================

st.subheader("Nivel de riesgo")

fig2, ax2 = plt.subplots(figsize=(6,1))
ax2.barh(0, prob_minoca, color="red")
ax2.set_xlim(0,1)
ax2.set_yticks([])
ax2.set_xlabel("Probabilidad MINOCA")
ax2.axvline(0.10, color="green", linestyle="--")
ax2.axvline(0.30, color="orange", linestyle="--")

st.pyplot(fig2)

st.caption("⚠️ Herramienta de apoyo clínico. No sustituye el juicio médico.")
