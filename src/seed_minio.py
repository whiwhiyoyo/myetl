from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)


mc = Minio('minio:9000',
           access_key='minio',
           secret_key='minio123',
           secure=False)

def create_urls_buckets(buckets=('urls','urlsraw')):
    try:
        for bucket in buckets:
            mc.make_bucket(bucket, location="us-east-1")
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except ResponseError as err:
        raise

def put_picsum_urls_file(bucket='urls', path='/opt/picsum'):
    try:
        mc.fput_object(bucket, 'picsum_urls', path)
    except ResponseError as err:
        print(err)

create_urls_buckets()
put_picsum_urls_file()
