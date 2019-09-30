# Demande Arnaud jeansen ##########
## Contexte
* Faire un ETL capable d'ingérer de la donnée streamée sans avoir de composantes bloquantes. 
* Data d'entrée : queue d'urls (chaque url avec le format https://picsum.photos/[width]/[height]). Ce fichier contient des erreurs, et des doublons.
## Spec
### Fonctionnelles en fin d'ETL
#### Data store contenant :
l'image en base 64 transformée en niveaux de gris 
des metadonnées, dont voici des exemples non exhaustifs : date d'insertion, width, height, source
une garantie d'unicité de l'image ainsi que la possibilité de diagnostiquer des corruptions éventuelles

#### Bonus :
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
    
-------------------------------------------------------------------------------

# ETL QuickSign ###########
	
## Buisness Cases
Capture pictures from a website, storing them in gray. Catalogs of pictures are continiously send to the system. A catalog of these pictures is a list of urls. Each urls is a record in a file.
The desired solution is an ETL with no bottlenecks and single points of failure, able to capture stream datas. This ETL need to be flexible enough for new transforms to be set up, and aware for scalability in term of number of pictures. 

## System Requirements

### Use Cases


| Use Case                                 | Description                                                                                                                                   |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| UC-1: Monitor online services	           | Operations staff can monitor the current state of services and IT infrastructur through a real-time operational dashboard                     |
| UC-2: Troubleshoot online service issues | Ops, SRE, PO can do troubleshooting and root-cause analysis on the latest collected logs by searching log patterns and filtering log messages |
| UC-3: Provide management reports         | Product managers can see historical information through reports such product usage, SLA violations, QA                                        |
| UC-4: Support Data Acces                 | Extracted pictures need to be easily acces by queries                                                                                         |
| UC-5: Integrating Data                   | integrating data from a single web source (the file containing the list of urls)                                                              |
| UC-6: Aggregating Data                   | Pre-aggregating data to speed up queries                                                                                                      |
|                                          |                                                                                                                                               |


alerting, login information and many more are future requirements not yet considered.

### Scenarios

| Scenario | Quality Attribute | Description                                                                                                                                                                                     | Associated UC |
|----------|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------:|
| SC-1     | Performance       | The system shall provide real-time search queries for emergency troubelshooting with less than [s][search_latency] sec query execution time, for the last [w][retention_in_weeks] weeks of data |          UC-2 |
| SC-2     | Scalability       | The system shall store raw data for the last [w][retention_in_weeks] weeks available for emergency troubelshooting                                                                              |          UC-2 |
| SC-3     | Scalability       | The system shall store raw data for the last [d][retrention_in_days] days (~[vd][vol_per_day]TB/day, ~[vt][vol_total]TB in total)                                                               |          UC-4 |
| SC-4     | Extensibility     | The system shall support adding new data sources by just updating a configuration, with no interruption of ongoing data collection                                                              |        UC-1,2 |
| SC-5     | Availability      | The system shall continue operating with no downtime if any single node or component fails.                                                                                                     |       All UCs |
| SC-6     | Deployability     | The system deployment procedure shall be fully automated and support a number of environments: dev, int, prod                                                                                   |       All UCs |
| SC-7     | Idempotence       | The system procedures should be reproductible during the retention time                                                                                                                         |    UC-5, UC-6 |
|          |                   |                                                                                                                                                                                                 |               |

[search_latency]: 10
[retention_in_weeks]: 2
[retention_in_days]: 60
[vol_per_day]: 1
[vol_total]: 60

### Constraints
resilient, maintenable, scalable


| Constraint | Description                                                                                            |
|------------|--------------------------------------------------------------------------------------------------------|
| CON-1      | The system shall comparsed primarily of known technologies (docker, python, mongo, airflow, celery...) |
| CON-2      | The system shall support local deployment and cluster deployment                                       |
|            |                                                                                                        |


### Architectural concerns


| Concerns | Description                                                       |
|----------|-------------------------------------------------------------------|
| CRN-1    | Establishing an initial overall structure as this is a new system |
| CRN-2    | Leverage the knowledge on scheduler open source projects          |


### Security
**TODO**
1. connection with IAM
2. network segmentation
3. roles and rights

## Design

### Reference Architecture

| Design decisions                                                                            | Rationale                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Build the ETL as an insstance of the Lambda Architecture                                    | Lambda architecture splits the processing of a data stream into two streams: the __speed layer__ which support access to real-time data (**TODO** UC-x), and a layer that groups the __batch__ and __serving layers__, which access to historical data (**TODO** UC-x). a 4th layer is considered t process all data generated by the processing.<br> Immutability in this case means tha the data is not updated or deleted when it s collected. It can be only appended. As all data is collected, no data can be lost nd a machine or human error can be tolerated. In our case, primary datas (ie: the pictures from picsum.photos) are processed by the batch layer. Secondary datas (ie: generated by the processing itself) are processed by the monitor layer.<br>1. The batch layer acts as a landing zone that corresponds to the master dataset element (as an immutable, append-only set of raw data), and also precomputes that will be use by the batch views.<br>2. The serving layer contains precalculated and aggregates views ptimized for querying with low latency.<br>3. The monitor layer processes and provides access to data generated by the processing (logs, indicators, timestamp)<br>4. All data in the system is available for querying, whether it is historical or recent. |
| Use fault tolerance and no single point of failure principle for all elements in the system | Fault tolerance has become a standard for long running processing. We will need to make sur, in all design and deployment  point of view, that all candidate technologies will support fault-tolerant configurations and adhering to the __no single point of failure__ principle.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

#### lambda architecture blocks
1. Data Stream: Collector for all data to be processed 
2. Batch layer: Master Data (Raw Data Storage) + Precomputing (Scheduler, programmatic paradigm, monitoring)
3. Serving layer: Batch views
4. Speed layer: Real-time procesing ( __future requirements__)
5. Monitor layer: Real-time views (Dashboard, Distributed search engine, Visualization tool, monitoring activites)

### Selection of technologies

| Design decisions                                                    | Rationale                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|                                                                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| the Data Collector: Kafka Connect                                   | Data Collector is a technology family that collects, aggregates, and transfer data for later use. The destination is the Raw Data Storage. Kafka Connect can run either as a standalone process for running jobs on a single machine, or as a distributed, scalable, fault tolerant service. This allows it to scale down to development, testing, and small production deployments with a low barrier to entry and low operational overhead, and to scale up to support a large data pipeline.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| the Raw Data Storage: MinIO                                         | Data in the Raw Data Storage element must be immutable. New data should not modufy existing data, but just be appended to the dataset. In such a block store, each process will be associated by a specific directory. As S3, MinIO is able to be partitionned through different nodes (scale principle **TODO**)<br>**Alternatives:**<br>1) Use HDFS (Distributed File System family). was designed to support this type of usage scenario for large data sets. A bit overkill here<br>2) NoSQL DataBase like Cassandra                                                                                                                                                                                                                                                                                                                                                                                                                        |
| the Interactive Query Engine for Batch Views: MongoDB               | The Batch Views element can be implemented with the Materialized View pattern. because of the GridFS storing option, large files are chunked into numbers of defined size blocks. For our purpose, pictures are not limited by the well-known 16MB size document limitation in MongoDB.<br>**Alternatives:**<br>1) Impala offers an ODBC interface for connectivity with tools, known for its competitive performance.<br>2) Apache Hive: speed of queries still slower compared to other alternatives. The choice of Hive depends on the choice of HDFS for the storage.<br>3) Spark SQL: The mainstream technologie but overkill here.<br> 4) Analytics RDBMS ....__rationale is let to the reader__                                                                                                                                                                                                                                          |
| Distributed Search Engine for real-time views: ELK                  | The Real-time views element is responsible for full-text search over recent logs and for feeding an operational dashboard with real-time monitoring data. ElasticSearch is a technology that serves just such purposes. Kibana provides interactive dashboard for the visualization tool elemant. It is a relatively simple dashboard without role-based security( as I know). It satisfies **TODO** UC and QA.<br>**Alternatives:**<br>1) Splunk: provides indexing and visualization capabilities (better than ELK). However it is not an open source solution.<br>2) analytic RDBMS: Somme DB provide full-text search capabilities (e.g. Postgres with GiST index). however they are less desirable from extensibility and maintenance.<br>3) Distributed File System and Interactive Query Engine: this approach works well for batch historical data; however, the latency of storing and processing will be too high for real-time data. |
| the Data Processing Framework for the precomputing element: Airflow | A platform to programmatically author, schedule and monitor workflows. Scalable executors, rich web UI for monitoring and logs. The scheduler a single point of failure, but seems stateless; it can restart tasks after reboot (can be enough with an orchestrator). The main reason id to write python scripts easy to test and maintain.<br>**Alternatives:**<br>1) Oozi + Hadoop: the old overkill manner. Require substantial knowledge of low-level primitives (e.g. for writing MapReduce tasks)<br>2) Hive or Spark: provide a SQL-like language, could leverage the skills of data warehousing designers when writing data transformation scripts. Depends of the choice of HDFS (instead of minIO).                                                                                                                                                                                                                                   |
| DataBase for monitoring the batch processes: MariaDB                | Airflow scheduler use a backend to store the state of each activites (tasks and dag). Airflow webserver uses this backend to provide monitoring sceens. MariaDB is a robust DBMS with a CDC (until the release 2018) feature. The Change Data Capture store all changes in a separate base (a column base DB is proposed), to provide analytic queries. transfering data in a secondary base allow a low retention in the main base for better performance<br>**Alternatives:**<br>1)Postgres should be considered for scalability. It is overkill in case we use a secondary base for historical datas.                                                                                                                                                                                                                                                                                                                                        |
| metrics: Prometheus/Grafana                                         | a pull based metrics system, auto scrape with kunerbnetes annotations                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|                                                                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |




