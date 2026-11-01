# Usa o interpretador Python do ambiente ativo (Conda/Windows)
PYTHON=python
PIP=$(PYTHON) -m pip

# Configura as dependências do ambiente
.PHONY: setup
setup:
	@echo "Instalando dependencias a partir do requirements.txt..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Executa a coleta de dados
.PHONY: collect
collect:
	@echo "Executando script de engenharia (coleta de dados)..."
	$(PYTHON) src/engineering/get_data.py

# ETL das features
.PHONY: etl
etl:
	@echo "Executando pipeline de analytics..."
	$(PYTHON) src/analytics/pipeline_analytics.py

# Predição
.PHONY: predict
predict:
	@echo "Executando script de predicao..."
	$(PYTHON) src/analytics/predict_fiel.py

# Alvo para rodar a esteira completa igual ao vídeo
.PHONY: run
run: collect etl predict

# Alvo padrão
.PHONY: all
all: run