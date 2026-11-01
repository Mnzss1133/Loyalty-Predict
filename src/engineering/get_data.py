#%%
import os
import pathlib
import dotenv

# 1. Definir o caminho absoluto baseado na localização deste arquivo
BASE_DIR = pathlib.Path(__file__).resolve().parents[2]  # Raiz do projeto (loyalty-predict-main)

# 2. Carregar variáveis de ambiente ANTES de importar o Kaggle
dotenv.load_dotenv(BASE_DIR / '.env')

# Se não estiverem no .env, defina antes do import:
os.environ['KAGGLE_USERNAME'] = 'seu_usuario'
os.environ['KAGGLE_KEY'] = 'sua_chave'

from kaggle import api

#%%
datasets = [
    'teocalvo/teomewhy-loyalty-system',
    'teocalvo/teomewhy-education-platform',
]

for d in datasets:
    dataset_name = d.split("teomewhy-")[-1]
    print(f"Baixando: {dataset_name}...")

    # Garante que a pasta destino exista
    target_dir = BASE_DIR / 'data' / dataset_name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Faz o download e já descompacta direto no diretório final
    api.dataset_download_file(
        dataset=d,
        file_name='database.db',
        path=str(target_dir),
        force=True,
        quiet=False
    )
# %%
