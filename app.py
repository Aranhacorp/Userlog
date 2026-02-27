"""
MASTER CODE DEEP SEEK LOG v.2.0
Userlog - Sistema de Transportes com persistência em PostgreSQL (Supabase)
Autor: Aranhacorp
"""

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
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="Userlog - Sistema de Transportes",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CONEXÃO COM O BANCO DE DADOS =================
# Tenta obter a URL do banco das secrets do Streamlit Cloud, senão usa variável de ambiente
DB_URL = st.secrets.get("SUPABASE_DB_URL", os.getenv("SUPABASE_DB_URL", None))
if DB_URL is None:
    st.error("❌ URL do banco de dados não configurada. Configure a secrets SUPABASE_DB_URL.")
    st.stop()

@st.cache_resource
def init_connection():
    """Inicializa a conexão com o banco (pool simples)"""
    return psycopg2.connect(DB_URL)

def get_cursor():
    """Retorna um cursor para executar queries"""
    conn = init_connection()
    return conn.cursor(cursor_factory=RealDictCursor), conn

# ================= CRIAÇÃO DAS TABELAS (SE NÃO EXISTIREM) =================
def create_tables():
    """Cria as tabelas necessárias no banco de dados"""
    commands = [
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            cpf_cnpj VARCHAR(20) UNIQUE NOT NULL,
            email VARCHAR(100),
            telefone VARCHAR(20),
            data_cadastro TIMESTAMP DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS motoristas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            cnh VARCHAR(20) UNIQUE NOT NULL,
            telefone VARCHAR(20),
            status VARCHAR(50) DEFAULT 'Disponível',
            data_cadastro TIMESTAMP DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS empresas (
            id SERIAL PRIMARY KEY,
            razao_social VARCHAR(200) NOT NULL,
            nome_fantasia VARCHAR(200),
            cnpj VARCHAR(20) UNIQUE NOT NULL,
            email VARCHAR(100),
            telefone VARCHAR(20),
            data_cadastro TIMESTAMP DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS cargas (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER REFERENCES clientes(id),
            motorista_id INTEGER REFERENCES motoristas(id),
            origem VARCHAR(200),
            destino VARCHAR(200),
            tipo_carga VARCHAR(50),
            peso NUMERIC(10,2),
            status VARCHAR(50) DEFAULT 'agendada',
            data_agendamento DATE,
            hora_agendamento TIME,
            data_criacao TIMESTAMP DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS pagamentos (
            id SERIAL PRIMARY KEY,
            carga_id INTEGER REFERENCES cargas(id),
            cliente_id INTEGER REFERENCES clientes(id),
            valor NUMERIC(10,2),
            descricao TEXT,
            data_pagamento TIMESTAMP DEFAULT NOW(),
            status VARCHAR(50) DEFAULT 'pago'
        )
        """
    ]
    cur, conn = get_cursor()
    try:
        for cmd in commands:
            cur.execute(cmd)
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Erro ao criar tabelas: {e}")
    finally:
        cur.close()
        conn.close()

# Chama a criação das tabelas na inicialização
create_tables()

# ================= CSS PERSONALIZADO =================
st.markdown("""
<style>
    /* Fundo da área principal com azul escuro transparente */
    .main > div {
        background-color: rgba(0, 0, 139, 0.15);
        padding: 1rem;
        border-radius: 10px;
    }
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.2);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
        padding: 0 1rem;
    }
    .logo-container img {
        width: 100%;
        max-width: 600px;
        height: auto;
        border-radius: 10px;
    }
    .custom-sidebar {
        background-color: #f8f9fa;
        padding: 2rem 1rem;
        border-radius: 10px;
        height: 100%;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }
    .custom-sidebar h3 {
        color: #333;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .custom-sidebar a {
        display: block;
        color: #555;
        text-decoration: none;
        padding: 0.5rem;
        margin: 0.2rem 0;
        border-radius: 5px;
        transition: background 0.3s;
    }
    .custom-sidebar a:hover {
        background-color: #e9ecef;
        color: #667eea;
    }
    .partner-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .partner-card p {
        margin: 0.2rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ================= INICIALIZAÇÃO DO ESTADO DA SESSÃO =================
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "login"
    if 'notificacoes' not in st.session_state:
        st.session_state.notificacoes = []
    if 'config_empresa' not in st.session_state:
        st.session_state.config_empresa = {
            'nome': 'Userlog Transportes',
            'cnpj': '12.345.678/0001-90',
            'ie': '123.456.789.012',
            'email': 'contato@userlog.com.br',
            'telefone': '(11) 3456-7890',
            'chave_pix': 'userlog@transportes.com.br',
            'endereco': 'Av. Paulista, 1000 - São Paulo, SP'
        }

init_session_state()

# ================= FUNÇÕES AUXILIARES =================
def format_currency(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def gerar_qrcode_pix(valor, chave_pix, descricao):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"PIX:{chave_pix}:{valor}:{descricao}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def adicionar_notificacao(titulo, mensagem, tipo="info"):
    notificacao = {
        'id': len(st.session_state.notificacoes) + 1,
        'titulo': titulo,
        'mensagem': mensagem,
        'tipo': tipo,
        'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'lida': False
    }
    st.session_state.notificacoes.append(notificacao)

def mostrar_notificacoes():
    nao_lidas = [n for n in st.session_state.notificacoes if not n['lida']]
    if nao_lidas:
        with st.sidebar.expander(f"🔔 Notificações ({len(nao_lidas)})"):
            for n in nao_lidas[-5:]:
                if n['tipo'] == 'success':
                    st.success(f"**{n['titulo']}**\n\n{n['mensagem']}")
                elif n['tipo'] == 'warning':
                    st.warning(f"**{n['titulo']}**\n\n{n['mensagem']}")
                elif n['tipo'] == 'error':
                    st.error(f"**{n['titulo']}**\n\n{n['mensagem']}")
                else:
                    st.info(f"**{n['titulo']}**\n\n{n['mensagem']}")
                n['lida'] = True

def exibir_logo():
    caminhos = ["assets/logistics-sunset_png.avif", "logistics-sunset_png.avif"]
    for caminho in caminhos:
        if os.path.exists(caminho):
            img = Image.open(caminho)
            st.image(img, use_column_width=True)
            return True
    return False

# ================= PÁGINA DE LOGIN COM SIDEBAR PERSONALIZADA =================
def login_page():
    col_sidebar, col_main = st.columns([1, 3])
    with col_sidebar:
        st.markdown("<div class='custom-sidebar'>", unsafe_allow_html=True)
        st.markdown("## MENU")
        st.markdown("[Quem somos](#)")
        st.markdown("[Serviços](#)")
        st.markdown("[Equipamentos](#)")
        st.markdown("[Cotações](#)")
        st.markdown("[Contato](#)")
        st.markdown("---")
        st.markdown("### PARCEIROS LOGÍSTICOS")
        st.markdown("""
        <div class='partner-card'>
            <strong>PLAY TENNIS Ibiraquera</strong>
            <p>R. Estado de Israel, 860 - SP</p>
            <p>(11) 97752-0488</p>
            <p>https://www.playtennis.com.br/</p>
        </div>
        <div class='partner-card'>
            <strong>TOP One Tennis</strong>
            <p>Av. Indianópolis, 647 - SP</p>
            <p>(11) 93236-3828</p>
            <p>https://toponetennis.com.br/</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_main:
        with st.container():
            st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
            if not exibir_logo():
                st.markdown("<div class='main-header'><h1>🚚 Userlog - Sistema de Transportes</h1></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='main-header'><h1>Userlog - Sistema de Transportes</h1></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("👤 Usuário")
            password = st.text_input("🔒 Senha", type="password")
            user_type = st.selectbox("📋 Tipo", ["admin", "cliente", "motorista"])
            if st.form_submit_button("🚪 Entrar", use_container_width=True):
                if username and password:
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_type
                    st.session_state.username = username
                    st.session_state.current_page = "dashboard"
                    adicionar_notificacao("Bem-vindo!", f"Seja bem-vindo, {username}!", "success")
                    st.rerun()
                else:
                    st.error("❌ Usuário e senha obrigatórios!")

# ================= MENU LATERAL (APÓS LOGIN) =================
def menu_sidebar():
    with st.sidebar:
        if not exibir_logo():
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;'>
                <h2 style='color: white; margin: 0;'>USERLOG</h2>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 10px 0;'>
            <p><strong>👤 Usuário:</strong> {st.session_state.username}</p>
            <p><strong>📋 Tipo:</strong> {st.session_state.user_type.upper()}</p>
            <p><strong>🕐 Login:</strong> {datetime.now().strftime('%H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        mostrar_notificacoes()
        st.markdown("### 📌 Menu Principal")
        menu_options = {
            "📊 Dashboard": "dashboard",
            "👥 Clientes": "clientes",
            "👨‍✈️ Motoristas": "motoristas",
            "🏢 Empresas": "empresas",
            "📦 Agendamentos": "agendamentos",
            "💰 Pagamentos": "pagamentos",
            "📈 Relatórios": "relatorios",
            "🛰️ Monitoramento": "monitoramento",
            "⚙️ Configurações": "config"
        }
        for label, page in menu_options.items():
            if st.button(label, use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        st.markdown("---")
        with st.expander("⚡ Ações Rápidas"):
            if st.button("➕ Novo Agendamento"):
                st.session_state.current_page = "agendamentos"
                st.rerun()
            if st.button("💰 Novo Pagamento"):
                st.session_state.current_page = "pagamentos"
                st.rerun()
        st.markdown(f"""
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
            <p>🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p>MASTER CODE DEEP SEEK LOG v.2.0</p>
            <p>© 2026 - Userlog</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# ================= FUNÇÕES DE CADA PÁGINA (COM BANCO DE DADOS) =================

def dashboard():
    st.markdown("<div class='main-header'><h1>📊 Dashboard Userlog</h1></div>", unsafe_allow_html=True)
    cur, conn = get_cursor()
    # Estatísticas
    cur.execute("SELECT COUNT(*) FROM cargas WHERE status IN ('agendada','em andamento')")
    cargas_ativas = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) FROM motoristas")
    total_motoristas = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cur.fetchone()['count']
    cur.execute("SELECT COALESCE(SUM(valor),0) FROM pagamentos WHERE status='pago'")
    total_faturamento = cur.fetchone()['coalesce'] or 0
    cur.close()
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📦 Cargas Ativas", cargas_ativas)
    with col2: st.metric("👨‍✈️ Motoristas", total_motoristas)
    with col3: st.metric("👥 Clientes", total_clientes)
    with col4: st.metric("💰 Faturamento", format_currency(total_faturamento))

    # Gráfico de distribuição de cargas por status
    cur, conn = get_cursor()
    cur.execute("SELECT status, COUNT(*) FROM cargas GROUP BY status")
    data = cur.fetchall()
    if data:
        df = pd.DataFrame(data)
        fig = px.pie(df, values='count', names='status', title="Distribuição de Cargas")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma carga cadastrada")
    cur.close()
    conn.close()

def clientes():
    st.markdown("<div class='main-header'><h1>👥 Cadastro de Clientes</h1></div>", unsafe_allow_html=True)
    cur, conn = get_cursor()
    with st.form("form_cliente"):
        nome = st.text_input("Nome completo *")
        cpf_cnpj = st.text_input("CPF/CNPJ *")
        email = st.text_input("E-mail *")
        telefone = st.text_input("Telefone *")
        if st.form_submit_button("Cadastrar Cliente"):
            if nome and cpf_cnpj and email and telefone:
                try:
                    cur.execute(
                        "INSERT INTO clientes (nome, cpf_cnpj, email, telefone) VALUES (%s, %s, %s, %s)",
                        (nome, cpf_cnpj, email, telefone)
                    )
                    conn.commit()
                    st.success("Cliente cadastrado!")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro: {e}")
            else:
                st.error("Preencha todos os campos obrigatórios!")
    # Lista clientes
    cur.execute("SELECT id, nome, cpf_cnpj, email, telefone, data_cadastro FROM clientes ORDER BY id DESC")
    rows = cur.fetchall()
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df)
    else:
        st.info("Nenhum cliente cadastrado")
    cur.close()
    conn.close()

def motoristas():
    st.markdown("<div class='main-header'><h1>👨‍✈️ Cadastro de Motoristas</h1></div>", unsafe_allow_html=True)
    cur, conn = get_cursor()
    with st.form("form_motorista"):
        nome = st.text_input("Nome completo *")
        cnh = st.text_input("CNH *")
        telefone = st.text_input("Telefone *")
        status = st.selectbox("Status", ["Disponível", "Em viagem", "Descanso"])
        if st.form_submit_button("Cadastrar Motorista"):
            if nome and cnh and telefone:
                try:
                    cur.execute(
                        "INSERT INTO motoristas (nome, cnh, telefone, status) VALUES (%s, %s, %s, %s)",
                        (nome, cnh, telefone, status)
                    )
                    conn.commit()
                    st.success("Motorista cadastrado!")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro: {e}")
            else:
                st.error("Preencha todos os campos obrigatórios!")
    cur.execute("SELECT id, nome, cnh, telefone, status, data_cadastro FROM motoristas ORDER BY id DESC")
    rows = cur.fetchall()
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df)
    else:
        st.info("Nenhum motorista cadastrado")
    cur.close()
    conn.close()

def empresas():
    st.markdown("<div class='main-header'><h1>🏢 Cadastro de Empresas</h1></div>", unsafe_allow_html=True)
    cur, conn = get_cursor()
    with st.form("form_empresa"):
        razao_social = st.text_input("Razão Social *")
        nome_fantasia = st.text_input("Nome Fantasia *")
        cnpj = st.text_input("CNPJ *")
        email = st.text_input("E-mail *")
        telefone = st.text_input("Telefone *")
        if st.form_submit_button("Cadastrar Empresa"):
            if razao_social and nome_fantasia and cnpj and email and telefone:
                try:
                    cur.execute(
                        "INSERT INTO empresas (razao_social, nome_fantasia, cnpj, email, telefone) VALUES (%s, %s, %s, %s, %s)",
                        (razao_social, nome_fantasia, cnpj, email, telefone)
                    )
                    conn.commit()
                    st.success("Empresa cadastrada!")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro: {e}")
            else:
                st.error("Preencha todos os campos obrigatórios!")
    cur.execute("SELECT id, razao_social, nome_fantasia, cnpj, email, telefone, data_cadastro FROM empresas ORDER BY id DESC")
    rows = cur.fetchall()
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df)
    else:
        st.info("Nenhuma empresa cadastrada")
    cur.close()
    conn.close()

