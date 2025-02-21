# Real Projekt PV-Reinigungsroboter

# Putty
---
## Programm ausführen mit debuger
```Python
python -m debugpy --listen 192.168.7.2:6000 --wait-for-client ./
```
## Bus
Buss anzeigen
```
i2cdetect -r -y 0
```


## Programm unterbrechen
- Ctrl + z