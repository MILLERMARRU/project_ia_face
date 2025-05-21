
import numpy as np
from insightface.app import FaceAnalysis

# Inicialización global del modelo con CUDA
try:
    app = FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
except Exception as e:
    raise RuntimeError(f"❌ Error cargando InsightFace con CUDA: {e}")

def crear_embedding(img: np.ndarray) -> np.ndarray:
    """
    Procesa una imagen y retorna el embedding del primer rostro detectado.

    Args:
        img (np.ndarray): Imagen en formato BGR (como la da OpenCV)

    Returns:
        np.ndarray: Embedding de 512 dimensiones

    Raises:
        ValueError: Si no se detecta ningún rostro
    """
    # Convertir de BGR a RGB (InsightFace requiere RGB)
    img_rgb = img[:, :, ::-1]

    # Obtener rostros
    faces = app.get(img_rgb)
    
    if not faces:
        raise ValueError("❌ No se detectaron rostros en la imagen proporcionada.")

    
    return faces[0].embedding