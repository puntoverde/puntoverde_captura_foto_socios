import mysql.connector

class Conexion:

    conexion=None

    def get_conexion(self):
        self.conexion=mysql.connector.connect(host="192.168.2.111",user="dev_pv",password="pss_dEv_pv_18",database="punto_verde_v2")

    def close_conexion(self):
        self.conexion.close()