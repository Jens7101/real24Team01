# Real Projekt PV-Reinigungsroboter

# Putty
---
## Programm ausführen mit debuger
```Python
python -m debugpy --listen 192.168.7.2:6000 --wait-for-client ./
```
Wenn debugger nicht erneut ausgeführt werden kann: (noch nicht klar was es für auswirkungen auf das Programm hat.)
```
# könnte sein das auch dinge beendet werden von denen ich nicht will, dass sie beendet weerden
sudo pkill -f python

# andernfals geht vieleicht dies
sudo kill -9 <PID>

```

## Bus
Buss anzeigen
```
i2cdetect -r -y 0
```


## Programm unterbrechen
- Ctrl + z