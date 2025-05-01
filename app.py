import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import random
import plotly.graph_objs as go

# Dados fictícios para simulação
casos_historicos = {
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

tribunais_modernos = ["STJ (Brasil)", "Tribunal Europeu de Direitos Humanos", "Corte Interamericana de Direitos Humanos"]

# Inicializa app Dash
app = dash.Dash(__name__)
app.title = "Simulador Jurídico com IA"

app.layout = html.Div([
    html.H1("⚖️ Simulador Jurídico - IA para Julgamentos Históricos", style={"textAlign": "center"}),

    # 🔽 Filtros alinhados e encostados à esquerda
    html.Div([
        html.Label("🕰️ Caso histórico:", style={"marginBottom": "4px"}),
        dcc.Dropdown(
            id="caso",
            options=[{"label": k, "value": k} for k in casos_historicos],
            value=list(casos_historicos.keys())[0],
            style={"width": "280px", "marginBottom": "8px"}
        ),

        html.Label("🏛️ Tribunal moderno:", style={"marginBottom": "4px"}),
        dcc.Dropdown(
            id="tribunal",
            options=[{"label": t, "value": t} for t in tribunais_modernos],
            value=tribunais_modernos[0],
            style={"width": "280px", "marginBottom": "12px"}
        ),

        html.Button(
            "Simular Julgamento",
            id="simular",
            n_clicks=0,
            style={"padding": "6px 14px"}
        )
    ],
    style={
        "position": "relative",
        "left": "0px",        # alinhado ao canto esquerdo
        "margin": "0",        # sem margem
        "padding": "0",       # sem padding
        "textAlign": "left"
    }),

    html.Br(),

    html.Div(id="parecer-gerado", style={"marginTop": "20px"}),

    dcc.Graph(id="grafico-resultado")
])


@app.callback(
    [Output("parecer-gerado", "children"),
     Output("grafico-resultado", "figure")],
    [Input("simular", "n_clicks")],
    [Input("caso", "value"), Input("tribunal", "value")]
)
def simular_julgamento(n, caso, tribunal):
    if n == 0:
        figura_vazia = go.Figure()
        figura_vazia.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        return "", figura_vazia

    # Dados simulados
    prob_abs = random.randint(60, 85)
    prob_reduzida = random.randint(40, 70)
    similaridade = random.randint(70, 90)

    parecer = html.Div([
        html.H3("📄 Parecer Simulado:"),
        html.P(f"Caso: {caso} ({casos_historicos[caso]['ano']}) - {casos_historicos[caso]['descrição']}"),
        html.P(f"Tribunal: {tribunal}"),
        html.P(f"🔍 Probabilidade de absolvição: {prob_abs}%"),
        html.P(f"🔍 Probabilidade de pena reduzida: {prob_reduzida}%"),
        html.P(f"🧠 Similaridade com jurisprudência moderna: {similaridade}%"),
        html.P("📌 Decisão provável: " + ("Absolvição" if prob_abs > 70 else "Pena reduzida")),
    ])

    figura = go.Figure(data=[
        go.Bar(name="Resultado", x=["Absolvição", "Pena Reduzida", "Similaridade"],
               y=[prob_abs, prob_reduzida, similaridade],
               marker_color=['green', 'orange', 'blue'])
    ])
    figura.update_layout(
        title="Resultado da IA Jurídica",
        yaxis_title="Probabilidade (%)",
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return parecer, figura


if __name__ == "__main__":
    app.run_server(debug=True)
