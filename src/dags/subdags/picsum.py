from airflow import DAG
from airflow.models import Variable

from airflow.operators.python_operator import PythonOperator



def image_filename_definition(image_url):
    return (image_url.replace("https://","")
            .replace("/","")
            .replace(".photos","")
    )

def coucou():
    print("coucou")
#def picsum_collector(image_url, bucket_raw='yoyo3'):
def picsum_collector(**kwargs):
    from etlqs.actions import action_wget, action_store_mongodb, action_encoding64


    image_url = kwargs['image_url']
    file_id = image_filename_definition(image_url)
    prefix = kwargs['task_instance'].xcom_pull(
        dag_id= 'dag_picsum', task_ids='filter_task')
    directory = kwargs['directory']
   
    # destination = ''
    # print("yoyoyoyo")
    # print(image_url)
    # print(directory)
    # file_id = kwargs['file_id']
    

    

    image_file  = action_wget(image_url, file_id, prefix, directory)
    action_store_mongodb(action_encoding64(image_file), file_id)



def load_subdag(parent_dag_name, child_dag_name, args):
    
    dag_subdag = DAG(
        dag_id='{0}.{1}'.format(parent_dag_name, child_dag_name),
        default_args=args,
        schedule_interval="@daily",
    )
    print("glouglou")
    #print(prefix)
    with dag_subdag:

        final_urls_file = Variable.get('final_urls_file')     
        for line in tuple(open(final_urls_file, 'r')):
            file_id = image_filename_definition(line)
            directory = (final_urls_file.split('/')[-1]
                                        .replace('_urls_final',''))
            wget_task = PythonOperator(
                task_id='wget_' + file_id,
                python_callable=picsum_collector,
                op_kwargs={'image_url': line,
                           'directory': directory},
                provide_context=True,
                dag=dag_subdag
            )

            # encoding_task = PythonOperator(
            #     task_id='encode_' + file_id,
            #     python_callable=encoding64,
            #     op_kwargs={'file_id': file_id},
            #     provide_context=True,
            #     dag=dag_subdag
            # )       

            # wget_task >> encoding_task

    return dag_subdag

