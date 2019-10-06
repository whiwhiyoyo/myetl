from pymongo import MongoClient
import gridfs
import base64
from PIL import Image
from io import BytesIO

client = MongoClient('mongodb', 27017)
db = client['picsum']
fs = gridfs.GridFS(db)
dbcollection = db['grayCollection']

assert dbcollection.count_documents({"name": "picsum104105"}) == 1

imageID = dbcollection.find_one({"name": "picsum104105"})['imageID']
assert fs.exists({"_id": imageID})

data = fs.find_one({"_id": imageID},no_cursor_timeout=True).read()

# a =  open('picpic.jpg', 'rb')
# # a.seek(0)
# # im = a.read()
# # a.seek(0)
# # image_read = a.read()
# image_64_encode = base64.b64encode(a.read()) 
# a.close()
# print(image_64_encode)

print(data)
image_64_decode = base64.b64decode(data) 
image_result = open('rrr4.jpg', 'wb')
#image_result.seek(0)
image_result.write(image_64_decode)
image_result.close()
#im = Image.open(base64.b64decode(data))
#im = Image.open(BytesIO(base64.b64decode(data)))
#im.save('image.jpg', 'JPEG')

# with open('rr.jpg', 'wb') as d:
#     d.write(base64.b64decode(data))

    
