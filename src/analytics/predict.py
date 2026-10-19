#%%
import pandas as pd
import sqlalchemy
from pathlib import Path
import sqlite3
import mlflow
db_path = Path(r"C:\Users\joaop\Desktop\loyalty-predict-main\loyalty-predict-main\data\analytics\database.db")
mlflow.set_tracking_uri('http://localhost:5000')
# Garante que o arquivo realmente existe antes de tentar abrir
if not db_path.exists():
    raise FileNotFoundError(f"Banco não encontrado em: {db_path}")

engine = sqlalchemy.create_engine(
    "sqlite://",
    creator=lambda: sqlite3.connect(str(db_path))
)
#%%
model = mlflow.sklearn.load_model("models:///model_fiel/1")
#%%
model
#%%
data=pd.read_sql('SELECT * FROM abt_fiel',engine)
predict = model.predict_proba(data[model.feature_names_in_])[:,1]
data['predict']=predict

# %%

DATA
# %%

# %%
