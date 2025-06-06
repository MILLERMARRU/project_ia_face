from conexion import obtener_conexion
import json
import numpy as np
import pymysql


def guardar_embedding(embedding, id_usuario, cursor=None):
    """
    Guarda un embedding facial (como BLOB) asociado a un usuario en la tabla embeddings.
    Si se pasa un cursor, lo usa; si no, crea su propia conexión.
    """
    embedding_bin = embedding.astype(np.float32).tobytes()
    if cursor is not None:
        sql = """
        INSERT INTO embeddings (idUser, embedding)
        VALUES (%s, %s)
        """
        cursor.execute(sql, (id_usuario, embedding_bin))
    else:
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor_local:
                sql = """
                INSERT INTO embeddings (idUser, embedding)
                VALUES (%s, %s)
                """
                cursor_local.execute(sql, (id_usuario, embedding_bin))
            conexion.commit()
        finally:
            conexion.close()


def guardar_usuario(nombre, codigo, facultad, carrera, embeddings):
    """
    Guarda un usuario con su embedding facial promediado (como BLOB)
    y almacena todos los embeddings individuales en la tabla embeddings.
    """
    mean_embedding = np.mean(embeddings, axis=0).astype(np.float32)
    mean_embedding_bin = mean_embedding.tobytes()

    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Inserta el usuario con el embedding promedio
            sql = """
            INSERT INTO usuarios (nombre, codigo, facultad, carrera, mean_embedding)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, codigo, facultad, carrera, mean_embedding_bin))
            id_usuario = cursor.lastrowid

            for emb in embeddings:
                # Guarda cada embedding individual usando el mismo cursor
                guardar_embedding(emb, id_usuario, cursor=cursor)
        conexion.commit()
    finally:
        conexion.close()


def obtener_embeddings(tipo='velocidad'):
    """
    Obtiene embeddings de la base de datos.
    tipo:
        - 'precision': retorna todos los embeddings individuales con datos de usuario.
        - 'velocidad': retorna solo los usuarios con su embedding promedio.

    Resultados y usuarios son prácticamente lo mismo en ambos enfoques. La diferencia está en que precisión se enfoca en los embeddings individuales,
    mientras que velocidad se enfoca en los embeddings promediados de los usuarios. Pero ambos contienen la información del usuario.
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            if tipo == 'precision':
                cursor.execute("""
                    SELECT e.idEmb, e.embedding, u.idUser, u.nombre, u.codigo, u.facultad, u.carrera
                    FROM embeddings e
                    INNER JOIN usuarios u ON e.idUser = u.idUser
                """)
                resultados = cursor.fetchall()
                embeddings = []
                for resultado in resultados:
                    emb_raw = resultado['embedding']
                    if isinstance(emb_raw, (bytes, bytearray)) and len(emb_raw) == 2048: #comprobamos la existencia de 4 embeddings de 512
                        try:
                            emb = np.frombuffer(emb_raw, dtype=np.float32)
                            if emb.shape == (512,):
                                resultado['embedding'] = emb
                                embeddings.append(resultado)
                            else:
                                print(f"⚠️ Embedding tamaño inválido: {resultado['idUser']} ({emb.shape})")
                        except Exception as e:
                            print(f"❌ Error al procesar embedding de {resultado['idUser']}: {e}")
                    else:
                        print(f"❌ Embedding inválido para usuario: {resultado.get('idUser', '[Sin ID]')}")
                return embeddings

            elif tipo == 'velocidad':
                cursor.execute("""
                    SELECT idUser, nombre, codigo, facultad, carrera, mean_embedding
                    FROM usuarios
                """)
                resultados = cursor.fetchall()
                embeddings = []
                for usuario in resultados:
                    emb_raw = usuario['mean_embedding']
                    if isinstance(emb_raw, (bytes, bytearray)) and len(emb_raw) == 2048:
                        try:
                            emb = np.frombuffer(emb_raw, dtype=np.float32)
                            if emb.shape == (512,):
                                usuario['mean_embedding'] = emb
                                embeddings.append(usuario)
                            else:
                                print(f"⚠️ Embedding tamaño inválido: {usuario['nombre']} ({emb.shape})")
                        except Exception as e:
                            print(f"❌ Error al procesar embedding de {usuario['nombre']}: {e}")
                    else:
                        print(f"❌ Embedding inválido para usuario: {usuario.get('nombre', '[Sin Nombre]')}")
                return embeddings

            else:
                raise ValueError("Tipo debe ser 'individual' o 'promedio'")
    finally:
        conexion.close()