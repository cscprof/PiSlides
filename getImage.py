import os
import pycurl
import certifi
import xml.etree.ElementTree as ET
from io import BytesIO


#Setup Constants for the S3 bucket
S3BUCKET = "https://geneva-mediacenter.s3.us-east-2.amazonaws.com/"
DEVICE_BUCKET = "main343/"
LOCAL_PATH = "./images/"

# Get listing of local image files
local_list = os.listdir(LOCAL_PATH)

# Get the S3 bucket contents list as XML document
buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, S3BUCKET)
c.setopt(c.WRITEDATA, buffer)
c.setopt(c.CAINFO, certifi.where())
c.perform()
c.close()

xml_response = buffer.getvalue().decode('iso-8859-1')
root = ET.fromstring(xml_response)

s3_images_list = []

# Walk the document to find image names on S3
for images in root.iter('{http://s3.amazonaws.com/doc/2006-03-01/}Key'):
    # Get the Image names for this device, if any
    if images.text[:len(DEVICE_BUCKET)] == DEVICE_BUCKET and len(images.text) > len(DEVICE_BUCKET):
        
        s3_images_list.append( images.text[len(DEVICE_BUCKET):] )
        

# Download the images if there are differences
if set(s3_images_list) == set(local_list):
     print('Same images, no download needed')
else:      
    
    # Delete existing local files
    for root, dirs, files in os.walk(LOCAL_PATH):
        for file in files:
            os.remove(os.path.join(root, file))
    
    
    # Download the images
    for image_name in s3_images_list:

            # Get image from S3 and save locally
            with open(LOCAL_PATH + image_name, 'wb') as f:
                c = pycurl.Curl()
                c.setopt(c.URL, S3BUCKET+ DEVICE_BUCKET + image_name)
                c.setopt(c.WRITEDATA, f)
                c.perform()
                c.close()

