# Proyecto Final - Computación II


## Chat en tiempo real

### Instalación de dependencias
```bash
pip3 install -r requirements.txt
```

### Correr el servidor
```bash
python3 chat/server.py
```

### Correr el cliente
```bash
python3 chat/client.py
```

### Docker 🐋
```bash
docker build -t compu2-server . # buildear la imagen docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' server-container
docker run -d --name server-container compu2-server # correr la imagen
```
Luego de correr el servidor, se puede correr el cliente de manera normal.


> [!NOTE]  
> Para ver en que dirección IP se encuentra el servidor, se puede correr el siguiente comando:
```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' server-container
```

### Firebase 🔥
Para correr el servidor con Firebase, se debe tener un archivo `credentials.json` con las credenciales de Firebase. El mismo se consigue en Firebase. Dicho archivo tiene el siguiente formato:
```json
  {
    "type": "EXAMPLE",
    "project_id": "EXAMPLE",
    "private_key_id": "EXAMPLE",
    "private_key": "-----BEGIN PRIVATE KEY-----\nEXAMPLE\n-----END PRIVATE KEY-----\n",
    "client_email": "EXAMPLE",
    "client_id": "0123456789",
    "auth_uri": "EXAMPLE",
    "token_uri": "EXAMPLE",
    "auth_provider_x509_cert_url": "EXAMPLE",
    "client_x509_cert_url": "EXAMPLE",
    "universe_domain": "EXAMPLE"
  }
```

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Firebase](https://img.shields.io/badge/firebase-%23039BE5.svg?style=for-the-badge&logo=firebase)