import os

from deta import Deta
from dotenv import load_dotenv

load_dotenv()

PROJECT_DETA_KEY = os.getenv("project_deta_key")

# init with the key
deta = Deta(PROJECT_DETA_KEY)

# This is how to create/connect a database
db = deta.Base("finance_app")
db_income = deta.Base("finance_app_income")


def insert_facada(payload):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db.put(payload)


def insert_income(payload):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db_income.put(payload)


def fetch_all_periods_expense():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items


def fetch_all_periods_income():
    """Returns a dict of all periods"""
    res = db_income.fetch()
    return res.items


def get_period(period):
    """If not found, the function will return None"""
    return db.get(period)
