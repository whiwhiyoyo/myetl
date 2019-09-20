# Demande Arnaud jeansen
## Contexte
### Faire un ETL capable d'ingérer de la donnée streamée sans avoir de composantes bloquantes. 
###  Data d'entrée : queue d'urls (chaque url avec le format https://picsum.photos/[width]/[height]). Ce fichier contient des erreurs, et des doublons.
## Spec
### Fonctionnelles en fin d'ETL
#### Data store contenant :
l'image en base 64 transformée en niveaux de gris 
des metadonnées, dont voici des exemples non exhaustifs : date d'insertion, width, height, source
une garantie d'unicité de l'image ainsi que la possibilité de diagnostiquer des corruptions éventuelles
#### Bonus:
spécifier des moyens d'accès aux images stockées
monitoring des différents process intervenant dans l'ETL, par ex : nombre d'images en cours, erreur etc
### Caractéristiques techniques
Scalabilité volumétrique
Souplesse vis à vis d'ajouts de fonctionnalités, ex: nouvelles transformations autre que niveaux de gris
Asynchronicité
## Technologies conseillées / appréciées
docker
python3
mongo
Airflow, Luigi, Prefect, Celery
## Resultat attendu
Un design d'architecture
Le code d'une ou deux briques au choix parmi le design présenté
    


# ETL QuickSign

## Buisness Cases
Capture pictures from a website, storing them in gray. Catalogs of pictures are continiously send to the system. A catalog of these pictures is a list of urls. Each urls is a record in a file.
The desired solution is an ETL with no bloquant, able to capture stream datas. This ETL need to be souple enough for new transforms to be set up, and aware for scalability in term of number of pictures. 
## System Requirements
### Use Cases


| Use Case                                 | Description                                                                                                                                   |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| UC-1: Monitoronline services             | Operations staff can monitor the current state of services and IT infrastructur through a real-time operational dashboard                     |
| UC-2: Troubleshoot online service issues | Ops, SRE, PO can do troubleshooting and root-cause analysis on the latest collected logs by searching log patterns and filtering log messages |
| UC-3: Provide management reports         | Product managers can see historical information through reports such product usage, SLA violations, QA                                        |
| UC-4: Support Data Acces                 |                                                                                                                                               |
| UC-5: Integrating Data                   | integrating data from multiple sources                                                                                                        |
| UC-6: Aggregating Data                   | Pre-aggregating data to speed up queries                                                                                                      |
|                                          |                                                                                                                                               |


alerting, login information and many more are future requirements.

### Scenarios


| Scenario | Quality Attribute | Description                                                                                                                                      | Associated UC |
|----------|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|--------------:|
| SC-1     | Performance       | The system shall provide real-time search queries for emergency troubelshooting with < 10 sec query execution time, for the last 2 weeks of data |          UC-2 |
| SC-2     | Scalability       | The system shall store raw data for the last 2 weeks available for emergency troubelshooting                                                     |          UC-2 |
| SC-3     | Scalability       | The system shall store raw data for the last 60 days (~1TB/day, ~60TB in total)                                                                  |          UC-4 |
| SC-4     | Extensibility     | The system shall support adding new data sources by just updating a configuration, with no interruption of ongoing data collection               |        UC-1,2 |
| SC-5     | Availability      | The system shall continue operating with no downtime if any single node or component fails.                                                      |       All UCs |
| SC-6     | Deployability     | The system deployment procedure shall be fully automated and support a number of environments: dev, test, prod                                   |       All UCs |
| SC-7     | Reproducibility   | The system procedures should be reproductible during the retention time                                                                          |    UC-5, UC-6 |
|          |                   |                                                                                                                                                  |               |


### Contraintes
resilient, maintenable, scalable


| Constraint | Description                                                                                            |
|------------|--------------------------------------------------------------------------------------------------------|
| CON-1      | The system shall compased primarily of known tecvhnologies (docker, python, mongo, airflow, celery...) |
| CON-2      | The system shall support local deployment and cluster deployment                                       |
|            |                                                                                                        |


### Architectures
Data should be immutable
### Security
TODO
## Design
### architecture de reference
### Selections des technologies
1. Distributed Task Queue

2. Redis or RabbitMQ
3. Airflow : a platform to programmatically author, schedule and monitor workflows
Scalable executor and scheduler, rich web UI for monitoring and logs
Scheduler a single point of failure.
### patterns
1. no pipelining (ant-pattern)
no pipelining between tasks. Airflow is designed to run on multiple workers. each task must read from and write to systems accessible to all workers (DBs, remote FS, APIs).
airflow workflow are not able to handle big data processing pipelines 
Spark jobs may be launched (in client mode to capture logs, Spark 2.4.0), or use pandas pipeline in one single task.
2. immutability
Data should be immutable for transformations to be reproductible.
3. batch processing
no strem processing. triggers from eventto simulate real time. could be difficult to simulate windowing.
## ETL Interfaces
### Concepts 
Garantir la souplesse fonctionnelle. Fournir une interface indépendante de la solution technique
### Actions
chargement, agrégation et intégration de programmes custom en python
-	Load : intégrer la donnée brute selon le mapping référencé des attributs en entrée et en sortie 
-	Agregate : transformer une table du DWH vers la même table, une autre table, ou vers un agrégat, tout en incluant des jointures



