# %%
import pandas as pd
import sqlalchemy

# %%
from pathlib import Path
import sqlite3
# %%
# Define o caminho absoluto para a pasta onde este ficheiro/scripts residem
# Se __file__ não estiver disponível na célula, usamos o caminho absoluto direto:
CURRENT_DIR = (
    Path(__file__).resolve().parent
    if "__file__" in locals()
    else Path(r"C:\Users\joaop\Desktop\loyalty-predict-main\loyalty-predict-main\src\analytics")
)

def import_query(filename):
    filepath = CURRENT_DIR / filename
    with open(filepath, "r", encoding="utf-8") as open_file:
        return open_file.read()

query = import_query("life_cycle.sql")

# %%
# Caminho exato para a pasta do banco ('loyalty-sistem')
db_path = Path(r"C:\Users\joaop\Desktop\loyalty-predict-main\loyalty-predict-main\data\loyalty-sistem\database.db")

# 4 barras no SQLite para caminho absoluto no Windows
engine = sqlalchemy.create_engine(
    "sqlite://",
    creator=lambda: sqlite3.connect(str(db_path))
)

# %%
df = pd.read_sql(query, engine)
df.head()
# %%
db_path2 =Path(r"C:\Users\joaop\Desktop\loyalty-predict-main\loyalty-predict-main\data\analytics\database.db")
# %%
engine_analytical = sqlalchemy.create_engine(
    "sqlite://",
    creator=lambda: sqlite3.connect(str(db_path2))
)

# %%
dates = [
    '2024-03-01',
    '2024-04-01',
    '2024-05-01',
    '2024-06-01',
    '2024-07-01',
    '2024-08-01',
    '2024-09-01',
    '2024-10-01',
    '2024-11-01',
    '2024-12-01',
    '2025-01-01',
    '2025-02-01',
    '2025-03-01',
    '2025-04-01',
    '2025-05-01',
    '2025-06-01',
    '2025-07-01',
    '2025-08-01',
    '2025-09-01',
]
for i in dates:
    with engine_analytical.connect() as conn:
        try:
            conn.execute(sqlalchemy.text(f"DELETE FROM life_cycle WHERE dtRef='{i}'"))
            conn.commit()
        except Exception as err:
            print(err)

    query_format = query.format(date=i)
    df = pd.read_sql(query_format, engine)
    df.to_sql('life_cycle',engine_analytical,index=False,if_exists='append')


# %%