def agendamentos():
    st.markdown("<div class='main-header'><h1>📦 Agendamento de Cargas</h1></div>", unsafe_allow_html=True)
    cur, conn = get_cursor()
    # Carregar listas para selects
    cur.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes_list = cur.fetchall()
    cur.execute("SELECT id, nome FROM motoristas WHERE status='Disponível' ORDER BY nome")
    motoristas_list = cur.fetchall()
    cliente_opcoes = {c['nome']: c['id'] for c in clientes_list}
    motorista_opcoes = {m['nome']: m['id'] for m in motoristas_list}

    with st.form("form_agendamento"):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de Transporte", ["Rodoviário", "Aéreo"])
            cliente_nome = st.selectbox("Cliente", list(cliente_opcoes.keys()) if cliente_opcoes else ["Nenhum"])
            motorista_nome = st.selectbox("Motorista", list(motorista_opcoes.keys()) if motorista_opcoes else ["Nenhum"])
            origem = st.text_input("Origem *")
        with col2:
            destino = st.text_input("Destino *")
            data = st.date_input("Data", min_value=datetime.now().date())
            hora = st.time_input("Horário")
            peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
        if st.form_submit_button("Agendar Carga"):
            if origem and destino and peso>0 and cliente_nome!="Nenhum" and motorista_nome!="Nenhum":
                cliente_id = cliente_opcoes[cliente_nome]
                motorista_id = motorista_opcoes[motorista_nome]
                try:
                    cur.execute("""
                        INSERT INTO cargas (cliente_id, motorista_id, origem, destino, tipo_carga, peso, data_agendamento, hora_agendamento, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                    """, (cliente_id, motorista_id, origem, destino, tipo, peso, data, hora, 'agendada'))
                    carga_id = cur.fetchone()['id']
                    conn.commit()
                    st.success(f"Carga agendada com sucesso! ID: {carga_id}")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro: {e}")
            else:
                st.error("Preencha todos os campos e selecione cliente/motorista válidos!")
    # Listar agendamentos
    cur.execute("""
        SELECT c.id, cl.nome as cliente, m.nome as motorista, c.origem, c.destino, c.data_agendamento, c.hora_agendamento, c.status
        FROM cargas c
        JOIN clientes cl ON c.cliente_id = cl.id
        JOIN motoristas m ON c.motorista_id = m.id
        ORDER BY c.data_agendamento DESC
    """)
    rows = cur.fetchall()
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df)
    else:
        st.info("Nenhum agendamento")
    cur.close()
    conn.close()

