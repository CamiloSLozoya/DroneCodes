import pigpio
import time

# Iniciar pigpio
pi = pigpio.pi()
#Cambiar este numero dependiendo de los ciclos deseados
n=5
if not pi.connected:
    print("No se pudo conectar a pigpiod")
    exit()

servo_pin = 18  # GPIO18 = pin físico 12

def set_angle(angle):
    angle = max(0, min(180, angle))
    pulse = 500 + int((angle / 180) * 2000)
    pi.set_servo_pulsewidth(servo_pin, pulse)
    print(f"⟶ Ángulo: {angle}° | PWM: {pulse} μs")

try:
    print("🌀 Ejecutando secuencia 0→5, 90→95→90, y regreso a 0\n")
    for i in range(1,n+1):
        set_angle(90)
        time.sleep(0.01)
        set_angle(95)
        time.sleep(0.01)
        set_angle(90)
        time.sleep(0.01)
        set_angle(0)
        time.sleep(0.01)
        set_angle(5)
        time.sleep(0.01)
        set_angle(0)
        time.sleep(0.2)
        print(f"\n secuencia n {i}")
    print("\n✅ Secuencia completada")

except KeyboardInterrupt:
    print("\n⛔ Interrumpido por el usuario")

finally:
    print("🛑 Apagando PWM")
    pi.set_servo_pulsewidth(servo_pin, 0)
    pi.stop()