import streamlit as st

from frontend.pages.codequest import inicializar_estado_global, renderizar_pagina_atual


st.set_page_config(page_title="CodeQuest", page_icon="🎮", layout="centered")

inicializar_estado_global()

st.title("🚀 CodeQuest")
st.caption("O Arquipélago de Bythos te aguarda!")

renderizar_pagina_atual()
