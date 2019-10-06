from minio import Minio

def put_to_store_mongodb(collection, encoded_string, file_id):
    """
    input [string]: 
    output []: None
    TODO: exception management
    """       
    from pymongo import MongoClient
    import gridfs
    import os
    
    mongodb_host = os.environ['MONGODB_HOST']
    mongodb_port = int(os.environ['MONGODB_PORT'])
    mongodb_picsumdb_name = os.environ['MONGODB_PICSUMDB_NAME']

    client = MongoClient(mongodb_host, mongodb_port)
    db = client[mongodb_picsumdb_name]
    dbcollection = db[collection]

    fs = gridfs.GridFS(db)
    # insert image, return the reference
    imageID = fs.put(encoded_string)

    # create our image meta data
    meta = {
        'imageID': imageID,
        'name': file_id
    }

    # insert the meta data
    dbcollection.update_one({"name": file_id},{"$set":meta}, upsert=True)

 
def get_from_raw_store(bucket, file_path):
    import os
    from minio import Minio
    from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
    
    #bucket = 'urlsraw'

    # Initialize minioClient with an endpoint and access/secret keys.
    mc = Minio('minio:9000',
               access_key='minio',
               secret_key='minio123',
               secure=False)
  
    urls_file = mc.get_object(bucket, file_path)
    return urls_file


def put_to_raw_store(bucket, file_path):
    import os
    from minio import Minio
    from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

    bucket = 'urlsraw'
    destination_path = file_path.split('/')[-1]
    # Initialize minioClient with an endpoint and access/secret keys.
    mc = Minio('minio:9000',
               access_key='minio',
               secret_key='minio123',
               secure=False)
    
    try:
        mc.fput_object(bucket,
                       destination_path,
                       file_path)


    except ResponseError as err:
        print(err)

def find_by_name_from_raw_store(bucket, file_name,
                                mc=Minio('minio:9000',
                                           access_key='minio',
                                           secret_key='minio123',
                                           secure=False)):
    from minio import Minio
    from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
    
    # Initialize minioClient with an endpoint and access/secret keys.

    objects = mc.list_objects_v2(bucket, recursive=False)
    for obj in objects:
        print(obj.bucket_name,
              obj.object_name,
              obj.last_modified,
              obj.etag,
              obj.size,
              obj.content_type)
        if obj.object_name == file_name:
            #TODO condition of the local existance of the file
            #urls_file = mc.get_object(bucket, urls_filename)
            #return urls_file
            return {'name':obj.object_name,
                    'last_modified':obj.last_modified,
                    'size': obj.size,
                    'content_type': obj.content_type}
    # we shouldn't be here
    print("{} is not found in the bucket {}".format(urls_filename, bucket))
    # TODO write a specific exception instead of returning None
    return None


