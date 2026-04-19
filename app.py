import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

# ======================================
# CONFIGURACIÓN
# ======================================

st.set_page_config(page_title="Calculadora MINOCA", layout="centered")

# ======================================
# ESTILO VISUAL
# ======================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F2EA;
    }
    .block-container {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Calculadora clínica de probabilidad de MINOCA")
st.markdown("Introduce los datos clínicos iniciales del paciente con infarto.")
st.divider()

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
# COEFICIENTES
# ======================================

COEF = {
    "edad": 0.198357,
    "sexo": 1.0,
    "tabaco": 0.231265,
    "diabetes": 0.471615,
    "hta": 0.218579,
    "dislipemia": 0.395783,
    "irc_previo": 0.070659,
    "ictus_final": 0.038478,
    "troponina_ths": 0.405527,
    "hb": 0.134931,
    "ck": 0.208151,
    "frecuencia_cardiaca": 0.149204,
    "tas": 0.132517,
    "ritmo_en_ecg": 0.163148,
    "colesterol_total": 0.193213,
    "pcr_normal": 0.098491,
    "pcrus_al_ingreso": 0.130386,
    "il_6_a": 0.052608,
    "fevi_cat": 0.301552
}

# ======================================
# SCORE
# ======================================

score = (
    edad * COEF["edad"] +
    sexo_val * COEF["sexo"] +
    tabaco_val * COEF["tabaco"] +
    diabetes_val * COEF["diabetes"] +
    hta_val * COEF["hta"] +
    dislipemia_val * COEF["dislipemia"] +
    irc_previo_val * COEF["irc_previo"] +
    ictus_final_val * COEF["ictus_final"] +
    troponina_ths * COEF["troponina_ths"] +
    hb * COEF["hb"] +
    ck * COEF["ck"] +
    frecuencia_cardiaca * COEF["frecuencia_cardiaca"] +
    tas * COEF["tas"] +
    ritmo_en_ecg * COEF["ritmo_en_ecg"] +
    colesterol_total * COEF["colesterol_total"] +
    pcr_normal * COEF["pcr_normal"] +
    pcrus_al_ingreso * COEF["pcrus_al_ingreso"] +
    il_6_a * COEF["il_6_a"] +
    fevi_cat * COEF["fevi_cat"]
)

# ======================================
# MODELO ORIGINAL
# ======================================

a = 0.6233327289350132
b = -0.0009401927501036586

prob_model = sigmoid(a + b * score)

pi_real = 0.10

odds_model = prob_model / (1 - prob_model)
odds_corrected = odds_model * (pi_real / (1 - pi_real))

prob_minoca = odds_corrected / (1 + odds_corrected)

# ======================================
# BOXPLOT STATS
# ======================================

stats0 = {'q1': 295.72, 'med': 591.33, 'q3': 1251.13}
stats1 = {'q1': 177.95, 'med': 293.23, 'q3': 465.23}

# ======================================
# NUEVA LÓGICA HÍBRIDA
# ======================================

med_minoca = stats1['med']
med_obstructivo = stats0['med']

dist_minoca = abs(score - med_minoca)
dist_obstructivo = abs(score - med_obstructivo)

aff_minoca = 1 / (dist_minoca + 1)
aff_obstructivo = 1 / (dist_obstructivo + 1)

total_aff = aff_minoca + aff_obstructivo
aff_minoca /= total_aff

# combinación
peso_modelo = 0.6
peso_dist = 0.4

prob_minoca = (peso_modelo * prob_minoca) + (peso_dist * aff_minoca)

# ajuste por IQR
if stats1['q1'] <= score <= stats1['q3']:
    prob_minoca += 0.15

if stats0['q1'] <= score <= stats0['q3']:
    prob_minoca -= 0.15

# límites
prob_minoca = max(0, min(1, prob_minoca))
prob_obstructivo = 1 - prob_minoca

# ======================================
# RESULTADOS
# ======================================

st.divider()
st.header("Resultado")

st.metric("Probabilidad MINOCA", f"{prob_minoca*100:.1f} %")
st.metric("Probabilidad IAM obstructivo", f"{prob_obstructivo*100:.1f} %")

# ======================================
# TERMÓMETRO
# ======================================

st.subheader("Nivel de riesgo")

fig2, ax2 = plt.subplots(figsize=(6,1))
ax2.barh(0, prob_minoca)
ax2.set_xlim(0,1)
ax2.set_yticks([])
ax2.set_xlabel("Probabilidad MINOCA")
ax2.axvline(0.10, linestyle="--")
ax2.axvline(0.30, linestyle="--")
st.pyplot(fig2)

# ======================================
# BOXPLOT
# ======================================

st.subheader("Posición del paciente en la distribución del score")

stats0_full = {'q1': 295.72, 'med': 591.33, 'q3': 1251.13, 'whislo': 83.40, 'whishi': 2684.25}
stats1_full = {'q1': 177.95, 'med': 293.23, 'q3': 465.23, 'whislo': 91.66, 'whishi': 896.16}

fig, ax = plt.subplots()

box_data = [
    dict(label="Obstructivo", **stats0_full),
    dict(label="MINOCA", **stats1_full)
]

ax.bxp(box_data, showfliers=False)
ax.axhline(score, linestyle="--", label="Score paciente")
ax.set_ylabel("Score")
ax.legend()

st.pyplot(fig)

# ======================================
# CONTRIBUCIONES
# ======================================

st.subheader("Principales contribuyentes al score")

sorted_contrib = sorted(score_components.items(), key=lambda x: abs(x[1]), reverse=True)

for var, val in sorted_contrib[:5]:
    st.write(f"{var}: {val:.2f}")

st.caption("⚠️ Herramienta de apoyo clínico. No sustituye el juicio médico.")