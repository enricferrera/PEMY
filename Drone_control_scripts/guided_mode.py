from pymavlink import mavutil
import time

# Conectar con el FC a través del puerto serial
print("Conectando con el FC...")
master = mavutil.mavlink_connection('/dev/serial0', baud=57600)
master.wait_heartbeat()
print(f"Conectado al sistema ({master.target_system}, componente {master.target_component})")

# Cambiar a GUIDED mode
master.mav.set_mode_send(
    master.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    4  # GUIDED mode en ArduCopter
)
print("Modo GUIDED solicitado")
time.sleep(2)

# Armar motores
print("Armando...")
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1, 0, 0, 0, 0, 0, 0
)

# Esperar hasta que esté armado
master.motors_armed_wait()
print("Dron ARMADO")

# Enviar comando de despegue a 0.3 metros (30 cm)
print("Despegando a 0.3 m...")
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,
    0, 0, 0, 0, 0, 0, 0.3  # Altura en metros
)

# Esperar unos segundos para que alcance la altura
print("Subiendo...")
time.sleep(10)

# Aterrizar suavemente
print("Iniciando aterrizaje...")
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND,
    0,
    0, 0, 0, 0, 0, 0, 0
)

# Esperar a que aterrice
time.sleep(10)

# Desarmar por seguridad
print("Desarmando...")
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    0, 0, 0, 0, 0, 0, 0
)
master.motors_disarmed_wait()
print("Dron DESARMADO y aterrizado")
