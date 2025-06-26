from pymavlink import mavutil
import time

print("🔌 Conectando al controlador de vuelo...")
master = mavutil.mavlink_connection('/dev/serial0', baud=57600)
master.wait_heartbeat()
print(f"✅ Conectado al sistema (ID: {master.target_system}, componente: {master.target_component})")

# Cambiar a modo STABILIZE
print("⚙️ Cambiando a moddo STABILIZE..")
master.set_mode('STABILIZED')
time.sleep(1)

# Enviar comando de armado
print("🛫 Enviando comando de ARMADO...")
master.arducopter_arm()

# Escuchar mensajes por unos segundos
print("🛰️ Escuchando mensajes de estado por 10 segundos...")
start = time.time()
armed = False

while time.time() - start < 10:
    msg = master.recv_match(blocking=True, timeout=1)
    if msg:
        if msg.get_type() == "HEARTBEAT":
            if msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
                armed = True
        elif msg.get_type() == "STATUSTEXT":
            print(f"📢 [{msg.severity}] {msg.text}")

if armed:
    print("✅ ¡Dron ARMADO correctamente!")
else:
    print("❌ El dron NO se armó.")

# Desarmar (opcional para pruebas)
print("🛑 Desarmando...")
master.arducopter_disarm()
