import calendar
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
import yaml
from callbacks.callbacks import callback_clear_session
from components.viz import show_values
from database.database import (
    fetch_all_periods_expense,
    fetch_all_periods_income,
    insert_income,
)
from dateutil.relativedelta import relativedelta
from streamlit_option_menu import option_menu
from yaml.loader import SafeLoader

with open("app/config.yaml") as f:
    configs = yaml.load(f, Loader=SafeLoader)

CATEGORIES = configs["categories"]
INCOMES = configs["incomes"]
EXPENSES = configs["expenses"]
CURRENCY = "R$"
PAGE_TITLE = "Gastos e Entradas"
PAGE_ICON = ":knife: :money_with_wings:"
LAYOUT = "wide"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
st.title(PAGE_TITLE + " " + PAGE_ICON)

# dropdown
years = [2022, 2023]
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# hide streamlit style
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.header("KPIs - WIP")
kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric("Gastos do mês", "R$ 1.000,00")
kpi2.metric("Entradas", "R$ 1.000,00")
kpi3.metric("Valor ações - Mês passado", "R$ 1.000,00")

st.text("")
st.text("")
st.text("")
st.text("")

# navigation menu
selected = option_menu(
    menu_title=None,
    options=[
        "Entrada da Facada",
        "Entrada do Cacau",
        "Vendo o Rombo",
        "Variável",
    ],
    icons=["graph-down-arrow", "cash-stack", "bar-chart-fill", "graph-up-arrow"],
    orientation="horizontal",
)


# input and save periods
if selected == "Entrada do Cacau":
    st.header("Entrada do Cacau")
    with st.form("income_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Escolha o mês:", months, key="month_income")
        col2.selectbox("Escolha o ano:", years, key="year_income")

        "---"
        with st.expander("Adiciona ae nossos ganhos!"):
            for income in INCOMES:
                st.number_input(
                    f"{income}:", min_value=0.0, format="%.2f", step=10.0, key=income
                )
        submitted = st.form_submit_button("Salvar entrada")

        if submitted:
            period = (
                str(st.session_state["year_income"])
                + "_"
                + str(st.session_state["month_income"])
            )
            incomes = {income: st.session_state[income] for income in INCOMES}
            incomes["period"] = period

            _ = insert_income(incomes)
            st.success("Dados enviados!")


