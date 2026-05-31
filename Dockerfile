# Imagem base Python
FROM python:3.11-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro (cache de camadas)
COPY projeto_todo/ .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe a porta que o Flask usa
EXPOSE 5000

# Variáveis de ambiente do Flask
ENV FLASK_APP=projeto_tj.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando para iniciar a aplicação
CMD ["flask", "run"]
