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
LAYOUT = "centered"

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

# navigation menu
selected = option_menu(
    menu_title=None,
    options=["Entrada da Facada", "Entrada do Cacau", "Vendo o Rombo"],
    icons=["graph-down-arrow", "cash-stack", "bar-chart-fill"],
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

            # create metrics
            total_income = incomes_date_df.iloc[:, 0:4].values.sum()
            total_expense = expenses_date_df["total"].sum()
            remaining_budget = total_income - total_expense

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {CURRENCY}")
            col2.metric("Total Expense", f"{total_expense} {CURRENCY}")
            col3.metric("Diff", f"{remaining_budget} {CURRENCY}")

            # barplots
            sns.set_theme(style="whitegrid")
            fig = plt.figure(figsize=(10, 4))

            axs = sns.barplot(
                x="total", y="category", data=expenses_date_df, errorbar=None
            )
            plt.xlabel("Total")
            plt.ylabel("")
            _ = show_values(axs, orient="h")
            _ = sns.despine(left=True, bottom=True)

            st.pyplot(fig)
