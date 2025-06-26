import cv2
import numpy as np

# Parámetros del sistema
KNOWN_HEIGHT = 1.85         # Altura real estimada de la persona (metros)
FOCAL_LENGTH = 300          # Focal de la cámara (ajustada para tu móvil)
DESIRED_DISTANCE = 3.0      # Distancia deseada del dron al objetivo (metros)
MIN_AREA = 1000             # Área mínima del objeto rojo a considerar

def estimate_distance(bbox_height):
    if bbox_height == 0:
        return float('inf')
    return (KNOWN_HEIGHT * FOCAL_LENGTH) / bbox_height

def procesar_video(video_path, output_path="output_deteccion.avi"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Error al abrir el vídeo.")
        return

    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    center_x = width // 2

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detectar color rojo (dos rangos)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([179, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # Filtrar ruido
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.dilate(mask, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        instrucciones = ["Buscando objetivo rojo..."]

        if contours:
            main_cnt = max(contours, key=cv2.contourArea)
            if cv2.contourArea(main_cnt) > MIN_AREA:
                x, y, w, h = cv2.boundingRect(main_cnt)
                distance = estimate_distance(h)

                # Cálculo del centro y desplazamientos
                object_center_x = x + w // 2
                lateral_offset_px = object_center_x - center_x
                px_to_m = distance / FOCAL_LENGTH
                lateral_offset_m = lateral_offset_px * px_to_m
                forward_offset_m = distance - DESIRED_DISTANCE
                angle_deg = np.degrees(np.arctan2(lateral_offset_m, distance))

                instrucciones = []

                # 1. Instrucción lateral
                if abs(lateral_offset_m) > 0.1:
                    dir_lat = "derecha" if lateral_offset_m > 0 else "izquierda"
                    instrucciones.append(f" Mover {abs(lateral_offset_m):.2f} m a la {dir_lat}")
                else:
                    instrucciones.append(" Alineado lateralmente")

                # 2. Instrucción frontal
                if abs(forward_offset_m) > 0.1:
                    dir_fwd = "adelante" if forward_offset_m > 0 else "atrás"
                    instrucciones.append(f" Mover {abs(forward_offset_m):.2f} m hacia {dir_fwd}")
                else:
                    instrucciones.append(" A distancia correcta")

                # 3. Instrucción de rotación
                if abs(angle_deg) > 1:
                    dir_rot = "derecha" if angle_deg > 0 else "izquierda"
                    instrucciones.append(f" Girar {abs(angle_deg):.1f} grados a la {dir_rot}")
                else:
                    instrucciones.append("  Orientación correcta")

                # Dibujar bounding box y centro
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (object_center_x, y + h // 2), 5, (255, 0, 0), -1)
                cv2.putText(frame, f"Distancia: {distance:.2f} m", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Escribir instrucciones en el frame
        for i, msg in enumerate(instrucciones):
            cv2.putText(frame, msg, (10, height - 20 - i * 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        out.write(frame)

    cap.release()
    out.release()
    print(f"✅ Vídeo procesado y guardado en: {output_path}")

# 👉 Ruta al vídeo original
video_path = "video/video3.mp4"
procesar_video(video_path)
