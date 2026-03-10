"""
USERLOG - Sistema de Transportes v2.0
Autor: Aranhacorp
Melhorias: Visual premium, persistência JSON, correções de bugs
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from io import BytesIO
import base64
import plotly.express as px
import plotly.graph_objects as go

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="Userlog - Sistema de Transportes",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= PERSISTÊNCIA DE DADOS =================
DATA_FILE = "userlog_data.json"

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_dados():
    dados = {
        "clientes": st.session_state.clientes,
        "motoristas": st.session_state.motoristas,
        "empresas": st.session_state.empresas,
        "cargas": st.session_state.cargas,
        "agendamentos": st.session_state.agendamentos,
        "pagamentos": st.session_state.pagamentos,
        "config_empresa": st.session_state.config_empresa,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ================= DICIONÁRIO DE TRADUÇÕES =================
translations = {
    "pt": {
        "app_name": "Userlog - Sistema de Transportes",
        "welcome": "Bem-vindo",
        "login": "Entrar", "logout": "Sair",
        "username": "Usuário", "password": "Senha",
        "user_type": "Tipo", "admin": "admin",
        "cliente": "cliente", "motorista": "motorista",
        "save": "Salvar", "cancel": "Cancelar",
        "add": "Adicionar", "edit": "Editar", "delete": "Excluir",
        "search": "Buscar", "filter": "Filtrar", "export": "Exportar",
        "actions": "Ações", "confirm": "Confirmar",
        "success": "Sucesso", "error": "Erro", "warning": "Aviso",
        "no_data": "Sem dados", "loading": "Carregando...",
        "menu_dashboard": "📊 Dashboard",
        "menu_clientes": "👥 Clientes",
        "menu_motoristas": "👨‍✈️ Motoristas",
        "menu_empresas": "🏢 Empresas",
        "menu_agendamentos": "📦 Agendamentos",
        "menu_pagamentos": "💰 Pagamentos",
        "menu_relatorios": "📈 Relatórios",
        "menu_monitoramento": "🛰️ Monitoramento",
        "menu_configuracoes": "⚙️ Configurações",
        "quick_actions": "⚡ Ações Rápidas",
        "new_agendamento": "➕ Novo Agendamento",
        "new_pagamento": "💰 Novo Pagamento",
        "login_title": "Userlog - Sistema de Transportes",
        "login_button": "🚪 Entrar",
        "login_error": "❌ Usuário e senha obrigatórios!",
        "dashboard_title": "Dashboard",
        "metric_cargas_ativas": "Cargas Ativas",
        "metric_motoristas": "Motoristas",
        "metric_clientes": "Clientes",
        "metric_faturamento": "Faturamento",
        "chart_distribuicao": "Distribuição de Cargas",
        "chart_proximos": "Próximos Agendamentos",
        "recent_activities": "Atividades Recentes",
        "no_cargas": "Nenhuma carga cadastrada",
        "no_agendamentos": "Nenhum agendamento",
        "no_activities": "Nenhuma atividade recente",
        "clientes_title": "Cadastro de Clientes",
        "cliente_nome": "Nome completo *",
        "cliente_cpf_cnpj": "CPF/CNPJ *",
        "cliente_email": "E-mail *",
        "cliente_telefone": "Telefone *",
        "cliente_cadastrar": "Cadastrar Cliente",
        "cliente_cadastrado": "✅ Cliente cadastrado com sucesso!",
        "cliente_erro": "Preencha todos os campos obrigatórios!",
        "clientes_lista": "Clientes Cadastrados",
        "motoristas_title": "Cadastro de Motoristas",
        "motorista_nome": "Nome completo *",
        "motorista_cnh": "CNH *",
        "motorista_telefone": "Telefone *",
        "motorista_status": "Status",
        "status_disponivel": "Disponível",
        "status_viagem": "Em viagem",
        "status_descanso": "Descanso",
        "motorista_cadastrar": "Cadastrar Motorista",
        "motorista_cadastrado": "✅ Motorista cadastrado com sucesso!",
        "motoristas_lista": "Motoristas Cadastrados",
        "empresas_title": "Cadastro de Empresas",
        "empresa_razao": "Razão Social *",
        "empresa_fantasia": "Nome Fantasia *",
        "empresa_cnpj": "CNPJ *",
        "empresa_email": "E-mail *",
        "empresa_telefone": "Telefone *",
        "empresa_cadastrar": "Cadastrar Empresa",
        "empresa_cadastrada": "✅ Empresa cadastrada com sucesso!",
        "empresas_lista": "Empresas Cadastradas",
        "agendamentos_title": "Agendamento de Cargas",
        "ag_tipo_transporte": "Tipo de Transporte",
        "ag_rodoviario": "Rodoviário",
        "ag_aereo": "Aéreo",
        "ag_cliente": "Cliente",
        "ag_motorista": "Motorista",
        "ag_origem": "Origem *",
        "ag_destino": "Destino *",
        "ag_data": "Data",
        "ag_hora": "Horário",
        "ag_peso": "Peso (kg)",
        "ag_agendar": "Agendar Carga",
        "ag_sucesso": "✅ Carga agendada com sucesso!",
        "ag_erro": "Preencha origem, destino e peso válido!",
        "ag_lista": "Agendamentos Realizados",
        "pagamentos_title": "Pagamentos via PIX",
        "pag_valor": "Valor (R$)",
        "pag_descricao": "Descrição",
        "pag_gerar": "Gerar QR Code PIX",
        "pag_chave": "Chave PIX",
        "pag_registrado": "✅ Pagamento registrado com sucesso!",
        "pag_erro": "Preencha valor e descrição",
        "pag_lista": "Histórico de Pagamentos",
        "relatorios_title": "Relatórios",
        "rel_tipo": "Tipo de relatório",
        "rel_cargas": "Cargas",
        "rel_pagamentos": "Pagamentos",
        "rel_motoristas": "Motoristas",
        "rel_total_recebido": "Total recebido",
        "monitoramento_title": "Monitoramento de Cargas",
        "mon_status": "Status",
        "mon_em_rota": "🟢 Em rota",
        "mon_entregue": "✅ Entregue",
        "mon_agendada": "🟡 Agendada",
        "mon_carga": "Carga",
        "config_title": "Configurações",
        "config_dados_empresa": "Dados da Empresa",
        "config_nome": "Nome da Empresa",
        "config_cnpj": "CNPJ",
        "config_chave_pix": "Chave PIX",
        "config_salvar": "Salvar Configurações",
        "config_sucesso": "✅ Configurações salvas!",
        "language": "Idioma",
        "lang_pt": "🇧🇷 Português",
        "lang_en": "🇺🇸 Inglês",
        "lang_es": "🇪🇸 Espanhol",
        "lang_zh": "🇨🇳 Chinês",
        "user_info": "👤 {}",
        "user_type_info": "📋 {}",
        "login_time": "🕐 {}",
        "notifications": "Notificações",
        "pagamentos": "Pagamento",
    },
    "en": {
        "app_name": "Userlog - Transport System",
        "welcome": "Welcome",
        "login": "Login", "logout": "Logout",
        "username": "Username", "password": "Password",
        "user_type": "Type", "admin": "admin",
        "cliente": "client", "motorista": "driver",
        "save": "Save", "cancel": "Cancel",
        "add": "Add", "edit": "Edit", "delete": "Delete",
        "search": "Search", "filter": "Filter", "export": "Export",
        "actions": "Actions", "confirm": "Confirm",
        "success": "Success", "error": "Error", "warning": "Warning",
        "no_data": "No data", "loading": "Loading...",
        "menu_dashboard": "📊 Dashboard",
        "menu_clientes": "👥 Clients",
        "menu_motoristas": "👨‍✈️ Drivers",
        "menu_empresas": "🏢 Companies",
        "menu_agendamentos": "📦 Schedules",
        "menu_pagamentos": "💰 Payments",
        "menu_relatorios": "📈 Reports",
        "menu_monitoramento": "🛰️ Monitoring",
        "menu_configuracoes": "⚙️ Settings",
        "quick_actions": "⚡ Quick Actions",
        "new_agendamento": "➕ New Schedule",
        "new_pagamento": "💰 New Payment",
        "login_title": "Userlog - Transport System",
        "login_button": "🚪 Login",
        "login_error": "❌ Username and password required!",
        "dashboard_title": "Dashboard",
        "metric_cargas_ativas": "Active Loads",
        "metric_motoristas": "Drivers",
        "metric_clientes": "Clients",
        "metric_faturamento": "Revenue",
        "chart_distribuicao": "Load Distribution",
        "chart_proximos": "Upcoming Schedules",
        "recent_activities": "Recent Activities",
        "no_cargas": "No loads registered",
        "no_agendamentos": "No schedules",
        "no_activities": "No recent activities",
        "clientes_title": "Client Registration",
        "cliente_nome": "Full name *",
        "cliente_cpf_cnpj": "CPF/CNPJ *",
        "cliente_email": "Email *",
        "cliente_telefone": "Phone *",
        "cliente_cadastrar": "Register Client",
        "cliente_cadastrado": "✅ Client registered successfully!",
        "cliente_erro": "Fill all required fields!",
        "clientes_lista": "Registered Clients",
        "motoristas_title": "Driver Registration",
        "motorista_nome": "Full name *",
        "motorista_cnh": "Driver's License *",
        "motorista_telefone": "Phone *",
        "motorista_status": "Status",
        "status_disponivel": "Available",
        "status_viagem": "On trip",
        "status_descanso": "Resting",
        "motorista_cadastrar": "Register Driver",
        "motorista_cadastrado": "✅ Driver registered successfully!",
        "motoristas_lista": "Registered Drivers",
        "empresas_title": "Company Registration",
        "empresa_razao": "Company Name *",
        "empresa_fantasia": "Trade Name *",
        "empresa_cnpj": "CNPJ *",
        "empresa_email": "Email *",
        "empresa_telefone": "Phone *",
        "empresa_cadastrar": "Register Company",
        "empresa_cadastrada": "✅ Company registered successfully!",
        "empresas_lista": "Registered Companies",
        "agendamentos_title": "Load Scheduling",
        "ag_tipo_transporte": "Transport Type",
        "ag_rodoviario": "Road",
        "ag_aereo": "Air",
        "ag_cliente": "Client",
        "ag_motorista": "Driver",
        "ag_origem": "Origin *",
        "ag_destino": "Destination *",
        "ag_data": "Date",
        "ag_hora": "Time",
        "ag_peso": "Weight (kg)",
        "ag_agendar": "Schedule Load",
        "ag_sucesso": "✅ Load scheduled successfully!",
        "ag_erro": "Fill origin, destination and valid weight!",
        "ag_lista": "Scheduled Loads",
        "pagamentos_title": "PIX Payments",
        "pag_valor": "Amount (R$)",
        "pag_descricao": "Description",
        "pag_gerar": "Generate PIX QR Code",
        "pag_chave": "PIX Key",
        "pag_registrado": "✅ Payment recorded successfully!",
        "pag_erro": "Fill amount and description",
        "pag_lista": "Payment History",
        "relatorios_title": "Reports",
        "rel_tipo": "Report type",
        "rel_cargas": "Loads",
        "rel_pagamentos": "Payments",
        "rel_motoristas": "Drivers",
        "rel_total_recebido": "Total received",
        "monitoramento_title": "Load Monitoring",
        "mon_status": "Status",
        "mon_em_rota": "🟢 On route",
        "mon_entregue": "✅ Delivered",
        "mon_agendada": "🟡 Scheduled",
        "mon_carga": "Load",
        "config_title": "Settings",
        "config_dados_empresa": "Company Data",
        "config_nome": "Company Name",
        "config_cnpj": "CNPJ",
        "config_chave_pix": "PIX Key",
        "config_salvar": "Save Settings",
        "config_sucesso": "✅ Settings saved!",
        "language": "Language",
        "lang_pt": "🇧🇷 Portuguese",
        "lang_en": "🇺🇸 English",
        "lang_es": "🇪🇸 Spanish",
        "lang_zh": "🇨🇳 Chinese",
        "user_info": "👤 {}",
        "user_type_info": "📋 {}",
        "login_time": "🕐 {}",
        "notifications": "Notifications",
        "pagamentos": "Payment",
    },
    "es": {
        "app_name": "Userlog - Sistema de Transporte",
        "welcome": "Bienvenido",
        "login": "Iniciar sesión", "logout": "Cerrar sesión",
        "username": "Usuario", "password": "Contraseña",
        "user_type": "Tipo", "admin": "admin",
        "cliente": "cliente", "motorista": "conductor",
        "save": "Guardar", "cancel": "Cancelar",
        "add": "Agregar", "edit": "Editar", "delete": "Eliminar",
        "search": "Buscar", "filter": "Filtrar", "export": "Exportar",
        "actions": "Acciones", "confirm": "Confirmar",
        "success": "Éxito", "error": "Error", "warning": "Advertencia",
        "no_data": "Sin datos", "loading": "Cargando...",
        "menu_dashboard": "📊 Panel",
        "menu_clientes": "👥 Clientes",
        "menu_motoristas": "👨‍✈️ Conductores",
        "menu_empresas": "🏢 Empresas",
        "menu_agendamentos": "📦 Agendamientos",
        "menu_pagamentos": "💰 Pagos",
        "menu_relatorios": "📈 Informes",
        "menu_monitoramento": "🛰️ Monitoreo",
        "menu_configuracoes": "⚙️ Configuración",
        "quick_actions": "⚡ Acciones rápidas",
        "new_agendamento": "➕ Nuevo agendamiento",
        "new_pagamento": "💰 Nuevo pago",
        "login_title": "Userlog - Sistema de Transporte",
        "login_button": "🚪 Entrar",
        "login_error": "❌ ¡Usuario y contraseña obligatorios!",
        "dashboard_title": "Panel",
        "metric_cargas_ativas": "Cargas activas",
        "metric_motoristas": "Conductores",
        "metric_clientes": "Clientes",
        "metric_faturamento": "Facturación",
        "chart_distribuicao": "Distribución de cargas",
        "chart_proximos": "Próximos agendamientos",
        "recent_activities": "Actividades recientes",
        "no_cargas": "Ninguna carga registrada",
        "no_agendamentos": "Ningún agendamiento",
        "no_activities": "Ninguna actividad reciente",
        "clientes_title": "Registro de Clientes",
        "cliente_nome": "Nombre completo *",
        "cliente_cpf_cnpj": "CPF/CNPJ *",
        "cliente_email": "Correo *",
        "cliente_telefone": "Teléfono *",
        "cliente_cadastrar": "Registrar Cliente",
        "cliente_cadastrado": "✅ ¡Cliente registrado con éxito!",
        "cliente_erro": "¡Complete todos los campos obligatorios!",
        "clientes_lista": "Clientes Registrados",
        "motoristas_title": "Registro de Conductores",
        "motorista_nome": "Nombre completo *",
        "motorista_cnh": "Licencia *",
        "motorista_telefone": "Teléfono *",
        "motorista_status": "Estado",
        "status_disponivel": "Disponible",
        "status_viagem": "En viaje",
        "status_descanso": "Descanso",
        "motorista_cadastrar": "Registrar Conductor",
        "motorista_cadastrado": "✅ ¡Conductor registrado con éxito!",
        "motoristas_lista": "Conductores Registrados",
        "empresas_title": "Registro de Empresas",
        "empresa_razao": "Razón Social *",
        "empresa_fantasia": "Nombre Fantasía *",
        "empresa_cnpj": "CNPJ *",
        "empresa_email": "Correo *",
        "empresa_telefone": "Teléfono *",
        "empresa_cadastrar": "Registrar Empresa",
        "empresa_cadastrada": "✅ ¡Empresa registrada con éxito!",
        "empresas_lista": "Empresas Registradas",
        "agendamentos_title": "Agendamiento de Cargas",
        "ag_tipo_transporte": "Tipo de Transporte",
        "ag_rodoviario": "Carretera",
        "ag_aereo": "Aéreo",
        "ag_cliente": "Cliente",
        "ag_motorista": "Conductor",
        "ag_origem": "Origen *",
        "ag_destino": "Destino *",
        "ag_data": "Fecha",
        "ag_hora": "Hora",
        "ag_peso": "Peso (kg)",
        "ag_agendar": "Agendar Carga",
        "ag_sucesso": "✅ ¡Carga agendada con éxito!",
        "ag_erro": "¡Complete origen, destino y peso válido!",
        "ag_lista": "Agendamientos Realizados",
        "pagamentos_title": "Pagos vía PIX",
        "pag_valor": "Valor (R$)",
        "pag_descricao": "Descripción",
        "pag_gerar": "Generar código QR PIX",
        "pag_chave": "Clave PIX",
        "pag_registrado": "✅ ¡Pago registrado con éxito!",
        "pag_erro": "Complete valor y descripción",
        "pag_lista": "Historial de Pagos",
        "relatorios_title": "Informes",
        "rel_tipo": "Tipo de informe",
        "rel_cargas": "Cargas",
        "rel_pagamentos": "Pagos",
        "rel_motoristas": "Conductores",
        "rel_total_recebido": "Total recibido",
        "monitoramento_title": "Monitoreo de Cargas",
        "mon_status": "Estado",
        "mon_em_rota": "🟢 En ruta",
        "mon_entregue": "✅ Entregado",
        "mon_agendada": "🟡 Agendada",
        "mon_carga": "Carga",
        "config_title": "Configuración",
        "config_dados_empresa": "Datos de la Empresa",
        "config_nome": "Nombre de la Empresa",
        "config_cnpj": "CNPJ",
        "config_chave_pix": "Clave PIX",
        "config_salvar": "Guardar",
        "config_sucesso": "✅ ¡Configuración guardada!",
        "language": "Idioma",
        "lang_pt": "🇧🇷 Portugués",
        "lang_en": "🇺🇸 Inglés",
        "lang_es": "🇪🇸 Español",
        "lang_zh": "🇨🇳 Chino",
        "user_info": "👤 {}",
        "user_type_info": "📋 {}",
        "login_time": "🕐 {}",
        "notifications": "Notificaciones",
        "pagamentos": "Pago",
    },
    "zh": {
        "app_name": "Userlog - 运输系统",
        "welcome": "欢迎",
        "login": "登录", "logout": "登出",
        "username": "用户名", "password": "密码",
        "user_type": "类型", "admin": "管理员",
        "cliente": "客户", "motorista": "司机",
        "save": "保存", "cancel": "取消",
        "add": "添加", "edit": "编辑", "delete": "删除",
        "search": "搜索", "filter": "筛选", "export": "导出",
        "actions": "操作", "confirm": "确认",
        "success": "成功", "error": "错误", "warning": "警告",
        "no_data": "无数据", "loading": "加载中...",
        "menu_dashboard": "📊 仪表板",
        "menu_clientes": "👥 客户",
        "menu_motoristas": "👨‍✈️ 司机",
        "menu_empresas": "🏢 公司",
        "menu_agendamentos": "📦 日程安排",
        "menu_pagamentos": "💰 付款",
        "menu_relatorios": "📈 报告",
        "menu_monitoramento": "🛰️ 监控",
        "menu_configuracoes": "⚙️ 设置",
        "quick_actions": "⚡ 快速操作",
        "new_agendamento": "➕ 新日程",
        "new_pagamento": "💰 新付款",
        "login_title": "Userlog - 运输系统",
        "login_button": "🚪 登录",
        "login_error": "❌ 用户名和密码为必填项！",
        "dashboard_title": "仪表板",
        "metric_cargas_ativas": "活跃货物",
        "metric_motoristas": "司机",
        "metric_clientes": "客户",
        "metric_faturamento": "收入",
        "chart_distribuicao": "货物分布",
        "chart_proximos": "即将到来的日程",
        "recent_activities": "最近活动",
        "no_cargas": "无货物登记",
        "no_agendamentos": "无日程安排",
        "no_activities": "无最近活动",
        "clientes_title": "客户登记",
        "cliente_nome": "全名 *",
        "cliente_cpf_cnpj": "CPF/CNPJ *",
        "cliente_email": "电子邮件 *",
        "cliente_telefone": "电话 *",
        "cliente_cadastrar": "登记客户",
        "cliente_cadastrado": "✅ 客户登记成功！",
        "cliente_erro": "请填写所有必填字段！",
        "clientes_lista": "已登记客户",
        "motoristas_title": "司机登记",
        "motorista_nome": "全名 *",
        "motorista_cnh": "驾照 *",
        "motorista_telefone": "电话 *",
        "motorista_status": "状态",
        "status_disponivel": "可用",
        "status_viagem": "途中",
        "status_descanso": "休息",
        "motorista_cadastrar": "登记司机",
        "motorista_cadastrado": "✅ 司机登记成功！",
        "motoristas_lista": "已登记司机",
        "empresas_title": "公司登记",
        "empresa_razao": "公司名称 *",
        "empresa_fantasia": "商业名称 *",
        "empresa_cnpj": "CNPJ *",
        "empresa_email": "电子邮件 *",
        "empresa_telefone": "电话 *",
        "empresa_cadastrar": "登记公司",
        "empresa_cadastrada": "✅ 公司登记成功！",
        "empresas_lista": "已登记公司",
        "agendamentos_title": "货物日程安排",
        "ag_tipo_transporte": "运输类型",
        "ag_rodoviario": "公路",
        "ag_aereo": "航空",
        "ag_cliente": "客户",
        "ag_motorista": "司机",
        "ag_origem": "出发地 *",
        "ag_destino": "目的地 *",
        "ag_data": "日期",
        "ag_hora": "时间",
        "ag_peso": "重量 (kg)",
        "ag_agendar": "安排货物",
        "ag_sucesso": "✅ 货物安排成功！",
        "ag_erro": "请填写出发地、目的地和有效重量！",
        "ag_lista": "已安排的货物",
        "pagamentos_title": "PIX 付款",
        "pag_valor": "金额 (R$)",
        "pag_descricao": "描述",
        "pag_gerar": "生成 PIX 二维码",
        "pag_chave": "PIX 密钥",
        "pag_registrado": "✅ 付款记录成功！",
        "pag_erro": "请填写金额和描述",
        "pag_lista": "付款历史",
        "relatorios_title": "报告",
        "rel_tipo": "报告类型",
        "rel_cargas": "货物",
        "rel_pagamentos": "付款",
        "rel_motoristas": "司机",
        "rel_total_recebido": "总收入",
        "monitoramento_title": "货物监控",
        "mon_status": "状态",
        "mon_em_rota": "🟢 途中",
        "mon_entregue": "✅ 已交付",
        "mon_agendada": "🟡 已安排",
        "mon_carga": "货物",
        "config_title": "设置",
        "config_dados_empresa": "公司数据",
        "config_nome": "公司名称",
        "config_cnpj": "CNPJ",
        "config_chave_pix": "PIX 密钥",
        "config_salvar": "保存",
        "config_sucesso": "✅ 设置已保存！",
        "language": "语言",
        "lang_pt": "🇧🇷 葡萄牙语",
        "lang_en": "🇺🇸 英语",
        "lang_es": "🇪🇸 西班牙语",
        "lang_zh": "🇨🇳 中文",
        "user_info": "👤 {}",
        "user_type_info": "📋 {}",
        "login_time": "🕐 {}",
        "notifications": "通知",
        "pagamentos": "付款",
    }
}

def t(key):
    lang = st.session_state.get("language", "pt")
    return translations.get(lang, translations["pt"]).get(key, key)

# ================= CSS PREMIUM =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --primary: #0A0F1E;
    --accent: #F4A623;
    --accent2: #00D4AA;
    --surface: #111827;
    --surface2: #1F2937;
    --border: rgba(255,255,255,0.08);
    --text: #F9FAFB;
    --text-muted: #9CA3AF;
    --danger: #EF4444;
    --success: #10B981;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--primary) !important;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

section[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* ---- Inputs ---- */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

/* ---- Buttons ---- */
.stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, #e8951f 100%) !important;
    color: #0A0F1E !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 12px rgba(244,166,35,0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(244,166,35,0.4) !important;
}

/* ---- DataFrames ---- */
.stDataFrame {
    background: var(--surface2) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}

/* ---- Alerts ---- */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 10px !important;
}

/* ---- Metric ---- */
[data-testid="metric-container"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.2rem 1.5rem !important;
}

[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
}

/* ---- Custom cards ---- */
.page-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

.page-header h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
    color: var(--text) !important;
    margin: 0 !important;
}

.page-header .accent-dot {
    width: 10px;
    height: 10px;
    background: var(--accent);
    border-radius: 50%;
    margin-left: auto;
    box-shadow: 0 0 12px var(--accent);
}

.brand-block {
    background: linear-gradient(135deg, var(--accent) 0%, #e8951f 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.brand-block h2 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.3rem !important;
    color: #0A0F1E !important;
    margin: 0 !important;
}

.brand-block span {
    font-size: 0.7rem !important;
    color: rgba(10,15,30,0.7) !important;
    font-weight: 500 !important;
    display: block;
}

.user-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin: 0.75rem 0;
    font-size: 0.82rem;
    line-height: 1.8;
}

.menu-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.2rem 0 0.5rem 0;
    padding-left: 0.25rem;
}

.activity-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.7rem 1rem;
    background: var(--surface2);
    border-radius: 8px;
    margin-bottom: 0.5rem;
    border-left: 3px solid var(--accent);
    font-size: 0.85rem;
}

.activity-row.green {
    border-left-color: var(--accent2);
}

.tag {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}

.tag-agendada { background: rgba(244,166,35,0.15); color: var(--accent); }
.tag-em-andamento { background: rgba(0,212,170,0.15); color: var(--accent2); }
.tag-entregue { background: rgba(16,185,129,0.15); color: #10B981; }
.tag-pago { background: rgba(16,185,129,0.15); color: #10B981; }

.load-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    gap: 1rem;
    align-items: center;
}

.load-card:hover {
    border-color: rgba(244,166,35,0.3);
}

.load-id {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

.load-title {
    font-size: 0.95rem;
    font-weight: 500;
}

.sep { color: var(--text-muted); }

.version-tag {
    text-align: center;
    padding: 0.5rem;
    font-size: 0.7rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    margin-top: 1rem;
    letter-spacing: 0.05em;
}

/* Login page */
.login-container {
    max-width: 420px;
    margin: 0 auto;
}

.login-brand {
    text-align: center;
    margin-bottom: 2rem;
}

.login-brand h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.2rem !important;
    color: var(--accent) !important;
    margin: 0 !important;
    letter-spacing: -0.02em;
}

.login-brand p {
    color: var(--text-muted) !important;
    font-size: 0.85rem !important;
    margin: 0.25rem 0 0 0 !important;
}

.login-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
}

/* Plotly dark fix */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1rem 0;
}

/* Form container */
.form-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface2) !important;
    border-radius: 8px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface2) !important;
    border-radius: 10px !important;
    padding: 0.25rem !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: var(--text-muted) !important;
}

.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #0A0F1E !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# ================= INICIALIZAÇÃO =================
def init_session_state():
    dados = carregar_dados()
    defaults = {
        'logged_in': False,
        'user_type': None,
        'username': None,
        'current_page': "login",
        'clientes': dados.get('clientes', []),
        'motoristas': dados.get('motoristas', []),
        'empresas': dados.get('empresas', []),
        'cargas': dados.get('cargas', []),
        'agendamentos': dados.get('agendamentos', []),
        'pagamentos': dados.get('pagamentos', []),
        'notificacoes': [],
        'language': 'pt',
        'config_empresa': dados.get('config_empresa', {
            'nome': 'Userlog Transportes',
            'cnpj': '12.345.678/0001-90',
            'email': 'contato@userlog.com.br',
            'telefone': '(11) 3456-7890',
            'chave_pix': 'userlog@transportes.com.br',
            'endereco': 'Av. Paulista, 1000 - São Paulo, SP'
        }),
        'login_time': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ================= FUNÇÕES AUXILIARES =================
def format_currency(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def page_header(icon, title):
    st.markdown(f"""
    <div class="page-header">
        <span style="font-size:1.5rem">{icon}</span>
        <h1>{title}</h1>
        <div class="accent-dot"></div>
    </div>
    """, unsafe_allow_html=True)

def status_tag(status):
    classes = {
        "agendada": "tag-agendada", "agendado": "tag-agendada",
        "em andamento": "tag-em-andamento",
        "entregue": "tag-entregue",
        "pago": "tag-pago",
    }
    css = classes.get(status.lower(), "tag-agendada")
    return f'<span class="tag {css}">{status}</span>'

def plotly_dark_layout():
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9CA3AF', family='DM Sans'),
        margin=dict(l=10, r=10, t=30, b=10),
    )

# ================= LOGIN =================
def login_page():
    # Language selector at top
    col_lang, _ = st.columns([1, 4])
    with col_lang:
        lang_map = {"pt": "🇧🇷 PT", "en": "🇺🇸 EN", "es": "🇪🇸 ES", "zh": "🇨🇳 ZH"}
        sel = st.selectbox("", list(lang_map.keys()), format_func=lambda x: lang_map[x],
                           index=list(lang_map.keys()).index(st.session_state.language),
                           label_visibility="collapsed")
        if sel != st.session_state.language:
            st.session_state.language = sel
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown(f"""
        <div class="login-brand">
            <div style="font-size:3rem;margin-bottom:0.5rem">🚛</div>
            <h1>USERLOG</h1>
            <p>{t('app_name')}</p>
        </div>
        <div class="login-box">
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input(f"👤 {t('username')}", placeholder="seu usuário")
            password = st.text_input(f"🔒 {t('password')}", type="password", placeholder="••••••••")
            user_type = st.selectbox(f"📋 {t('user_type')}", [t('admin'), t('cliente'), t('motorista')])
            submitted = st.form_submit_button(t('login_button'), use_container_width=True)
            if submitted:
                if username and password:
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_type
                    st.session_state.username = username
                    st.session_state.current_page = "dashboard"
                    st.session_state.login_time = datetime.now().strftime("%H:%M")
                    st.rerun()
                else:
                    st.error(t('login_error'))

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <p style="text-align:center;font-size:0.75rem;color:#6B7280;margin-top:1rem">
            v2.0 · Aranhacorp · 2026
        </p>
        """, unsafe_allow_html=True)

# ================= SIDEBAR =================
def menu_sidebar():
    with st.sidebar:
        # Brand
        st.markdown(f"""
        <div class="brand-block">
            <span style="font-size:1.5rem">🚛</span>
            <div>
                <h2>USERLOG</h2>
                <span>Sistema de Transportes</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Language
        lang_map = {"pt": "🇧🇷 PT", "en": "🇺🇸 EN", "es": "🇪🇸 ES", "zh": "🇨🇳 ZH"}
        sel = st.selectbox(f"🌐 {t('language')}", list(lang_map.keys()),
                           format_func=lambda x: lang_map[x],
                           index=list(lang_map.keys()).index(st.session_state.language))
        if sel != st.session_state.language:
            st.session_state.language = sel
            st.rerun()

        # User card
        st.markdown(f"""
        <div class="user-card">
            <div>{t('user_info').format(st.session_state.username)}</div>
            <div>{t('user_type_info').format(st.session_state.user_type)}</div>
            <div>{t('login_time').format(st.session_state.login_time or datetime.now().strftime('%H:%M'))}</div>
        </div>
        """, unsafe_allow_html=True)

        # Menu
        st.markdown('<div class="menu-label">MENU PRINCIPAL</div>', unsafe_allow_html=True)

        menu_items = [
            (t('menu_dashboard'), "dashboard"),
            (t('menu_clientes'), "clientes"),
            (t('menu_motoristas'), "motoristas"),
            (t('menu_empresas'), "empresas"),
            (t('menu_agendamentos'), "agendamentos"),
            (t('menu_pagamentos'), "pagamentos"),
            (t('menu_relatorios'), "relatorios"),
            (t('menu_monitoramento'), "monitoramento"),
            (t('menu_configuracoes'), "config"),
        ]
        for label, page in menu_items:
            active = st.session_state.current_page == page
            if st.button(label, use_container_width=True, key=f"menu_{page}"):
                st.session_state.current_page = page
                st.rerun()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        with st.expander(t('quick_actions')):
            if st.button(t('new_agendamento'), use_container_width=True):
                st.session_state.current_page = "agendamentos"
                st.rerun()
            if st.button(t('new_pagamento'), use_container_width=True):
                st.session_state.current_page = "pagamentos"
                st.rerun()

        st.markdown(f"""
        <div class="version-tag">
            🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
            MASTER CODE DEEP SEEK LOG v2.0<br>
            © 2026 Userlog · Aranhacorp
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🚪 {t('logout')}", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# ================= DASHBOARD =================
def dashboard():
    page_header("📊", t('dashboard_title'))

    col1, col2, col3, col4 = st.columns(4)
    cargas_ativas = len([c for c in st.session_state.cargas if c.get('status') in ['agendada', 'em andamento']])
    total_fat = sum(p.get('valor', 0) for p in st.session_state.pagamentos if p.get('status') == 'pago')

    with col1:
        st.metric(t('metric_cargas_ativas'), cargas_ativas, delta=None)
    with col2:
        st.metric(t('metric_motoristas'), len(st.session_state.motoristas))
    with col3:
        st.metric(t('metric_clientes'), len(st.session_state.clientes))
    with col4:
        st.metric(t('metric_faturamento'), format_currency(total_fat))

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.markdown(f"**{t('chart_distribuicao')}**")
        if st.session_state.cargas:
            df = pd.DataFrame(st.session_state.cargas)
            counts = df['status'].value_counts().reset_index()
            counts.columns = ['status', 'count']
            fig = px.pie(counts, values='count', names='status',
                        color_discrete_sequence=['#F4A623', '#00D4AA', '#6366F1', '#EF4444'])
            fig.update_layout(**plotly_dark_layout())
            fig.update_traces(textfont_color='white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t('no_cargas'))

    with col2:
        st.markdown(f"**{t('chart_proximos')}**")
        if st.session_state.agendamentos:
            df = pd.DataFrame(st.session_state.agendamentos)
            cols_show = [c for c in ['data', 'cliente', 'origem', 'destino', 'status'] if c in df.columns]
            st.dataframe(df[cols_show].head(6), use_container_width=True, hide_index=True)
        else:
            st.info(t('no_agendamentos'))

    st.markdown(f"<br>**{t('recent_activities')}**", unsafe_allow_html=True)
    has_activity = False
    for p in st.session_state.pagamentos[-3:]:
        st.markdown(f"""
        <div class="activity-row green">
            💰 <strong>{t('pagamentos')}</strong> — {p.get('descricao', '')} — {format_currency(p.get('valor', 0))}
            &nbsp;&nbsp;{status_tag(p.get('status', 'pago'))}
        </div>
        """, unsafe_allow_html=True)
        has_activity = True
    for c in st.session_state.cargas[-3:]:
        st.markdown(f"""
        <div class="activity-row">
            📦 <strong>{t('mon_carga')} #{c.get('id', '')}</strong> — {c.get('origem', '')} → {c.get('destino', '')}
            &nbsp;&nbsp;{status_tag(c.get('status', 'agendada'))}
        </div>
        """, unsafe_allow_html=True)
        has_activity = True
    if not has_activity:
        st.info(t('no_activities'))

# ================= CLIENTES =================
def clientes():
    page_header("👥", t('clientes_title'))
    tab1, tab2 = st.tabs(["➕ Novo", "📋 Lista"])

    with tab1:
        with st.form("form_cliente"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input(t('cliente_nome'))
                cpf_cnpj = st.text_input(t('cliente_cpf_cnpj'))
            with col2:
                email = st.text_input(t('cliente_email'))
                telefone = st.text_input(t('cliente_telefone'))
            if st.form_submit_button(t('cliente_cadastrar'), use_container_width=True):
                if nome and cpf_cnpj and email and telefone:
                    st.session_state.clientes.append({
                        "id": len(st.session_state.clientes) + 1,
                        "nome": nome, "cpf_cnpj": cpf_cnpj,
                        "email": email, "telefone": telefone,
                        "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    salvar_dados()
                    st.success(t('cliente_cadastrado'))
                else:
                    st.error(t('cliente_erro'))

    with tab2:
        if st.session_state.clientes:
            df = pd.DataFrame(st.session_state.clientes)
            busca = st.text_input("🔍 Buscar", placeholder="Nome ou CPF/CNPJ...")
            if busca:
                df = df[df.apply(lambda r: busca.lower() in str(r.values).lower(), axis=1)]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(t('no_data'))

# ================= MOTORISTAS =================
def motoristas():
    page_header("👨‍✈️", t('motoristas_title'))
    tab1, tab2 = st.tabs(["➕ Novo", "📋 Lista"])

    with tab1:
        with st.form("form_motorista"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input(t('motorista_nome'))
                cnh = st.text_input(t('motorista_cnh'))
            with col2:
                telefone = st.text_input(t('motorista_telefone'))
                status = st.selectbox(t('motorista_status'),
                                      [t('status_disponivel'), t('status_viagem'), t('status_descanso')])
            if st.form_submit_button(t('motorista_cadastrar'), use_container_width=True):
                if nome and cnh and telefone:
                    st.session_state.motoristas.append({
                        "id": len(st.session_state.motoristas) + 1,
                        "nome": nome, "cnh": cnh,
                        "telefone": telefone, "status": status,
                        "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    salvar_dados()
                    st.success(t('motorista_cadastrado'))
                else:
                    st.error(t('cliente_erro'))

    with tab2:
        if st.session_state.motoristas:
            df = pd.DataFrame(st.session_state.motoristas)
            busca = st.text_input("🔍 Buscar", placeholder="Nome ou CNH...")
            if busca:
                df = df[df.apply(lambda r: busca.lower() in str(r.values).lower(), axis=1)]

            # Status overview
            disponivel = len([m for m in st.session_state.motoristas if m.get('status') == t('status_disponivel')])
            viagem = len([m for m in st.session_state.motoristas if m.get('status') == t('status_viagem')])
            c1, c2, c3 = st.columns(3)
            c1.metric("🟢 " + t('status_disponivel'), disponivel)
            c2.metric("🔵 " + t('status_viagem'), viagem)
            c3.metric("🟡 " + t('status_descanso'), len(st.session_state.motoristas) - disponivel - viagem)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(t('no_data'))

# ================= EMPRESAS =================
def empresas():
    page_header("🏢", t('empresas_title'))
    tab1, tab2 = st.tabs(["➕ Nova", "📋 Lista"])

    with tab1:
        with st.form("form_empresa"):
            col1, col2 = st.columns(2)
            with col1:
                razao = st.text_input(t('empresa_razao'))
                fantasia = st.text_input(t('empresa_fantasia'))
                cnpj = st.text_input(t('empresa_cnpj'))
            with col2:
                email = st.text_input(t('empresa_email'))
                telefone = st.text_input(t('empresa_telefone'))
            if st.form_submit_button(t('empresa_cadastrar'), use_container_width=True):
                if razao and fantasia and cnpj and email and telefone:
                    st.session_state.empresas.append({
                        "id": len(st.session_state.empresas) + 1,
                        "razao_social": razao, "nome_fantasia": fantasia,
                        "cnpj": cnpj, "email": email, "telefone": telefone,
                        "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    salvar_dados()
                    st.success(t('empresa_cadastrada'))
                else:
                    st.error(t('cliente_erro'))

    with tab2:
        if st.session_state.empresas:
            st.dataframe(pd.DataFrame(st.session_state.empresas), use_container_width=True, hide_index=True)
        else:
            st.info(t('no_data'))

# ================= AGENDAMENTOS =================
def agendamentos():
    page_header("📦", t('agendamentos_title'))
    tab1, tab2 = st.tabs(["➕ Novo", "📋 Lista"])

    with tab1:
        with st.form("form_agendamento"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox(t('ag_tipo_transporte'), [t('ag_rodoviario'), t('ag_aereo')])
                clientes_list = [c['nome'] for c in st.session_state.clientes] or [t('no_data')]
                cliente = st.selectbox(t('ag_cliente'), clientes_list)
                motoristas_disp = [m['nome'] for m in st.session_state.motoristas
                                   if m.get('status') == t('status_disponivel')] or [t('no_data')]
                motorista = st.selectbox(t('ag_motorista'), motoristas_disp)
                origem = st.text_input(t('ag_origem'))
            with col2:
                destino = st.text_input(t('ag_destino'))
                data = st.date_input(t('ag_data'), min_value=datetime.now().date(), format="DD/MM/YYYY")
                hora = st.time_input(t('ag_hora'))
                peso = st.number_input(t('ag_peso'), min_value=0.0, step=0.1)

            if st.form_submit_button(t('ag_agendar'), use_container_width=True):
                if origem and destino and peso > 0:
                    novo = {
                        "id": len(st.session_state.agendamentos) + 1,
                        "tipo": tipo, "cliente": cliente, "motorista": motorista,
                        "origem": origem, "destino": destino,
                        "data": data.strftime("%d/%m/%Y"),
                        "hora": hora.strftime("%H:%M"),
                        "peso": peso, "status": "agendado",
                        "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state.agendamentos.append(novo)
                    st.session_state.cargas.append({
                        "id": len(st.session_state.cargas) + 1,
                        "agendamento_id": novo["id"],
                        "cliente": cliente, "motorista": motorista,
                        "origem": origem, "destino": destino,
                        "tipo_carga": tipo, "peso": peso,
                        "status": "agendada",
                        "data_criacao": novo["data_criacao"]
                    })
                    salvar_dados()
                    st.success(t('ag_sucesso'))
                else:
                    st.error(t('ag_erro'))

    with tab2:
        if st.session_state.agendamentos:
            df = pd.DataFrame(st.session_state.agendamentos)
            busca = st.text_input("🔍 Buscar", placeholder="Origem, destino ou cliente...")
            if busca:
                df = df[df.apply(lambda r: busca.lower() in str(r.values).lower(), axis=1)]
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Update status
            st.markdown("---")
            st.markdown("**Atualizar status de carga**")
            col1, col2, col3 = st.columns(3)
            with col1:
                ids = [a['id'] for a in st.session_state.agendamentos]
                sel_id = st.selectbox("ID da carga", ids) if ids else None
            with col2:
                novo_status = st.selectbox("Novo status", ["agendado", "em andamento", "entregue", "cancelado"])
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Atualizar") and sel_id:
                    for a in st.session_state.agendamentos:
                        if a['id'] == sel_id:
                            a['status'] = novo_status
                    for c in st.session_state.cargas:
                        if c.get('agendamento_id') == sel_id:
                            c['status'] = novo_status if novo_status != 'agendado' else 'agendada'
                    salvar_dados()
                    st.success("Status atualizado!")
                    st.rerun()
        else:
            st.info(t('no_data'))

# ================= PAGAMENTOS =================
def pagamentos():
    page_header("💰", t('pagamentos_title'))
    tab1, tab2 = st.tabs(["➕ Novo", "📋 Histórico"])

    with tab1:
        col1, col2 = st.columns([1.2, 1])
        with col1:
            with st.form("form_pagamento"):
                valor = st.number_input(t('pag_valor'), min_value=0.01, step=10.0, value=100.0)
                descricao = st.text_input(t('pag_descricao'), placeholder="Frete SP-RJ, serviço #123...")
                if st.form_submit_button(t('pag_gerar'), use_container_width=True):
                    if valor > 0 and descricao:
                        try:
                            import qrcode
                            chave = st.session_state.config_empresa['chave_pix']
                            qr = qrcode.QRCode(version=1, box_size=8, border=4)
                            qr.add_data(f"PIX:{chave}:{valor}:{descricao}")
                            qr.make(fit=True)
                            img = qr.make_image(fill_color="black", back_color="white")
                            buf = BytesIO()
                            img.save(buf, format="PNG")
                            b64 = base64.b64encode(buf.getvalue()).decode()
                            with col2:
                                st.markdown(f"""
                                <div style="background:white;padding:1rem;border-radius:12px;text-align:center">
                                    <img src="data:image/png;base64,{b64}" width="200">
                                    <p style="color:#111;font-size:0.8rem;margin-top:0.5rem">
                                        🔑 {chave}<br>
                                        💰 {format_currency(valor)}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                        except ImportError:
                            st.warning("Instale qrcode: pip install qrcode[pil]")

                        st.session_state.pagamentos.append({
                            "id": len(st.session_state.pagamentos) + 1,
                            "valor": valor, "descricao": descricao,
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "status": "pago"
                        })
                        salvar_dados()
                        st.success(t('pag_registrado'))
                    else:
                        st.error(t('pag_erro'))

    with tab2:
        if st.session_state.pagamentos:
            df = pd.DataFrame(st.session_state.pagamentos)
            total = df['valor'].sum()

            c1, c2 = st.columns(2)
            c1.metric(t('rel_total_recebido'), format_currency(total))
            c2.metric("Transações", len(df))

            # Chart
            if len(df) > 1:
                fig = px.bar(df, x='data', y='valor',
                            color_discrete_sequence=['#F4A623'],
                            title="Histórico de Pagamentos")
                fig.update_layout(**plotly_dark_layout())
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(t('no_data'))

# ================= RELATÓRIOS =================
def relatorios():
    page_header("📈", t('relatorios_title'))
    tipo = st.selectbox(t('rel_tipo'), [t('rel_cargas'), t('rel_pagamentos'), t('rel_motoristas')])

    if tipo == t('rel_cargas'):
        if st.session_state.cargas:
            df = pd.DataFrame(st.session_state.cargas)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total de cargas", len(df))
            c2.metric("Em andamento", len(df[df['status'] == 'em andamento']) if 'status' in df else 0)
            c3.metric("Entregues", len(df[df['status'] == 'entregue']) if 'status' in df else 0)

            fig = px.bar(df['status'].value_counts().reset_index(),
                        x='status', y='count',
                        color_discrete_sequence=['#F4A623', '#00D4AA', '#6366F1'])
            fig.update_layout(**plotly_dark_layout())
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(t('no_data'))

    elif tipo == t('rel_pagamentos'):
        if st.session_state.pagamentos:
            df = pd.DataFrame(st.session_state.pagamentos)
            total = df['valor'].sum()
            st.metric(t('rel_total_recebido'), format_currency(total))
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(t('no_data'))

    elif tipo == t('rel_motoristas'):
        if st.session_state.motoristas:
            df = pd.DataFrame(st.session_state.motoristas)
            fig = px.pie(df['status'].value_counts().reset_index(),
                        values='count', names='status',
                        color_discrete_sequence=['#00D4AA', '#F4A623', '#6366F1'])
            fig.update_layout(**plotly_dark_layout())
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(t('no_data'))

# ================= MONITORAMENTO =================
def monitoramento():
    page_header("🛰️", t('monitoramento_title'))
    status_filter = st.multiselect(t('mon_status'),
                                   ["agendada", "em andamento", "entregue"],
                                   default=["agendada", "em andamento"])
    cargas_filtradas = [c for c in st.session_state.cargas if c.get('status') in status_filter]

    if cargas_filtradas:
        for c in cargas_filtradas:
            status = c.get('status', 'agendada')
            icon = "🟢" if status == "em andamento" else ("✅" if status == "entregue" else "🟡")
            st.markdown(f"""
            <div class="load-card">
                <div>
                    <div class="load-id">CARGA #{c['id']} · {c.get('tipo_carga', 'N/A')}</div>
                    <div class="load-title">📍 {c.get('origem', '')} <span class="sep">→</span> {c.get('destino', '')}</div>
                    <div style="font-size:0.8rem;color:#9CA3AF;margin-top:0.25rem">🚚 {c.get('motorista', 'N/A')} · ⚖️ {c.get('peso', 0)} kg</div>
                </div>
                <div style="font-size:0.8rem;color:#9CA3AF">
                    👤 {c.get('cliente', 'N/A')}<br>
                    🗓 {c.get('data_criacao', '')}
                </div>
                <div>{status_tag(status)}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(t('no_data'))

# ================= CONFIGURAÇÕES =================
def configuracoes():
    page_header("⚙️", t('config_title'))
    with st.form("config_empresa"):
        st.markdown(f"**{t('config_dados_empresa')}**")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input(t('config_nome'), value=st.session_state.config_empresa.get('nome', ''))
            cnpj = st.text_input(t('config_cnpj'), value=st.session_state.config_empresa.get('cnpj', ''))
            email = st.text_input("E-mail", value=st.session_state.config_empresa.get('email', ''))
        with col2:
            chave_pix = st.text_input(t('config_chave_pix'), value=st.session_state.config_empresa.get('chave_pix', ''))
            telefone = st.text_input("Telefone", value=st.session_state.config_empresa.get('telefone', ''))
            endereco = st.text_input("Endereço", value=st.session_state.config_empresa.get('endereco', ''))

        if st.form_submit_button(t('config_salvar'), use_container_width=True):
            st.session_state.config_empresa.update({
                'nome': nome, 'cnpj': cnpj, 'email': email,
                'chave_pix': chave_pix, 'telefone': telefone, 'endereco': endereco
            })
            salvar_dados()
            st.success(t('config_sucesso'))

    # Backup / Restore
    st.markdown("---")
    st.markdown("**📁 Backup de dados**")
    col1, col2 = st.columns(2)
    with col1:
        dados_json = json.dumps({
            "clientes": st.session_state.clientes,
            "motoristas": st.session_state.motoristas,
            "empresas": st.session_state.empresas,
            "cargas": st.session_state.cargas,
            "agendamentos": st.session_state.agendamentos,
            "pagamentos": st.session_state.pagamentos,
        }, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ Exportar dados (JSON)",
            data=dados_json,
            file_name=f"userlog_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )

# ================= ROTEAMENTO =================
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        menu_sidebar()
        pages = {
            "dashboard": dashboard,
            "clientes": clientes,
            "motoristas": motoristas,
            "empresas": empresas,
            "agendamentos": agendamentos,
            "pagamentos": pagamentos,
            "relatorios": relatorios,
            "monitoramento": monitoramento,
            "config": configuracoes,
        }
        fn = pages.get(st.session_state.current_page, dashboard)
        fn()

if __name__ == "__main__":
    main()