def pagamentos():
    st.markdown("<div class='main-header'><h1>💰 Pagamentos via PIX</h1></div>", unsafe_allow_html=True)
    cur, conn = get_cursor()
    # Carregar cargas não pagas
    cur.execute("""
        SELECT c.id, cl.nome as cliente, c.origem, c.destino, c.peso
        FROM cargas c
        JOIN clientes cl ON c.cliente_id = cl.id
        WHERE c.status != 'paga'
    """)
    cargas_abertas = cur.fetchall()
    carga_opcoes = {f"{c['id']} - {c['cliente']} - {c['origem']}→{c['destino']}": c['id'] for c in cargas_abertas}

    with st.form("form_pagamento"):
        valor = st.number_input("Valor (R$)", min_value=0.01, step=10.0)
        descricao = st.text_input("Descrição")
        carga_sel = st.selectbox("Carga relacionada (opcional)", ["Nenhuma"] + list(carga_opcoes.keys()))
        if st.form_submit_button("Gerar QR Code PIX"):
            if valor > 0 and descricao:
                chave = st.session_state.config_empresa['chave_pix']
                img = gerar_qrcode_pix(valor, chave, descricao)
                buf = BytesIO()
                img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                st.image(f"data:image/png;base64,{b64}", width=300)
                st.code(f"Chave PIX: {chave}")
                # Registrar pagamento no banco
                carga_id = carga_opcoes[carga_sel] if carga_sel != "Nenhuma" else None
                cliente_id = None
                if carga_id:
                    cur.execute("SELECT cliente_id FROM cargas WHERE id=%s", (carga_id,))
                    res = cur.fetchone()
                    if res:
                        cliente_id = res['cliente_id']
                try:
                    cur.execute("""
                        INSERT INTO pagamentos (carga_id, cliente_id, valor, descricao, status)
                        VALUES (%s, %s, %s, %s, 'pago')
                    """, (carga_id, cliente_id, valor, descricao))
                    if carga_id:
                        cur.execute("UPDATE cargas SET status='paga' WHERE id=%s", (carga_id,))
                    conn.commit()
                    st.success("Pagamento registrado com sucesso!")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro ao registrar: {e}")
            else:
                st.error("Preencha valor e descrição")
    # Listar pagamentos
    cur.execute("""
        SELECT p.id, cl.nome as cliente, p.valor, p.descricao, p.data_pagamento, p.status
        FROM pagamentos p
        LEFT JOIN clientes cl ON p.cliente_id = cl.id
        ORDER BY p.data_pagamento DESC
    """)
    rows = cur.fetchall()
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df)
    else:
        st.info("Nenhum pagamento registrado")
    cur.close()
    conn.close()

