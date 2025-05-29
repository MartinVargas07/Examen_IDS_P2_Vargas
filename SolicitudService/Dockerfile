# Usar una imagen base de Python optimizada y oficial.
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor.
WORKDIR /usr/src/app

# Copiar primero el archivo de requerimientos.
COPY requirements.txt ./

# Instalar las dependencias de Python.
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación.
# El primer './app' es la carpeta 'app' local.
# El segundo './app' es el destino DENTRO de WORKDIR (/usr/src/app) en el contenedor.
# Esto crea la estructura /usr/src/app/app/ donde estarán main.py y security.py
COPY ./app ./app  

# Exponer el puerto en el que la aplicación Flask correrá.
EXPOSE 5001

# Comando para correr la aplicación.
# Usar "python -m app.main" permite que Python maneje correctamente
# el path para los imports dentro del paquete 'app'.
CMD ["python", "-m", "app.main"]
