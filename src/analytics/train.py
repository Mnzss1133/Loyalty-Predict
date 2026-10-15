#%%
import pandas as pd
import sqlalchemy
from pathlib import Path
import sqlite3
#%%
db_path = Path(r"C:\Users\joaop\Desktop\loyalty-predict-main\loyalty-predict-main\data\analytics\database.db")

# Garante que o arquivo realmente existe antes de tentar abrir
if not db_path.exists():
    raise FileNotFoundError(f"Banco não encontrado em: {db_path}")

engine = sqlalchemy.create_engine(
    "sqlite://",
    creator=lambda: sqlite3.connect(str(db_path))
)

#%%
df = pd.read_sql_table("abt_fiel", engine)
df.head()

# %%
# OOT
df_oot = df[df['dtRef']==df['dtRef'].max()]
df_oot
# %%
# SAMPLES
target ='flFiel'
features = df.columns.to_list()[3:]

df_train_test = df[df['dtRef']<df['dtRef'].max()].reset_index(drop=True)
df_train_test
# %%
X = df_train_test[features]# Isso é uma matriz
y = df_train_test[target]# Isso é um pd.Series, ou seja, um vetor
#%%
print(f'Taxa da target {100*y.mean():.2f}%')
# %%
from sklearn.model_selection import train_test_split
# %%
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3,random_state=42,stratify=y)

print(f"Base treino: {y_train.shape[0]} Unid. | Tx_Target: {100*y_train.mean():.2f}%")
print(f"Base teste: {y_test.shape[0]} Unid. | Tx_Target: {100*y_test.mean():.2f}%")

# %%
#Explore
nas = X_train.isna().mean()
nas = nas[nas>0]
nas
#%%

cat_features =['descLifeCycleAtual','descLifeCycleD28']
num_features = list(set(features)-set(cat_features))
df_train=X_train.copy()
df_train[target]=y_train.copy()
df_train[num_features]=df_train[num_features].astype(float)

bivariada = df_train.groupby(target)[num_features].median().T
bivariada['ratio'] =(bivariada[1]+0.001)/(bivariada[0]+0.001)
bivariada.sort_values(by='ratio',ascending=False)

#%%
to_remove = bivariada[(bivariada['ratio'] == 1) | (bivariada['ratio'].isna())].index.tolist()
print(to_remove)
#%%
for i in to_remove:
    features.remove(i)
    num_features.remove(i)
#%%
len(num_features)
#%%
bivariada = df_train.groupby(target)[num_features].median().T
bivariada['ratio'] =(bivariada[1]+0.001)/(bivariada[0]+0.001)
bivariada.sort_values(by='ratio',ascending=False)

# %%
df_train.groupby('descLifeCycleAtual')[target].mean()
#%%
df_train.groupby('descLifeCycleD28')[target].mean()

# %%

# %%
