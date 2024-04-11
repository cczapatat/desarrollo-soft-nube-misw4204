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

### Delete old containers

```shell
docker rm queue_nube postgres_nube worker_nube api_nube
```

### Delete old images

```shell
docker rmi desarrollo-soft-nube-misw4204-worker desarrollo-soft-nube-misw4204-api
```

### Delete old volumes

```shell
docker volume rm desarrollo-soft-nube-misw4204_shared-volume
```

### Run All Apps

```shell
docker-compose -f docker-compose.yaml up
```

