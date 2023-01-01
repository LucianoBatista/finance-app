import streamlit as st
from database.database import insert_facada


def callback_clear_session():

    if st.session_state["parcela"] == "S":
        for i in range(st.session_state["qt_parcelas"]):
            qt_parcelas = st.session_state["qt_parcelas"]
            description = st.session_state["description"] + " " + f"{i+1}/{qt_parcelas}"

            payload = {
                "product": description,
                "category": st.session_state["category_expense"],
                "sub_category": st.session_state["subcategory_expense"],
                "total": st.session_state["total"],
                "type_spent": st.session_state["type_spent"],
                "type_buy": st.session_state["type_buy"],
                "bank": st.session_state["bank"],
                "created_at": st.session_state[f"date_buy_{i}"].strftime("%d-%m-%Y"),
                "due_date": st.session_state[f"due_date_{i}"].strftime("%d-%m-%Y"),
            }

            insert_facada(payload)

    elif st.session_state["parcela"] == "N":
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

        insert_facada(payload)

    for key in st.session_state.keys():
        del st.session_state[key]

    st.session_state["description"] = ""
    st.session_state["category_expense"] = "Alimentação"
    st.session_state["total"] = 0.00
    st.session_state["type_spent"] = "Variável"
    st.session_state["type_buy"] = "débito"
    st.session_state["bank"] = "Nubank"
    st.session_state["user"] = "Tica"
    st.session_state["parcela"] = "N"
