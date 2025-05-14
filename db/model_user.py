from db.conexion import obtener_conexion
import json
import numpy as np
import pymysql

def guardar_usuario(nombre, codigo, facultad, carrera, embedding_np):
    """
    Guarda un usuario con su embedding facial (como BLOB).
    """
    embedding_bin = embedding_np.astype(np.float32).tobytes()
    
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = """
            INSERT INTO usuarios (nombre, codigo, facultad, carrera, embedding)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, codigo, facultad, carrera, embedding_bin))
        conexion.commit()
    finally:
        conexion.close()



def obtener_usuarios_con_embedding_blob():
    """
    Retorna usuarios con embedding BLOB válido de 512 valores float32.
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT id, nombre, codigo, facultad, carrera, embedding FROM usuarios")
            resultados = cursor.fetchall()

            usuarios = []
            for usuario in resultados:
                emb_raw = usuario['embedding']

                if isinstance(emb_raw, (bytes, bytearray)) and len(emb_raw) == 2048:
                    try:
                        emb = np.frombuffer(emb_raw, dtype=np.float32)
                        if emb.shape == (512,):
                            usuario['embedding'] = emb
                            usuarios.append(usuario)
                        else:
                            print(f"⚠️ Embedding tamaño inválido: {usuario['nombre']} ({emb.shape})")
                    except Exception as e:
                        print(f"❌ Error al procesar embedding de {usuario['nombre']}: {e}")
                else:
                    print(f"❌ Embedding inválido para usuario: {usuario.get('nombre', '[Sin Nombre]')}")

            return usuarios
    finally:
        conexion.close()






def buscar_usuario_por_codigo(codigo):
    """
    Busca un usuario por su código y devuelve su info + embedding.
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE codigo = %s", (codigo,))
            fila = cursor.fetchone()
            if not fila:
                return None

            columnas = [desc[0] for desc in cursor.description]
            usuario = dict(zip(columnas, fila))

            emb_raw = usuario['embedding']
            if isinstance(emb_raw, str):
                usuario['embedding'] = np.array(json.loads(emb_raw), dtype=np.float32)
            else:
                usuario['embedding'] = np.frombuffer(emb_raw, dtype=np.float32)

            return usuario
    finally:
        conexion.close()
