from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

df = pd.read_csv("data/taco_data.csv",sep=';')


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tabela Nutricional Oficial</title>
        <script src="https://unpkg.com/htmx.org@1.9.2"></script>
        <style>
            body { font-family: Arial; padding: 2em; }
            input { padding: 0.5em; width: 300px; }
            .sugestao { cursor: pointer; padding: 0.3em; }
            .sugestao:hover { background-color: #eee; }
            table { border-collapse: collapse; margin-top: 1em; }
            th, td { padding: 8px 12px; border: 1px solid #ccc; text-align: left; }
        </style>
    </head>
    <body>
        <h1>Buscar Alimentos</h1>
        <input type="text" name="busca" id="busca"
               hx-get="/autocomplete"
               hx-trigger="keyup changed delay:300ms"
               hx-target="#sugestoes"
               autocomplete="off" placeholder="Digite o nome do alimento..." />
        <div id="sugestoes"></div>
        <div id="tabela"></div>
    </body>
    </html>
    """)


@app.get("/autocomplete", response_class=HTMLResponse)
async def autocomplete(busca: str = ""):
    resultados = df[df['Alimento'].str.contains(busca, case=False, na=False)]['Alimento'].head(5).tolist()
    html = "".join([f'<div class="sugestao" hx-get="/detalhes?alimento={r}" hx-target="#tabela">{r}</div>' for r in resultados])
    return HTMLResponse(content=html)


@app.get("/detalhes", response_class=HTMLResponse)
async def detalhes(alimento: str):
    dados = df[df['Alimento'] == alimento].to_dict(orient="records")
    if not dados:
        return HTMLResponse("<p>Alimento não encontrado</p>")
    item = dados[0]
    tabela = "<table><thead><tr><th>Nutriente</th><th>Valor</th></tr></thead><tbody>"
    tabela += "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in item.items()])
    tabela += "</tbody></table>"
    return HTMLResponse(content=tabela)