def relatorios():
    st.markdown("<div class='main-header'><h1>📊 Relatórios</h1></div>", unsafe_allow_html=True)
    tipo = st.selectbox("Tipo de relatório", ["Cargas", "Pagamentos", "Motoristas"])
    cur, conn = get_cursor()
    if tipo == "Cargas":
        cur.execute("""
            SELECT c.id, cl.nome as cliente, m.nome as motorista, c.origem, c.destino, c.status, c.data_criacao
            FROM cargas c
            JOIN clientes cl ON c.cliente_id = cl.id
            JOIN motoristas m ON c.motorista_id = m.id
            ORDER BY c.data_criacao DESC
        """)
        rows = cur.fetchall()
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
            fig = px.bar(df, x='status', title="Cargas por status")
            st.plotly_chart(fig)
        else:
            st.info("Sem dados")
    elif tipo == "Pagamentos":
        cur.execute("SELECT * FROM pagamentos ORDER BY data_pagamento DESC")
        rows = cur.fetchall()
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
            total = df['valor'].sum()
            st.metric("Total recebido", format_currency(total))
        else:
            st.info("Sem dados")
    elif tipo == "Motoristas":
        cur.execute("SELECT * FROM motoristas ORDER BY id")
        rows = cur.fetchall()
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
        else:
            st.info("Sem dados")
    cur.close()
    conn.close()

