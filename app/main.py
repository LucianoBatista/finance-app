import calendar
from datetime import datetime

import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

INCOMES = ["salary", "photography", "oc3"]
EXPENSES = ["Rent", "Utilities", "Car", "Hospital", "Others"]
CURRENCY = "USD"
PAGE_TITLE = "Income and Expense Tracker"
PAGE_ICON = ":sparkles:"
LAYOUT = "centered"

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
    options=["Data Entry", "Data Visualization"],
    icons=["pencil-fill", "bar-chart-fill"],
    orientation="horizontal",
)

# input and save periods
if selected == "Data Entry":
    st.header("Data Entry in {}".format(CURRENCY))
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month:", months, key="month")
        col2.selectbox("Select Year:", years, key="year")

        "---"
        with st.expander("Income"):
            for income in INCOMES:
                st.number_input(
                    f"{income}:", min_value=0.0, format="%.2f", step=10.0, key=income
                )
        with st.expander("Expanse"):
            for expense in EXPENSES:
                st.number_input(
                    f"{expense}:", min_value=0.0, format="%.2f", step=10.0, key=expense
                )
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment here...")

        "---"
        submitted = st.form_submit_button("Save Data")
        if submitted:
            # session state get the values referencing the keys from the objects
            period = (
                str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            )
            incomes = {income: st.session_state[income] for income in INCOMES}
            expenses = {expense: st.session_state[expense] for expense in EXPENSES}
            # TODO: insert values into the database
            st.write("incomes: {}".format(incomes))
            st.write("expenses: {}".format(expenses))
            st.success("Data saved")

if selected == "Data Visualization":
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
