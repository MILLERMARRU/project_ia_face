import numpy as np
from insightface.app import FaceAnalysis

# Inicialización global del modelo con CUDA (mismo enfoque que tu actual código)
try:
    detector = FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'])
    detector.prepare(ctx_id=0, det_size=(640, 640))
except Exception as e:
    raise RuntimeError(f"❌ Error cargando InsightFace con CUDA: {e}")

def crear_embeddings_multiples(frame: np.ndarray):
    """
    Detecta múltiples rostros en la imagen y devuelve una lista de objetos que contienen:
    - .embedding (vector de características)
    - .bbox (coordenadas del rostro)
    """
    # Convertimos de BGR a RGB (InsightFace requiere RGB)
    frame_rgb = frame[:, :, ::-1]

    faces = detector.get(frame_rgb)  # lista de rostros detectados
    return faces  # cada face tiene: .embedding, .bbox, .landmark, etc.