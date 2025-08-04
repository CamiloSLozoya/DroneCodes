import cv2
import numpy as np

def adjust_gamma(image, gamma=1.5):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(256)]).astype("uint8")
    return cv2.LUT(image, table)

# Configuración de la cámara
cap = cv2.VideoCapture(1)  # Captura de video desde la cámara 0
d = 0
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)  # ancho
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)  # alto

while True:
    ret, frame = cap.read()  # Lee un fotograma de la cámara
    if not ret:
        break

    # Ajuste de brillo/saturación
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = np.clip(v * 0.6, 0, 255).astype(np.uint8)  # reducir brillo
    s = np.clip(s * 1.7, 0, 255).astype(np.uint8)  # aumentar saturación
    hsv_adjusted = cv2.merge((h, s, v))
    frame = cv2.cvtColor(hsv_adjusted, cv2.COLOR_HSV2BGR)

    # Ajuste dinámico de gamma según el brillo
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    gamma = 1.5 if mean_brightness < 80 else 0.8
    frame = adjust_gamma(frame, gamma=gamma)

    # Nombre del archivo con contador
    filename = "file_" + str(d) + ".jpg"
    
    # Mostrar la imagen en ventana
    cv2.imshow('Original', frame)
    
    # Detección de teclas
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('f'):
        cv2.imwrite('C:\\Users\\camil\\Documents\\GitHub\\DroneCodes\\Images\\feril' + filename, frame)
        d += 1
        print(f"Imagen fértil guardada: {filename}")
    elif key == ord('j'):
        cv2.imwrite('C:\\Users\\camil\\Documents\\GitHub\\DroneCodes\\Images\\notfertil' + filename, frame)
        d += 1
        print(f"Imagen no fértil guardada: {filename}")
    elif key == ord('q'):
        break

# Guardar una última imagen antes de salir
#cv2.imwrite('C:\\Users\\Usuario\\OneDrive\\Documentos\\Programacion\\phyton\\Vision\\imagenes\\imagen1.jpg', frame)
cap.release()
cv2.destroyAllWindows()