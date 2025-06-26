
import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO

st.set_page_config(page_title="Sistema Inteligente de Controle de Peças", layout="wide")
st.markdown("<h1 style='color:#2A7F62'>📊 Sistema Inteligente de Controle de Peças</h1>", unsafe_allow_html=True)

DB_PATH = "pecas.db"

def criar_tabela():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            fornecedor TEXT,
            quantidade INTEGER,
            dias_uso INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def importar_para_banco(dados):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM pecas")
    dados.to_sql("pecas", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()

def carregar_dados():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT nome AS 'Nome da Peça', fornecedor AS Fornecedor, quantidade AS Quantidade, dias_uso AS 'Dias de Uso' FROM pecas", conn)
    conn.close()
    return df

def process_file(uploaded_file):
    df = pd.read_excel(uploaded_file, sheet_name="Controle de Peças")  # sem skiprows
    df = df.dropna(subset=["Nome da Peça", "Quantidade"])
    df = df.rename(columns={
        "Nome da Peça": "nome",
        "Fornecedor": "fornecedor",
        "Quantidade": "quantidade",
        "Dias de Uso": "dias_uso"
    })
    return df

def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Controle de Peças', index=False)
    output.seek(0)
    return output

criar_tabela()

with st.sidebar:
    st.subheader("📤 Importar nova planilha (.xlsx)")
    uploaded_file = st.file_uploader("Envie a planilha", type=["xlsx"])
    if uploaded_file:
        try:
            df_importado = process_file(uploaded_file)
            importar_para_banco(df_importado)
            st.success("✅ Planilha importada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao processar a planilha: {e}")

    st.markdown("---")
    st.subheader("⬇️ Exportar dados em Excel")
    df_atual = carregar_dados()
    excel_bytes = exportar_excel(df_atual)
    st.download_button("📥 Baixar Excel", data=excel_bytes, file_name="controle_pecas_exportado.xlsx")

# Interface principal
st.subheader("📋 Tabela de Controle de Peças")
df = carregar_dados()
st.dataframe(df.style.apply(lambda row: ["background-color: #FFCCCC" if row["Quantidade"] == 0 else "" for _ in row], axis=1), use_container_width=True)

faltando = df[df["Quantidade"] == 0]
if not faltando.empty:
    st.subheader("🔴 Peças em Falta")
    st.table(faltando)
