from app.embedings import crear_embedding
import cv2

# Leer imagen desde archivo o captura
img = cv2.imread("billie.jpg")
embedding = crear_embedding(img)

print("Embedding generado:", embedding)
