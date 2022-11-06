import os

from deta import Deta
from dotenv import load_dotenv

load_dotenv()

PROJECT_DETA_KEY = os.getenv("project_deta_key")

if __name__ == "__main__":
    # 2) initialize with a project key
    deta = Deta(PROJECT_DETA_KEY)

    # 3) create and use as many DBs as you want!
    db = deta.Base("finance_app")

    db.insert({"name": "Geordi", "title": "Chief Engineer", "salary": 12})

    fetch_res = db.fetch({"name": "Geordi"})

    for item in fetch_res.items:
        db.delete(item["key"])
