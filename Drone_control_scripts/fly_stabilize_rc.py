from pymavlink import mavutil
import time

# === CONFIGURACIÓN ===
SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 57600
THROTTLE_CHANNEL = 3  # Canal 3 = Throttle
THROTTLE_ARM = 1500   # Valor mínimo para armar
THROTTLE_TAKEOFF = 1600  # Aproximado para subir (ajustar si es necesario)
THROTTLE_IDLE = 1000  # Para aterrizar
DURATION_ASCENT = 3   # Segundos de subida
DURATION_DESCENT = 2  # Segundos de bajada

# === CONEXIÓN ===
print("🔌 Conectando con el dron...")
master = mavutil.mavlink_connection(SERIAL_PORT, baud=BAUD_RATE)
master.wait_heartbeat()
print(f"✅ Conectado con el sistema (ID: {master.target_system})")

# === CAMBIO A MODO STABILIZE ===
print("⚙️ Estableciendo modo STABILIZE...")
master.set_mode_apm('STABILIZE')

# === ARMADO ===
print("🛫 Armando motores...")
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1, 0, 0, 0, 0, 0, 0
)

# Esperar armado

master.motors_armed_wait()
print("✅ Dron ARMADO")

# PRESUBIDA
master.mav.rc_channels_override_send(
    master.target_system,
    master.target_component,
    65535, 65535, 1500, 65535,
    65535, 65535, 65535, 65535
)
time.sleep(DURATION_ASCENT)

# === SUBIDA ===
print("⬆️ Despegando (50cm aprox)...")
master.mav.rc_channels_override_send(
    master.target_system,
    master.target_component,
    65535, 65535, THROTTLE_TAKEOFF, 65535,
    65535, 65535, 65535, 65535
)
time.sleep(DURATION_ASCENT)

# === DESCENSO SUAVE ===
print("⬇️ Aterrizando...")
master.mav.rc_channels_override_send(
    master.target_system,
    master.target_component,
    65535, 65535, THROTTLE_IDLE, 65535,
    65535, 65535, 65535, 65535
)
time.sleep(DURATION_DESCENT)

# === PARAR OVERRIDE ===
print("🛑 Deteniendo control manual...")
master.mav.rc_channels_override_send(
    master.target_system,
    master.target_component,
    0, 0, 0, 0, 0, 0, 0, 0
)

# === DESARMAR ===
print("🛑 Desarmando...")
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    0, 0, 0, 0, 0, 0, 0
)
master.motors_disarmed_wait()
print("✅ Dron DESARMADO")

