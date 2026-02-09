import streamlit as st
import math

st.set_page_config(
    page_title="Calculadora MINOCA",
    layout="centered"
)

st.title("Calculadora clínica de probabilidad de MINOCA")

st.markdown(
    "Introduce los datos clínicos iniciales del paciente con infarto."
)

st.divider()

st.header("Datos del paciente")

edad = st.number_input(
    "Edad (años)",
    min_value=18,
    max_value=100,
    value=60
)

sexo = st.selectbox(
    "Sexo",
    ["Varón", "Mujer"]
)

tabaco = st.checkbox("Tabaquismo activo")
diabetes = st.checkbox("Diabetes mellitus")
hta = st.checkbox("Hipertensión arterial")

# =========================
# Conversión a variables numéricas
# =========================

sexo_num = 1 if sexo == "Mujer" else 0
tabaco_num = int(tabaco)
diabetes_num = int(diabetes)
hta_num = int(hta)

# =========================
# Coeficientes del SCORE MINOCA
# =========================

COEF = {
    "edad": 0.198357,
    "sexo": 1.0,
    "tabaco": 0.231265,
    "diabetes": 0.471615,
    "hta": 0.218579
}

# =========================
# Cálculo del score
# =========================

score = (
    edad * COEF["edad"]
    + sexo_num * COEF["sexo"]
    + tabaco_num * COEF["tabaco"]
    + diabetes_num * COEF["diabetes"]
    + hta_num * COEF["hta"]
)

# =========================
# Conversión a probabilidad
# =========================

a = -3.0   # pendiente a calibrar
b = 0.15

prob = 1 / (1 + math.exp(-(a + b * score)))

# =========================
# Interpretación clínica
# =========================

if prob < 0.20:
    interpretacion = "Riesgo bajo de MINOCA"
    color = "green"
elif prob < 0.50:
    interpretacion = "Riesgo intermedio de MINOCA"
    color = "orange"
else:
    interpretacion = "Alto riesgo de MINOCA"
    color = "red"

# =========================
# Mostrar resultado
# =========================

st.divider()
st.header("Resultado")

st.metric(
    "Probabilidad estimada de MINOCA",
    f"{prob * 100:.1f} %"
)

st.markdown(f":{color}[**{interpretacion}**]")

st.divider()

st.caption(
    "⚠️ Esta herramienta es de apoyo clínico y no sustituye el juicio médico. "
    "No debe utilizarse como único criterio para la toma de decisiones."
)
