import unittest
#target = __import__("/opt/src/my_sum.py")
#sum = target.sum



class TestMongoDB(unittest.TestCase):
    def setUp(self):
        import os
        from pymongo import MongoClient

        self.testdb = 'testdb'
        
        os.environ['MONGODB_PICSUMDB_NAME'] = self.testdb
        mongodb_host = os.environ['MONGODB_HOST']
        mongodb_port = int(os.environ['MONGODB_PORT'])
        mongodb_picsumdb_name = os.environ['MONGODB_PICSUMDB_NAME']
        self.cl = MongoClient(mongodb_host, mongodb_port)
        self.mdb = self.cl[mongodb_picsumdb_name] 
             
    def tearDown(self):
        self.cl.drop_database(self.testdb)
        
    def test_put_to_store_mongodb(self):
        from etlqs.ambassador import put_to_store_mongodb
        import gridfs

        testcol = 'testcol'
        fs = gridfs.GridFS(self.mdb)

        put_to_store_mongodb(testcol, b'yoyo', 'whiwhi')
        assert self.mdb[testcol].count_documents({"name": "whiwhi"}) >= 1

        imageID = self.mdb[testcol].find_one({"name": "whiwhi"})['imageID']
        assert fs.exists({"_id": imageID})

        data = fs.find_one({"_id": imageID},no_cursor_timeout=True).read()
        
        self.assertEqual(data, b'yoyo')

    # def test_existence_of_customer(self):
    #     customer = self.app.get_customer(id=10)
    #     self.assertEqual(customer.name, "Org XYZ")
    #     self.assertEqual(customer.address, "10 Red Road, Reading")


class TestMinio(unittest.TestCase):
    def setUp(self):
        import os
        from minio import Minio
        from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
        
        self.bucket = 'test'
        file_path = 'fixtures/rrr5.jpg'
        self.destination_path = 'rrr5'
        
        os.environ['MINIO_BUCKET'] = self.bucket 
        minio_host = os.environ['MINIO_HOST']
        minio_port = os.environ['MINIO_PORT']
        minio_access_key = os.environ['MINIO_ACCESS_KEY']
        minio_secret_key = os.environ['MINIO_SECRET_KEY']
        self.mc = Minio('{}:{}'.format(minio_host, minio_port),
                   access_key=minio_access_key,
                   secret_key=minio_secret_key,
                   secure=False)

        try:
            self.mc.make_bucket(self.bucket, location="us-east-1")
            self.mc.fput_object(self.bucket,
                                self.destination_path,
                                file_path)
        except ResponseError as err:
            print(err)


        
    def tearDown(self):
        from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                     BucketAlreadyExists)

        try:
            objects_to_delete = [self.destination_path]
            for del_err in self.mc.remove_objects(self.bucket,
                                                      objects_to_delete):
                print("Deletion Error: {}".format(del_err))
        except ResponseError as err:
            print(err)

        self.mc.remove_bucket(self.bucket)
  
    def test_find_by_name_from_raw_store(self):
        from etlqs.ambassador import find_by_name_from_raw_store
        
        data = find_by_name_from_raw_store(self.bucket, self.destination_path)
        self.assertEqual(len(data.keys()), 4)
        self.assertEqual(data['name'], 'rrr5')
        self.assertGreater(data['size'], 0)
       
    
if __name__ == '__main__':
    unittest.main()
