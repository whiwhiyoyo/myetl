
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
    description='Workflow picsum.photo gray',
    schedule_interval=timedelta(days=1),
)

#Variable.set("final_urls_file", "/opt/aaa")


# def image_filename_definition(image_url):
#     return (image_url.replace("https://","")
#             .replace("/","")
#             .replace(".photos","")
#     )

# UGLY should be a trigger by a change event from the bucket
def action_urls_file_collector(urls_filename='picsum_urls'):
    """
    Get metas remotely, from the file where the list of urls is recorded
    Get file 
    Write it locally
    Store it in raw storage
    return its path in raw storage
    """
    from etlqs.actions.actions_urls_file import (get_metas, get_urls_file,
                                         load_urls_file, extract_urls_file)
 
    metas = get_metas(urls_filename)
    # UGLY write the file locally is for debugging during the dev
    local_urls_filename = '/tmp/{}'.format(
        urls_file_definition(filename=metas['name'],
                             last_modified=metas['last_modified'])
    )

    urls_file = extract_urls_file(urls_filename)
    with open(local_urls_filename, 'wb') as f:
        for d in urls_file.stream(32*1024):
            f.write(d)

    load_urls_file(local_urls_filename)
    return local_urls_filename.split('/')[-1]
        


def urls_file_definition(filename='picsum_urls',
                         last_modified=str(datetime.now())):
    return '{}_{}'.format(
        datetime.timestamp(last_modified),
        filename)


t1 = PythonOperator(
    task_id='collect_picsum_urls',
    python_callable=action_urls_file_collector,
    op_kwargs={'urls_filename':'picsum_urls'},
    dag=dag
)




    
    

###### task: get images from picsum  ###########

    

def action_filter(**context):
    """
    Get urls_file from raw store 
    Store the file to a temporary file.
    Clean it with a filter script
    Set a variable with the path of the cleaned file 
    """
    import subprocess
    import shlex
    from etlqs.actions.actions_urls_file import get_urls_file

    urls_filename = context['task_instance'].xcom_pull(
        dag_id= 'dag_picsum', task_ids='collect_picsum_urls')
    print(urls_filename)
    # bucket = 'urlsraw'
    # urls_file = mc.get_object(bucket, urls_filename)
    local_urls_file = '/tmp/{}'.format(urls_filename)
    urls_file = get_urls_file(urls_filename)
    with open(local_urls_file, 'wb') as f:
        for d in urls_file.stream(32*1024):
            f.write(d)

    # UGLY rien a faire la
    final_urls_file = '/tmp/{}_final'.format(urls_filename)
    subprocess.call(shlex.split(
        '/opt/src/filter.sh {} {}'.format(local_urls_file, final_urls_file)))

    # DANGER: Variable est global a l ensemble des dag
    Variable.set("final_urls_file", final_urls_file)

    return datetime.timestamp(datetime.now())
    

filter_task = PythonOperator(
    task_id='filter_task',
    python_callable=action_filter,
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