Lors de la création d’une action, il est impératif de préciser les caractéristiques de l’action : 
-	Source : choisir la source de données
-	Destination : objet dans lequel seront insérées les données
-	Mapping : au centre de l’écran se trouve un écran de correspondance entre les attributs de la source de donnée, et la destination pouvant être une table en prim ou en mart.

### Workflows
structuration d'enchainement d'actions et possibilité de le lancer manuellement
parallelisme (stage) et enchainement sequentiel
-	Un workflow constitue une succession d’actions réparties dans des stages
-	Les stages sont exécutés en étapes successives
-	Les actions au sein d’un stage sont exécutées en parallèle
-	Il est ainsi possible de personnaliser tous les traitements de data
-	Lorsqu’un workflow est lancé l’ accès aux logs est ouvert

branches, tributaries and deltas
### Plans
automatiser le chargement des données, permettre du real-time 
start workflow on a schedule or trigger a workflow by an event
Une planification des workflows permet d’automatiser la récupération des données et les traitements définis. À savoir :
Les workflows peuvent être lancés manuellement ou planifiés
-	Le plan de lancement automatique est défini au niveau de chaque workflow
-	le nombre de workers affectés à un workflow peut être défini, ce qui permet de gérer les gros volumes via une scalabilité horizontale

lancement manuel, recurences, hooks (airflow provide ftp hooks)
## technical solution
No Celery: Queue or Cluster Redis to manage and bottelneck
## Building Blocks
### 
### Workflow Monitor
for Product owners
airflow webserver
1. Adhoc Queries
2. DAG's Dashboard


### Workflow Scheduler
airflow scheduler


### Real-time Monitor
ELK



### Analytic System
CDC from Airflow backend
derived datas, Schema en etoile




## Implementations
### Action Load
Recuperation & Sauvegarde du fichier urls
### Action BluePrint
shell script
UC 1, 
1. pros: synthetique, easy reading, performance
2. cons: no inverted function (collect errors to past mistakes), 
### construction du DAG
Actions are tasks instances - represents an execution of a node in the DAG
Plan define dag runs with a cron-like interface.  
### Action get & transformation
wget
store raw in minio
transform in gray
store in minio
fact in analytics
logs in real-time layer
## Deployment
### continuous delivery

###  Local deploiment(Dev env)
#### docker-compose
1. airflow docker (initdb, scheduler, webserver, )
2. minio docker
3. mongodb docker
#### commands
airflow run ${dag_id} ${task_id} ${execution_date}
### cluster deployment(Prod env)
#### Updates DAGs
1. helm charts
helm upgrade airflow-pod charts/airflow --set tag=v0.0.2
1.1. helm upgrade updates the Deployments state in K8S
1.2. K8s gracefully terminates the webserver and scheduler and reboots pods with updated image tag
1.3. task pods continue running to completion
1.4. negligible amount of downtime
1.5. can be automated via CI/CD tooling






#### Orchestrator: K8S
1. DAG in one PV (ReadWriteMany mode) shared for all Pods (scheduler, web server, workers). Need Ceph or Gluster (so reserved for high instances of Airflow)
2. CI/CD pipeline update DAGs (sync by everly relevant components)
3. Logs from web server, scheduler and Celery workers on minio
4. Airflow workers managed by Kubernetes pod operator (deployments and rollbacks). Airflow focus on scheduling tasks.
5. Dynamic Ressource Allocation with Kubernetes Executor
6. Ingress controllers to expose tp the outside world. Ingress is connected to the Auth Server. Proxy to the airflow webserver. the ingress send a JWT in header
7. a SecurityManager plugin read JWT from Auth server and create/update user/role
#### Scalability
0.1. Celery Executor: Distributed Task Queeus
Airflow scheduler publish tasks on Redis/Rabbit 
Airflow Workers get tasks from Redis/Rabbit
1. Kubernetes Executor
1.1. scale to zero
1.2. a new pod for each tasks
1.2. no QUeues or additional application infrastructure to manage
1.3. Scheduler subscribes to Kubernetes event stream
1.4 need a remote logging backend plugin (S3, Elasticsearch). 
airflow aebserver requests object when log viewer is opened. Log files uploaded after each task before pod terminates
Elasticsearch is seed by fluentd pod. airflow webserver requests to ES Client Nodes. Kibana for deeper log analysis
2. Number of worker: K8S Horizontal Pod Autoscaller
3. worker size: K8S resource requests/limits
#### HA
1. One POD with UI One Pod with scheduler
2. executor config in airflow.cfg
3. FaultTlerance: resourceVersion to re create state
4. DAG propagation
5. Airflow scheduler is a single point of failure
use an external database for task states. But self-healing is not garanteed after a pod reboot.
But scheduler detects inconsistancies in database and automaticly relaunchs tasks on failure.
#### metrics: Prometheus/Grafana
a pull based metrics system, auto scrape with kunerbnetes annotations
airflow natively exports statsd metrics, Statsd Exporter as a bridge to Prometheus
one Statd exporter pod for each airflow pod
1. airflow-exporter plug-in
2. metrics available by airflow: tasks and DAG status, DAG run duration
#### node provisioning: Terraform/Ansible



future:
learning curve with those tools
1. emphasis on datat quality
Data profiling
Datat validation
