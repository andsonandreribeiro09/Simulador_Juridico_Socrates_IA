import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from flask import Flask
import joblib
import sqlite3
import bcrypt

# ==============================
# BANCO DE DADOS DE USUÁRIOS
# ==============================

def init_db():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def cadastrar_usuario(username, password):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute('INSERT INTO usuarios (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def autenticar_usuario(username, password):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('SELECT password_hash FROM usuarios WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode(), result[0])
    return False

init_db()

# ==============================
# CLASSE DO SIMULADOR
# ==============================

class SimuladorJuridicoIA:
    def __init__(self, modelo, casos, tribunais):
        self.modelo = modelo
        self.casos = casos
        self.tribunais = tribunais

    def gerar_texto(self, caso, tribunal):
        dados = self.casos[caso]
        return f"Descrição do Caso: {dados['descrição']}. Contexto histórico: {dados['contexto']}, no ano {dados['ano']}. Tribunal de julgamento: {tribunal}."

    def prever(self, texto):
        return self.modelo.predict([texto])[0]

    def resultados_simulados(self, decisao):
        if decisao == "absolvição":
            return 85, 15, 90, "Liberdade de expressão e contexto filosófico favorável."
        elif decisao == "pena reduzida":
            return 15, 85, 75, "Conduta atenuada por fatores históricos e culturais."
        else:
            return 0, 0, 0, "Resultado inesperado."

    def gerar_parecer(self, caso, tribunal, decisao, prob_abs, prob_red, similaridade, justificativa):
        dados = self.casos[caso]
        return html.Div([
            html.H3("📄 Parecer da IA:"),
            html.P(f"Caso: {caso} ({dados['ano']}) - {dados['descrição']}", style={"fontWeight": "bold"}),
            html.P(f"Tribunal: {tribunal}"),
            html.P(f"🔍 Probabilidade de absolvição: {prob_abs}%"),
            html.P(f"🔍 Probabilidade de pena reduzida: {prob_red}%"),
            html.P(f"🧠 Similaridade com jurisprudência moderna: {similaridade}%"),
            html.P(f"📌 Decisão provável: {decisao.capitalize()}"),
            html.P(f"📚 Justificativa: {justificativa}")
        ])

    def gerar_grafico(self, prob_abs, prob_red, similaridade):
        fig = go.Figure(data=[
            go.Bar(x=["Absolvição", "Pena Reduzida", "Similaridade"],
                   y=[prob_abs, prob_red, similaridade],
                   marker_color=["green", "orange", "blue"])
        ])
        fig.update_layout(title="Resultado da IA Jurídica", yaxis_title="Probabilidade (%)",
                          height=500, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        return fig

# ==============================
# FLASK + DASH CONFIG
# ==============================

server = Flask(__name__)
dash_app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
dash_app.title = "Simulador Jurídico com IA"
user_logged = {"status": False}

modelo = joblib.load("modelo_binario_absolvicao_pena_reduzida.pkl")

casos = {
    "Julgamento de Sócrates": {
        "descrição": "Acusado de corromper a juventude e negar os deuses de Atenas.",
        "ano": 399,
        "contexto": "Grécia Antiga"
    },
    "Julgamento de Joana d'Arc": {
        "descrição": "Acusada de heresia e feitiçaria.",
        "ano": 1431,
        "contexto": "França Medieval"
    }
}

tribunais = [
    "STJ (Brasil)",
    "Tribunal Europeu de Direitos Humanos",
    "Corte Interamericana de Direitos Humanos"
]

simulador = SimuladorJuridicoIA(modelo, casos, tribunais)

# ==============================
# LAYOUTS: LOGIN + APP
# ==============================

login_layout = html.Div([
    html.H2("🔐 Acesso ao Simulador Jurídico"),
    dcc.Input(id='login-usuario', placeholder='Usuário', type='text'),
    dcc.Input(id='login-senha', placeholder='Senha', type='password'),
    html.Br(), html.Button("Entrar", id='btn-login', n_clicks=0),
    html.Div(id='login-mensagem', style={'color': 'red', 'marginTop': '10px'}),
    html.Hr(),
    html.H4("Novo por aqui? Cadastre-se:"),
    dcc.Input(id='cadastro-usuario', placeholder='Novo usuário', type='text'),
    dcc.Input(id='cadastro-senha', placeholder='Nova senha', type='password'),
    html.Br(), html.Button("Cadastrar", id='btn-cadastro', n_clicks=0),
    html.Div(id='cadastro-mensagem', style={'color': 'green', 'marginTop': '10px'})
])

app_layout = html.Div([
    html.H1("⚖️ Simulador Jurídico - IA para Julgamentos Históricos", style={"textAlign": "center"}),
    html.Div([
        html.Label("🕰️ Caso histórico:"),
        dcc.Dropdown(id="caso", options=[{"label": k, "value": k} for k in casos],
                     value=list(casos.keys())[0], style={"width": "300px"}),
        html.Label("🏛️ Tribunal moderno:"),
        dcc.Dropdown(id="tribunal", options=[{"label": t, "value": t} for t in tribunais],
                     value=tribunais[0], style={"width": "300px"}),
        html.Br(),
        html.Button("Simular Julgamento", id="simular", n_clicks=0, style={"padding": "8px 16px"})
    ]),
    html.Div(id="parecer-gerado", style={"marginTop": "20px"}),
    dcc.Graph(id="grafico-resultado")
])

# ==============================
# ROTAS & CALLBACKS
# ==============================

dash_app.layout = html.Div([
    dcc.Location(id='url'),
    html.Div(id='pagina-atual')
])

@dash_app.callback(Output('pagina-atual', 'children'), [Input('url', 'pathname')])
def carregar_pagina(path):
    return app_layout if user_logged['status'] else login_layout

@dash_app.callback(
    Output('url', 'pathname'),  # <- alterar isso
    Output('login-mensagem', 'children'),
    Input('btn-login', 'n_clicks'),
    State('login-usuario', 'value'),
    State('login-senha', 'value')
)
def login(n, usuario, senha):
    if n > 0 and usuario and senha:
        if autenticar_usuario(usuario, senha):
            user_logged['status'] = True
            return "/", ""  # Redireciona para a página principal
        return dash.no_update, "Usuário ou senha incorretos."
    return dash.no_update, ""


@dash_app.callback(
    Output('cadastro-mensagem', 'children'),
    Input('btn-cadastro', 'n_clicks'),
    State('cadastro-usuario', 'value'),
    State('cadastro-senha', 'value')
)
def cadastro(n, usuario, senha):
    if n > 0 and usuario and senha:
        sucesso = cadastrar_usuario(usuario, senha)
        return "Cadastro realizado!" if sucesso else "Usuário já existe."
    return ""

@dash_app.callback(
    Output("parecer-gerado", "children"),
    Output("grafico-resultado", "figure"),
    Input("simular", "n_clicks"),
    State("caso", "value"),
    State("tribunal", "value")
)
def simular(n, caso, tribunal):
    if n == 0:
        return "", go.Figure(layout={"height": 500})
    try:
        texto = simulador.gerar_texto(caso, tribunal)
        decisao = simulador.prever(texto)
        prob_abs, prob_red, similaridade, justificativa = simulador.resultados_simulados(decisao)
        parecer = simulador.gerar_parecer(caso, tribunal, decisao, prob_abs, prob_red, similaridade, justificativa)
        grafico = simulador.gerar_grafico(prob_abs, prob_red, similaridade)
        return parecer, grafico
    except Exception as e:
        return html.Div([html.H3("❌ Erro na simulação:"), html.P(str(e))]), go.Figure(layout={"height": 500})

# ==============================
# RUN
# ==============================

if __name__ == '__main__':
    dash_app.run_server(debug=True)


