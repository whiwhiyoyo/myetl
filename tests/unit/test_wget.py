import requests
import wget
import os


image_url = "https://picsum.photos/100/200"
tmp_images_dir = '/tmp/{}_image'.format('yoyo')
if not os.path.isdir(tmp_images_dir):
    os.mkdir(tmp_images_dir)
# else:
#     import shutil
#     shutil.rmtree(tmp_images_dir) 
local_image_filename = '{}'.format(
    'yoyo.jpg'
)
# r = requests.get(image_url)
# with open(local_image_filename, 'w') as f:
#     f.write(r)
print(local_image_filename)
print(image_url)
# wget.download(image_url, local_image_filename)


r = requests.get(image_url, allow_redirects=True)
#print(r.content)
with open(local_image_filename, 'wb') as f:
    f.write(r.content)
