import cv2

# Abrir la cámara (0 es generalmente la cámara por defecto)
cap = cv2.VideoCapture(0)

# Verificar que la cámara se abrió correctamente
if not cap.isOpened():
    print("❌ No se pudo abrir la cámara.")
    exit()

print("✅ Cámara abierta. Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Error al capturar el frame.")
        break

    # Mostrar el frame
    cv2.imshow("Vista de la cámara", frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar ventanas
cap.release()
cv2.destroyAllWindows()