### patterns and anti-patterns used
1. no pipelining (anti-pattern)
no pipelining between tasks. Airflow is designed to run on multiple workers. each task must read from and write to systems accessible to all workers (DBs, remote FS, APIs).
airflow workflow are not able to handle big data processing pipelines 
Spark jobs may be launched (in client mode to capture logs, Spark 2.4.0), or use pandas pipeline in one single task.
2. immutability
Data should be immutable for transformations to be reproductible.
3. batch processing/no stream processing
no strem processing. triggers from eventto simulate real time. could be difficult to simulate windowing.
4. Materialized View pattern.
Data are stored in a form that is ready for querying. a view is updated after each batch process. Datas inside a view are not immutable.
5. Change Data Capture
6. orchestrator instead of standalone cluster: Kubernetes esecutor instead of Celery executors. CeleryExecutor is one of the ways you can scale out the number of workers.

## ETL Interfaces

### Concepts 
This part is to provide an interface independent of the technical solution and guarantee functional flexibility.
Functional concepts need to be find separately from technical concepts proposed by frameworks and tools. UI interface presents functional ressources, a transformation engine composes with these ressources to generate running scripts for the chosing technical tools.

### Ressources

| Ressource | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | technical derivation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|           |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Action    | an action has the finest granularity among all the notions of the ETL functionnalities. It describes an operation on the data: loading,aggregation, backup, filtering and so on.                                                                                                                                                                                                                                                                                                                                                                                                        | one action is contained in one Airflow task. One single task may be generated by several actions.                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Workflow  | sequence of actions and parallel execution of actions. A stage is a ressource containing actions executing in parallel. Sequence of action is described by a sequence of stages.<br>1) A workflow is a succession of actions distributed in stages<br>2) stages are executed successively.<br>actions within a single stage are run in parallel.<br> workflows are graphs designed by branches, tributaries and deltas. Operations need to have the same interface to pipe a sequence of actions. It could be a dataframe for structured manner, a set of files for unstructured manner | a single workflow generate a single main dag. It may generate several subdags too. A workflow generates also tasks. depend on which operation the actions in a workflow are, tasks may contained several actions. The principe of stage is described in Airflow by the operations of upstream and downstream. these operations describe the sequence of tasks. Tasks are not able to pipe each others: data can't travel through tasks (except few key/values: XCom). So actions coupled need to be often in the same task. |
| Plan      | Describe how workflows are handled. start a workflow on a schedule or trigger it by an event. Workflow planning automates data retrieval and defined processes.                                                                                                                                                                                                                                                                                                                                                                                                                         | a plan describe the __start_date__, also __trigger_rule__, __the retry_delay__ fields in the args of dags.                                                                                                                                                                                                                                                                                                                                                                                                                 |


