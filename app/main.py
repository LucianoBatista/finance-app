import calendar
from datetime import datetime, timezone

import plotly.graph_objects as go
import streamlit as st
from dateutil.relativedelta import relativedelta
from streamlit_option_menu import option_menu

INCOMES = ["Salário", "Fotografia", "Oc3"]
CATEGORIES = {
    "Alimentação": ["Mercado", "Lazer", "Trabalho", "Marmita"],
    "Casa": [
        "Móveis",
        "Aluguel",
        "Condomínio",
        "Internet",
        "Gás",
        "Luz",
        "Seguro Incêndio",
        "Cozinha",
        "Detalhes",
        "Contas",
        "Faxina",
        "IPTU",
    ],
    "Celular": ["Lu/Oi"],
    "Empresa": ["MEI"],
    "Dog": ["Diversos", "Veterinário", "Ração", "Hospedagem"],
    "Educação": [
        "Pós/ESSS",
        "Livros",
        "Cursos (MOOCs)",
        "Inglês",
        "Bootcamp",
    ],
    "HomeOffice": ["Papelaria", "Eletrônicos"],
    "Hospedagem": ["Trabalho"],
    "Lazer": ["Viagem", "Cinema", "Desenho"],
    "Outros": ["Gifts", "Outros"],
    "Pessoal": ["Vestuário", "Hair", "Estética", "Bunda"],
    "Planta": ["Químicos", "Planta", "Utensílios"],
    "Saúde": [
        "Fisioterapia",
        "Farmácia",
        "Suplementos",
        "Exames",
        "Consulta",
        "Olhos",
        "Academia",
    ],
    "Shopee": ["Shopee"],
    "Transporte": ["App", "Ônibus", "Avião"],
}
EXPENSES = ["Rent", "Utilities", "Car", "Hospital", "Others"]
CURRENCY = "BRA"
PAGE_TITLE = "Gastos e Entradas"
PAGE_ICON = ":knife: :money_with_wings:"
LAYOUT = "centered"


def clean_session():
    for key in st.session_state.keys():
        del st.session_state[key]

    st.session_state["description"] = ""
    st.session_state["category_expense"] = "Alimentação"
    st.session_state["total"] = 0.00
    st.session_state["type_spent"] = "Variável"
    st.session_state["type_buy"] = "débito"
    st.session_state["bank"] = "Nubank"
    st.session_state["user"] = "Tica"


st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
st.title(PAGE_TITLE + " " + PAGE_ICON)

# dropdown
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])

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
        col1.selectbox("Select Month:", months, key="month_income")
        col2.selectbox("Select Year:", years, key="year_income")

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
            # TODO: insert values into the database
            st.write("incomes: {}".format(incomes))
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

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        st.radio("Tipo de gasto", ["Variável", "Fixo"], key="type_spent")

    with c2:
        st.radio("Tipo de compra", ["débito", "crédito"], key="type_buy")

    with c3:
        st.radio("Quem foi?", ["Tica", "Luba"], key="user")

    with c4:
        st.radio("Banco", ["Nubank", "BB", "Ticket", "Flash", "Cash"], key="bank")

    "---"
    st.subheader("Vencimento")
    c_1, c_2 = st.columns(2)
    with c_1:
        st.date_input("Data da Compra", datetime.now(tz=timezone.utc), key="date_buy")

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

    submitted2 = st.button("Send data!", on_click=clean_session)

    if submitted2:
        # TODO: data de criação e data do débito
        payload = {
            "product": st.session_state["description"],
            "category": st.session_state["category_expense"],
            "sub_category": st.session_state["subcategory_expense"],
            "total": st.session_state["total"],
            "type_spent": st.session_state["type_spent"],
            "type_buy": st.session_state["type_buy"],
            "bank": st.session_state["bank"],
            "created_at": st.session_state["date_buy"].strftime("%d-%m-%Y"),
            "due_date": st.session_state["due_date"].strftime("%d-%m-%Y"),
        }
        st.json(payload)
        st.success("Sended Data!")

if selected == "Vendo o Rombo":
    # plot periods
    st.header("Data Viz")
    with st.form("saved_periods"):
        # TODO: get periods from database
        period = st.selectbox("Select Period:", ["22022_March"])
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            # TODO: get data from database
            comment = "Some comment"
            incomes = {"Salary": 2000}
            expenses = {"Car": 1000, "Courses": 125}

            # create metrics
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {CURRENCY}")
            col2.metric("Total Expense", f"{total_expense} {CURRENCY}")
            col3.metric("Remaining Budget", f"{remaining_budget} {CURRENCY}")
            st.text("Comment {}".format(comment))

            # graph
            label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [
                label.index(expense) for expense in expenses.keys()
            ]
            value = list(incomes.values()) + list(expenses.values())

            # Data to dict, dict to sankey
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=30, color="#E694FF")
            data = go.Sankey(link=link, node=node)

            # Plot it!
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)
