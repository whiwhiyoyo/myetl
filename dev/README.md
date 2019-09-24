## Launch
1. docker-compose up
2. docker exec -it -w /opt airflow /bin/bash
3. python seed_minio.py
4. airflow scheduler &
5. go to airflow UI http://localhost:8080/admin/
6. enjoy with your code editor

## Troubleshooting
### XCom
We are iterating explicitly over our previous tasks contained in the SubDAG that's mean that we have to know the structure of the whole DAG and the name of its tasks when we want to pull messages from certain tasks. Heuristics like "retrieve all the messages from the previous n tasks" seems to be not possible to implement.

Note that we had also to explicitly pass the name of the SubDAG since we want to pull from tasks contained there. The dag_idparam is not required if the 2 comunicating tasks belong to the same "DAG level".
### Space for sh script