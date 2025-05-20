import base64
from io import BytesIO
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import sys
import flet as ft
import cv2
from PIL import Image

import numpy as np
import threading
import time
import io
from playsound3 import playsound
from deepface import DeepFace

from cvzone.FaceMeshModule import FaceMeshDetector
import mediapipe as mp
from usuarios_flet_dao import UsuariosFletDao



# variable de guarda el estado de la camara
cap=None
# para iniciar el video, en un while indica que tiene que estar ciclando los fotogramas
init_video=False
#id de colaborador
id_colaborador=0
# variable que gurada el rostro desde bd
rostro_colaborador=None
# inicia en 15 para que no duere mucho no es 0 porque es mod 0 ejemplo mod de 0 % 30 =0 esto tomaria la imagen enseguida
counter=15
# indica que se esta realizando la validacion por parde de deepface es para el tiempo que tarde y no volver a ejecutar otra vez
is_valid_face=False
# se basa es media pipe y es para tomar la distancia y saber que es un rostro humano
detector_cvzone=FaceMeshDetector(maxFaces=1)





def gracias():
        playsound("C:/Users/Sistemas2/Desktop/reloj_checador/sound/thank-you-168416.mp3",block=False)




def main(page: ft.Page):
    page.title = "Capturar foto socio"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width=900
    page.window.height=900

    def init_camara():
        global cap,init_video
        cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        init_video=True
        while init_video:
            fn_init_video()


    def fn_init_video():        
        ret,frame=cap.read()
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        frame=cv2.flip(frame,1)# se pone como espejo
        frame=frame[0:640,460:820]#recorta solo esl centro de la camara y que se vea como celular

        mask=np.zeros((640, 360),dtype=np.uint8) 
        mask=cv2.ellipse(mask,(180,320),(150,200) ,0,0,360,(255),-1)
        mask2=cv2.bitwise_not(mask)

        image_mask_ovalo=cv2.bitwise_and(frame,frame,mask=mask)  

        fondo=cv2.imread("C:/Users/Sistemas2/Desktop/reloj_checador/wp.jpeg")
        fondo=fondo[0:640,460:820]
        # imagen que muestra fuera del ovalo y lo convina con fondo para que se vea como opacidad
        image_mask_ovalo_inverso=cv2.addWeighted(frame,0.9,fondo,0.1,0)
        image_mask_ovalo_inverso=cv2.bitwise_and(image_mask_ovalo_inverso,image_mask_ovalo_inverso,mask=mask2)
        image_final_ovalo=cv2.add(image_mask_ovalo, image_mask_ovalo_inverso)
        
        visualizar(image_final_ovalo,frame)    

    # def visualizar(imagen_,image_origin):
    #     global counter,is_valid_face
       
    #     #inicia con la captura cada 30 segundos y siepre no este ya en proceso una verificacion
    #     if counter % 30 == 0  and is_valid_face==False:
    #         # ejecuta el hilo para verificar pasandole la imagen original
    #         print("entra y corre el hilo")
    #         threading.Thread(target=match,kwargs={'frame':image_origin}).start()                    
    #     counter=counter+1
    #     #proceso para convertir la imagen a base64 y mostrarla 
    #     im =Image.fromarray(imagen_)
    #     buffered = BytesIO()
    #     im.save(buffered, format="JPEG")
    #     img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    #     imagen_video.src_base64=img_str
    #     imagen_video.update() 

    def visualizar(imagen_,image_origin):
        global counter,is_valid_face
        # busca un rostro con cvzone(mediapipe)
        _,faces_cv_zone=detector_cvzone.findFaceMesh(imagen_,draw=False)
        if faces_cv_zone:
            # el primer rostro encontrado
            face_=faces_cv_zone[0]
            # ojo izq
            pointLeft=face_[145]
            # ojo der
            pointRigth=face_[374]
            #punto de la nariz
            pointNose=face_[4] 
            # proceso para calcular la distanca y guardar en variale d
            w,_=detector_cvzone.findDistance(pointLeft,pointRigth)
            W=6.3
            f=840
            d=(W*f)/w
            cv2.circle(imagen_,pointNose,2,(250, 193, 19),cv2.FILLED)                             
            cv2.line(imagen_,(180,320),(180,380),(250, 193, 19),1)
            cv2.line(imagen_,(150,350),(210,350),(250, 193, 19),1)

            # valida la distancia entre un rango de 40 a 70 cm de distancia y que la nariz este en el punto central mayor a 150 y menor a 210 en x y mayor a 320 y menor a 380b en y
            if(d>35 and d<70 and pointNose[0]>150 and pointNose[0]<210 and pointNose[1]>320 and pointNose[1]<380):
                #se pinta un rectangulo en la orilla de color amarilllo para indicar que se esta leyendo el rostro
                imagen_=cv2.rectangle(imagen_,(0,0),(360,640),(250, 193, 19),30)
                #inicia con la captura cada 30 segundos y siepre no este ya en proceso una verificacion
                if counter % 30 == 0  and is_valid_face==False:
                    # ejecuta el hilo para verificar pasandole la imagen original
                    threading.Thread(target=match,kwargs={'frame':image_origin}).start()                    
                counter=counter+1
        #proceso para convertir la imagen a base64 y mostrarla 
        im =Image.fromarray(imagen_)
        buffered = BytesIO()
        im.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        imagen_video.src_base64=img_str
        imagen_video.update() 

    def setTextInput(e):
        txt_nomina.value="%s%s"%(txt_nomina.value,e)
        txt_nomina.focus()
        txt_nomina.update()

    def clear():
        global init_video,id_colaborador,is_valid_face,counter
        init_video=False#cancela con esto el while que muestra los fotogramas
        id_colaborador=0#se regresa el id de colaborador a 0
        is_valid_face=False#indica que no se esta en proceso de verificacion
        counter=20# se reinicia el contador a el origen 
        # se verifica que la camara no este encendida 
        if cap is not None and cap.isOpened():
            cap.release()

        txt_nomina.value=''#se borra del input la nomina
        txt_nomina.focus()#se regresa el foco
        txt_nombre.value='Nombre de Empleado.'
        
        time.sleep(1)
        imagen_video.src_base64=None
        imagen_video.src=None
        imagen_video.src="C:/Users/Sistemas2/Desktop/reloj_checador/db/capture_rostro.png"
        page.update()
        
    def buscar(_):
        global id_colaborador,rostro_colaborador,init_video

        if(len(txt_nomina.value)!=4):
            print("no puede buscar debe de ser de 4 digitos incluyendo 0 al inicio ")
            page.snack_bar = ft.SnackBar(content=ft.Text("El Numero de empleado debe tener 4 digitos incluyendo 0 en caso de que lo tenga",style=ft.TextStyle(size=30,color="#000000")),action="",bgcolor="#FFB300",duration=10000)
            page.snack_bar.open = True
            page.update()
            txt_nomina.focus()
            return      

        if cap is not None and cap.isOpened():
            init_video=False
            cap.release()

        tolerancia=UsuariosFletDao.get_tolerancia_entrada(txt_nomina.value)
        print("tolerancia:",tolerancia)

        if(tolerancia is not None and tolerancia["aplica_tiempo"]==1 and tolerancia["flag"]==0):
            print('no puedes acceder')
            # self.msg.configure(text="15 minutos antes de entrada",fg='#F48430')
            page.snack_bar = ft.SnackBar(content=ft.Text("Espere 15 minutos antes de su entrada para poder checar",style=ft.TextStyle(size=30,color="#000000")),action="",bgcolor="#FFB300",duration=10000)
            page.snack_bar.open = True
            page.update()
            txt_nomina.focus()
            return
        
        data=UsuariosFletDao.get_colaborador(txt_nomina.value)
        if data is not None:
            id_colaborador=data["id_colaborador"]
            txt_nombre.value="%s %s %s" %(data["apellido_paterno"],data["apellido_materno"],data["nombre"])
            txt_nombre.update()
            
            image=UsuariosFletDao.get_foto(id_colaborador)
            if(image[0] is not None):
                image_ = Image.open(io.BytesIO(image[0])).convert("RGB")
                rostro_colaborador = np.array(image_)
                init_camara()                
            else: 
                page.snack_bar = ft.SnackBar(content=ft.Text("No emlpeado con numero "+txt_nomina.value+" no tiene foto registrada",style=ft.TextStyle(size=30,color="#000000")),action="",bgcolor="#FFB300",duration=10000)
                page.snack_bar.open = True
                page.update()
                txt_nomina.focus()
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text("No existe empleado con este numero "+txt_nomina.value,style=ft.TextStyle(size=30,color="#000000")),action="",bgcolor="#FFB300",duration=10000)
            page.snack_bar.open = True
            page.update()
            txt_nomina.focus()


    def resourse_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def match(frame):
        global is_valid_face

        # indeica que emepieza la validacion 
        is_valid_face=True

        is_success, im_buf_arr = cv2.imencode(".jpg", cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY))
        byte_im = im_buf_arr.tobytes()

        print("inicia verificacion")
        print(counter)
        # DeepFace.build_model("VGG-Face")
        data=DeepFace.verify(img1_path=frame,img2_path=rostro_colaborador,model_name="VGG-Face",detector_backend="mediapipe",threshold=.55)
            
        if data is not None and data["verified"]: 
            UsuariosFletDao.registrar_acceso(id_colaborador,byte_im,data["distance"],data["model"],data["threshold"])
            page.snack_bar = ft.SnackBar(content=ft.Text("Gracias",style=ft.TextStyle(size=30)),action="exito",bgcolor="#5a98de",duration=2500)
            page.snack_bar.open = True            
            page.update()
            audio=threading.Thread(target=gracias)
            audio.start()
            time.sleep(3)
            clear()
        print("finaliza verificacion")
        is_valid_face=False
         

    imagen_video=ft.Image(src="C:/Users/Sistemas2/Desktop/reloj_checador/db/capture_rostro.png",width=360,height=640,border_radius=10)
    txt_nomina=ft.TextField(hint_text="Numero Empleado",hint_style=ft.TextStyle(size=20),text_align="center",text_size=50,max_length=4,content_padding=ft.Padding(top=2,bottom=2,right=0,left=0),autofocus=True,on_submit=buscar)
    txt_nombre=ft.Text("nombre del colaborador.",theme_style=ft.TextThemeStyle.TITLE_MEDIUM)
    btn_buscar=ft.ElevatedButton(content=ft.Icon(name=ft.icons.CHECK,size=40),style=ft.ButtonStyle(shape=ft.CircleBorder()),bgcolor=ft.colors.TEAL_ACCENT,color=ft.colors.WHITE,width=90,height=90,on_click=buscar)


    def on_keyboard(e: ft.KeyboardEvent):       
        if(e.key=="Numpad Multiply"):
            clear()

    page.on_keyboard_event=on_keyboard
    

    page.add(
        ft.Column(controls=[
        #     ft.Row([
        #     ft.Container(width=200,content=ft.TextField(hint_text="Numero Empleado",hint_style=ft.TextStyle(size=20),text_align="center",text_size=50,max_length=4,content_padding=ft.Padding(top=2,bottom=2,right=0,left=0),autofocus=True,on_submit=buscar,),alignment=ft.alignment.center,bgcolor=ft.Colors.RED),
        #     ft.Container(width=200,content=ft.TextField(hint_text="Numero Empleado",hint_style=ft.TextStyle(size=20),text_align="center",text_size=50,max_length=4,content_padding=ft.Padding(top=2,bottom=2,right=0,left=0),autofocus=True,on_submit=buscar),alignment=ft.alignment.center,bgcolor=ft.Colors.BLUE),
        #     ft.Container(width=200,content=ft.TextField(hint_text="Numero Empleado",hint_style=ft.TextStyle(size=20),text_align="center",text_size=50,max_length=4,content_padding=ft.Padding(top=2,bottom=2,right=0,left=0),autofocus=True,on_submit=buscar),alignment=ft.alignment.center,bgcolor=ft.Colors.PURPLE)
        # ],alignment=ft.MainAxisAlignment.CENTER),
        
        ft.Row([
                ft.Card(content=
                        ft.Container(content=
                    ft.Column(
                        [
                        ft.Card(content=ft.Container(content=imagen_video),color=ft.colors.BLUE_GREY),
                        ft.Row([
                        ]),
                        
                        
                        ]
                ),padding=5)),
            ft.Column([
                # ft.Container(width=300,height=60,bgcolor=ft.colors.BLUE_GREY_100,content=txt_nombre,alignment=ft.alignment.center,border_radius=10,padding=5),
                ft.Container(width=300,content=txt_nomina),
            ft.Row(
            controls=[
                ft.ElevatedButton(text="A",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=33,text_style=ft.TextStyle(size=40)),color=ft.Colors.PURPLE,bgcolor=ft.Colors.PURPLE_200,on_click=lambda _:setTextInput(7)),
                ft.ElevatedButton(text="B",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=33,text_style=ft.TextStyle(size=40)),color=ft.Colors.PURPLE,bgcolor=ft.Colors.PURPLE_200,on_click=lambda _:setTextInput(8)),
                ft.ElevatedButton(text="C",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=33,text_style=ft.TextStyle(size=40)),color=ft.Colors.PURPLE,bgcolor=ft.Colors.PURPLE_200,on_click=lambda _:setTextInput(9)),
            ]
        ),
            ft.Row(
            controls=[
                ft.ElevatedButton(text="7",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(7)),
                ft.ElevatedButton(text="8",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(8)),
                ft.ElevatedButton(text="9",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(9)),
            ]
        ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(text="4",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(4)),
                    ft.ElevatedButton(text="5",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(5)),
                    ft.ElevatedButton(text="6",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(6)),
                ]
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(text="1",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(1)),
                    ft.ElevatedButton(text="2",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(2)),
                    ft.ElevatedButton(text="3",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(3)),                    
                ]
            ),
            ft.Row(
                 controls=[
                    ft.ElevatedButton(text="0",style=ft.ButtonStyle(shape=ft.CircleBorder(),text_style=ft.TextStyle(size=40)),width=90,height=90,on_click=lambda _:setTextInput(0)),
                    ft.ElevatedButton(content=ft.Icon(name=ft.icons.CLEAR,size=40),style=ft.ButtonStyle(shape=ft.CircleBorder()),bgcolor=ft.colors.RED_ACCENT,color=ft.colors.WHITE,width=90,height=90,on_click=lambda _:threading.Thread(target=clear).start()),
                    btn_buscar,
                ]
            )
            ]),
            ft.Card(content=
                        ft.Container(content=
                    ft.Column(
                        [
                        ft.Card(content=ft.Container(content=imagen_video),color=ft.colors.BLUE_GREY),
                        ft.Row([
                            
                        ]),
                        
                        
                        ]
                ),padding=5)),
            # )
            
            ],alignment=ft.MainAxisAlignment.CENTER),
        
        ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    

ft.app(target=main)