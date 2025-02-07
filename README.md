# Real24Team01
## GitHub einrichten
1. Lade Git für Windows herunter und installiere es.
2. Git konfigurieren  
- Öffne Git Bash oder die Eingabeaufforderung und gib Folgendes ein:  
git config --global user.name "Dein Name"  
git config --global user.email "deine@email.com"  
- Überprüfe die Konfiguration mit:  
git config --list
## Powershel Configurieren
1. Neun Ordner erstellen und Öffnen
2. Auf Source Control gehen
<img src="https://github.com/user-attachments/assets/ab44d7bd-76c3-478a-a3f8-c7cbf26464dd" alt="image" style="width:50%; height:auto;">

4. Remote einrichten  
- Auf Remote/Add Remote gehen.  
<img src="https://github.com/user-attachments/assets/426b066c-251d-4731-94b6-69b60e20bda4" alt="image" style="width:50%; height:auto;">

- Auf Add remote frome Github gehen.  
- Freigegebenen Ordner auswählen  
- Beliebigen Remote Name eingeben  
- Auf den Folgenen abschnitt Klicken und den Remote auswählen  
<img src="https://github.com/user-attachments/assets/e0d8e7c4-201b-4f47-a223-749a45855ad7" alt="image" style="width:50%; height:auto;">

- Dan refresh und anschliessend Commit auswählen  
<img src="https://github.com/user-attachments/assets/3da7c544-ecfd-4612-85ae-8c482a8d015b" alt="image" style="width:50%; height:auto;">  

## Virtuelle Umgebung venv erstellen/aktualisieren
### Neu erstellen
1. Projekt klonen
2. In Visual Studio Verzeichnis auswählen
3. Im Terminal folgende Eingaben machen
```
python -m venv venv
```
```
venv/Scripts/activate
```
```
pip install -r requirements.txt
```

### Aktuallisieren nachdem neue Bibliothek installiert wurde
1. Im Terminal folgende Eingabe machen
   - pip freeze > requirements.txt
2. Auf Github laden
3. Danach müssen die anderen Benutzer die venv aktualisieren
   - venv/Scripts/activate
   - pip install -r requirements.txt