if selected == "Entrada da Facada":
    col1, col2 = st.columns([1, 1])

    col1.subheader("Categoria")
    col2.subheader("Sub-categoria")

    with col1:
        value = st.selectbox(
            "Categoria geral",
            CATEGORIES.keys(),
            key="category_expense",
        )
        st.session_state["subs"] = CATEGORIES[st.session_state["category_expense"]]

    with col2:
        option = st.selectbox(
            "Detalha mais um pouco",
            options=st.session_state.subs,
            key="subcategory_expense",
        )

    "---"
    st.subheader("Descritivo da Compra")
    st.text_area("Produto/Descrição", key="description")
    st.number_input("Total ou valor da parcela", key="total")

    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
    with c1:
        st.radio("Tipo de gasto", ["Variável", "Fixo"], key="type_spent")

    with c2:
        st.radio("Tipo de compra", ["débito", "crédito"], key="type_buy")

    with c3:
        st.radio("Quem foi?", ["Tica", "Luba"], key="user")

    with c4:
        st.radio("Banco", ["Nubank", "BB", "Ticket", "Flash", "Cash"], key="bank")

    with c5:
        st.radio("Parcelado", ["N", "S"], key="parcela")

    "---"
    if st.session_state["parcela"] == "N":
        st.subheader("Vencimento")
        c_1, c_2 = st.columns(2)
        with c_1:
            st.date_input(
                "Data da Compra", datetime.now(tz=timezone.utc), key="date_buy"
            )

        with c_2:
            user = st.session_state["user"]
            type_buy = st.session_state["type_buy"]
            date_buy = st.session_state["date_buy"]

            if type_buy == "débito":
                date = datetime.now(tz=timezone.utc)
            elif type_buy == "crédito":
                # we just have nubank cards for credit shopping
                if user == "Tica":
                    day = date_buy.day
                    if day < 12:
                        date = datetime(date_buy.year, date_buy.month, 19)
                    else:
                        next_date = date_buy + relativedelta(months=1)
                        date = datetime(next_date.year, next_date.month, 19)

                elif user == "Luba":
                    day = date_buy.day
                    if day < 8:
                        date = datetime(date_buy.year, date_buy.month, 15)
                    else:
                        next_date = date_buy + relativedelta(months=1)
                        date = datetime(next_date.year, next_date.month, 15)

            st.date_input("Data de Vencimento", date, key="due_date")

    elif st.session_state["parcela"] == "S":
        st.subheader("Vencimento")
        st.number_input(
            "Quantas Parcelas",
            min_value=0,
            max_value=100,
            value=1,
            step=1,
            key="qt_parcelas",
        )

        for i in range(st.session_state["qt_parcelas"]):
            c_1, c_2, c_3 = st.columns([0.3, 1, 1])
            with c_1:
                # st.markdown("Parcela")
                st.write("Parcela")
                st.markdown(f"**{i+1}**")
            with c_2:
                st.date_input(
                    "Data da Compra", datetime.now(tz=timezone.utc), key=f"date_buy_{i}"
                )

            with c_3:
                user = st.session_state["user"]
                type_buy = st.session_state["type_buy"]
                date_buy = st.session_state[f"date_buy_{i}"]

                if type_buy == "débito":
                    date = datetime.now(tz=timezone.utc)
                elif type_buy == "crédito":
                    # we just have nubank cards for credit shopping
                    if user == "Tica":
                        day = date_buy.day
                        if day < 12:
                            date = datetime(date_buy.year, date_buy.month, 19)
                        else:
                            next_date = date_buy + relativedelta(months=1)
                            date = datetime(next_date.year, next_date.month, 19)

                    elif user == "Luba":
                        day = date_buy.day
                        if day < 8:
                            date = datetime(date_buy.year, date_buy.month, 15)
                        else:
                            next_date = date_buy + relativedelta(months=1)
                            date = datetime(next_date.year, next_date.month, 15)

                st.date_input("Data de Vencimento", date, key=f"due_date_{i}")

    submitted2 = st.button("Send data!", on_click=callback_clear_session)

    if submitted2:
        st.success("Sended Data!")

        # creating a table to show the last 10 expenses
        items = fetch_all_periods_expense()
        data = pd.DataFrame(items)
        data["created_at"] = pd.to_datetime(data["created_at"], format="%d-%m-%Y")
        data = data.sort_values(by="created_at", ascending=False)
        data.drop(["key"], axis=1, inplace=True)
        data = data.head(20)
        st.table(data)

