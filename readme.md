## How to open the program:
```bash

    cd path\to\inventory_project

    docker-compose up
    docker-compose down

    open the index.html file
```


## Check Database Postgre:
```bash

    docker exec -it inventory_postgres psql -U admin -d inventory_db
    \dt
    SELECT * FROM inventory_items;
    \q
```


## Check Logs MongoDB:
```bash

    docker exec -it inventory_mongo mongosh
    use inventory_logs
    db.api_logs.find().pretty()
    exit
```


View the Database in easier way: http://localhost:8000/docs
