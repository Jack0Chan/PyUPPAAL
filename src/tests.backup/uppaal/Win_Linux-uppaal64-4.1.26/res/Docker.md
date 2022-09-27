# Docker Virtualization of Uppaal Linux engine

Docker provides lightweight virtualization to run Uppaal Linux engine (e.g. on Windows, MacOSX).

# Instructions:

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

2. Visit `upppaal-4.1.20` folder where Dockerfile is and create Uppaal engine image by running on the command line:
```
cd uppaal-4.1.20/
docker image build --tag uppaal-4.1.20 -f res/Dockerfile .
```

3. Start the docker container in a detached state with port 2350 mapped to 2350:
```
docker run -d -p 2350:2350 uppaal-4.1.20
```

4. Start Uppaal GUI (it will try connecting to port 2350 by default)
   by double-clicking on `uppaal.exe` or `uppaal.jar`, or on command line:
```
java -jar uppaal.jar
```
The hosting server and port can be customized, e.g.:
```
java -jar uppaal.jar --serverHost localhost --serverPort 2350
```


Uppaal engine exits (and releases the resources) when the Uppaal GUI is closed, but the Docker container remains running and ready for other connections.

To stop the container, first find its identifier and then stop it, for example:
```
docker ps

CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS                    NAMES
345c8263c4a8        uppaal-4.1.20       "./socketserver"    6 seconds ago       Up 5 seconds        0.0.0.0:2350->2350/tcp   modest_kare
```
```
docker stop 345c8263c4a8
```

