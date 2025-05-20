import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from deepface import DeepFace
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
tf.data

def verify(img1_path,img2_path):
    img1= cv2.imread(img1_path)
    img2= cv2.imread(img2_path)

    # print(img1)
    
    plt.imshow(img1[:,:,::-1])
    plt.show()
    plt.imshow(img2[:,:,::-1])
    plt.show()
    DeepFace.build_model("VGG-Face")
    output = DeepFace.verify(img1_path=img1_path,img2_path=img2_path)
    print(output)
    verification = output['verified']
    if verification:
       print('They are same')
    else:
       print('The are not same')

verify('db/img1.jpg','db/img2.jpg')