if selected == "Vendo o Rombo":
    # plot periods
    st.header("_Vizús_")
    with st.form("saved_periods"):
        period = st.selectbox(
            "Selecione o ano e o mês:",
            [
                "2023_01",
                "2023_02",
                "2023_03",
                "2023_04",
                "2023_05",
                "2023_06",
                "2023_07",
                "2023_08",
                "2023_09",
                "2023_10",
                "2023_11",
                "2023_12",
            ],
        )
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            month = int(period.split("_")[-1])
            year = int(period.split("_")[0])

            items_expenses = fetch_all_periods_expense()
            items_incomes = fetch_all_periods_income()

            # dataframe transformations
            incomes_df = pd.DataFrame(items_incomes)
            expenses_df = pd.DataFrame(items_expenses)

            incomes_df["month"] = incomes_df["period"].map(
                lambda x: int(x.split("_")[-1])
            )
            incomes_df["year"] = incomes_df["period"].map(
                lambda x: int(x.split("_")[0])
            )

            expenses_df["due_month"] = expenses_df["due_date"].map(
                lambda x: int(x.split("-")[1])
            )
            expenses_df["due_year"] = expenses_df["due_date"].map(
                lambda x: int(x.split("-")[-1])
            )

            # filtering the data
            expenses_date_df = expenses_df[
                (expenses_df["due_year"] == year) & (expenses_df["due_month"] == month)
            ]
            incomes_date_df = incomes_df[
                (incomes_df["year"] == year) & (incomes_df["month"] == month)
            ]

            # create metrics: Totals
            total_income = incomes_date_df.iloc[:, 0:4].values.sum()
            category_totals = (
                expenses_date_df.groupby(["category"])["total"].sum().reset_index()
            )
            subcategories_totals = (
                expenses_date_df.groupby(["category", "sub_category"])["total"]
                .sum()
                .reset_index()
            )
            total_expense = category_totals["total"].sum()
            remaining_budget = total_income - total_expense

            # create metrics: Credit or Debit
            expenses_by_type_buy = (
                expenses_date_df.groupby("type_buy")["total"].agg(sum).reset_index()
            )

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {CURRENCY}")
            col2.metric("Total Expense", f"{total_expense} {CURRENCY}")
            col3.metric("Diff", f"{remaining_budget} {CURRENCY}")

            # barplots: by category
            sns.set_theme(style="whitegrid")
            fig = plt.figure(figsize=(10, 4))

            axs = sns.barplot(
                x="total", y="category", data=category_totals, errorbar=None
            )
            plt.title("Gastos por Categorias")
            plt.xlabel("Total")
            plt.ylabel("")
            _ = show_values(axs, orient="h", space_y=0.3)
            _ = sns.despine(left=True, bottom=True)

            st.pyplot(fig)

            # barplots: by subcategory
            sns.set_theme(style="whitegrid")
            fig = plt.figure(figsize=(10, 12))

            axs = sns.barplot(
                x="total",
                y="sub_category",
                data=subcategories_totals,
                hue="category",
                dodge=False,
                errorbar=None,
                palette="tab10",
            )
            plt.title("Gastos por Subcategorias")
            plt.xlabel("Total")
            plt.ylabel("")
            _ = show_values(axs, orient="h", space_y=0.4)
            _ = sns.despine(left=True, bottom=True)

            st.pyplot(fig)

            # barplots: by type buy
            sns.set_theme(style="whitegrid")
            fig = plt.figure(figsize=(10, 4))

            axs = sns.barplot(
                x="total", y="type_buy", data=expenses_by_type_buy, errorbar=None
            )
            plt.title("Gastos por Tipo da Compra")
            plt.xlabel("Total")
            plt.ylabel("")
            _ = show_values(axs, orient="h", space_y=0.4)
            _ = sns.despine(left=True, bottom=True)

            st.pyplot(fig)

