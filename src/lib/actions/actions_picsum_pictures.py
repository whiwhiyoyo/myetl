


BUCKET_RAW='picsumraw'

def image_filename_definition(image_url):
    return (image_url.replace("https://","")
            .replace("/","")
            .replace(".photos","")
    )

def action_wget(image_url, prefix, directory, bucket_raw=BUCKET_RAW):

    file_id = image_filename_definition(image_url)
    
    def get_picture_to_local(image_url):
        import requests
        import os
        
        tmp_images_dir = '/tmp/{}_image'.format(prefix)
        if not os.path.isdir(tmp_images_dir):
            os.mkdir(tmp_images_dir)
        # else:
        #     import shutil
        #     shutil.rmtree(tmp_images_dir) 
        local_image_filename = '{}/{}'.format(
            tmp_images_dir,
            file_id
        )

        r = requests.get(image_url, allow_redirects=True)
    
        with open(local_image_filename, 'wb') as f:
            f.write(r.content)
        
        print(local_image_filename)
        return local_image_filename


    def put_picture_to_raw_storage(local_image_filename):
        # Import MinIO library.
        from minio import Minio
        from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                     BucketAlreadyExists)

        # Initialize minioClient with an endpoint and access/secret keys.
        mc = Minio('minio:9000',
                access_key='minio',
                secret_key='minio123',
                secure=False)
        

        for bucket in mc.list_buckets():
            print(bucket)

        # Make a bucket with the make_bucket API call.
        try:
            mc.make_bucket(bucket_raw, location="us-east-1")
        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            raise
        
        dire = '{}/{}'.format(prefix, directory)
        destination = '{}/{}'.format(dire, local_image_filename.split('/')[-1])
        try:
            mc.fput_object(bucket_raw,
                           destination,
                           local_image_filename)
        except ResponseError as err:
            print(err)
        #kwargs['ti'].xcom_push(key='destination', value=destination)
        
        image_file = mc.get_object(bucket_raw, destination)
        #return image_file
        return local_image_filename
    
    return put_picture_to_raw_storage(get_picture_to_local(image_url)), file_id


def action_encoding64(image_file):
    """
    input [string]: path of file
    output [string]: the file encode in base64
    """
    import base64

    return base64.b64encode(open(image_file, 'rb').read())


def action_load_picture(encoded_string, file_id, collection='grayCollection'):
    from etlqs.ambassador import put_to_store_mongodb

    put_to_store_mongodb(collection,
                         encoded_string=encoded_string,
                         file_id=file_id)
    
