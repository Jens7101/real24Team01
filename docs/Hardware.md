# Hardware

## Board
---
[Pin Belegung](https://wiki.ost.ch/display/EDS/Pin+Mapping+flink2/)

## Sensoren
---
### Distance sensor VL53L0X
[doc](https://gitlab.ost.ch/tech/inf/public/real/software/python-scripts/driver/-/wikis/documentation)
- Test ausführen
```
python tofTest.py -g 0 -o 0
python Sensoren_Vorgeben.py -g 0 1 -o 2 3
```

### PA.HUB 2 Unit
Haben keinen Treiber. Laut Michael Zimmeli mit absprachen von Urs Graf: Hoher Zeitaufwand um Treiber zu erstellen.  

[Link Datasheet](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/datasheet/unit/TCA9548A_en.pdf)  
[Link Bus Infos](https://docs.m5stack.com/en/unit/pahub)  
[Link Git Code](https://github.com/m5stack/M5Stack/blob/master/examples/Unit/PaHUB_TCA9548A/PaHUB_TCA9548A.ino)  


### MPU6050
Beschreibung:  
- 3-axis gyroscope and 3-axis accelerometer  
Treiber von OST bereits erstellt  

[Link Rasperipy Webseite](https://pypi.org/project/mpu6050-raspberrypi/)  
[Link Datasheet](https://wiki.ost.ch/display/EDS/Sensors?preview=/346161158/413237316/MPU-6000-Datasheet1.pdf)  
[Link Arduino anschluss](https://components101.com/sensors/mpu6050-module)  



Befehl zum installieren:  
```python
# muss noch etwas davor gehängt werden, irgendwas mit Python
pip install mpu6050-raspberrypi
```

## Flink
---
Mann kann direkt auf dem Board die Sensoren ansteuern. Befhele dazu auf folgender Webseite:  
[Link Flink befehle für Terminal](https://api.flink-project.ch/doc/flinklib/html/md_doc_utils.html)  