def monitoramento():
    st.markdown("<div class='main-header'><h1>🛰️ Monitoramento de Cargas</h1></div>", unsafe_allow_html=True)
    status_filter = st.multiselect("Status", ["agendada", "em andamento", "entregue"], default=["agendada","em andamento"])
    cur, conn = get_cursor()
    query = """
        SELECT c.id, cl.nome as cliente, m.nome as motorista, c.origem, c.destino, c.tipo_carga, c.peso, c.status
        FROM cargas c
        JOIN clientes cl ON c.cliente_id = cl.id
        JOIN motoristas m ON c.motorista_id = m.id
        WHERE c.status = ANY(%s)
        ORDER BY c.id
    """
    cur.execute(query, (status_filter,))
    rows = cur.fetchall()
    if rows:
        for c in rows:
            with st.container():
                col1, col2, col3 = st.columns([2,2,1])
                with col1:
                    st.markdown(f"**Carga #{c['id']}**")
                    st.markdown(f"📦 {c['tipo_carga']} - {c['peso']}kg")
                with col2:
                    st.markdown(f"📍 {c['origem']} → {c['destino']}")
                    st.markdown(f"👤 {c['cliente']} / 🚚 {c['motorista']}")
                with col3:
                    if c['status'] == 'em andamento':
                        st.markdown("🟢 **Em rota**")
                    elif c['status'] == 'entregue':
                        st.markdown("✅ **Entregue**")
                    else:
                        st.markdown("🟡 **Agendada**")
                st.markdown("---")
    else:
        st.info("Nenhuma carga encontrada")
    cur.close()
    conn.close()

