import pymysql
import pymysql.cursors

def obtener_conexion():
    return pymysql.connect(
        host='localhost',         
        user='root',              
        password='Sam06092003',    
        database='ucss',
        cursorclass=pymysql.cursors.DictCursor
)
