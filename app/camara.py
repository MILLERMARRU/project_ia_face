import cv2

def capturar_rostro():
    cap = cv2.VideoCapture(0)
    print("Presiona 's' para capturar la imagen")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al acceder a la cámara")
            break

        cv2.imshow("Captura de rostro", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):  # Capturar imagen
            cap.release()
            cv2.destroyAllWindows()
            return frame
        elif key == ord('q'):  # Salir sin capturar
            break

    cap.release()
    cv2.destroyAllWindows()
    return None
