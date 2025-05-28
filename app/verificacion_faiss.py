import faiss
import numpy as np
from db.model_user import obtener_usuarios_con_embedding_blob  # función nueva y segura

# Normalizar para similitud coseno
def normalizar(vec):
    norm = np.linalg.norm(vec)
    return vec / norm if norm != 0 else vec

# Índice y mapeo global
index = faiss.IndexFlatIP(512)  # IP = Inner Product → simula similitud coseno con vectores normalizados
usuarios_indexados = []

def construir_indice():
    global index, usuarios_indexados
    index.reset()
    usuarios_indexados.clear()

    usuarios = obtener_usuarios_con_embedding_blob()  # nueva función robusta
    print(f"Usuarios obtenidos: {len(usuarios)}") 
    for usuario in usuarios:
        emb = normalizar(usuario['embedding'].astype(np.float32))
        index.add(emb.reshape(1, -1))  # FAISS espera (n, d)
        usuarios_indexados.append(usuario)

def buscar_usuario_por_embedding(embedding_consulta: np.ndarray, umbral: float = 0.4):
    if index.ntotal == 0:
        raise RuntimeError("El índice FAISS está vacío. Ejecuta construir_indice() primero.")

    emb_norm = normalizar(embedding_consulta.astype(np.float32)).reshape(1, -1)
    similitudes, indices = index.search(emb_norm, 1)  # top-1

    sim = float(similitudes[0][0])
    idx = int(indices[0][0])

    if sim >= umbral:
        return usuarios_indexados[idx], sim
    else:
        return None, sim