## Building Blocks
**TODO**
### dsq

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
**TODO**

### Action Load
Input: 

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
3 environnements are disposals for the CI:
1. dev envs: local deployments for back-end, front end, dev ops developpements 
2. int env: all blocks without HA considerations
3. prod and pre-prod env: HA, Scale and security concerns

###  Local deployment(Dev and int env)

#### docker-compose dev
1. airflow (initdb, scheduler, webserver)
2. minio
3. mongodb

#### docker-compose int
1. airflow scheduler
2. airflow webserver
3. minio
4. mongodb
5. mariadb
6. adminer

### cluster deployment(Prod env)

#### cluster provisionning

| Concern    | provisionning method                                     |
|------------|----------------------------------------------------------|
| nodes      | Terraform generalized for On-premise and cloud providers |
| Kubernetes | Ansible script to install components (etcd, KubeDNS...)  |
|            |                                                          |

#### Airflow


| Concern          | Strategie                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Orchestrator     | 1) distinct Pods for each Airflow components (scheduler, webserver, worker)<br>2) One POD with webserver, One Pod with scheduler.<br>3) executor config in airflow.cfg <br>4) Airflow workers managed by Kubernetes pod operator (deployments). Airflow focus on scheduling tasks.<br>5. Dynamic Ressource Allocation with Kubernetes Executor<br>6. Ingress controllers to expose tp the outside world. Ingress is connected to the Auth Server. Proxy to the airflow webserver. the ingress send a JWT in header |
| Pod Deployment   | 1) use helm charts.<br>2) helm upgrade updates the Deployments state in K8S.<br>3) K8s gracefully terminates the webserver and scheduler and reboots pods with updated image tag.<br>4) task pods continue running to completion.<br>5) negligible amount of downtime.<br>6) can be automated via CI/CD tooling                                                                                                                                                                                                    |
| DAG Deployment   | 1) DAG in one PV (ReadWriteMany mode) shared for all Pods (scheduler, web server, workers). Need Ceph or Gluster (so reserved for high instances of Airflow).<br>2) CI/CD pipeline update DAGs (sync by everly relevant components).                                                                                                                                                                                                                                                                               |
| Network Policies | 1) webserver:<br>IN: Scheduler<br>OUT: ES, MariaDB<br>2)scheduler:<br>IN: webserver<br>OUT: webserver, ES, MariaDB<br>worker:<br>IN: <br>OUT: ES                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Scalability      | 1) implicit use of Kubernetes Executor:<br>* scale to zero<br>* a new pod for each task<br>* no Queues or additional application infrastructure to manage<br>* Scheduler subscribes to Kubernetes event stream<br>* need a remote logging backend plugin (S3, Elasticsearch).<br>2. Number of worker: K8S Horizontal Pod Autoscaller<br>3. worker size: K8S resource requests/limits                                                                                                                               |
| Logs             | 1) airflow webserver requests object when log viewer is opened.<br>2) Log files uploaded after each task before pod terminates.<br>3) Elasticsearch is seed by fluentd pod.<br>4)airflow webserver requests to ES Client Nodes.<br>5)Kibana for deeper log analysis                                                                                                                                                                                                                                                |
| HA               | 1) horizontal scale for airflow webserver by the number of replicats<br>2) Airflow scheduler is a single point of failure. use an external database for task states. self-healing is not garanteed after a pod reboot. But scheduler detects inconsistancies in database and automaticly relaunchs tasks on failure.                                                                                                                                                                                               |
| metrics          | airflow natively exports statsd metrics, Statsd Exporter as a bridge to Prometheus. one Statd exporter pod for each airflow pod.<br>1) airflow-exporter plug-in<br>2) metrics available by airflow: tasks and DAG status, DAG run duration                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |



