import pandas as pd
import requests
import sqlalchemy

# 1. Ler uma linha de exemplo diretamente da Feature Store para obter todas as variáveis esperadas
engine = sqlalchemy.create_engine(
    r"sqlite:///C:\Users\joaop\Desktop\loyalty-predict-main\loyalty-predict-main\data\analytics\database.db"
)
sample_data = (
    pd.read_sql("SELECT * FROM fs_all LIMIT 1", engine)
    .to_dict(orient="records")[0]
)

# 2. Enviar a requisição POST para a API
url = "http://127.0.0.1:8080/predict"
payload = {"data": sample_data}

response = requests.post(url, json=payload)

# 3. Visualizar o resultado retornado pela API
print("Código HTTP:", response.status_code)
print("Resposta JSON:", response.json())