if selected == "Variável":
    st.header("Ações na carteira")
    st.markdown(
        """
        - BBSE3: BB Seguridade
        - CVCB3: CVC Brasil
        - EGIE3: Engie Brasil
        - ENBR3: EDP Brasil
        - ITSA4: Itausa SA Preference Shares
        - PETR4: Petroleo Brasileiro SA Petrobras Preference
        - TAEE11: Taesa S.A.
        - UNIP6: Unipar Participacoes B Pref Shs
        - VIVT3: Telefônica Brasil
        - WIZC3: Wiz Soluções e Corretagem de Seguros S.A.
        - BRAP4: Bradespar SA Preference Shares
        - ALUP11: Alupar Investimento SA
        - TUPY3: Tupy
        - BPAC11: Banco BTG Pactual SA Unit
        - HSML11: Hsi Malls Fundo DE Investimento Imobiliario
        - RBRP11: FI Imobiliario RBR Properties - FII
        - RDOR3: Rede D'or São Luiz
        - ABCB4: ABC Brasil
        - CCRO3: Grupo CCR 
        - MRVE3: MRV Engenharia e Participacoes SA
        - ODPV3: Odontoprev
        - VALE3: Vale S.A.
        - CPLE6: Companhia Paranaense de Energia
        """
    )

    sectors = {
        "BBSE3": "Financeiro / Previdência e Seguros / Seguradoras",
        "CVCB3": "Consumo Cíclico / Viagens e Lazer / Viagens e Turismo",
        "EGIE3": "Utilidade Pública / Energia Elétrica / Energia Elétrica",
        "ENBR3": "Utilidade Pública / Energia Elétrica / Energia Elétrica",
        "ITSA4": "Financeiro / Intermediários Financeiros / Bancos",
        "PETR4": "Petróleo. Gás e Biocombustíveis / Petróleo. Gás e Biocombustíveis / Exploração. Refino e Distribuição",
        "TAEE11": "Utilidade Pública / Energia Elétrica / Energia Elétrica",
        "UNIP6": "Materiais Básicos / Químicos / Químicos Diversos",
        "VIVT3": "Comunicações / Telecomunicações / Telecomunicações",
        "WIZC3": "Financeiro / Previdência e Seguros / Corretoras de Seguros e Resseguros",
        "BRAP4": "Materiais Básicos / Mineração / Minerais Metálicos",
        "ALUP11": "Utilidade Pública / Energia Elétrica / Energia Elétrica",
        "TUPY3": "Bens Industriais / Material de Transporte / Material Rodoviário",
        "BPAC11": "Financeiro / Intermediários Financeiros / Bancos",
        "HSML11": "Fundo Imobiliário",
        "RBRP11": "Fundo Imobiliário",
        "RDOR3": "Saúde / Serv.Méd.Hospit..Análises e Diagnósticos / Serv.Méd.Hospit..Análises e Diagnósticos",
        "ABCB4": "Financeiro / Intermediários Financeiros / Bancos",
        "CCRO3": "Bens Industriais / Transporte / Exploração de Rodovias",
        "MRVE3": "Consumo Cíclico / Construção Civil / Incorporações",
        "ODPV3": "Saúde / Serv.Méd.Hospit..Análises e Diagnósticos / Serv.Méd.Hospit..Análises e Diagnósticos",
        "VALE3": "Materiais Básicos / Mineração / Minerais Metálicos",
        "CPLE6": "Utilidade Pública / Energia Elétrica / Energia Elétrica",
    }

    df_qtd = pd.read_csv("app/stocks_qtt.csv")
    df_patrimonio = pd.read_csv("app/stocks_patrimonio.csv")

    st.header("Qtd de Ações por Setor")
    companies_sectors_df = pd.DataFrame(
        {"companies": sectors.keys(), "sector": sectors.values()}
    )
    companies_sectors_df["sector_simple"] = (
        companies_sectors_df["sector"].str.split("/").map(lambda x: x[0])
    )

    sector_pie = (
        df_qtd.merge(
            companies_sectors_df, left_on="stock", right_on="companies", how="left"
        )
        .groupby("sector_simple")["feb"]
        .agg(sum)
        .reset_index()
    )

    quantities = sector_pie["feb"]
    labels = sector_pie["sector_simple"]

    colors = sns.color_palette("pastel")[0:13]

    fig = plt.figure(figsize=(10, 4))
    plt.pie(quantities, labels=labels, colors=colors, autopct="%.0f%%")
    plt.title("Considerando o mês de Fevereiro de 2023")
    st.pyplot(fig)

    st.header("R$ de Ações por Setor")

    sector_pie = (
        df_patrimonio.merge(
            companies_sectors_df, left_on="stock", right_on="companies", how="left"
        )
        .groupby("sector_simple")["feb"]
        .agg(sum)
        .reset_index()
    )

    quantities = sector_pie["feb"]
    labels = sector_pie["sector_simple"]

    colors = sns.color_palette("pastel")[0:13]

    fig = plt.figure(figsize=(10, 4))
    plt.pie(quantities, labels=labels, colors=colors, autopct="%.0f%%")
    plt.title("Considerando o mês de Fevereiro de 2023")
    st.pyplot(fig)

    # pie by company
    st.header("Qtd de Ações por Empresa")
    quantities = df_qtd["feb"]
    labels = df_qtd["stock"]

    colors = sns.color_palette("pastel")[0:18]

    fig = plt.figure(figsize=(10, 4))
    plt.pie(quantities, labels=labels, colors=colors, autopct="%.0f%%")
    st.pyplot(fig)

    st.header("Evolução ao longo do ano")

    df_lines = df_patrimonio.melt(id_vars="stock")

    fig = plt.figure(figsize=(10, 9))
    _ = sns.lineplot(
        data=df_lines, x="variable", y="value", hue="stock", palette="tab20b"
    )
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
    plt.xlabel("")
    plt.ylabel("Total R$")
    st.pyplot(fig)

    st.header("Totais Absolutos")
    fig = plt.figure(figsize=(10, 4))
    df_totals = df_patrimonio.drop("stock", axis=1).sum(axis=0).reset_index()
    axs = sns.barplot(data=df_totals, x="index", y=0)
    _ = show_values(axs, orient="v", space_y=0.0)
    st.pyplot(fig)
