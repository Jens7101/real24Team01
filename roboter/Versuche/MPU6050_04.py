import math, time
from mpu6050 import mpu6050

# Verwende den korrekten Bus (prüfe mit: ls /dev/i2c-*)
bus_num = 0  # i2c-0 → MIO10/11

# Sensor initialisieren mit explizitem Bus
sensor = mpu6050(0x68, bus=bus_num)

dt = 0.02  # Abtastzeit (20 ms → 50 Hz)
alpha = 0.98  # Filterkonstante

# Anfangswerte aus Beschleunigung
accel = sensor.get_accel_data()
ax, ay, az = accel['x'], accel['y'], accel['z']
roll = math.degrees(math.atan2(ay, az))
pitch = math.degrees(math.atan2(-ax, math.sqrt(ay**2 + az**2)))

while True:
    start = time.time()
    
    # Gyroskopdaten
    gyro = sensor.get_gyro_data()
    gx, gy, gz = gyro['x'], gyro['y'], gyro['z']
    
    # Integriere Gyro-Daten
    roll_gyro = roll + gx * dt
    pitch_gyro = pitch + gy * dt
    
    # Beschleunigungsdaten
    accel = sensor.get_accel_data()
    ax, ay, az = accel['x'], accel['y'], accel['z']
    roll_acc = math.degrees(math.atan2(ay, az))
    pitch_acc = math.degrees(math.atan2(-ax, math.sqrt(ay**2 + az**2)))
    
    # Komplementärfilter
    roll = alpha * roll_gyro + (1 - alpha) * roll_acc
    pitch = alpha * pitch_gyro + (1 - alpha) * pitch_acc
    
    print(f"Roll: {roll:.2f}°, Pitch: {pitch:.2f}°")
    
    time.sleep(max(0, dt - (time.time() - start)))
