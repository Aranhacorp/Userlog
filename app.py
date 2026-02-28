"""
MASTER CODE DEEP SEEK LOG v.1.7
Userlog - Sistema de Transportes (Multilíngue)
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
    page_icon="🔼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= DICIONÁRIO DE TRADUÇÕES =================
translations = {
    "pt": {
        # Geral
        "app_name": "Userlog - Sistema de Transportes",
        "welcome": "Bem-vindo",
        "login": "Entrar",
        "logout": "Sair",
        "username": "Usuário",
        "password": "Senha",
        "user_type": "Tipo",
        "admin": "admin",
        "cliente": "cliente",
        "motorista": "motorista",
        "required_field": "Campo obrigatório",
        "save": "Salvar",
        "cancel": "Cancelar",
        "add": "Adicionar",
        "edit": "Editar",
        "delete": "Excluir",
        "search": "Buscar",
        "filter": "Filtrar",
        "export": "Exportar",
        "actions": "Ações",
        "confirm": "Confirmar",
        "success": "Sucesso",
        "error": "Erro",
        "warning": "Aviso",
        "info": "Informação",
        "no_data": "Sem dados",
        "loading": "Carregando...",
        
        # Menu
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
        
        # Login
        "login_title": "Userlog - Sistema de Transportes",
        "login_button": "🚪 Entrar",
        "login_error": "❌ Usuário e senha obrigatórios!",
        
        # Dashboard
        "dashboard_title": "📊 Dashboard Userlog",
        "metric_cargas_ativas": "📦 Cargas Ativas",
        "metric_motoristas": "👨‍✈️ Motoristas",
        "metric_clientes": "👥 Clientes",
        "metric_faturamento": "💰 Faturamento",
        "chart_distribuicao": "📈 Distribuição de Cargas",
        "chart_proximos": "📅 Próximos Agendamentos",
        "recent_activities": "🔄 Atividades Recentes",
        "no_cargas": "Nenhuma carga cadastrada",
        "no_agendamentos": "Nenhum agendamento",
        "no_activities": "Nenhuma atividade recente",
        
        # Clientes
        "clientes_title": "👥 Cadastro de Clientes",
        "cliente_nome": "Nome completo *",
        "cliente_cpf_cnpj": "CPF/CNPJ *",
        "cliente_email": "E-mail *",
        "cliente_telefone": "Telefone *",
        "cliente_cadastrar": "Cadastrar Cliente",
        "cliente_cadastrado": "Cliente cadastrado!",
        "cliente_erro": "Preencha todos os campos obrigatórios!",
        "clientes_lista": "Clientes Cadastrados",
        
        # Motoristas
        "motoristas_title": "👨‍✈️ Cadastro de Motoristas",
        "motorista_nome": "Nome completo *",
        "motorista_cnh": "CNH *",
        "motorista_telefone": "Telefone *",
        "motorista_status": "Status",
        "status_disponivel": "Disponível",
        "status_viagem": "Em viagem",
        "status_descanso": "Descanso",
        "motorista_cadastrar": "Cadastrar Motorista",
        "motorista_cadastrado": "Motorista cadastrado!",
        "motoristas_lista": "Motoristas Cadastrados",
        
        # Empresas
        "empresas_title": "🏢 Cadastro de Empresas",
        "empresa_razao": "Razão Social *",
        "empresa_fantasia": "Nome Fantasia *",
        "empresa_cnpj": "CNPJ *",
        "empresa_email": "E-mail *",
        "empresa_telefone": "Telefone *",
        "empresa_cadastrar": "Cadastrar Empresa",
        "empresa_cadastrada": "Empresa cadastrada!",
        "empresas_lista": "Empresas Cadastradas",
        
        # Agendamentos
        "agendamentos_title": "📦 Agendamento de Cargas",
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
        "ag_sucesso": "Carga agendada com sucesso!",
        "ag_erro": "Preencha origem, destino e peso válido!",
        "ag_lista": "Agendamentos Realizados",
        
        # Pagamentos
        "pagamentos_title": "💰 Pagamentos via PIX",
        "pag_valor": "Valor (R$)",
        "pag_descricao": "Descrição",
        "pag_gerar": "Gerar QR Code PIX",
        "pag_chave": "Chave PIX",
        "pag_registrado": "Pagamento registrado (simulado)!",
        "pag_erro": "Preencha valor e descrição",
        "pag_lista": "Histórico de Pagamentos",
        
        # Relatórios
        "relatorios_title": "📊 Relatórios",
        "rel_tipo": "Tipo de relatório",
        "rel_cargas": "Cargas",
        "rel_pagamentos": "Pagamentos",
        "rel_motoristas": "Motoristas",
        "rel_total_recebido": "Total recebido",
        
        # Monitoramento
        "monitoramento_title": "🛰️ Monitoramento de Cargas",
        "mon_status": "Status",
        "mon_em_rota": "🟢 Em rota",
        "mon_entregue": "✅ Entregue",
        "mon_agendada": "🟡 Agendada",
        "mon_carga": "Carga",
        
        # Configurações
        "config_title": "⚙️ Configurações",
        "config_dados_empresa": "Dados da Empresa",
        "config_nome": "Nome da Empresa",
        "config_cnpj": "CNPJ",
        "config_chave_pix": "Chave PIX",
        "config_salvar": "Salvar",
        "config_sucesso": "Configurações salvas!",
        
        # Idioma
        "language": "Idioma",
        "lang_pt": "Português",
        "lang_en": "Inglês",
        "lang_es": "Espanhol",
        "lang_zh": "Chinês",
        
        # Sidebar
        "user_info": "👤 Usuário: {}",
        "user_type_info": "📋 Tipo: {}",
        "login_time": "🕐 Login: {}",
    },
    "en": {
        # General
        "app_name": "Userlog - Transport System",
        "welcome": "Welcome",
        "login": "Login",
        "logout": "Logout",
        "username": "Username",
        "password": "Password",
        "user_type": "Type",
        "admin": "admin",
        "cliente": "client",
        "motorista": "driver",
        "required_field": "Required field",
        "save": "Save",
        "cancel": "Cancel",
        "add": "Add",
        "edit": "Edit",
        "delete": "Delete",
        "search": "Search",
        "filter": "Filter",
        "export": "Export",
        "actions": "Actions",
        "confirm": "Confirm",
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "info": "Info",
        "no_data": "No data",
        "loading": "Loading...",
        
        # Menu
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
        
        # Login
        "login_title": "Userlog - Transport System",
        "login_button": "🚪 Login",
        "login_error": "❌ Username and password required!",
        
        # Dashboard
        "dashboard_title": "📊 Userlog Dashboard",
        "metric_cargas_ativas": "📦 Active Loads",
        "metric_motoristas": "👨‍✈️ Drivers",
        "metric_clientes": "👥 Clients",
        "metric_faturamento": "💰 Revenue",
        "chart_distribuicao": "📈 Load Distribution",
        "chart_proximos": "📅 Upcoming Schedules",
        "recent_activities": "🔄 Recent Activities",
        "no_cargas": "No loads registered",
        "no_agendamentos": "No schedules",
        "no_activities": "No recent activities",
        
        # Clients
        "clientes_title": "👥 Client Registration",
        "cliente_nome": "Full name *",
        "cliente_cpf_cnpj": "CPF/CNPJ *",
        "cliente_email": "Email *",
        "cliente_telefone": "Phone *",
        "cliente_cadastrar": "Register Client",
        "cliente_cadastrado": "Client registered!",
        "cliente_erro": "Fill all required fields!",
        "clientes_lista": "Registered Clients",
        
        # Drivers
        "motoristas_title": "👨‍✈️ Driver Registration",
        "motorista_nome": "Full name *",
        "motorista_cnh": "Driver's License *",
        "motorista_telefone": "Phone *",
        "motorista_status": "Status",
        "status_disponivel": "Available",
        "status_viagem": "On trip",
        "status_descanso": "Resting",
        "motorista_cadastrar": "Register Driver",
        "motorista_cadastrado": "Driver registered!",
        "motoristas_lista": "Registered Drivers",
        
        # Companies
        "empresas_title": "🏢 Company Registration",
        "empresa_razao": "Company Name *",
        "empresa_fantasia": "Trade Name *",
        "empresa_cnpj": "CNPJ *",
        "empresa_email": "Email *",
        "empresa_telefone": "Phone *",
        "empresa_cadastrar": "Register Company",
        "empresa_cadastrada": "Company registered!",
        "empresas_lista": "Registered Companies",
        
        # Schedules
        "agendamentos_title": "📦 Load Scheduling",
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
        "ag_sucesso": "Load scheduled successfully!",
        "ag_erro": "Fill origin, destination and valid weight!",
        "ag_lista": "Scheduled Loads",
        
        # Payments
        "pagamentos_title": "💰 PIX Payments",
        "pag_valor": "Amount (R$)",
        "pag_descricao": "Description",
        "pag_gerar": "Generate PIX QR Code",
        "pag_chave": "PIX Key",
        "pag_registrado": "Payment recorded (simulated)!",
        "pag_erro": "Fill amount and description",
        "pag_lista": "Payment History",
        
        # Reports
        "relatorios_title": "📊 Reports",
        "rel_tipo": "Report type",
        "rel_cargas": "Loads",
        "rel_pagamentos": "Payments",
        "rel_motoristas": "Drivers",
        "rel_total_recebido": "Total received",
        
        # Monitoring
        "monitoramento_title": "🛰️ Load Monitoring",
        "mon_status": "Status",
        "mon_em_rota": "🟢 On route",
        "mon_entregue": "✅ Delivered",
        "mon_agendada": "🟡 Scheduled",
        "mon_carga": "Load",
        
        # Settings
        "config_title": "⚙️ Settings",
        "config_dados_empresa": "Company Data",
        "config_nome": "Company Name",
        "config_cnpj": "CNPJ",
        "config_chave_pix": "PIX Key",
        "config_salvar": "Save",
        "config_sucesso": "Settings saved!",
        
        # Language
        "language": "Language",
        "lang_pt": "Portuguese",
        "lang_en": "English",
        "lang_es": "Spanish",
        "lang_zh": "Chinese",
        
        # Sidebar
        "user_info": "👤 User: {}",
        "user_type_info": "📋 Type: {}",
        "login_time": "🕐 Login: {}",
    },
    "es": {
        # General
        "app_name": "Userlog - Sistema de Transporte",
        "welcome": "Bienvenido",
        "login": "Iniciar sesión",
        "logout": "Cerrar sesión",
        "username": "Usuario",
        "password": "Contraseña",
        "user_type": "Tipo",
        "admin": "admin",
        "cliente": "cliente",
        "motorista": "conductor",
        "required_field": "Campo obligatorio",
        "save": "Guardar",
        "cancel": "Cancelar",
        "add": "Agregar",
        "edit": "Editar",
        "delete": "Eliminar",
        "search": "Buscar",
        "filter": "Filtrar",
        "export": "Exportar",
        "actions": "Acciones",
        "confirm": "Confirmar",
        "success": "Éxito",
        "error": "Error",
        "warning": "Advertencia",
        "info": "Información",
        "no_data": "Sin datos",
        "loading": "Cargando...",
        
        # Menu
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
        
        # Login
        "login_title": "Userlog - Sistema de Transporte",
        "login_button": "🚪 Entrar",
        "login_error": "❌ ¡Usuario y contraseña obligatorios!",
        
        # Dashboard
        "dashboard_title": "📊 Panel Userlog",
        "metric_cargas_ativas": "📦 Cargas activas",
        "metric_motoristas": "👨‍✈️ Conductores",
        "metric_clientes": "👥 Clientes",
        "metric_faturamento": "💰 Facturación",
        "chart_distribuicao": "📈 Distribución de cargas",
        "chart_proximos": "📅 Próximos agendamientos",
        "recent_activities": "🔄 Actividades recientes",
        "no_cargas": "Ninguna carga registrada",
        "no_agendamentos": "Ningún agendamiento",
        "no_activities": "Ninguna actividad reciente",
        
        # Clients
        "clientes_title": "👥 Registro de Clientes",
        "cliente_nome": "Nombre completo *",
        "cliente_cpf_cnpj": "CPF/CNPJ *",
        "cliente_email": "Correo *",
        "cliente_telefone": "Teléfono *",
        "cliente_cadastrar": "Registrar Cliente",
        "cliente_cadastrado": "¡Cliente registrado!",
        "cliente_erro": "¡Complete todos los campos obligatorios!",
        "clientes_lista": "Clientes Registrados",
        
        # Drivers
        "motoristas_title": "👨‍✈️ Registro de Conductores",
        "motorista_nome": "Nombre completo *",
        "motorista_cnh": "Licencia *",
        "motorista_telefone": "Teléfono *",
        "motorista_status": "Estado",
        "status_disponivel": "Disponible",
        "status_viagem": "En viaje",
        "status_descanso": "Descanso",
        "motorista_cadastrar": "Registrar Conductor",
        "motorista_cadastrado": "¡Conductor registrado!",
        "motoristas_lista": "Conductores Registrados",
        
        # Companies
        "empresas_title": "🏢 Registro de Empresas",
        "empresa_razao": "Razón Social *",
        "empresa_fantasia": "Nombre Fantasía *",
        "empresa_cnpj": "CNPJ *",
        "empresa_email": "Correo *",
        "empresa_telefone": "Teléfono *",
        "empresa_cadastrar": "Registrar Empresa",
        "empresa_cadastrada": "¡Empresa registrada!",
        "empresas_lista": "Empresas Registradas",
        
        # Schedules
        "agendamentos_title": "📦 Agendamiento de Cargas",
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
        "ag_sucesso": "¡Carga agendada con éxito!",
        "ag_erro": "¡Complete origen, destino y peso válido!",
        "ag_lista": "Agendamientos Realizados",
        
        # Payments
        "pagamentos_title": "💰 Pagos vía PIX",
        "pag_valor": "Valor (R$)",
        "pag_descricao": "Descripción",
        "pag_gerar": "Generar código QR PIX",
        "pag_chave": "Clave PIX",
        "pag_registrado": "¡Pago registrado (simulado)!",
        "pag_erro": "Complete valor y descripción",
        "pag_lista": "Historial de Pagos",
        
        # Reports
        "relatorios_title": "📊 Informes",
        "rel_tipo": "Tipo de informe",
        "rel_cargas": "Cargas",
        "rel_pagamentos": "Pagos",
        "rel_motoristas": "Conductores",
        "rel_total_recebido": "Total recibido",
        
        # Monitoring
        "monitoramento_title": "🛰️ Monitoreo de Cargas",
        "mon_status": "Estado",
        "mon_em_rota": "🟢 En ruta",
        "mon_entregue": "✅ Entregado",
        "mon_agendada": "🟡 Agendada",
        "mon_carga": "Carga",
        
        # Settings
        "config_title": "⚙️ Configuración",
        "config_dados_empresa": "Datos de la Empresa",
        "config_nome": "Nombre de la Empresa",
        "config_cnpj": "CNPJ",
        "config_chave_pix": "Clave PIX",
        "config_salvar": "Guardar",
        "config_sucesso": "¡Configuración guardada!",
        
        # Language
        "language": "Idioma",
        "lang_pt": "Portugués",
        "lang_en": "Inglés",
        "lang_es": "Español",
        "lang_zh": "Chino",
        
        # Sidebar
        "user_info": "👤 Usuario: {}",
        "user_type_info": "📋 Tipo: {}",
        "login_time": "🕐 Hora de inicio: {}",
    },
    "zh": {
        # General
        "app_name": "Userlog - 运输系统",
        "welcome": "欢迎",
        "login": "登录",
        "logout": "登出",
        "username": "用户名",
        "password": "密码",
        "user_type": "类型",
        "admin": "管理员",
        "cliente": "客户",
        "motorista": "司机",
        "required_field": "必填字段",
        "save": "保存",
        "cancel": "取消",
        "add": "添加",
        "edit": "编辑",
        "delete": "删除",
        "search": "搜索",
        "filter": "筛选",
        "export": "导出",
        "actions": "操作",
        "confirm": "确认",
        "success": "成功",
        "error": "错误",
        "warning": "警告",
        "info": "信息",
        "no_data": "无数据",
        "loading": "加载中...",
        
        # Menu
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
        
        # Login
        "login_title": "Userlog - 运输系统",
        "login_button": "🚪 登录",
        "login_error": "❌ 用户名和密码为必填项！",
        
        # Dashboard
        "dashboard_title": "📊 Userlog 仪表板",
        "metric_cargas_ativas": "📦 活跃货物",
        "metric_motoristas": "👨‍✈️ 司机",
        "metric_clientes": "👥 客户",
        "metric_faturamento": "💰 收入",
        "chart_distribuicao": "📈 货物分布",
        "chart_proximos": "📅 即将到来的日程",
        "recent_activities": "🔄 最近活动",
        "no_cargas": "无货物登记",
        "no_agendamentos": "无日程安排",
        "no_activities": "无最近活动",
        
        # Clients
        "clientes_title": "👥 客户登记",
        "cliente_nome": "全名 *",
        "cliente_cpf_cnpj": "CPF/CNPJ *",
        "cliente_email": "电子邮件 *",
        "cliente_telefone": "电话 *",
        "cliente_cadastrar": "登记客户",
        "cliente_cadastrado": "客户登记成功！",
        "cliente_erro": "请填写所有必填字段！",
        "clientes_lista": "已登记客户",
        
        # Drivers
        "motoristas_title": "👨‍✈️ 司机登记",
        "motorista_nome": "全名 *",
        "motorista_cnh": "驾照 *",
        "motorista_telefone": "电话 *",
        "motorista_status": "状态",
        "status_disponivel": "可用",
        "status_viagem": "途中",
        "status_descanso": "休息",
        "motorista_cadastrar": "登记司机",
        "motorista_cadastrado": "司机登记成功！",
        "motoristas_lista": "已登记司机",
        
        # Companies
        "empresas_title": "🏢 公司登记",
        "empresa_razao": "公司名称 *",
        "empresa_fantasia": "商业名称 *",
        "empresa_cnpj": "CNPJ *",
        "empresa_email": "电子邮件 *",
        "empresa_telefone": "电话 *",
        "empresa_cadastrar": "登记公司",
        "empresa_cadastrada": "公司登记成功！",
        "empresas_lista": "已登记公司",
        
        # Schedules
        "agendamentos_title": "📦 货物日程安排",
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
        "ag_sucesso": "货物安排成功！",
        "ag_erro": "请填写出发地、目的地和有效重量！",
        "ag_lista": "已安排的货物",
        
        # Payments
        "pagamentos_title": "💰 PIX 付款",
        "pag_valor": "金额 (R$)",
        "pag_descricao": "描述",
        "pag_gerar": "生成 PIX 二维码",
        "pag_chave": "PIX 密钥",
        "pag_registrado": "付款记录 (模拟)!",
        "pag_erro": "请填写金额和描述",
        "pag_lista": "付款历史",
        
        # Reports
        "relatorios_title": "📊 报告",
        "rel_tipo": "报告类型",
        "rel_cargas": "货物",
        "rel_pagamentos": "付款",
        "rel_motoristas": "司机",
        "rel_total_recebido": "总收入",
        
        # Monitoring
        "monitoramento_title": "🛰️ 货物监控",
        "mon_status": "状态",
        "mon_em_rota": "🟢 途中",
        "mon_entregue": "✅ 已交付",
        "mon_agendada": "🟡 已安排",
        "mon_carga": "货物",
        
        # Settings
        "config_title": "⚙️ 设置",
        "config_dados_empresa": "公司数据",
        "config_nome": "公司名称",
        "config_cnpj": "CNPJ",
        "config_chave_pix": "PIX 密钥",
        "config_salvar": "保存",
        "config_sucesso": "设置已保存！",
        
        # Language
        "language": "语言",
        "lang_pt": "葡萄牙语",
        "lang_en": "英语",
        "lang_es": "西班牙语",
        "lang_zh": "中文",
        
        # Sidebar
        "user_info": "👤 用户: {}",
        "user_type_info": "📋 类型: {}",
        "login_time": "🕐 登录时间: {}",
    }
}

# ================= FUNÇÃO DE TRADUÇÃO =================
def t(key):
    """Retorna a tradução da chave no idioma atual."""
    lang = st.session_state.get("language", "pt")
    return translations.get(lang, translations["pt"]).get(key, key)

# ================= CSS PERSONALIZADO =================
st.markdown("""
<style>
    /* Fundo da área principal com azul escuro transparente */
    .main > div {
        background-color: rgba(0, 0, 139, 0.15);  /* Azul escuro com 15% de opacidade */
        padding: 1rem;
        border-radius: 10px;
    }
    /* Sidebar com fundo cinza transparente */
    section[data-testid="stSidebar"] {
        background-color: rgba(240, 242, 246, 0.7);  /* Cinza claro com 70% de opacidade */
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
    /* Container para centralizar a imagem e dar espaçamento */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
        padding: 0 1rem;
    }
    .logo-container img {
        width: 100%;
        max-width: 600px; /* Limita o tamanho em telas muito largas */
        height: auto;
        border-radius: 10px;
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
    if 'language' not in st.session_state:
        st.session_state.language = "pt"  # Idioma padrão

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
        with st.sidebar.expander(f"🔔 {t('notifications')} ({len(nao_lidas)})"):
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
def exibir_logo():
    """Tenta carregar a imagem logistics-sunset_png.avif e exibi-la com largura total do container."""
    caminhos_possiveis = [
        "assets/logistics-sunset_png.avif",
        "logistics-sunset_png.avif"
    ]
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            img = Image.open(caminho)
            # Exibe a imagem ocupando toda a largura do container (respeitando o max-width definido no CSS)
            st.image(img, use_column_width=True)
            return True
    return False

# ================= PÁGINA DE LOGIN =================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Container para centralizar a imagem com espaçamento
        with st.container():
            st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
            if not exibir_logo():
                # Se não encontrar a imagem, mostra o título padrão
                st.markdown(f"<div class='main-header'><h1>🚚 {t('app_name')}</h1></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Título abaixo da imagem (mesmo estilo do balão)
        st.markdown(f"<div class='main-header'><h1>{t('app_name')}</h1></div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(f"👤 {t('username')}")
            password = st.text_input(f"🔒 {t('password')}", type="password")
            user_type = st.selectbox(f"📋 {t('user_type')}", [t('admin'), t('cliente'), t('motorista')])
            
            if st.form_submit_button(t('login_button'), use_container_width=True):
                if username and password:
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_type
                    st.session_state.username = username
                    st.session_state.current_page = "dashboard"
                    adicionar_notificacao(t('welcome'), f"{t('welcome')}, {username}!", "success")
                    st.rerun()
                else:
                    st.error(t('login_error'))

# ================= MENU LATERAL =================
def menu_sidebar():
    with st.sidebar:
        # Logo na barra lateral (menor, mas ainda usando largura total)
        if not exibir_logo():
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;'>
                <h2 style='color: white; margin: 0;'>USERLOG</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Seletor de idioma
        lang_options = {
            "pt": t('lang_pt'),
            "en": t('lang_en'),
            "es": t('lang_es'),
            "zh": t('lang_zh')
        }
        selected_lang = st.selectbox(
            f"🌐 {t('language')}",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=list(lang_options.keys()).index(st.session_state.language)
        )
        if selected_lang != st.session_state.language:
            st.session_state.language = selected_lang
            st.rerun()
        
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 10px 0;'>
            <p><strong>{t('user_info').format(st.session_state.username)}</strong></p>
            <p><strong>{t('user_type_info').format(st.session_state.user_type)}</strong></p>
            <p><strong>{t('login_time').format(datetime.now().strftime('%H:%M'))}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        mostrar_notificacoes()
        
        st.markdown(f"### {t('menu_dashboard').split()[0]} Menu Principal")
        menu_options = {
            t('menu_dashboard'): "dashboard",
            t('menu_clientes'): "clientes",
            t('menu_motoristas'): "motoristas",
            t('menu_empresas'): "empresas",
            t('menu_agendamentos'): "agendamentos",
            t('menu_pagamentos'): "pagamentos",
            t('menu_relatorios'): "relatorios",
            t('menu_monitoramento'): "monitoramento",
            t('menu_configuracoes'): "config"
        }
        
        for label, page in menu_options.items():
            if st.button(label, use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        with st.expander(t('quick_actions')):
            if st.button(t('new_agendamento'), use_container_width=True):
                st.session_state.current_page = "agendamentos"
                st.rerun()
            if st.button(t('new_pagamento'), use_container_width=True):
                st.session_state.current_page = "pagamentos"
                st.rerun()
        
        st.markdown(f"""
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
            <p>🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p>MASTER CODE DEEP SEEK LOG v.1.7</p>
            <p>© 2026 - Userlog</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🚪 {t('logout')}", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# ================= DASHBOARD =================
def dashboard():
    st.markdown(f"<div class='main-header'><h1>{t('dashboard_title')}</h1></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(t('metric_cargas_ativas'), len([c for c in st.session_state.cargas if c.get('status') in ['agendada','em andamento']]))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(t('metric_motoristas'), len(st.session_state.motoristas))
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(t('metric_clientes'), len(st.session_state.clientes))
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        total = sum([p.get('valor',0) for p in st.session_state.pagamentos if p.get('status')=='pago'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(t('metric_faturamento'), format_currency(total))
        st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t('chart_distribuicao'))
        if st.session_state.cargas:
            df = pd.DataFrame(st.session_state.cargas)
            status_count = df['status'].value_counts()
            fig = px.pie(values=status_count.values, names=status_count.index)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t('no_cargas'))
    with col2:
        st.subheader(t('chart_proximos'))
        if st.session_state.agendamentos:
            df = pd.DataFrame(st.session_state.agendamentos)
            st.dataframe(df[['data','cliente','origem','destino','status']].head(5), use_container_width=True)
        else:
            st.info(t('no_agendamentos'))
    
    st.subheader(t('recent_activities'))
    if st.session_state.pagamentos or st.session_state.cargas:
        for p in st.session_state.pagamentos[-3:]:
            st.success(f"💰 {t('pagamentos')} {p.get('cliente','')} - {format_currency(p.get('valor',0))}")
        for c in st.session_state.cargas[-3:]:
            st.info(f"📦 {t('mon_carga')} #{c.get('id','')} - {c.get('origem','')} → {c.get('destino','')}")
    else:
        st.info(t('no_activities'))

# ================= CADASTRO DE CLIENTES =================
def clientes():
    st.markdown(f"<div class='main-header'><h1>{t('clientes_title')}</h1></div>", unsafe_allow_html=True)
    with st.form("form_cliente"):
        nome = st.text_input(t('cliente_nome'))
        cpf_cnpj = st.text_input(t('cliente_cpf_cnpj'))
        email = st.text_input(t('cliente_email'))
        telefone = st.text_input(t('cliente_telefone'))
        if st.form_submit_button(t('cliente_cadastrar')):
            if nome and cpf_cnpj and email and telefone:
                st.session_state.clientes.append({
                    "id": len(st.session_state.clientes)+1,
                    "nome": nome,
                    "cpf_cnpj": cpf_cnpj,
                    "email": email,
                    "telefone": telefone,
                    "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                st.success(t('cliente_cadastrado'))
            else:
                st.error(t('cliente_erro'))
    
    if st.session_state.clientes:
        st.subheader(t('clientes_lista'))
        st.dataframe(pd.DataFrame(st.session_state.clientes))

# ================= CADASTRO DE MOTORISTAS =================
def motoristas():
    st.markdown(f"<div class='main-header'><h1>{t('motoristas_title')}</h1></div>", unsafe_allow_html=True)
    with st.form("form_motorista"):
        nome = st.text_input(t('motorista_nome'))
        cnh = st.text_input(t('motorista_cnh'))
        telefone = st.text_input(t('motorista_telefone'))
        status = st.selectbox(t('motorista_status'), [t('status_disponivel'), t('status_viagem'), t('status_descanso')])
        if st.form_submit_button(t('motorista_cadastrar')):
            if nome and cnh and telefone:
                st.session_state.motoristas.append({
                    "id": len(st.session_state.motoristas)+1,
                    "nome": nome,
                    "cnh": cnh,
                    "telefone": telefone,
                    "status": status,
                    "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                st.success(t('motorista_cadastrado'))
            else:
                st.error(t('cliente_erro'))
    
    if st.session_state.motoristas:
        st.subheader(t('motoristas_lista'))
        st.dataframe(pd.DataFrame(st.session_state.motoristas))

# ================= CADASTRO DE EMPRESAS =================
def empresas():
    st.markdown(f"<div class='main-header'><h1>{t('empresas_title')}</h1></div>", unsafe_allow_html=True)
    with st.form("form_empresa"):
        razao = st.text_input(t('empresa_razao'))
        fantasia = st.text_input(t('empresa_fantasia'))
        cnpj = st.text_input(t('empresa_cnpj'))
        email = st.text_input(t('empresa_email'))
        telefone = st.text_input(t('empresa_telefone'))
        if st.form_submit_button(t('empresa_cadastrar')):
            if razao and fantasia and cnpj and email and telefone:
                st.session_state.empresas.append({
                    "id": len(st.session_state.empresas)+1,
                    "razao_social": razao,
                    "nome_fantasia": fantasia,
                    "cnpj": cnpj,
                    "email": email,
                    "telefone": telefone,
                    "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                st.success(t('empresa_cadastrada'))
            else:
                st.error(t('cliente_erro'))
    
    if st.session_state.empresas:
        st.subheader(t('empresas_lista'))
        st.dataframe(pd.DataFrame(st.session_state.empresas))

# ================= AGENDAMENTO DE CARGAS =================
def agendamentos():
    st.markdown(f"<div class='main-header'><h1>{t('agendamentos_title')}</h1></div>", unsafe_allow_html=True)
    with st.form("form_agendamento"):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox(t('ag_tipo_transporte'), [t('ag_rodoviario'), t('ag_aereo')])
            cliente = st.selectbox(t('ag_cliente'), [c['nome'] for c in st.session_state.clientes] if st.session_state.clientes else [t('no_data')])
            motorista = st.selectbox(t('ag_motorista'), [m['nome'] for m in st.session_state.motoristas if m.get('status')==t('status_disponivel')] if st.session_state.motoristas else [t('no_data')])
            origem = st.text_input(t('ag_origem'))
        with col2:
            destino = st.text_input(t('ag_destino'))
            data = st.date_input(t('ag_data'), min_value=datetime.now().date(), format="DD/MM/YYYY")
            hora = st.time_input(t('ag_hora'))
            peso = st.number_input(t('ag_peso'), min_value=0.0, step=0.1)
        
        if st.form_submit_button(t('ag_agendar')):
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
                st.success(t('ag_sucesso'))
            else:
                st.error(t('ag_erro'))
    
    if st.session_state.agendamentos:
        st.subheader(t('ag_lista'))
        st.dataframe(pd.DataFrame(st.session_state.agendamentos))

# ================= PAGAMENTOS PIX =================
def pagamentos():
    st.markdown(f"<div class='main-header'><h1>{t('pagamentos_title')}</h1></div>", unsafe_allow_html=True)
    with st.form("form_pagamento"):
        valor = st.number_input(t('pag_valor'), min_value=0.01, step=10.0)
        descricao = st.text_input(t('pag_descricao'))
        if st.form_submit_button(t('pag_gerar')):
            if valor > 0 and descricao:
                chave = st.session_state.config_empresa['chave_pix']
                img = gerar_qrcode_pix(valor, chave, descricao)
                buf = BytesIO()
                img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                st.image(f"data:image/png;base64,{b64}", width=300)
                st.code(f"{t('pag_chave')}: {chave}")
                st.session_state.pagamentos.append({
                    "id": len(st.session_state.pagamentos)+1,
                    "valor": valor,
                    "descricao": descricao,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "status": "pago"  # simulado
                })
                st.success(t('pag_registrado'))
            else:
                st.error(t('pag_erro'))
    
    if st.session_state.pagamentos:
        st.subheader(t('pag_lista'))
        st.dataframe(pd.DataFrame(st.session_state.pagamentos))

# ================= RELATÓRIOS =================
def relatorios():
    st.markdown(f"<div class='main-header'><h1>{t('relatorios_title')}</h1></div>", unsafe_allow_html=True)
    tipo = st.selectbox(t('rel_tipo'), [t('rel_cargas'), t('rel_pagamentos'), t('rel_motoristas')])
    if tipo == t('rel_cargas') and st.session_state.cargas:
        df = pd.DataFrame(st.session_state.cargas)
        st.dataframe(df)
        fig = px.bar(df, x='status', title=f"{t('rel_cargas')} {t('chart_distribuicao')}")
        st.plotly_chart(fig)
    elif tipo == t('rel_pagamentos') and st.session_state.pagamentos:
        df = pd.DataFrame(st.session_state.pagamentos)
        st.dataframe(df)
        total = df['valor'].sum()
        st.metric(t('rel_total_recebido'), format_currency(total))
    elif tipo == t('rel_motoristas') and st.session_state.motoristas:
        df = pd.DataFrame(st.session_state.motoristas)
        st.dataframe(df)
    else:
        st.info(t('no_data'))

# ================= MONITORAMENTO =================
def monitoramento():
    st.markdown(f"<div class='main-header'><h1>{t('monitoramento_title')}</h1></div>", unsafe_allow_html=True)
    status_filter = st.multiselect(t('mon_status'), ["agendada", "em andamento", "entregue"], default=["agendada","em andamento"])
    cargas_filtradas = [c for c in st.session_state.cargas if c.get('status') in status_filter]
    if cargas_filtradas:
        for c in cargas_filtradas:
            with st.container():
                col1, col2, col3 = st.columns([2,2,1])
                with col1:
                    st.markdown(f"**{t('mon_carga')} #{c['id']}**")
                    st.markdown(f"📦 {c.get('tipo_carga','N/A')}")
                with col2:
                    st.markdown(f"📍 {c['origem']} → {c['destino']}")
                    st.markdown(f"🚚 {c['motorista']}")
                with col3:
                    if c['status'] == 'em andamento':
                        st.markdown(t('mon_em_rota'))
                    elif c['status'] == 'entregue':
                        st.markdown(t('mon_entregue'))
                    else:
                        st.markdown(t('mon_agendada'))
                st.markdown("---")
    else:
        st.info(t('no_data'))

# ================= CONFIGURAÇÕES =================
def configuracoes():
    st.markdown(f"<div class='main-header'><h1>{t('config_title')}</h1></div>", unsafe_allow_html=True)
    with st.form("config_empresa"):
        st.subheader(t('config_dados_empresa'))
        nome = st.text_input(t('config_nome'), value=st.session_state.config_empresa.get('nome',''))
        cnpj = st.text_input(t('config_cnpj'), value=st.session_state.config_empresa.get('cnpj',''))
        chave_pix = st.text_input(t('config_chave_pix'), value=st.session_state.config_empresa.get('chave_pix',''))
        if st.form_submit_button(t('config_salvar')):
            st.session_state.config_empresa.update({
                'nome': nome,
                'cnpj': cnpj,
                'chave_pix': chave_pix
            })
            st.success(t('config_sucesso'))

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
