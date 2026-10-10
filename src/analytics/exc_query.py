# %%
import argparse
import datetime
from tqdm import tqdm

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

def date_range(start, stop, monthly=False):
    dates = []
    while start <= stop:
        dates.append(start)
        dt_start = datetime.datetime.strptime(start, '%Y-%m-%d') + datetime.timedelta(days=1)
        start = datetime.datetime.strftime(dt_start, '%Y-%m-%d')
        
    if monthly:
        return [i for i in dates if i.endswith("01")]
    
    return dates

DATA_DIR = CURRENT_DIR.parent.parent / "data"

def exec_query(table, db_origin, db_target, dt_start, dt_stop, monthly, mode="append"):
    # Monta os caminhos exatos
    path_origin = DATA_DIR / db_origin / "database.db"
    path_target = DATA_DIR / db_target / "database.db"

    # Garante que o diretório de destino exista antes de tentar gravar
    path_target.parent.mkdir(parents=True, exist_ok=True)

    # Cria as conexões usando o creator
    engine = sqlalchemy.create_engine(
        "sqlite://",
        creator=lambda: sqlite3.connect(str(path_origin))
    )

    engine_analytical = sqlalchemy.create_engine(
        "sqlite://",
        creator=lambda: sqlite3.connect(str(path_target))
    )
    query = import_query(f"{table}.sql")
    dates = date_range(dt_start, dt_stop, monthly)

    for i in tqdm(dates):
        
        if mode == 'append':
            with engine_analytical.connect() as con:
                try:
                    query_delete = f"DELETE FROM {table} WHERE dtRef = date('{i}', '-1 day')"
                    con.execute(sqlalchemy.text(query_delete))
                    con.commit()
                except Exception as err:
                    print(err)
        
        query_format = query.format(date=i)
        df = pd.read_sql(query_format, engine)
        df.to_sql(table, engine_analytical, index=False, if_exists=mode)


#%%
# 4 barras no SQLite para caminho absoluto no Windows
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_origin", choices=['loyalty-system', 'education-platform', 'analytics'],
                        default='loyalty-system')
    
    parser.add_argument("--db_target", choices=['analytics'], default='analytics')
    parser.add_argument("--table", type=str, help="Tabela que será processada com o mesmo nome do arquivo.")

    now = datetime.datetime.now().strftime("%Y-%m-%d")
    parser.add_argument("--start", type=str, default=now)
    parser.add_argument("--stop", type=str, default=now)
    parser.add_argument("--monthly", action='store_true')
    parser.add_argument("--mode", choices=['append', 'replace'])
    args = parser.parse_args()
    
    exec_query(args.table, args.db_origin, args.db_target, args.start, args.stop, args.monthly)


if __name__ == "__main__":
    main()

