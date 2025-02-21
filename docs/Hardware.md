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
Haben keinen Treiber. Laut Michael Zimmeli mit absprachen von Urs Graf: Hoher Zeitaufwand um Treiber zu erstellen

### MPU6050
Beschreibung:  
- 3-axis gyroscope and 3-axis accelerometer  
Treiber von OST bereits erstellt  
[Datasheet](https://wiki.ost.ch/display/EDS/Sensors?preview=/346161158/413237316/MPU-6000-Datasheet1.pdf)
