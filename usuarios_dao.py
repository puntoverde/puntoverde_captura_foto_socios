from mysql_conexion import Conexion
import time

class UsuariosDao:

    @staticmethod
    def get_config():
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor(dictionary=True)
        cursor.execute("SELECT distancia FROM reloj_checador_config WHERE id_reloj_checador_config=1")
        data=cursor.fetchone()
        
        con.close_conexion()
        return data["distancia"]
    
    
    @staticmethod
    def get_socios(n_accion,clasificacion):
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor(dictionary=True)
        cursor.execute("""
                       SELECT 
                            socios.cve_socio,
                            socios.posicion,
                            persona.nombre,
                            persona.apellido_paterno,
                            persona.apellido_materno                            
                       FROM socios 
                       INNER JOIN acciones ON socios.cve_accion=acciones.cve_accion
                       INNER JOIN persona ON socios.cve_persona=persona.cve_persona
                       WHERE numero_accion=%s AND clasificacion=%s
                       ORDER BY socios.posicion
                       """,(n_accion,clasificacion))
        data=cursor.fetchall()        
        # for base in data:
            # print(base)
        con.close_conexion()
        return data
    

    @staticmethod
    def get_colaborador(nomina):
        #SELECT 
        #    colaborador.id_colaborador,
	    #    socios.cve_socio,
        #    socios.posicion,
        #    persona.nombre,
        #    persona.apellido_paterno,
        #    persona.apellido_materno
        #FROM colaborador
        #INNER JOIN persona ON persona.cve_persona=colaborador.cve_persona
        #INNER JOIN socios ON socios.cve_persona=colaborador.cve_persona
        #WHERE colaborador.nomina=%(nomina)s OR colaborador.nomina_reloj=%(nomina)s AND  colaborador.estatus=1 LIMIT 1
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor(dictionary=True)
        cursor.execute("""
                        SELECT 
                            colaborador.id_colaborador,
	                        1 AS cve_socio,
                            0 AS posicion,
                            persona.nombre,
                            persona.apellido_paterno,
                            persona.apellido_materno
                        FROM colaborador
                        INNER JOIN persona ON persona.cve_persona=colaborador.cve_persona                        
                        WHERE colaborador.nomina=%(nomina)s OR colaborador.nomina_reloj=%(nomina)s AND  colaborador.estatus=1 LIMIT 1
                       """,{'nomina':nomina})
        data=cursor.fetchone()        
        # for base in data:
            # print(base)
        con.close_conexion()
        return data
    
    @staticmethod
    def get_foto(id_colaborador):
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor()
        cursor.execute("SELECT colaborador.foto FROM colaborador WHERE colaborador.id_colaborador=%s AND colaborador.estatus=1 LIMIT 1",(id_colaborador,))
        data=cursor.fetchone()
        con.close_conexion()
        return data
        

    @staticmethod
    def registrar_acceso(id_colaborador,imagen,distance,modelo,threshold):
        print("en el dao colaborador")
        print(id_colaborador)
        print(time.strftime('%Y-%m-%d %X'))
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor()
        cursor.execute("""
                        INSERT INTO colaborador_acceso(id_colaborador,hora_acceso,imagen_acceso,distance,modelo,threshold) VALUES(%s,%s,%s,%s,%s,%s)
                       """,(id_colaborador,time.strftime('%Y-%m-%d %X'),imagen,distance,modelo,threshold))                     
        con.conexion.commit()
        con.close_conexion()

        return cursor.rowcount
    
    @staticmethod
    def convertToBinaryData(filename):
        # Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData
    
    @staticmethod
    def insert_foto(id_colaborador):
        foto=UsuariosDao.convertToBinaryData("C:/xml_face/rostro_1237.jpg")
        print(foto)
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor()
        cursor.execute("""
                        UPDATE colaborador SET foto=%s WHERE id_colaborador=%s
                       """,(foto,id_colaborador))                   
        con.conexion.commit()
        con.close_conexion()

        return cursor.rowcount
    
    @staticmethod
    def get_colaboradores_fotos():
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor(dictionary=True)
        cursor.execute("SELECT colaborador.id_colaborador,colaborador.foto FROM colaborador WHERE colaborador.foto is not null AND colaborador.estatus=1")
        data=cursor.fetchall()
        con.close_conexion()
        return data
    
    @staticmethod
    def registrar_test_foto(id_colaborador,path,verific,distance,model,foto_path):
        foto_=UsuariosDao.convertToBinaryData(foto_path)
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor()
        cursor.execute("""
                        INSERT INTO test_foto(id_colaborador,imagen_compare,verific,distance,modelo,imagen_compare_file) VALUES(%s,%s,%s,%s,%s,%s)
                       """,(id_colaborador,path,verific,distance,model,foto_))                     
        con.conexion.commit()
        con.close_conexion()

        return cursor.rowcount
    
    @staticmethod
    def save_foto(id_colaborador,foto):
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor()
        cursor.execute("""
                        UPDATE colaborador SET foto=%s WHERE id_colaborador=%s
                       """,(foto,id_colaborador))                   
        con.conexion.commit()
        con.close_conexion()

        return cursor.rowcount
    
    @staticmethod
    def get_tolerancia_entrada(nomina):
        #select aplica_tiempo,hora_entrada from colaborador_horario where id_colaborador=42 and dia_entrada=(WEEKDAY(curdate())+1) order by hora_entrada limit 1;
        con=Conexion()
        con.get_conexion()
        cursor=con.conexion.cursor(dictionary=True)
        cursor.execute("""
                        SELECT 
                            aplica_tiempo,
                            IF( curtime() >= date_add(hora_entrada, INTERVAL -15 MINUTE),1,0) AS flag
                        FROM colaborador_horario
                        INNER JOIN colaborador ON colaborador_horario.id_colaborador = colaborador.id_colaborador
                        WHERE
                            nomina = %s AND dia_entrada = (WEEKDAY(CURDATE()) + 1)
                        ORDER BY hora_entrada
                        LIMIT 1;
                       """,(nomina,))
        data=cursor.fetchone()        
        # for base in data:
         
        con.close_conexion()
        return data

    
    