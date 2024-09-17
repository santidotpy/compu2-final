FROM python:3.10.12

# Definir el directorio de trabajo
WORKDIR /app

# Añadir archivos al directorio de trabajo
ADD chat/server.py ./chat/server.py
ADD chat/utils/utils.py ./chat/utils/utils.py
ADD chat/utils/testing_users.py ./chat/utils/testing_users.py

# Copiar el archivo de requisitos y credenciales
COPY requirements.txt ./
COPY credentials.json ./

# Instalar las dependencias
RUN pip install -r requirements.txt

# Comprobar el contenido del directorio actual
RUN pwd && ls

# Exponer el puerto
EXPOSE 55555

# Ejecutar el servidor
CMD ["python", "chat/server.py"]
