import cv2
from insightface.app import FaceAnalysis

# Inicializar la aplicación de InsightFace, forzando el uso de la GPU (CUDA)
app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider'])  # Utilizando CUDA para la GPU
app.prepare(ctx_id=0)  # ctx_id=0 para usar la GPU si está disponible, usa 1 para CPU si no se quiere usar la GPU

# Cargar la imagen de prueba (reemplaza 'samq.jpg' por la ruta de tu imagen)
img = cv2.imread('img_test/samq.jpg')


# Detectar rostros en la imagen
faces = app.get(img)

# Dibujar un rectángulo alrededor de cada rostro detectado
for face in faces:
    bbox = face.bbox  # Coordenadas del cuadro delimitador
    cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), 
                  (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)

# Mostrar la imagen con los rostros detectados
cv2.imshow("Rostros detectados", img)
cv2.waitKey(0)
cv2.destroyAllWindows()