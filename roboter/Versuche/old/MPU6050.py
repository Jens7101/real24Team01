from mpu6050 import mpu6050

sensor = mpu6050(0x68)  # Oder 0x69, je nach AD0

accel_data = sensor.get_accel_data()
gyro_data = sensor.get_gyro_data()
temp = sensor.get_temp()

print("Beschleunigung:", accel_data)
print("Gyro:", gyro_data)
print("Temperatur:", temp)