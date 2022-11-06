import streamlit as st


def callback_clear_session():
    for key in st.session_state.keys():
        del st.session_state[key]

    st.session_state["description"] = ""
    st.session_state["category_expense"] = "Alimentação"
    st.session_state["total"] = 0.00
    st.session_state["type_spent"] = "Variável"
    st.session_state["type_buy"] = "débito"
    st.session_state["bank"] = "Nubank"
    st.session_state["user"] = "Tica"
