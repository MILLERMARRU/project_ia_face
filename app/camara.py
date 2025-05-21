import cv2

num_capturas = 4  # Número de capturas deseadas

mensajes = [
    "Intenta una expresión facial diferente.",
    "Intenta con un fondo distinto.",
    "Ahora cambiemos la iluminación.",
    "Intenta con una distancia diferente.",
]

def capturar_rostro():
    cap = cv2.VideoCapture(0)
    print("Presiona 's' para capturar la imagen")

    capturas = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al acceder a la cámara")
            break

        cv2.imshow("Captura de rostro", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):  # Capturar imagen
            capturas.append(frame.copy())
            print(f"Imagen capturada: {len(capturas)}")
            
            if len(capturas) < num_capturas:
                mensaje = mensajes[(len(capturas)-1) % len(mensajes)]
                print(mensaje)

            if len(capturas) >= num_capturas:
                print("Número máximo de capturas alcanzado")
                break        
        elif key == ord('q'):  # Salir sin capturar
            break

    cap.release()
    cv2.destroyAllWindows()
    return capturas
