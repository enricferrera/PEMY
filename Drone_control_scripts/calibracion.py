from pymavlink import mavutil
import time

# Conexión con la FC
master = mavutil.mavlink_connection('/dev/serial0', baud=57600)
master.wait_heartbeat()
print("Conectado a FC")

def set_motor_pwm(channel, pwm):
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0,
        channel,
        pwm,
        0,0,0,0,0
    )

print("Enviando señal máxima para calibrar ESCs (PWM=2000)")
for i in range(1,5):  # Asumiendo 4 motores en canales 1-4
    set_motor_pwm(i, 2000)
time.sleep(5)  # Tiempo para conectar la batería y que ESC escuche el pulso máximo

print("Enviando señal mínima para calibrar ESCs (PWM=1000)")
for i in range(1,5):
    set_motor_pwm(i, 1000)
time.sleep(5)  # Tiempo para confirmar calibración

print("Calibración terminada. Motores en stop")
