# MISW-4204-Proyecto-MISW4204-202402-

## # MISW-4204-Proyecto-MISW4204-202402-GrupoXX

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
docker rm queue_nube postgres_nube worker_nube
```

### Delete old images

```shell
docker rmi 
```

### Run All Apps

```shell
docker-compose -f docker-compose.yaml up
```

