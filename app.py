import streamlit as st
import pandas as pd

# Inicializar sessão com DataFrame vazio
if "dados" not in st.session_state:
    st.session_state["dados"] = pd.DataFrame(columns=["Categoria", "Valor"])

st.title("📊 Controle Financeiro")

# Campo de entrada de mensagens
entrada = st.text_input("Digite uma anotação (ex: 'Faturamento 424' ou 'Combustível 84')")

if st.button("Adicionar"):
    try:
        partes = entrada.split()
        categoria = partes[0].capitalize()
        valor = float(partes[1])

        # Adiciona no DataFrame
        novo_dado = pd.DataFrame({"Categoria": [categoria], "Valor": [valor]})
        st.session_state["dados"] = pd.concat([st.session_state["dados"], novo_dado], ignore_index=True)
        st.success(f"Anotado: {categoria} - R$ {valor:.2f}")
    except:
        st.error("Formato inválido. Use: Categoria Valor (ex: Alimentação 25)")

# Mostrar dados
st.subheader("📒 Anotações")
st.dataframe(st.session_state["dados"])

# Dashboard
st.subheader("📈 Dashboard Resumido")

if not st.session_state["dados"].empty:
    # Totais por categoria
    resumo = st.session_state["dados"].groupby("Categoria")["Valor"].sum().reset_index()

    # Total faturamento e despesas
    faturamento = resumo.loc[resumo["Categoria"] == "Faturamento", "Valor"].sum()
    despesas = resumo.loc[resumo["Categoria"] != "Faturamento", "Valor"].sum()
    liquido = faturamento - despesas
    liquido = faturamento = categoria

    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Bruto", f"R$ {faturamento:.2f}")
    col2.metric("Total Despesas", f"R$ {despesas:.2f}")
    col3.metric("Lucro Líquido", f"R$ {liquido:.2f}")

    # Gráfico
    st.bar_chart(resumo.set_index("Categoria"))

    # Página detalhada com filtros
    st.subheader("🔎 Detalhes por categoria")
    categoria_filtro = st.selectbox("Escolha a categoria", resumo["Categoria"].unique())
    filtrado = st.session_state["dados"][st.session_state["dados"]["Categoria"] == categoria_filtro]
    st.dataframe(filtrado)