def configuracoes():
    st.markdown("<div class='main-header'><h1>⚙️ Configurações</h1></div>", unsafe_allow_html=True)
    with st.form("config_empresa"):
        nome = st.text_input("Nome da Empresa", value=st.session_state.config_empresa.get('nome',''))
        cnpj = st.text_input("CNPJ", value=st.session_state.config_empresa.get('cnpj',''))
        chave_pix = st.text_input("Chave PIX", value=st.session_state.config_empresa.get('chave_pix',''))
        if st.form_submit_button("Salvar"):
            st.session_state.config_empresa.update({'nome': nome, 'cnpj': cnpj, 'chave_pix': chave_pix})
            st.success("Configurações salvas!")

# ================= ROTEAMENTO PRINCIPAL =================
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        menu_sidebar()
        if st.session_state.current_page == "dashboard":
            dashboard()
        elif st.session_state.current_page == "clientes":
            clientes()
        elif st.session_state.current_page == "motoristas":
            motoristas()
        elif st.session_state.current_page == "empresas":
            empresas()
        elif st.session_state.current_page == "agendamentos":
            agendamentos()
        elif st.session_state.current_page == "pagamentos":
            pagamentos()
        elif st.session_state.current_page == "relatorios":
            relatorios()
        elif st.session_state.current_page == "monitoramento":
            monitoramento()
        elif st.session_state.current_page == "config":
            configuracoes()

if __name__ == "__main__":
    main()
