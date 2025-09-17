import streamlit as st
from supabase import create_client, Client
import os

# Configuração Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Financeiro", page_icon="💬", layout="centered")

# Autenticação
if "user" not in st.session_state:
    st.session_state["user"] = None

def login_screen():
    st.title("💬 Financeiro")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        try:
            auth_resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state["user"] = auth_resp.user
            st.success("Login realizado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro no login: {e}")

def app_screen():
    user = st.session_state["user"]
    st.title("💬 Financeiro -")
    st.markdown(f"**{user.email}**")
    
    if st.button("Sair"):
        st.session_state["user"] = None
        st.rerun()

    st.subheader("Novo lançamento")
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", step=0.01, format="%.2f")
    categoria = st.text_input("Categoria")

    if st.button("Salvar lançamento"):
        try:
            supabase.table("lancamentos").insert({
                "descricao": descricao,
                "valor": valor,
                "categoria": categoria,
                "user_id": str(user.id) if "user_id" in [c["name"] for c in supabase.table("lancamentos").select("*").execute().data[0].keys()] else None
            }).execute()
            st.success("Lançamento salvo com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar lançamento: {e}")

    st.subheader("Meus lançamentos")
    try:
        lancamentos = supabase.table("lancamentos").select("*").execute()
        if lancamentos.data:
            st.table(lancamentos.data)
        else:
            st.info("Nenhum lançamento encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar lançamentos: {e}")

# Roteamento
if st.session_state["user"] is None:
    login_screen()
else:
    app_screen()
