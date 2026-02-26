import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
import json
import os
from PIL import Image
import qrcode
from io import BytesIO
import base64
import plotly.express as px
import plotly.graph_objects as go
import time
import random

# Configuração da página
st.set_page_config(
    page_title="Userlog - Sistema de Transportes",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"
if 'clientes' not in st.session_state:
    st.session_state.clientes = []
if 'motoristas' not in st.session_state:
    st.session_state.motoristas = []
if 'cargas' not in st.session_state:
    st.session_state.cargas = []
if 'agendamentos' not in st.session_state:
    st.session_state.agendamentos = []
if 'pagamentos' not in st.session_state:
    st.session_state.pagamentos = []

# Funções auxiliares
def format_currency(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def gerar_qrcode_pix(valor, chave_pix, descricao):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"PIX:{chave_pix}:{valor}:{descricao}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# Página de login
def login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='main-header'><h1>🚚 Userlog - Sistema de Transportes</h1></div>", unsafe_allow_html=True)
        with st.form("login"):
            user = st.text_input("Usuário")
            pwd = st.text_input("Senha", type="password")
            tipo = st.selectbox("Tipo", ["admin","cliente","motorista"])
            if st.form_submit_button("Entrar"):
                st.session_state.logged_in = True
                st.session_state.user_type = tipo
                st.session_state.username = user
                st.session_state.current_page = "dashboard"
                st.rerun()

# Menu lateral
def menu_sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown(f"### 📋 {st.session_state.user_type}")
        st.markdown("---")
        if st.button("📊 Dashboard"): st.session_state.current_page = "dashboard"; st.rerun()
        if st.button("👥 Clientes"): st.session_state.current_page = "clientes"; st.rerun()
        if st.button("👨‍✈️ Motoristas"): st.session_state.current_page = "motoristas"; st.rerun()
        if st.button("📦 Agendamentos"): st.session_state.current_page = "agendamentos"; st.rerun()
        if st.button("💰 Pagamentos"): st.session_state.current_page = "pagamentos"; st.rerun()
        if st.button("📈 Relatórios"): st.session_state.current_page = "relatorios"; st.rerun()
        st.markdown("---")
        if st.button("🚪 Sair"):
            st.session_state.logged_in = False
            st.rerun()

# Dashboard
def dashboard():
    st.markdown("<div class='main-header'><h1>📊 Dashboard</h1></div>", unsafe_allow_html=True)
    col1,col2,col3,col4 = st.columns(4)
    with col1: st.metric("Cargas", len(st.session_state.cargas))
    with col2: st.metric("Motoristas", len(st.session_state.motoristas))
    with col3: st.metric("Clientes", len(st.session_state.clientes))
    with col4: st.metric("Pagamentos", len(st.session_state.pagamentos))
    st.info("Bem-vindo ao sistema Userlog!")

# Clientes
def clientes():
    st.markdown("<div class='main-header'><h1>👥 Clientes</h1></div>", unsafe_allow_html=True)
    with st.form("novo_cliente"):
        nome = st.text_input("Nome")
        cpf = st.text_input("CPF")
        email = st.text_input("Email")
        if st.form_submit_button("Cadastrar"):
            st.session_state.clientes.append({"id":len(st.session_state.clientes)+1, "nome":nome, "cpf":cpf, "email":email})
            st.success("Cliente cadastrado!")
    if st.session_state.clientes:
        st.dataframe(pd.DataFrame(st.session_state.clientes))

# Motoristas
def motoristas():
    st.markdown("<div class='main-header'><h1>👨‍✈️ Motoristas</h1></div>", unsafe_allow_html=True)
    with st.form("novo_motorista"):
        nome = st.text_input("Nome")
        cnh = st.text_input("CNH")
        telefone = st.text_input("Telefone")
        if st.form_submit_button("Cadastrar"):
            st.session_state.motoristas.append({"id":len(st.session_state.motoristas)+1, "nome":nome, "cnh":cnh, "telefone":telefone, "status":"Disponível"})
            st.success("Motorista cadastrado!")
    if st.session_state.motoristas:
        st.dataframe(pd.DataFrame(st.session_state.motoristas))

# Agendamentos
def agendamentos():
    st.markdown("<div class='main-header'><h1>📦 Agendamentos</h1></div>", unsafe_allow_html=True)
    with st.form("novo_agendamento"):
        cliente = st.selectbox("Cliente", [c['nome'] for c in st.session_state.clientes] if st.session_state.clientes else ["Nenhum"])
        motorista = st.selectbox("Motorista", [m['nome'] for m in st.session_state.motoristas] if st.session_state.motoristas else ["Nenhum"])
        origem = st.text_input("Origem")
        destino = st.text_input("Destino")
        data = st.date_input("Data")
        if st.form_submit_button("Agendar"):
            st.session_state.agendamentos.append({"id":len(st.session_state.agendamentos)+1, "cliente":cliente, "motorista":motorista, "origem":origem, "destino":destino, "data":data.strftime("%d/%m/%Y"), "status":"agendado"})
            st.success("Agendamento criado!")
    if st.session_state.agendamentos:
        st.dataframe(pd.DataFrame(st.session_state.agendamentos))

# Pagamentos
def pagamentos():
    st.markdown("<div class='main-header'><h1>💰 Pagamentos PIX</h1></div>", unsafe_allow_html=True)
    with st.form("pagamento"):
        valor = st.number_input("Valor", min_value=0.01)
        descricao = st.text_input("Descrição")
        if st.form_submit_button("Gerar PIX"):
            st.success("QR Code gerado (simulação)!")
            st.code(f"PIX copia e cola: 00020126360014BR.GOV.BCB.PIX0114userlog@teste.com520400005303986540{valor:.2f}5802BR5913Userlog6008SaoPaulo62070503***6304")
    if st.session_state.pagamentos:
        st.dataframe(pd.DataFrame(st.session_state.pagamentos))

# Relatórios
def relatorios():
    st.markdown("<div class='main-header'><h1>📊 Relatórios</h1></div>", unsafe_allow_html=True)
    st.info("Módulo em desenvolvimento")

# Roteamento
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        menu_sidebar()
        if st.session_state.current_page == "dashboard": dashboard()
        elif st.session_state.current_page == "clientes": clientes()
        elif st.session_state.current_page == "motoristas": motoristas()
        elif st.session_state.current_page == "agendamentos": agendamentos()
        elif st.session_state.current_page == "pagamentos": pagamentos()
        elif st.session_state.current_page == "relatorios": relatorios()

if __name__ == "__main__":
    main()
