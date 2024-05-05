# MISW-4204-Proyecto-MISW4204-202402-Grupo10

## # MISW-4204-Proyecto-MISW4204-202402-Grupo10

## Members

| **Name**                        | **Email**                   |
|---------------------------------|-----------------------------|
| Jhon Edinson Muñoz Riaños       | je.munozr1@uniandes.edu.co  |
| Juan Carlos Torres Machuca      | jc.torresm1@uniandes.edu.co |
| Cristian Eduardo Parada Criales | c.paradac@uniandes.edu.co   |
| Cristian Zapata Torres          | c.zapatat@uniandes.edu.co   |

---

## Despliegue Local - Entrega 1

Para un correcto despliegue en local debe tener instalado docker y docker-compose, a continuación siga
los siguientes pasos, los primeros son para eliminar residuos de ejecuciones anteriores y el último ejecutar
las aplicaciones.

### Eliminar contenedores locales

```shell
docker rm queue_nube postgres_nube worker_nube api_nube
```

### Eliminar imagenes locales

```shell
docker rmi desarrollo-soft-nube-misw4204-worker desarrollo-soft-nube-misw4204-api
```

### Eliminar volumenes locales

```shell
docker volume rm desarrollo-soft-nube-misw4204_shared-volume
```

### Ejecutar proyecto local

```shell
docker-compose -f docker-compose.yaml up
```

---

## Despliegue en Nube - Entrega 2

