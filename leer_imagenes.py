import os
from os import listdir
import cv2
import numpy
from os.path import join
import time
import mysql.connector

conexion=mysql.connector.connect(host="192.168.2.111",user="dev_pv",password="pss_dEv_pv_18",database="punto_verde_v2")

detector =cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")

cursor=conexion.cursor()
# cursor.execute("SELECT socios.cve_socio,socios.foto FROM socios WHERE socios.foto IS NOT NULL AND socios.foto !='' and is_foto=0")
cursor.execute("SELECT socios.cve_socio,REPLACE( replace(socios.foto,'\\serverPaquetesFOTOSSOCIOS6',''), ' ', '') as foto FROM socios WHERE  socios.foto_socio IS NOT NULL and socios.foto!=''")
data=cursor.fetchall()

count=0
for img in data:
    image=cv2.imread(join("upload",img[1]))
    if image is not None:
        # print(f"existe imagen {img[1]}")
        faces=detector.detectMultiScale(image,1.3,5)
        if len(faces)>0:               
            # x=faces[0][0]
            # y=faces[0][1]
            # w=faces[0][2]
            # h=faces[0][3]            
            count=count+1
            # rostro=image[y:y+h,x:x+w]
            # rostro=cv2.cvtColor(rostro,cv2.COLOR_RGB2BGR)#COLOR_BGR2RGB
            # rostro=cv2.cvtColor(rostro,cv2.COLOR_BGR2RGB)#COLOR_BGR2RGB
            if(image.shape[0]>400):
                rostro=cv2.resize(image,(400,400),interpolation=cv2.INTER_CUBIC)
                is_success, im_buf_arr = cv2.imencode(".jpg", rostro)
                byte_im = im_buf_arr.tobytes()
           
                print(f"existe imagen con rostro {img[1]}")
                cursor_insert=conexion.cursor()
                cursor.execute("""
                        UPDATE socios SET foto_socio=%s , is_foto=3 WHERE cve_socio=%s
                       """,(byte_im,img[0],))                   
                conexion.commit()
                print(cursor_insert)
            else:
                is_success, im_buf_arr = cv2.imencode(".jpg", image)
                byte_im = im_buf_arr.tobytes()
           
                print(f"existe imagen con rostro {img[1]}")
                cursor_insert=conexion.cursor()
                cursor.execute("""
                        UPDATE socios SET foto_socio=%s , is_foto=3 WHERE cve_socio=%s
                       """,(byte_im,img[0],))                   
                conexion.commit()
                print(cursor_insert)

        else: print("no contiene rostro")
    else: print("no existe imagen")  

print(count)  
conexion.close()

# for filename in os.listdir("prueba_imagen"):
#     img = cv2.imread(os.path.join("prueba_imagen",filename))
#     if img is not None:
#         print(img.shape)
#         if(img.shape[0]>400):
#             rostro=cv2.resize(img,(400,400),interpolation=cv2.INTER_CUBIC)
#             print(rostro.shape)
#             cv2.imwrite(join("prueba_imagen","2"+filename),rostro)

# image=cv2.imread(join("prueba_imagen","1.JPG"))
# print(image.shape)