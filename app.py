import streamlit as st
from supabase import create_client
import pandas as pd
import datetime
import re

# -----------------------------
# Conexão Supabase
# -----------------------------
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# -----------------------------
# Sessão de usuário
# -----------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

# -----------------------------
# Funções de categorização
# -----------------------------
def categorizar(descricao):
    desc = descricao.lower()
    if any(x in desc for x in ["mercado", "supermercado", "compras"]):
        return "Compras"
    elif any(x in desc for x in ["gasolina", "etanol", "combustível", "uber"]):
        return "Transporte"
    elif any(x in desc for x in ["restaurante", "lanche", "pizza", "comida"]):
        return "Alimentação"
    elif any(x in desc for x in ["lava rápido", "oficina", "manutenção"]):
        return "Serviços"
    elif "faturamento" in desc or "receita" in desc:
        return "Receita"
    else:
        return "Outros"

# -----------------------------
# Tela de login/cadastro
# -----------------------------
def login_screen():
    st.title("🔐 Login Financeiro")
    choice = st.radio("Selecione", ["Login", "Cadastro"])

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if choice == "Login":
        if st.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["user"] = res.user
                st.success("Login realizado!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro no login: {e}")
    else:
        if st.button("Cadastrar"):
            try:
                res = supabase.auth.sign_up({"email": email, "password": password})
                st.success("Conta criada! Verifique seu email.")
            except Exception as e:
                st.error(f"Erro no cadastro: {e}")

# -----------------------------
# Tela principal (após login)
# -----------------------------
def app_screen():
    st.title(f"💬 Financeiro - {st.session_state['user'].email}")
    if st.button("Sair"):
        st.session_state["user"] = None
        st.rerun()

    msg = st.chat_input("Digite algo como: Mercado 120 ou Faturamento 500")
    if msg:
        match = re.match(r"(.+?)\s+(\d+(\.\d{1,2})?)", msg)
        if match:
            descricao = match.group(1)
            valor = float(match.group(2))
            categoria = categorizar(descricao)
            data = datetime.date.today()

            supabase.table("lancamentos").insert({
                "user_id": st.session_state["user"].id,
                "descricao": descricao,
                "valor": valor,
                "categoria": categoria,
                "data": str(data)
            }).execute()

            st.success(f"Lançado: {descricao} - R$ {valor:.2f} [{categoria}]")
        else:
            st.error("⚠️ Escreva no formato: Descrição Valor (ex: Mercado 120)")

    # Carregar lançamentos do usuário
    dados = supabase.table("lancamentos").select("*").eq("user_id", st.session_state["user"].id).execute()
    df = pd.DataFrame(dados.data)

    if not df.empty:
        receita = df[df["categoria"] == "Receita"]["valor"].sum()
        despesas = df[df["categoria"] != "Receita"]["valor"].sum()
        liquido = receita - despesas

        st.metric("Faturamento Bruto", f"R$ {receita:.2f}")
        st.metric("Despesas", f"R$ {despesas:.2f}")
        st.metric("Lucro Líquido", f"R$ {liquido:.2f}")

        categoria_filtro = st.multiselect("Filtrar por categoria", df["categoria"].unique())
        if categoria_filtro:
            df = df[df["categoria"].isin(categoria_filtro)]

        st.subheader("Despesas por Categoria")
        st.bar_chart(df[df["categoria"] != "Receita"].groupby("categoria")["valor"].sum())

        st.subheader("Histórico Mensal")
        df["mes"] = pd.to_datetime(df["data"]).dt.to_period("M")
        st.line_chart(df.groupby("mes")["valor"].sum())
    else:
        st.info("Nenhum lançamento registrado ainda.")

# -----------------------------
# Roteamento
# -----------------------------
if st.session_state["user"]:
    app_screen()
else:
    login_screen()
