"""
MASTER CODE DEEP SEEK LOG v.1.2
Userlog - Sistema de Transportes
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

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="Userlog - Sistema de Transportes",
    page_icon="📆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CSS PERSONALIZADO =================
st.markdown("""
<style>
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
    .status-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        animation: slideIn 0.5s;
    }
    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    /* Centralizar imagem de logo */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
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
    if 'clientes' not in st.session_state:
        st.session_state.clientes = []
    if 'motoristas' not in st.session_state:
        st.session_state.motoristas = []
    if 'empresas' not in st.session_state:
        st.session_state.empresas = []
    if 'cargas' not in st.session_state:
        st.session_state.cargas = []
    if 'agendamentos' not in st.session_state:
        st.session_state.agendamentos = []
    if 'pagamentos' not in st.session_state:
        st.session_state.pagamentos = []
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
    """Gera QR Code PIX simplificado"""
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

# ================= FUNÇÃO PARA EXIBIR LOGO =================
def exibir_logo(largura=300):
    """Tenta carregar a imagem logistics-sunset_png.avif e exibi-la centralizada."""
    caminhos_possiveis = [
        "assets/logistics-sunset_png.avif",
        "logistics-sunset_png.avif"
    ]
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            img = Image.open(caminho)
            # Redimensionar para largura fixa (mantendo proporção)
            proporcao = img.height / img.width
            nova_altura = int(largura * proporcao)
            img = img.resize((largura, nova_altura), Image.Resampling.LANCZOS)
            st.image(img, use_column_width=False)
            return True
    return False

