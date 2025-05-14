import pymysql
import pymysql.cursors

def obtener_conexion():
    return pymysql.connect(
        host='localhost',         
        user='root',              
        password='123456',    
        database='ucss',
        cursorclass=pymysql.cursors.DictCursor
)
