import base64
import io
from io import BytesIO
import os
import sys
import flet as ft
import cv2
from PIL import Image as ImagePil
import numpy as np
import threading
import time
from playsound3 import playsound

from socios_dao import SociosDao


# para iniciar el video
init_video=False
#toma la foto
imagen_foto=None


id_socio=0

clasificacion=0

cap=None

def main(page: ft.Page):
    page.title = "Capturar Imagen"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width=1200
    page.window.height=900

    txt_password=ft.TextField(label="Contraseña",text_size=30,content_padding=ft.Padding(top=2,bottom=2,right=3,left=3))

    def handle_close(e):
        # honestidad2025
        if(txt_password.value=="honestidad2025"):            
            page.close(dlg_modal)

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Inicio"),
        content=ft.Container(content=ft.Column([
            ft.Text("Ingresa contraseña"),
            txt_password]),height=100),
        actions=[
            ft.TextButton("Entrar",on_click=handle_close),
            # ft.TextButton("Cancelar"),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        
    )

    
    # page.open(dlg_modal)
    
    

    def init_camara():
        global cap,init_video
        cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        init_video=True

        btnAbrirCamara.disabled=True
        btnCapturaFoto.disabled=False
        btnAbrirCamara.update()
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

        # fondo=cv2.imread("wp.jpeg")
        fondo=cv2.imread(resourse_path("wp.jpeg"))
        fondo=fondo[0:640,460:820]
        # imagen que muestra fuera del ovalo y lo convina con fondo para que se vea como opacidad
        image_mask_ovalo_inverso=cv2.addWeighted(frame,0.9,fondo,0.1,0)
        image_mask_ovalo_inverso=cv2.bitwise_and(image_mask_ovalo_inverso,image_mask_ovalo_inverso,mask=mask2)
        image_final_ovalo=cv2.add(image_mask_ovalo, image_mask_ovalo_inverso)
        
        visualizar(image_final_ovalo)    


    def visualizar(imagen_):
        
        im =ImagePil.fromarray(imagen_)
        buffered = BytesIO()
        im.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        imagen_video.src_base64=img_str
        imagen_video.update() 

    def setTextInput(e):
        txt_accion.value="%s%s"%(txt_accion.value,e)
        txt_accion.focus()
        txt_accion.update()
    
    def setTextAccionInput(e):
        global clasificacion       
        clasificacion=e
        buscar()
    
    def selectedSocio(soc_):
        global id_socio
        id_socio=soc_["cve_socio"]
        txt_nombre.value=f"{soc_["apellido_paterno"]} {soc_["apellido_materno"]} {soc_["nombre"]}"
        txt_nombre.update()
        # init_camara()
        btnAbrirCamara.disabled=False
        btnAbrirCamara.update()
    

    def clear():
        global init_video,imagen_foto,id_socio
        init_video=False
        imagen_foto=None
        id_socio=0

        txt_accion.value=''
        txt_nombre.value='nombre del socio.'
        time.sleep(1)
        imagen_video.src_base64=None
        imagen_video.src=None
        imagen_video.src="db/capture_rostro.png"
        lista_socios.controls=[]

        btnAbrirCamara.disabled=True
        btnCapturaFoto.disabled=True
        btnSaveFoto=ft.disabled=True

        btn_a.disabled=True
        btn_b.disabled=True
        btn_c.disabled=True

        page.update()
        if cap is not None and cap.isOpened():
            cap.release()
    
    def verificar_clasificacion(e):
        global clasificacion
        if(int(e.data)<=150):
            lista_socios.controls=[]
            
            btn_a.disabled=False
            btn_b.disabled=False
            btn_c.disabled=False

            btn_a.update()
            btn_b.update()
            btn_c.update()
            lista_socios.update()
            

        else:
            clasificacion=0
            btn_a.disabled=True
            btn_b.disabled=True
            btn_c.disabled=True

            btn_a.update()
            btn_b.update()
            btn_c.update()
            buscar()
      
    def view_foto_avatar(foto_):
        if(foto_ is not None):
            image_ = ImagePil.open(io.BytesIO(foto_)).convert("RGB")        
            buffered = BytesIO()
            image_.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')                       
            return ft.Image(src_base64=img_str,repeat=ft.ImageRepeat.NO_REPEAT,border_radius=ft.border_radius.all(50))
        else:
            return ft.CircleAvatar(content= ft.Icon(ft.Icons.ACCOUNT_CIRCLE),color=ft.Colors.YELLOW_200,bgcolor=ft.Colors.AMBER_700,)
        
    def buscar():
       
        data=SociosDao.get_socios(txt_accion.value,clasificacion)
      
        if data is not None:
            
            

            lista_socios.controls=[]
            data_map=map(lambda i:ft.ListTile(
                            leading=view_foto_avatar(i["foto_socio"]),
                            title=ft.Text(i["nombre"]),
                            subtitle=ft.Text(f"{i["apellido_paterno"]} {i["apellido_materno"]}"),
                            trailing=ft.Text(i["posicion"]),
                            data=ft.Text(i["nombre"]),                                                        
                            on_click=lambda _:selectedSocio(i),
                        ), data)
            
            lista_socios.controls=data_map
            lista_socios.update()                  
         



    def tomarRostro():
        global init_video,imagen_foto
        
        ret,frame=cap.read()
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        imagen_foto=frame
        # playsound("sound/iphone-camera-capture-6448.mp3")
        playsound(resourse_path("sound/iphone-camera-capture-6448.mp3"))


        file_path = resourse_path("haarcascade_frontalface_default.xml")   
        detector=cv2.CascadeClassifier(file_path)

        faces=detector.detectMultiScale(frame,1.3,5)       

        for(x,y,w,h) in faces:
            init_video=False
            btnCapturaFoto.disabled=True
            btnSaveFoto.disabled=False
            time.sleep(1)
            btnSaveFoto.update()
            btnCapturaFoto.update()
            rostro=frame[(y-50):y+(h+50),(x-50):x+(w+50)]

            im =ImagePil.fromarray(rostro)
            buffered = BytesIO()
            im.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            imagen_video.src_base64=img_str
            imagen_video.update() 
        
        

    def saveRostro(e):  
        global init_video,imagen_foto,id_socio
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
            id=SociosDao.save_foto(id_socio,byte_im)
        time.sleep(1)

        imagen_video.src_base64=None
        imagen_video.src=None
        imagen_video.src="db/capture_rostro.png"
        btnSaveFoto.content=ft.Row([ft.Icon(ft.icons.UPLOAD),ft.Text("Guardar foto")])

        init_video=False
        imagen_foto=None
        id_socio=0

        txt_nombre.value=""
        txt_accion.value=''

        btnAbrirCamara.disabled=True
        btnCapturaFoto.disabled=True
        btnSaveFoto.disabled=True

        clear()
        page.update()

    def findSocios(e):
        pass
        # print(e.data)
        # print(lista_socios.controls[0].title.value)
        # def iterator_func(x):
		# for v in x:
		# 	if e.data in v.title.value:
		# 		return True
		#     return False
	    # return filter(iterator_func, lista_socios.controls)
        


    def resourse_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


    imagen_video=ft.Image(src="db/capture_rostro.png",width=360,height=640,border_radius=10)
    txt_accion=ft.TextField(label="Accion",text_align="center",text_size=50,content_padding=ft.Padding(top=2,bottom=2,right=3,left=3),autofocus=True,max_length=4,on_submit=verificar_clasificacion)
    txt_nombre=ft.Text("nombre del usuario.",theme_style=ft.TextThemeStyle.TITLE_MEDIUM)

    btnAbrirCamara=ft.ElevatedButton(text="Abrir",color=ft.colors.BLUE,icon=ft.icons.CAMERA_ENHANCE_OUTLINED,disabled=True,on_click=lambda _:init_camara())
    btnCapturaFoto=ft.ElevatedButton(text="Capturar",color=ft.colors.BLUE,icon=ft.icons.CAMERA,disabled=True,on_click=lambda _:threading.Thread(target=tomarRostro).start())
    btnSaveFoto=ft.ElevatedButton(content=ft.Row([ft.Icon(ft.icons.UPLOAD),ft.Text("Guardar")]),disabled=True,color=ft.colors.BLUE,on_click=saveRostro)

    btn_a=ft.ElevatedButton(text="A",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=33,text_style=ft.TextStyle(size=40)),disabled=True,on_click=lambda _:setTextAccionInput(1))
    btn_b=ft.ElevatedButton(text="B",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=33,text_style=ft.TextStyle(size=40)),disabled=True,on_click=lambda _:setTextAccionInput(2))
    btn_c=ft.ElevatedButton(text="C",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=33,text_style=ft.TextStyle(size=40)),disabled=True,on_click=lambda _:setTextAccionInput(3))

    lista_socios = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    

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
                            btnAbrirCamara,
                        btnCapturaFoto,
                        btnSaveFoto
                        ]),
                        
                        
                        ]
                ),padding=5)),
            ft.Column([
                ft.Container(width=300,height=60,bgcolor=ft.colors.BLUE_GREY_100,content=txt_nombre,alignment=ft.alignment.center,border_radius=10),
                ft.Container(width=300,content=txt_accion),
                ft.Row(
            controls=[
                btn_a,btn_b,btn_c
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
                    ft.ElevatedButton(content=ft.Icon(name=ft.icons.CHECK,size=40),style=ft.ButtonStyle(shape=ft.CircleBorder()),bgcolor=ft.colors.TEAL_ACCENT,color=ft.colors.WHITE,width=90,height=90,on_click=lambda _:buscar()),
                ]
            )
            ]),
             ft.Card(content=
                ft.Column([

                      ft.Container(padding=ft.padding.only(top=10),width=360,content=ft.Text("Usuarios en la accion")
                    #   ft.TextField(label="Posicion",text_align="center",text_size=35,content_padding=ft.Padding(top=2,bottom=2,right=5,left=5),bgcolor=ft.Colors.WHITE,autofocus=True,on_change=findSocios)
                      ),

                        ft.Container( width=380,content=
            #        
                        ft.Card(content=ft.Container(
                width=360,height=550,
                content=lista_socios,
                # ft.Column(
                #     [                      
                #         ft.ListTile(
                #             leading=ft.Icon(ft.Icons.ALBUM),
                #             title=ft.Text("One-line with leading and trailing controls"),
                #             trailing=ft.Text("1")
                #         ),
                #         ft.ListTile(
                #             leading=ft.Icon(ft.Icons.SNOOZE),
                #             title=ft.Text("Two-line with leading and trailing controls"),
                #             subtitle=ft.Text("Here is a second title."),
                #             trailing=ft.Text("1")
                #         ),
                #     ],
                #     spacing=0,
                # ),
                padding=ft.padding.symmetric(vertical=10),
            ),color=ft.colors.WHITE)

                        
                        
                ,padding=5),
                
                ],horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                color=ft.Colors.BLUE_GREY,
                
                ),
            
            
            ],alignment=ft.MainAxisAlignment.CENTER),
        
        ])
    )

    page.open(dlg_modal)
ft.app(target=main)