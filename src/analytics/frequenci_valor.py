# %%
import pandas as pd
import sqlalchemy
# %%
from pathlib import Path
import sqlite3
# %% 
db_path = Path(r"C:\Users\joaop\Desktop\loyalty-predict-main\loyalty-predict-main\data\loyalty-sistem\database.db")

# 4 barras no SQLite para caminho absoluto no Windows
engine = sqlalchemy.create_engine(
    "sqlite://",
    creator=lambda: sqlite3.connect(str(db_path))
)
# %%
CURRENT_DIR = (
    Path(__file__).resolve().parent
    if "__file__" in locals()
    else Path(r"C:\Users\joaop\Desktop\loyalty-predict-main\loyalty-predict-main\src\analytics")
)
# %%
def import_query(filename):
    filepath = CURRENT_DIR / filename
    with open(filepath, "r", encoding="utf-8") as open_file:
        return open_file.read()

query = import_query("frequencia_valor.sql")
# %%
df = pd.read_sql(query, engine)
df.head()
#%%
df = df[df['qtdePontosPos']<4000]
# %%
import matplotlib.pyplot as plt
plt.plot(df['qtdeFrequencia'],df['qtdePontosPos'],'o')
plt.xlabel('Frequencia')
plt.ylabel('Valor')
plt.grid(True)
plt.show()
# %%
import seaborn as sns
sns.scatterplot(data=df,x='qtdeFrequencia',y='qtdePontosPos',palette='viridis')
plt.grid(True)
plt.show()
# %%
from sklearn import cluster
from sklearn import preprocessing
minmax = preprocessing.MinMaxScaler()
X = minmax.fit_transform(df[['qtdeFrequencia','qtdePontosPos']])
df_X =pd.DataFrame(X,columns=['normFreq','normValor'])
kmeans = cluster.KMeans(n_clusters=5,random_state=42,max_iter=1000)
kmeans.fit(X)
df['cluster_calc'] = kmeans.labels_
df_X['cluster_calc'] = kmeans.labels_
df.groupby(by='cluster_calc')['idCliente'].count()
# %%
import seaborn as sns
sns.scatterplot(data=df,x='qtdeFrequencia',y='qtdePontosPos',palette='deep',hue='cluster_calc')
plt.hlines(y=1500,xmin=0,xmax=25,color='black')
plt.hlines(y=750,xmin=0,xmax=25,color='black')
plt.vlines(x=4,ymin=0,ymax=750,color='black')
plt.vlines(x=10,ymin=0,ymax=3000,color='black')
plt.grid(True)
plt.show()
# %%
sns.scatterplot(data=df,x='qtdeFrequencia',y='qtdePontosPos',palette='deep',hue='cluster')
plt.grid(True)
plt.show()
# %%
