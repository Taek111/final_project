from firebase import firebase
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

# firebase = firebase.FirebaseApplication('https://pracs-be3b0.firebaseio.com', None)
# # cred = credentials.Certificate("pracs-be3b0-firebase-adminsdk-yqgu4-f92fb008fe.json")
# # firebase_admin.initialize_app(cred, {
# #     'storageBucket': 'pracs-be3b0.appspot.com'
# # })
# # bucket = storage.bucket()
# # #imageBlob = bucket.get_blob('C:/Python27/photo.png')
# # imageBlob = bucket.blob(os.path.basename('test.png'))
# # # use pillow to open and transform the file
# # #blob.upload_from_filename(filename="data/test.png")

#firebase = firebase.FirebaseApplication('https://pracs-be3b0.firebaseio.com', None)
cred = credentials.Certificate("pracs-be3b0-firebase-adminsdk-yqgu4-f92fb008fe.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'pracs-be3b0.appspot.com'})
#db = firestore.client()
bucket = storage.bucket()
zebraBlob = bucket.blob("yellowdog.png")
zebraBlob.upload_from_filename(filename="data/yellowdog.png")