# ================= PÁGINA DE LOGIN =================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Container para centralizar a imagem
        with st.container():
            st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
            if not exibir_logo(largura=300):
                # Se não encontrar a imagem, mostra o título padrão
                st.markdown("<div class='main-header'><h1>🚚 Userlog - Sistema de Transportes</h1></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Título abaixo da imagem (pode ser opcional, mas vou manter para consistência)
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

# ================= MENU LATERAL =================
def menu_sidebar():
    with st.sidebar:
        # Logo na barra lateral (menor)
        if not exibir_logo(largura=200):
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
            <p>MASTER CODE DEEP SEEK LOG v.1.2</p>
            <p>© 2026 - Userlog</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# ================= DASHBOARD =================
def dashboard():
    st.markdown("<div class='main-header'><h1>📊 Dashboard Userlog</h1></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("📦 Cargas Ativas", len([c for c in st.session_state.cargas if c.get('status') in ['agendada','em andamento']]))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("👨‍✈️ Motoristas", len(st.session_state.motoristas))
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("👥 Clientes", len(st.session_state.clientes))
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        total = sum([p.get('valor',0) for p in st.session_state.pagamentos if p.get('status')=='pago'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("💰 Faturamento", format_currency(total))
        st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Distribuição de Cargas")
        if st.session_state.cargas:
            df = pd.DataFrame(st.session_state.cargas)
            status_count = df['status'].value_counts()
            fig = px.pie(values=status_count.values, names=status_count.index)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma carga cadastrada")
    with col2:
        st.subheader("📅 Próximos Agendamentos")
        if st.session_state.agendamentos:
            df = pd.DataFrame(st.session_state.agendamentos)
            st.dataframe(df[['data','cliente','origem','destino','status']].head(5), use_container_width=True)
        else:
            st.info("Nenhum agendamento")
    
    st.subheader("🔄 Atividades Recentes")
    if st.session_state.pagamentos or st.session_state.cargas:
        for p in st.session_state.pagamentos[-3:]:
            st.success(f"💰 Pagamento de {p.get('cliente','')} - {format_currency(p.get('valor',0))}")
        for c in st.session_state.cargas[-3:]:
            st.info(f"📦 Carga #{c.get('id','')} - {c.get('origem','')} → {c.get('destino','')}")
    else:
        st.info("Nenhuma atividade recente")

# ================= CADASTRO DE CLIENTES =================
def clientes():
    st.markdown("<div class='main-header'><h1>👥 Cadastro de Clientes</h1></div>", unsafe_allow_html=True)
    with st.form("form_cliente"):
        nome = st.text_input("Nome completo *")
        cpf_cnpj = st.text_input("CPF/CNPJ *")
        email = st.text_input("E-mail *")
        telefone = st.text_input("Telefone *")
        if st.form_submit_button("Cadastrar Cliente"):
            if nome and cpf_cnpj and email and telefone:
                st.session_state.clientes.append({
                    "id": len(st.session_state.clientes)+1,
                    "nome": nome,
                    "cpf_cnpj": cpf_cnpj,
                    "email": email,
                    "telefone": telefone,
                    "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                st.success("Cliente cadastrado!")
            else:
                st.error("Preencha todos os campos obrigatórios!")
    
    if st.session_state.clientes:
        st.dataframe(pd.DataFrame(st.session_state.clientes))

# ================= CADASTRO DE MOTORISTAS =================
def motoristas():
    st.markdown("<div class='main-header'><h1>👨‍✈️ Cadastro de Motoristas</h1></div>", unsafe_allow_html=True)
    with st.form("form_motorista"):
        nome = st.text_input("Nome completo *")
        cnh = st.text_input("CNH *")
        telefone = st.text_input("Telefone *")
        status = st.selectbox("Status", ["Disponível", "Em viagem", "Descanso"])
        if st.form_submit_button("Cadastrar Motorista"):
            if nome and cnh and telefone:
                st.session_state.motoristas.append({
                    "id": len(st.session_state.motoristas)+1,
                    "nome": nome,
                    "cnh": cnh,
                    "telefone": telefone,
                    "status": status,
                    "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                st.success("Motorista cadastrado!")
            else:
                st.error("Preencha todos os campos obrigatórios!")
    
    if st.session_state.motoristas:
        st.dataframe(pd.DataFrame(st.session_state.motoristas))

# ================= CADASTRO DE EMPRESAS =================
def empresas():
    st.markdown("<div class='main-header'><h1>🏢 Cadastro de Empresas</h1></div>", unsafe_allow_html=True)
    with st.form("form_empresa"):
        razao_social = st.text_input("Razão Social *")
        nome_fantasia = st.text_input("Nome Fantasia *")
        cnpj = st.text_input("CNPJ *")
        email = st.text_input("E-mail *")
        telefone = st.text_input("Telefone *")
        if st.form_submit_button("Cadastrar Empresa"):
            if razao_social and nome_fantasia and cnpj and email and telefone:
                st.session_state.empresas.append({
                    "id": len(st.session_state.empresas)+1,
                    "razao_social": razao_social,
                    "nome_fantasia": nome_fantasia,
                    "cnpj": cnpj,
                    "email": email,
                    "telefone": telefone,
                    "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                st.success("Empresa cadastrada!")
            else:
                st.error("Preencha todos os campos obrigatórios!")
    
    if st.session_state.empresas:
        st.dataframe(pd.DataFrame(st.session_state.empresas))

# ================= AGENDAMENTO DE CARGAS =================
def agendamentos():
    st.markdown("<div class='main-header'><h1>📦 Agendamento de Cargas</h1></div>", unsafe_allow_html=True)
    with st.form("form_agendamento"):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de Transporte", ["Rodoviário", "Aéreo"])
            cliente = st.selectbox("Cliente", [c['nome'] for c in st.session_state.clientes] if st.session_state.clientes else ["Nenhum"])
            motorista = st.selectbox("Motorista", [m['nome'] for m in st.session_state.motoristas if m.get('status')=='Disponível'] if st.session_state.motoristas else ["Nenhum"])
            origem = st.text_input("Origem *")
        with col2:
            destino = st.text_input("Destino *")
            data = st.date_input("Data", min_value=datetime.now().date())
            hora = st.time_input("Horário")
            peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Agendar Carga"):
            if origem and destino and peso>0:
                novo = {
                    "id": len(st.session_state.agendamentos)+1,
                    "tipo": tipo,
                    "cliente": cliente,
                    "motorista": motorista,
                    "origem": origem,
                    "destino": destino,
                    "data": data.strftime("%d/%m/%Y"),
                    "hora": hora.strftime("%H:%M"),
                    "peso": peso,
                    "status": "agendado",
                    "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.agendamentos.append(novo)
                st.session_state.cargas.append({
                    "id": len(st.session_state.cargas)+1,
                    "agendamento_id": novo["id"],
                    "cliente": cliente,
                    "motorista": motorista,
                    "origem": origem,
                    "destino": destino,
                    "tipo_carga": tipo,
                    "peso": peso,
                    "status": "agendada",
                    "data_criacao": novo["data_criacao"]
                })
                st.success("Carga agendada com sucesso!")
            else:
                st.error("Preencha origem, destino e peso válido!")
    
    if st.session_state.agendamentos:
        st.dataframe(pd.DataFrame(st.session_state.agendamentos))

# ================= PAGAMENTOS PIX =================
def pagamentos():
    st.markdown("<div class='main-header'><h1>💰 Pagamentos via PIX</h1></div>", unsafe_allow_html=True)
    with st.form("form_pagamento"):
        valor = st.number_input("Valor (R$)", min_value=0.01, step=10.0)
        descricao = st.text_input("Descrição")
        if st.form_submit_button("Gerar QR Code PIX"):
            if valor > 0 and descricao:
                chave = st.session_state.config_empresa['chave_pix']
                img = gerar_qrcode_pix(valor, chave, descricao)
                buf = BytesIO()
                img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                st.image(f"data:image/png;base64,{b64}", width=300)
                st.code(f"Chave PIX: {chave}")
                st.session_state.pagamentos.append({
                    "id": len(st.session_state.pagamentos)+1,
                    "valor": valor,
                    "descricao": descricao,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "status": "pago"  # simulado
                })
                st.success("Pagamento registrado (simulado)!")
            else:
                st.error("Preencha valor e descrição")
    
    if st.session_state.pagamentos:
        st.dataframe(pd.DataFrame(st.session_state.pagamentos))

# ================= RELATÓRIOS =================
def relatorios():
    st.markdown("<div class='main-header'><h1>📊 Relatórios</h1></div>", unsafe_allow_html=True)
    tipo = st.selectbox("Tipo de relatório", ["Cargas", "Pagamentos", "Motoristas"])
    if tipo == "Cargas" and st.session_state.cargas:
        df = pd.DataFrame(st.session_state.cargas)
        st.dataframe(df)
        fig = px.bar(df, x='status', title="Cargas por status")
        st.plotly_chart(fig)
    elif tipo == "Pagamentos" and st.session_state.pagamentos:
        df = pd.DataFrame(st.session_state.pagamentos)
        st.dataframe(df)
        total = df['valor'].sum()
        st.metric("Total recebido", format_currency(total))
    elif tipo == "Motoristas" and st.session_state.motoristas:
        df = pd.DataFrame(st.session_state.motoristas)
        st.dataframe(df)
    else:
        st.info("Sem dados para exibir")

# ================= MONITORAMENTO =================
def monitoramento():
    st.markdown("<div class='main-header'><h1>🛰️ Monitoramento de Cargas</h1></div>", unsafe_allow_html=True)
    status_filter = st.multiselect("Status", ["agendada", "em andamento", "entregue"], default=["agendada","em andamento"])
    cargas_filtradas = [c for c in st.session_state.cargas if c.get('status') in status_filter]
    if cargas_filtradas:
        for c in cargas_filtradas:
            with st.container():
                col1, col2, col3 = st.columns([2,2,1])
                with col1:
                    st.markdown(f"**Carga #{c['id']}**")
                    st.markdown(f"📦 {c.get('tipo_carga','N/A')}")
                with col2:
                    st.markdown(f"📍 {c['origem']} → {c['destino']}")
                    st.markdown(f"🚚 {c['motorista']}")
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

# ================= CONFIGURAÇÕES =================
def configuracoes():
    st.markdown("<div class='main-header'><h1>⚙️ Configurações</h1></div>", unsafe_allow_html=True)
    with st.form("config_empresa"):
        st.subheader("Dados da Empresa")
        nome = st.text_input("Nome da Empresa", value=st.session_state.config_empresa.get('nome',''))
        cnpj = st.text_input("CNPJ", value=st.session_state.config_empresa.get('cnpj',''))
        chave_pix = st.text_input("Chave PIX", value=st.session_state.config_empresa.get('chave_pix',''))
        if st.form_submit_button("Salvar"):
            st.session_state.config_empresa.update({
                'nome': nome,
                'cnpj': cnpj,
                'chave_pix': chave_pix
            })
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
