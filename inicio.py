import base64
from io import BytesIO
import os
import sys
import flet as ft
import cv2
from PIL import Image
import mediapipe as mp
import numpy as np
import threading
import time
from playsound3 import playsound

from usuarios_flet_dao import UsuariosFletDao


# para iniciar el video
init_video=False
#toma la foto
imagen_foto=None
#id de colaborador
id_colaborador=0

cap=None

def main(page: ft.Page):
    page.title = "Capturar Imagen"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width=900
    page.window.height=900
    
    

    def init_camara():
        global cap,init_video
        cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        init_video=True
        btnCapturaFoto.disabled=False
        btnCapturaFoto.update()
        while init_video:
            fn_init_video()

    def fn_init_video():        
        ret,frame=cap.read()
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        frame=frame[0:640,460:820]

        mask=np.zeros((640, 360),dtype=np.uint8) 
        mask=cv2.ellipse(mask,(180,320),(150,200) ,0,0,360,(255),-1)
        mask2=cv2.bitwise_not(mask)

        image_mask_ovalo=cv2.bitwise_and(frame,frame,mask=mask)  

        fondo=cv2.imread("wp.jpeg")
        fondo=fondo[0:640,460:820]
        # imagen que muestra fuera del ovalo y lo convina con fondo para que se vea como opacidad
        image_mask_ovalo_inverso=cv2.addWeighted(frame,0.9,fondo,0.1,0)
        image_mask_ovalo_inverso=cv2.bitwise_and(image_mask_ovalo_inverso,image_mask_ovalo_inverso,mask=mask2)
        image_final_ovalo=cv2.add(image_mask_ovalo, image_mask_ovalo_inverso)
        
        visualizar(image_final_ovalo)    


    def visualizar(imagen_):
        
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
        global init_video,imagen_foto,id_colaborador
        init_video=False
        imagen_foto=None
        id_colaborador=0

        txt_nomina.value=''
        txt_nombre.value='nombre del colaborador.'
        time.sleep(1)
        imagen_video.src_base64=None
        imagen_video.src=None
        imagen_video.src="db/capture_rostro.png"
        page.update()
        
    def buscar(_):
        global id_colaborador
        data=UsuariosFletDao.get_colaborador(txt_nomina.value)
        if data is not None:
            id_colaborador=data["id_colaborador"]
            txt_nombre.value="%s %s %s" %(data["apellido_paterno"],data["apellido_materno"],data["nombre"])
            txt_nombre.update()
            init_camara()



    def tomarRostro():
        global init_video,imagen_foto
        
        ret,frame=cap.read()
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        imagen_foto=frame
        playsound("sound/iphone-camera-capture-6448.mp3")


        file_path = resourse_path("haarcascade_frontalface_default.xml")   
        detector=cv2.CascadeClassifier(file_path)

        faces=detector.detectMultiScale(frame,1.3,5)       

        for(x,y,w,h) in faces:
            init_video=False
            btnSaveFoto.disabled=False
            time.sleep(1)
            btnSaveFoto.update()
            rostro=frame[(y-50):y+(h+50),(x-50):x+(w+50)]

            im =Image.fromarray(rostro)
            buffered = BytesIO()
            im.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            imagen_video.src_base64=img_str
            imagen_video.update() 
        
        

    def saveRostro(e):  
        global init_video,imagen_foto,id_colaborador
        btnSaveFoto.content=ft.ProgressRing(width=20,height=20,color=ft.colors.BLUE,stroke_width=2)
        page.update()
        
        file_path = resourse_path("haarcascade_frontalface_default.xml")   
        detector=cv2.CascadeClassifier(file_path)

        faces=detector.detectMultiScale(imagen_foto,1.3,5)       

        for(x,y,w,h) in faces:
            rostro=imagen_foto[(y-50):y+(h+50),(x-50):x+(w+50)]
            rostro=cv2.cvtColor(rostro,cv2.COLOR_RGB2BGR)

            is_success, im_buf_arr = cv2.imencode(".jpg", rostro)
            byte_im = im_buf_arr.tobytes() 
            id=UsuariosFletDao.save_foto(id_colaborador,byte_im)
        time.sleep(1)

        imagen_video.src_base64=None
        imagen_video.src=None
        imagen_video.src="db/capture_rostro.png"
        btnSaveFoto.content=ft.Row([ft.Icon(ft.icons.UPLOAD),ft.Text("Guardar foto")])

        init_video=False
        imagen_foto=None
        id_colaborador=0

        txt_nombre.value=""
        txt_nomina.value=''

        # btnAbrirCamara.disabled=True
        btnCapturaFoto.disabled=True
        btnSaveFoto.disabled=True


        page.update()


    def resourse_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


    imagen_video=ft.Image(src="db/capture_rostro.png",width=360,height=640,border_radius=10)
    txt_nomina=ft.TextField(label="Nomina",text_align="center",text_size=50,content_padding=ft.Padding(top=2,bottom=2,right=0,left=0),autofocus=True,on_submit=buscar)
    txt_nombre=ft.Text("nombre del colaborador.",theme_style=ft.TextThemeStyle.TITLE_MEDIUM)

    btnCapturaFoto=ft.ElevatedButton(text="Capturar foto",color=ft.colors.BLUE,icon=ft.icons.CAMERA,disabled=True,on_click=lambda _:threading.Thread(target=tomarRostro).start())
    btnSaveFoto=ft.ElevatedButton(content=ft.Row([ft.Icon(ft.icons.UPLOAD),ft.Text("Guardar foto")]),disabled=True,color=ft.colors.BLUE,on_click=saveRostro)
    

    page.add(
        ft.Column(controls=[
        # txt_nombre,
        ft.Row([
                ft.Card(content=
                        ft.Container(content=
                    ft.Column(
                        [
                        ft.Card(content=ft.Container(content=imagen_video),color=ft.colors.BLUE_GREY),
                        ft.Row([
                        btnCapturaFoto,
                        btnSaveFoto
                        ]),
                        
                        
                        ]
                ),padding=5)),
            ft.Column([
                ft.Container(width=300,height=60,bgcolor=ft.colors.BLUE_GREY_100,content=txt_nombre,alignment=ft.alignment.center,border_radius=10),
                ft.Container(width=300,content=txt_nomina),
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
                    ft.ElevatedButton(content=ft.Icon(name=ft.icons.CHECK,size=40),style=ft.ButtonStyle(shape=ft.CircleBorder()),bgcolor=ft.colors.TEAL_ACCENT,color=ft.colors.WHITE,width=90,height=90,on_click=buscar),
                ]
            )
            ])
            # )
            
            ],alignment=ft.MainAxisAlignment.CENTER),
        
        ])
    )

ft.app(target=main)