#### Scalability
0.1. Celery Executor: Distributed Task Queeus
Airflow scheduler publish tasks on Redis/Rabbit 
Airflow Workers get tasks from Redis/Rabbit
 
 1. Distributed Task Queue
2. Redis or RabbitMQ
3. Airflow : .



future:
learning curve with those tools
1. emphasis on datat quality
Data profiling
Datat validation




In some situations, storing large files may be more efficient in a MongoDB database than on a system-level filesystem.

    If your filesystem limits the number of files in a directory, you can use GridFS to store as many files as needed.
    When you want to access information from portions of large files without having to load whole files into memory, you can use GridFS to recall sections of files without reading the entire file into memory.
    When you want to keep your files and metadata automatically synced and deployed across a number of systems and facilities, you can use GridFS. When using geographically distributed replica sets, MongoDB can distribute files and their metadata automatically to a number of mongod instances and facilities.

Do not use GridFS if you need to update the content of the entire file atomically. As an alternative you can store multiple versions of each file and specify the current version of the file in the metadata. You can update the metadata field that indicates “latest” status in an atomic update after uploading the new version of the file, and later remove previous versions if needed.

Furthermore, if your files are all smaller than the 16 MB BSON Document Size limit, consider storing each file in a single document instead of using GridFS. You may use the BinData data type to store the binary data. See your drivers documentation for details on using BinData.
