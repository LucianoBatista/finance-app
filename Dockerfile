FROM python:3.10-slim-buster

EXPOSE 8501

WORKDIR /app

COPY Pipfile* ./

RUN pip install -q --no-cache-dir \
    pipenv===2021.5.29 && \
    pipenv install --system

COPY . .

CMD streamlit run app/main.py