Para un correcto despliegue sobre la nube debe contar con acceso a [GCP](https://console.cloud.google.com/welcome),
debido a que las siguientes instrucciones son referentes a este proveedor.

Acceda a [GCP](https://console.cloud.google.com/welcome) y cree un nuevo proyecto (Como recomendación de nombre puede 
usar Soluciones-Cloud), al momento de crear el proyecto google cloud le asignará un id, este debe tenerlo presente ya
que luego lo utilizaremos, haciendo referencia a este como **ID_Proyecto_GCP**.

### Crear 3 instancias de VM

Para las tres instancias recomendamos los siguientes nombres ya que en pasos posteriores haremos referencia a ellas..

- instance-nfs-server
- instance-api
- instance-worker

Las caracteristicas bases de estas tres instancias son:

- 2 vCPU
- 2 GiB en RAM
- 20 GiB en almacenamiento
- Sistema Operativo: **Ubuntu 20.04 LTS**
- Modelo de aprovicionamiento de VM: **Estandar**

En la creación de **instancia-api** se debe habilitar **Permitir tráfico HTTP**

Para la creación de estas instancias puede hacer uso del siguiente recurso academico: [Link](https://jpadillaa.hashnode.dev/aprovisionar-una-instancia-de-computo-desde-la-consola-web-de-gcp)

### Crear una instancia de VM

Para esta instancia recomendamos el siguiente nombre ya que en pasos posteriores haremos referencia a ella.

- instance-queue

Las caracteristicas bases de esta instancia son:

- 2 vCPU
- 2 GiB en RAM
- 10 GiB en almacenamiento
- Sistema Operativo: **Ubuntu 20.04 LTS**
- Modelo de aprovicionamiento de VM: **Estandar**

### Crear Instancia de Base de Datos PostgreSQL

Antes de iniciar con este paso asegurese de tener corriendo las instancias **instance-api** y **instance-worker** ya que
vamos a necesitar la ip pública de cada una para añadirlas en la sección de Conexiones -> Nueva Red, de la instancia de bd

Para la instancia de bd deberá crear un usuario, password y base de datos especificas.

- *usuario*: **postgres** (Este usuario suele estar por defecto luego de inicia la instancia)
- *password*: Asigne una constraseña de su preferencia o generela con las opciones de GCP, guardela ya que luego la utilizaremos
- *base de datos*: Cree una nueva base de datos con el nombre **videos** 

Para la creación de la instancia de bd puede hacer uso del siguiente contenido academico: [Link](https://www.youtube.com/watch?v=vqFeLybeCNc)

#### En este punto debe contar con 4 instancias de VM y una de BD Postgres

##### Antes de iniciar con las configuraciones de instancias, habilitaremos puertos que posteriormente usaremos.

Para habilitar los puertos usaremos el Google CLI / Cloud Shell (Terminal de comandos desplegada en la web de GCP)

- Habilitar puertos del ActiveQM
```shell
gcloud compute --project=ID_Proyecto_GCP firewall-rules create activemq --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:8161,tcp:61616,tcp:61613,tcp:61614 --source-ranges=0.0.0.0/0
```

- Hailitar puertos de Base de datos
```shell
gcloud compute --project=ID_Proyecto_GCP firewall-rules create bd_pg --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:5432 --source-ranges=0.0.0.0/0
```

- Habilitar puertos de NFS
```shell
gcloud compute --project=ID_Proyecto_GCP firewall-rules create nfs --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:2049,tcp:111,tcp:1110,udp:2049,udp:111,udp:1110 --source-ranges=0.0.0.0/0
```

- Habilitar puertos del API
```shell
gcloud compute --project=ID_Proyecto_GCP firewall-rules create bd_pg --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:6000 --source-ranges=0.0.0.0/0
```

### Configurar server de Almacenamiento

Para configurar el servidor de almacenamiento conectese a la instancia **instance-nfs-server** mediante ssh

**Importante** se debe usar el siguiente carpeta **/var/nfs/shared_volume** como carpeta compartida, no usar el nombre
recomendado en el material academico, si decide usar el nombre del material academico tenerlo presente para los pasos
siguientes.

Al interior de la carpeta compartida cree dos carpetas más con los siguientes nombres:
- **ins**
- **outs**

Para este punto solo debe configurar el servidor, luego los clientes.
para esto puede hacer uso del siguiente contenido academico: [Link](https://jpadillaa.hashnode.dev/tutorial-nfs-network-file-system#heading-paso-3-resumen-de-la-instalacion-y-configuracion-del-servidor-y-cliente-nfs)

### Pasos Generales, para instalar dependecias en las diferentes instancias VM

Los siguientes pasos se deben ejecutar en las VM **instance-api**, **instance-worker**, **instance-queue**,
pero espere, ejecutelas cuando hablemos de cada instancia.

- Actualizar dependencias de apt
```shell
sudo apt update
```
- Instalar git
```shell
sudo apt install git
```
- Instalar Docker
```shell
sudo apt-get install ca-certificates curl
```
```shell
sudo install -m 0755 -d /etc/apt/keyrings
```
```shell
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
```
```shell
sudo chmod a+r /etc/apt/keyrings/docker.asc
```
```shell
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
```shell
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
```shell
sudo apt-get update
```
- Descargar repositorio
```shell
sudo git clone https://github.com/cczapatat/desarrollo-soft-nube-misw4204.git
```
```shell
cd desarrollo-soft-nube-misw4204
```

### Configurar ActiveQM - Servidor de Colas/Mensajeria

Para configurar el servidor de almacenamiento conectese a la instancia **instance-queue** mediante ssh.

Los siguientes pasos levantarán un ActiveQM en su instancia:

- Seguir los [Pasos Generales](#pasos-generales-para-instalar-dependecias-en-las-diferentes-instancias-vm)
- Ejecutar Cola
```shell
sudo docker compose -f docker-compose-queue.yaml up -d
```
Ahora puede ir a su navegador de preferencia y navegar a la página principal del ActiveQM usanddo la ip de la instancia

```http request
http://<instance-queue-ip>:8161
```

### Configurar Server Api

Para configurar el servidor tipo api conectese a la instancia **instance-api** mediante ssh.

Antes de continuar con los pasos del api, debemos configurar el NFS como cliente.

Recuerdo que la carpeta compartida en el server es la siguiente **/var/nfs/shared_volume** y la carpeta cliente debe ser
la siguiente **/home/ubuntu/videos**

Luego de creada la carpeta **/home/ubuntu/videos** vamos a darle super permisos para no tener problemas.

```shell
sudo chmod -R 777 /home/ubuntu/videos
```
para esto puede hacer uso
del material academico: [Link](https://jpadillaa.hashnode.dev/tutorial-nfs-network-file-system#heading-configuracion-del-cliente-nfs)

Los siguientes pasos levantarán el proyecto api en su instancia:

- Como puedo navegar fuera del path inicial
```shell
cd
```
- Seguir los [Pasos Generales](#pasos-generales-para-instalar-dependecias-en-las-diferentes-instancias-vm)

- Añadir valores de variables globales, usando nano
```shell
sudo nano .env
```
- Al interior del archivo .env complete los valores, tome como referencia el siguiente ejemplo.
```ini
URL_HOST_BASE=<instance-api-ip>:6000
HOST_QUEUE=<instance-queue-ip>
USER_QUEUE=admin
PWD_QUEUE=admin
HOST_PG=<instance-bd-ip>
USER_PG=<usuario-bd>
PWD_PG=<password-bd>
```
- Guarde los cambios y cierre el archivo .env (ctrl+o)(ctrl+x)

```shell
sudo docker compose -f docker-compose-api.yaml up -d
```
- En este punto puede consumir el servicio de SingUp de la documentación [Postman](https://documenter.getpostman.com/view/5528678/2sA3BhctkL), recuerde cambiar el host por la ip de **instance-api**


### Configurar Server Worker

Para configurar el servidor tipo api conectese a la instancia **instance-worker** mediante ssh.

Antes de continuar con los pasos del api, debemos configurar el NFS como cliente.

Recuerdo que la carpeta compartida en el server es la siguiente **/var/nfs/shared_volume** y la carpeta cliente debe ser
la siguiente **/home/ubuntu/videos**

Luego de creada la carpeta **/home/ubuntu/videos** vamos a darle super permisos para no tener problemas.

```shell
sudo chmod -R 777 /home/ubuntu/videos
```
para esto puede hacer uso
del material academico: [Link](https://jpadillaa.hashnode.dev/tutorial-nfs-network-file-system#heading-configuracion-del-cliente-nfs)

Los siguientes pasos levantarán el proyecto worker en su instancia:

- Como puedo navegar fuera del path inicial
```shell
cd
```
- Seguir los [Pasos Generales](#pasos-generales-para-instalar-dependecias-en-las-diferentes-instancias-vm)

- Añadir valores de variables globales, usando nano
```shell
sudo nano .env
```
- Al interior del archivo .env complete los valores, tome como referencia el siguiente ejemplo.
```ini
URL_HOST_BASE=<instance-api-ip>:6000
HOST_QUEUE=<instance-queue-ip>
USER_QUEUE=admin
PWD_QUEUE=admin
HOST_PG=<instance-bd-ip>
USER_PG=<usuario-bd>
PWD_PG=<password-bd>
```
- Guarde los cambios y cierre el archivo .env (ctrl+o)(ctrl+x)

```shell
sudo docker compose -f docker-compose-worker.yaml up -d
```
- En este punto puede consumir cualquier servicio (Probar *Save new Task*!!!) la documentación [Postman](https://documenter.getpostman.com/view/5528678/2sA3BhctkL), recuerde cambiar el host por la ip de **instance-api**


## Despliegue en Nube (Load Balancer, AutoScaling, Buckets ) - Entrega 3

Para este paso ya debe contar con el previo acceso a GCP y la ejecución de los diferentes proyectos, aunque varios de
ellos debemos proceder a apagarlos ya que son reemplazados por técnologías nube, los siguiente proyectos debe ser apagados.

- instance-nfs-server
- instance-api

**Nota** tener presente que las ips de los proyectos cambian a medida que se apagan y prende, con el fin de que actualicen

Ahora vamos a necesitar configurar un Load Balancer y su AutoScaling, y un Cloud Storage (Bucket).

Los recursos asociados al Load Balancer y AutoScaling son los siguientes:

A continuación se copia la receta para la plantilla del api la cual es la que debe quedar asociada a las instancias del
load balancer, es decir no use la plantilla del Lab sino la siguiente.

*Recuerde reemplazar los valores en <>*

```ìnit
gcloud compute instance-templates create template-api \
   --region=us-central1 \
   --network=default \
   --subnet=default \
   --tags=allow-health-check,http-server \
   --machine-type=e2-small \
   --image-family=ubuntu-2004-lts \
   --image-project=ubuntu-os-cloud \
   --labels=goog-ops-agent-policy=v2-x86-template-1-2-0,goog-ec-src=vm_add-gcloud,loggingns=true \
   --service-account=cloud-storage-with-pre-signed@soluciones-cloud-202402.iam.gserviceaccount.com \
   --metadata=startup-script='#!/bin/bash
     sudo curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
     sudo bash add-google-cloud-ops-agent-repo.sh --also-install
     sudo systemctl status google-cloud-ops-agent"*"
     sudo apt-get update
     sudo apt-get install git -y
     sudo apt-get install docker.io -y
     sudo apt-get install docker-compose -y
     cd /home
     sudo git clone https://github.com/cczapatat/desarrollo-soft-nube-misw4204.git
     cd desarrollo-soft-nube-misw4204
     echo -e "URL_HOST_BASE=<PortLoadBalancer>:<Port>" | sudo tee .env-prd
     echo -e "HOST_QUEUE=<QueuePort>" | sudo tee -a .env-prd
     echo -e "USER_QUEUE=admin" | sudo tee -a .env-prd
     echo -e "PWD_QUEUE=admin" | sudo tee -a .env-prd
     echo -e "HOST_PG=<HostDB>" | sudo tee -a .env-prd
     echo -e "USER_PG=postgres" | sudo tee -a .env-prd
     echo -e "API_KEY=<ApiApiKey>" | sudo tee -a .env-prd
     echo -e "TOTAL_THREADS=2" | sudo tee -a .env-prd
     echo -e "PWD_PG=<PasswordBD>" | sudo tee -a .env-prd
     sudo docker-compose -f docker-compose-api.yaml --env-file .env-prd up -d'
```

- [Load Balancer](https://www.cloudskillsboost.google/focuses/12007?parent=catalog)
- [Load Balancer y AutoScaling](https://www.youtube.com/watch?v=gjw1eaRn9U0)

los recursos asociados al Cloud Storage (Bucket.)

- [Cloud Storage](https://youtu.be/9uMiix6S_IE)

**Importante** asigne su nuevo rol o permisos a una cuenta de servicio que use sobre las instancias de load balancer,
de lo contrario el api desplegado no podra hacer uso del bucket