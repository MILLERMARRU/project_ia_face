# app/verificar.py
from app.camara import capturar_rostro
from app.embedings import generar_embedding
from app.utils import calcular_similitud
from db.model_user import obtener_todos_los_usuarios

def verificar_usuario():
    print("=== VERIFICACIÓN DE ASISTENCIA ===")
    print("Abriendo cámara...")
    imagen = capturar_rostro()
    if imagen is None:
        print("❌ No se capturó imagen.")
        return

    nuevo_embedding = generar_embedding(imagen)
    if nuevo_embedding is None:
        print("❌ No se pudo generar embedding.")
        return

    usuarios = obtener_todos_los_usuarios()

    umbral = 0.55  # entre 0.5 y 0.6 para embeddings reales
    mejor_similitud = 0
    usuario_encontrado = None

    for usuario in usuarios:
        similitud = calcular_similitud(nuevo_embedding, usuario['embedding'])
        if similitud > mejor_similitud and similitud >= umbral:
            mejor_similitud = similitud
            usuario_encontrado = usuario

    if usuario_encontrado:
        print(f"✅ Usuario identificado: {usuario_encontrado['nombre']} ({usuario_encontrado['codigo']})")
        print(f"Facultad: {usuario_encontrado['facultad']} | Carrera: {usuario_encontrado['carrera']}")
        print(f"Similitud: {mejor_similitud:.4f}")
    else:
        print("❌ No se encontró coincidencia.")
