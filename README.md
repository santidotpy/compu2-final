# Proyecto Final - Computación II


## Chat en tiempo real


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
Para correr el servidor con Firebase, se debe tener un archivo `credentials.json` con las credenciales de Firebase. El mismo se consigue en Firebase.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Firebase](https://img.shields.io/badge/firebase-%23039BE5.svg?style=for-the-badge&logo=firebase)