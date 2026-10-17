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
df = pd.read_sql("select * from abt_fiel", engine)
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
import seaborn as sns
sns.countplot(data=pd.DataFrame(data=y_train),x='flFiel')
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
##to_remove = bivariada[(bivariada['ratio'] == 1) | (bivariada['ratio'].isna())].index.tolist()
##print(to_remove)
#%%
####for i in to_remove:
####    features.remove(i)
####    num_features.remove(i)
#%%
##len(num_features)
###%%
##bivariada = df_train.groupby(target)[num_features].median().T
##bivariada['ratio'] =(bivariada[1]+0.001)/(bivariada[0]+0.001)
##bivariada.sort_values(by='ratio',ascending=False)

# %%
df_train.groupby('descLifeCycleAtual')[target].mean()
#%%
df_train.groupby('descLifeCycleD28')[target].mean()
#%%
X_train[num_features]=X_train[num_features].astype(float)
#%%
# MODIFY - DROP
from feature_engine import selection
to_remove = bivariada[(bivariada['ratio'] == 1)].index.tolist()
drop_features= selection.DropFeatures(to_remove)
X_train_transform=drop_features.fit_transform(X_train)
# %%
#MODIFY - MISSING
from feature_engine import imputation
s_na = X_train_transform.isna().mean()

lista_com_na = s_na[s_na == 1].index.difference(['qtdDiasUltiAtividade']).tolist()
fill_0 = lista_com_na
fill_0
#%%
input_0 = imputation.ArbitraryNumberImputer(arbitrary_number=0,variables=fill_0)
input_new = imputation.CategoricalImputer(fill_value='Nao-Usuario',variables=['descLifeCycleD28'])
input_1000 = imputation.ArbitraryNumberImputer(arbitrary_number=1000,variables=['avgIntervaloDiasD28','avgIntervaloDiasVida','qtdDiasUltiAtividade'])
# %%

X_train_transform = input_0.fit_transform(X_train_transform)
X_train_transform=input_new.fit_transform(X_train_transform)
X_train_transform=input_1000.fit_transform(X_train_transform)
# %%
nas = X_train_transform.isna().mean()
nas = nas[nas>0]
nas
# %%
# MODIFY - OneHot
from feature_engine import encoding
onehot = encoding.OneHotEncoder(variables=cat_features)
X_train_transform = onehot.fit_transform(X_train_transform)

# %%
# MODEL
from sklearn import tree
from sklearn import ensemble
#model = tree.DecisionTreeClassifier(random_state=42,min_samples_leaf=50)
model = ensemble.RandomForestClassifier(random_state=42,n_estimators=150,n_jobs=-1,min_samples_leaf=60)

model.fit(X_train_transform,y_train)
# %%
# ASSES
#USANDO ACURACIA (NÂO DEVE USAR POIS O MODELO É DESBALANCEADO
from sklearn import metrics
##y_pred = model.predict(X_train_transform)
##acc_train = metrics.accuracy_score(y_train,y_pred)
##acc_train
y_pred_train = model.predict_proba(X_train_transform)
roc_score_train = metrics.roc_auc_score(y_train,y_pred_train[:,1])
print(f" Curva ROC Treino: {roc_score_train}")
# %%
X_test_transform =drop_features.transform(X_test)
X_test_transform = input_0.transform(X_test_transform)
X_test_transform=input_new.transform(X_test_transform)
X_test_transform=input_1000.transform(X_test_transform)
X_test_transform = onehot.transform(X_test_transform)
#%%
#USANDO ACURACIA (NÂO DEVE USAR POIS O MODELO É DESBALANCEADO
#y_pred_test = model.predict(X_test_transform)
#acc_test = metrics.accuracy_score(y_test,y_pred_test)
#acc_test
y_pred_test = model.predict_proba(X_test_transform)
roc_score_teste = metrics.roc_auc_score(y_test,y_pred_test[:,1])
print(f" Curva ROC Teste: {roc_score_teste}")
# %%
feature_names = X_train_transform.columns.tolist()
feature_importance = pd.Series(model.feature_importances_,index=feature_names)
feature_importance.sort_values(ascending=False)
# %%
