
"""
### Tutorial Documentation
Documentation that goes along with the Airflow tutorial located
[here](https://airflow.apache.org/tutorial.html)
"""
from datetime import timedelta

import airflow
from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.subdag_operator import SubDagOperator
from subdags.picsum import load_subdag 
import os
from datetime import datetime

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(0),
    'email': ['bruantoine@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

dag = DAG(
    'dag_picsum',
    default_args=default_args,
    description='DAG du roudoudou',
    schedule_interval=timedelta(days=1),
)

#Variable.set("final_urls_file", "/opt/aaa")


def image_filename_definition(image_url):
    return (image_url.replace("https://","")
            .replace("/","")
            .replace(".photos","")
    )

# UGLY should be a trigger by a change event from the bucket
def urls_file_collector(bucket='urls',
                  urls_filename='picsum_urls'):
    from minio import Minio
    from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

    # Initialize minioClient with an endpoint and access/secret keys.
    mc = Minio('minio:9000',
               access_key='minio',
               secret_key='minio123',
               secure=False)

    objects = mc.list_objects_v2(bucket, recursive=False)
    for obj in objects:
        print(obj.bucket_name,
              obj.object_name,
              obj.last_modified,
              obj.etag,
              obj.size,
              obj.content_type)
        if obj.object_name == urls_filename:
            #TODO condition of the local existance of the file
            urls_file = mc.get_object(bucket, urls_filename)
            local_urls_filename = '/tmp/{}'.format(
                urls_file_definition(obj.object_name, obj.last_modified))
            with open(local_urls_filename, 'wb') as f:
                for d in urls_file.stream(32*1024):
                    f.write(d)

            # TODO condition of th remote existqnce of the file
            try:
                with open(local_urls_filename, 'rb') as f:
                    file_stat = os.stat(local_urls_filename)
                    print(mc.put_object('urlsraw',
                                        local_urls_filename.split('/')[-1],
                                        f, file_stat.st_size))
            except ResponseError as err:
                print(err)
            return local_urls_filename.split('/')[-1]
        
    #we shouldn't be here
    print("{} is not found in the bucket {}".format(urls_filename, bucket))
    # TODO write a specific exception instead of returning None
    return None


def urls_file_definition(filename='picsum_urls',
                         last_modified=str(datetime.now())):
    return '{}_{}'.format(datetime.timestamp(last_modified),
                          filename)


t1 = PythonOperator(
    task_id='collect_picsum_urls',
    python_callable=urls_file_collector,
    op_kwargs={'bucket':'urls',
               'urls_filename':'picsum_urls'},
    dag=dag
)



##### task: encode and put image on MongoDB ##############
def encoding64(**kwargs):
    """
    get a single image from Raw Data Store, encode it, 
    and store it into the materialized view
    """
    from pymongo import MongoClient
    import gridfs
    import base64
    # Import MinIO library.
    from minio import Minio
    from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

    # Initialize minioClient with an endpoint and access/secret keys.
    mc = Minio('minio:9000',
                    access_key='minio',
                    secret_key='minio123',
                    secure=False)

    # access our image collection
    client = MongoClient('mongodb', 27017)
    db = client['picsum']
    collection = db['grayCollection']

    fs = gridfs.GridFS(db)


    bucket_raw = 'picsumraw'
    file_id = kwargs['file_id']
    #directory = kwargs['directory']
    task_id='wget_'+file_id
    print(file_id)
    print(task_id)
    print(kwargs)
    yoyowhiwhi = kwargs['ti'].xcom_pull(
        dag_id='dag_picsum.load_tasks',task_ids='wget_picsum104105')
    print(yoyowhiwhi)
    destination = kwargs['ti'].xcom_pull(
        key='destination',
        task_ids='wget_'+file_id,
        dag_id='dag_picsum.load_tasks')
    print(destination)
    source = '{}/{}'.format(destination, file_id)
    print("whiwhiwhi")
    print(file_id)
    print(source)
    

    
    # image_filename = kwargs['task_instance'].xcom_pull(
    #     task_ids=kwargs['parent_task_id'])
    # print(image_filename)



    image_file = mc.get_object(bucket_raw, source)
    encoded_string = base64.b64encode(image_file.read())
    # with open("images_raw/picsum154155", "rb") as image_file:
    #     encoded_string = base64.b64encode(image_file.read())

    # store the image
    imageID= fs.put(encoded_string)

    # create our image meta data
    meta = {
        'imageID': imageID,
        'name': file_id
    }

    # insert the meta data
    collection.insert_one(meta)

    
    

###### task: get images from picsum  ###########

    

def get_urls_file_raw(**context): 
    import subprocess
    import shlex
    # Import MinIO library.
    from minio import Minio
    from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

    # Initialize minioClient with an endpoint and access/secret keys.
    mc = Minio('minio:9000',
                    access_key='minio',
                    secret_key='minio123',
                    secure=False)


    urls_filename = context['task_instance'].xcom_pull(
        dag_id= 'dag_picsum', task_ids='collect_picsum_urls')
    print(urls_filename)
    bucket = 'urlsraw'
    urls_file = mc.get_object(bucket, urls_filename)
    local_urls_file = '/tmp/{}'.format(urls_filename)
    with open(local_urls_file, 'wb') as f:
        for d in urls_file.stream(32*1024):
            f.write(d)

    # UGLY rien a faire la
    final_urls_file = '/tmp/{}_final'.format(urls_filename)
    # DANGER: Variable est global a l ensemble des dag
    Variable.set("final_urls_file", final_urls_file)
    subprocess.call(shlex.split(
        '/opt/filter.sh {} {}'.format(local_urls_file, final_urls_file)))

    return datetime.timestamp(datetime.now())
    

filter_task = PythonOperator(
    task_id='filter_task',
    python_callable=get_urls_file_raw,
    provide_context=True,
    dag=dag
)

t1 >> filter_task



load_tasks = SubDagOperator(
    task_id='load_tasks',
    subdag=load_subdag('dag_picsum', 'load_tasks',
                        default_args),
    default_args=default_args,
    dag=dag
)

filter_task >> load_tasks

# datetime.timestamp(datetime.now())




