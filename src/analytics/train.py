#%%
import pandas as pd
import sqlalchemy
from pathlib import Path
import sqlite3
import mlflow
import matplotlib.pyplot as plt
#%%
mlflow.set_tracking_uri('http://localhost:5000')
mlflow.set_experiment(experiment_id=1)
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
df_oot = df[df['dtRef'] >= '2026-01-01']
df_oot
# %%
# SAMPLES
target ='flFiel'
features = df.columns.to_list()[3:]

df_train_test = df[df['dtRef'] < '2026-01-01'].reset_index(drop=True)
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

# %%
#MODIFY - MISSING
from feature_engine import imputation
s_na = X_train.isna().mean()

lista_com_na = s_na[s_na == 1].index.difference(['qtdDiasUltiAtividade']).tolist()
fill_0 = lista_com_na
fill_0
#%%
input_0 = imputation.ArbitraryNumberImputer(arbitrary_number=0,variables=fill_0)
input_new = imputation.CategoricalImputer(fill_value='Nao-Usuario',variables=['descLifeCycleD28'])
input_1000 = imputation.ArbitraryNumberImputer(arbitrary_number=1000,variables=['avgIntervaloDiasD28','avgIntervaloDiasVida','qtdDiasUltiAtividade'])

# %%
nas = X_train.isna().mean()
nas = nas[nas>0]
nas
# %%
# MODIFY - OneHot
from feature_engine import encoding
onehot = encoding.OneHotEncoder(variables=cat_features)


# %%
# MODEL
from sklearn import tree
from sklearn import ensemble
#model = tree.DecisionTreeClassifier(random_state=42,min_samples_leaf=50)
model = ensemble.AdaBoostClassifier(random_state=42,n_estimators=150)
#%%
#Criando o pipeline

from sklearn import pipeline

with mlflow.start_run() as r:
    mlflow.sklearn.autolog()
    model_pipeline = pipeline.Pipeline(steps=[('Remocao de Features',drop_features),
                                            ('Imputacao de Zero',input_0),
                                            ('Imputacao de nao usuario',input_new),
                                            ('Inputacao de 1000',input_1000),
                                            ('Onehot',onehot),
                                            ('Algoritmo',model)])
    model_pipeline.fit(X_train,y_train)



    # ASSES
    #USANDO ACURACIA (NÂO DEVE USAR POIS O MODELO É DESBALANCEADO
    from sklearn import metrics
    ##y_pred = model.predict(X_train_transform)
    ##acc_train = metrics.accuracy_score(y_train,y_pred)
    ##acc_train
    y_pred_train = model_pipeline.predict_proba(X_train)
    roc_score_train = metrics.roc_auc_score(y_train,y_pred_train[:,1])
    print(f" Curva ROC Treino: {roc_score_train}")

  
    #USANDO ACURACIA (NÂO DEVE USAR POIS O MODELO É DESBALANCEADO
    #y_pred_test = model.predict(X_test_transform)
    #acc_test = metrics.accuracy_score(y_test,y_pred_test)
    #acc_test
    y_pred_test = model_pipeline.predict_proba(X_test)
    roc_score_teste = metrics.roc_auc_score(y_test,y_pred_test[:,1])
    print(f" Curva ROC Teste: {roc_score_teste}")

  
    #Metricas OOT
    X_oot = df_oot[features]
    y_oot = df_oot[target]
  
    y_pred_test_oot = model_pipeline.predict_proba(X_oot)
    roc_score_oot = metrics.roc_auc_score(y_oot,y_pred_test_oot[:,1])
    print(f" Curva ROC OOT: {roc_score_oot}")


    mlflow.log_metrics({'auc_train':roc_score_train,
        'auc_test':roc_score_teste})

    roc_train = metrics.roc_curve(y_train,y_pred_train[:,1])
    roc_test= metrics.roc_curve(y_test,y_pred_test[:,1])

    plt.figure(dpi=400)
    plt.plot(roc_train[0],roc_train[1])
    plt.plot(roc_test[0],roc_test[1])
    plt.legend(['Treino','Teste'])
    plt.title('Curva Roc')
    plt.savefig('v2_curva_roc.png')
    plt.show()
    mlflow.log_artifact('v2_curva_roc.png')
# %%
feature_names = model_pipeline[:-1].transform(X_train.head(1)).columns.tolist()
feature_importance = pd.Series(model_pipeline[-1].feature_importances_,index=feature_names)
feature_importance.sort_values(ascending=False)
    #%%
y_oot.value_counts()
# %%
model_series = pd.Series({
    'model':model_pipeline,
    'features':X_train.columns.tolist(),
    'auc_train':roc_score_train,
    'auc_test':roc_score_teste
})

model_series.to_pickle('modelo_fiel.pkl')
# %%
