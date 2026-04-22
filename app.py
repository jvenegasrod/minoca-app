import streamlit as st
import math
import matplotlib.pyplot as plt
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

def standard_scale(X, mean, scale):
    return [(x - m) / s if s != 0 else 0 for x, m, s in zip(X, mean, scale)]

# ======================================
# SCALER MANUAL (20 VARIABLES)
# ======================================

mean = [
    -0.036719805255204685, 0.37371487672802645, -0.037245115329270044,
    0.3831479423974633, -0.352703959052168, -0.0310957469756243,
    0.09592671687721055, 0.10200011935525558, 0.07880480531458219,
    0.6439905310506593, 0.04576804683337029, 0.6413664724706669,
    0.06120679901294951, 0.04417647682732945, 0.14500063939315203,
    0.05137186727852011, 0.8083621989745011, 0.40897606475162984,
    0.415764688004906, 0.025172529736040016
]

scale = [
    0.6806373781839579, 0.4463381328397996, 0.5085205389906217,
    0.5592998198177509, 0.4454544886937723, 0.46365220669395696,
    0.2738765147978888, 0.27888309014747065, 0.25033848421784255,
    2.3571431098781552, 1.2484655049454723, 1.8075454751071631,
    0.8549965566770581, 0.8054317324831691, 0.44978064776809584,
    0.816740582760879, 3.067299703648678, 1.4045030066428585,
    1.9908200370196334, 0.590764625120386
]

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
fa_flutter = st.selectbox("FA/Flutter auricular", ["No", "Sí"])

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
fa_flutter_val = 1 if fa_flutter == "Sí" else 0

# ======================================
# VECTOR DE INPUT
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
    fa_flutter_val,
    fevi_cat
]])

# ======================================
# ESCALADO
# ======================================

X_scaled = np.array(standard_scale(X_input[0], mean, scale))

# ======================================
# COEFICIENTES
# ======================================

COEF = [
    0.198357, 1.0, 0.231265, 0.471615, 0.218579,
    0.395783, 0.070659, 0.038478, 0.405527,
    0.134931, 0.208151, 0.149204, 0.132517,
    0.163148, 0.193213, 0.098491, 0.130386,
    0.052608, 0.0, 0.301552
]

FEATURE_NAMES = [
    "Edad", "Sexo", "Tabaco", "Diabetes", "HTA",
    "Dislipemia", "IRC", "Ictus", "Troponina",
    "Hb", "CK", "FC", "TAS", "ECG", "Colesterol",
    "PCR", "PCR-us", "IL-6", "FA/Flutter", "FEVI"
]

# ======================================
# SCORE
# ======================================

score = sum(x * c for x, c in zip(X_scaled, COEF))

# ======================================
# MODELO + AJUSTE POR POSICIÓN DEL SCORE
# ======================================

a = 0.6233327289350132
b = -0.0009401927501036586

# Probabilidad logística original
prob_model = sigmoid(a + b * score)

# Corrección por prevalencia real
pi_real = 0.10
odds_model = prob_model / (1 - prob_model)
odds_corrected = odds_model * (pi_real / (1 - pi_real))
prob_model_calibrada = odds_corrected / (1 + odds_corrected)

# Distribución clínica del score
stats0 = {'q1': 295.72, 'med': 591.33, 'q3': 1251.13}   # Obstructivo
stats1 = {'q1': 177.95, 'med': 293.23, 'q3': 465.23}    # MINOCA

iqr_obstructivo = stats0['q3'] - stats0['q1']
iqr_minoca = stats1['q3'] - stats1['q1']

# Distancia normalizada a cada grupo
dist_minoca = abs(score - stats1['med']) / iqr_minoca
dist_obstructivo = abs(score - stats0['med']) / iqr_obstructivo

# Afinidad suave a cada grupo
aff_minoca = math.exp(-dist_minoca)
aff_obstructivo = math.exp(-dist_obstructivo)

prob_dist = aff_minoca / (aff_minoca + aff_obstructivo)

# Combinación:
# - menos peso al modelo puro
# - más peso a la posición del score
peso_modelo = 0.25
peso_dist = 0.75

prob_minoca = (peso_modelo * prob_model_calibrada) + (peso_dist * prob_dist)

# Empujón suave si cae dentro del rango intercuartílico MINOCA
if stats1['q1'] <= score <= stats1['q3']:
    prob_minoca += 0.10

# Penalización suave si cae dentro del rango intercuartílico obstructivo
if stats0['q1'] <= score <= stats0['q3']:
    prob_minoca -= 0.05

# Límites finales
prob_minoca = max(0, min(1, prob_minoca))
prob_obstructivo = 1 - prob_minoca

# ======================================
# CONTRIBUCIONES
# ======================================

contribuciones = {
    name: value * coef
    for name, value, coef in zip(FEATURE_NAMES, X_scaled, COEF)
}

contrib_ordenadas = dict(
    sorted(contribuciones.items(), key=lambda x: abs(x[1]), reverse=True)
)

# ======================================
# RESULTADOS
# ======================================

st.divider()
st.header("Resultado")

st.metric("Probabilidad MINOCA", f"{prob_minoca*100:.1f} %")
st.metric("Probabilidad IAM obstructivo", f"{prob_obstructivo*100:.1f} %")

st.subheader("Score total")
st.metric("Valor del score", f"{score:.2f}")

# ======================================
# BOXPLOT
# ======================================

st.subheader("Posición del paciente en la distribución del score")

stats0_full = {
    'q1': 295.72,
    'med': 591.33,
    'q3': 1251.13,
    'whislo': 83.40,
    'whishi': 2684.25
}
stats1_full = {
    'q1': 177.95,
    'med': 293.23,
    'q3': 465.23,
    'whislo': 91.66,
    'whishi': 896.16
}

fig, ax = plt.subplots()

box_data = [
    dict(label="Obstructivo", **stats0_full),
    dict(label="MINOCA", **stats1_full)
]

ax.bxp(box_data, showfliers=False)
ax.axhline(score, color="red", linestyle="--", label="Score paciente")
ax.set_ylabel("Score")
ax.legend()

st.pyplot(fig)

# ======================================
# TERMÓMETRO
# ======================================

st.subheader("Nivel de riesgo")

fig2, ax2 = plt.subplots(figsize=(6, 1))
ax2.barh(0, prob_minoca, color="red")
ax2.set_xlim(0, 1)
ax2.set_yticks([])
ax2.set_xlabel("Probabilidad MINOCA")
ax2.axvline(0.10, color="green", linestyle="--", label="Bajo")
ax2.axvline(0.30, color="orange", linestyle="--", label="Intermedio")
ax2.legend(loc="upper right")
st.pyplot(fig2)

# ======================================
# CONTRIBUYENTES DEL SCORE
# ======================================

st.subheader("Variables que más contribuyen")

top_n = 8
labels = list(contrib_ordenadas.keys())[:top_n]
values = list(contrib_ordenadas.values())[:top_n]

fig3, ax3 = plt.subplots(figsize=(6, 4))
ax3.barh(labels, values)
ax3.invert_yaxis()
ax3.set_xlabel("Contribución al score")
st.pyplot(fig3)



st.caption("⚠️ Herramienta de apoyo clínico. No sustituye el juicio médico.")