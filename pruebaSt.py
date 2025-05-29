import streamlit as st
import pandas as pd
from io import StringIO
import requests
from openai import OpenAI
import json

# ---- Configuración de la app ----
st.set_page_config(page_title="Chatbot de CSV", layout="wide")
st.title("Chatbot de Datos - Voice Dataset")
st.caption("Interactúa con los datos contenidos en el CSV")

# ---- Panel lateral: API Key ----
with st.sidebar:
    st.header("🔑 Configuración")
    openai_api_key = st.text_input("🔐 Ingresa tu OpenAI API Key", type="password", value="")  # Tu key puede ir como valor (solo en local)
    st.markdown("[Consigue tu API key aquí](https://platform.openai.com/account/api-keys)")

# ---- Cargar datos desde GitHub ----
@st.cache_data
def cargar_datos():
    url = "https://raw.githubusercontent.com/JennyReaP/FUNDAMENTOS-DE-IA/main/Clase%2012/voice.csv"
    response = requests.get(url)
    response.raise_for_status()
    return pd.read_csv(StringIO(response.text))

try:
    df = cargar_datos()
    st.success(" Datos cargados correctamente.")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f" Error al cargar los datos: {e}")
    st.stop()

# ---- Inicializar mensajes ----
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": """
Eres un científico de datos. Solo puedes responder preguntas relacionadas con el contenido de esta tabla CSV. 
Si te preguntan algo que no está en el dataset, debes responder: 
'Lo siento, no tengo información sobre eso porque no está en el dataset proporcionado.'
Responde de forma clara, breve y profesional.
Aquí están las primeras filas del dataset para referencia:
""" + df.head().to_json(orient="records", lines=False)}]

# ---- Chat principal ----
for msg in st.session_state.messages[1:]:  # omitimos el mensaje system
    st.chat_message(msg["role"]).write(msg["content"])

# ---- Entrada del usuario ----
if prompt := st.chat_input("Escribe tu pregunta sobre el dataset..."):
    if not openai_api_key:
        st.info("Por favor ingresa tu OpenAI API Key en el panel lateral.")
        st.stop()

    # Mostrar mensaje del usuario
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Crear cliente OpenAI y generar respuesta
    client = OpenAI(api_key=openai_api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages,
            temperature=0.4
        )
        msg = response.choices[0].message.content
    except Exception as e:
        msg = f" Error al generar respuesta: {e}"

    st.chat_message("assistant").write(msg)
    st.session_state.messages.append({"role": "assistant", "content": msg})

