# Real24Team01
# GitHub einrichten
---
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
---
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
```
pip freeze > requirements.txt
```
3. Auf Github laden
4. Danach müssen die anderen Benutzer die venv aktualisieren
```
venv/Scripts/activate
```
```
pip install -r requirements.txt
```

# MkDocs installieren
---
## Use ov MkDocs


- If MkDocs is installed inside a **virtual environment**, activate it first:
```Powershel
venv\Scripts\Activate
```
- Then Rund
```Powershel
mkdocs serve
```
## Installation
---
### Make a new respository
- Go to Github and Create a new respository. Name it. Chose **.gitignare template Python**  and **GNU General Public Licences v3.0**. Then create it.
### Cloce the respository
- copie **SHH** Url
- Open Terminal
```
git clone 'URL'
```
- go into the generatet folder
```
cd 'Projekt Name'
```
- create the venv enviorment
```
python -m venv venv
```
- activate venv
```
venv\Scripts\Activate
```
### Instal MkDocscode .
```
pip install mkdocs-material
```
### Visual studio code
- open visual studio code
```
code .
```
### Create MkDocs
- create mkDocs folder
```
mkdocs new .
```
- If MkDocs is installed inside a **virtual environment**, activate it first:
```Powershel
venv\Scripts\Activate
```
- Then Rund
```Powershel
mkdocs serve
```
#### Chanche the Yaml file
- See this yaml file
## Debugging
---
### OSError: no library called "cairo-2" was found
##### **Option 1: Installiere Cairo über MSYS2 (empfohlen)**

1. Lade **MSYS2** von der offiziellen Seite herunter:  
    👉 [https://www.msys2.org/](https://www.msys2.org/)
2. Installiere MSYS2 und öffne die **MSYS2 "MinGW 64-bit" Shell**.
3. Führe folgenden Befehl aus:
```
pacman -S mingw-w64-x86_64-cairo
```
**Füge den Cairo-Ordner zu den Umgebungsvariablen hinzu**:

- Kontrolliere ob der Cairo-Installationsordner existiert. (`C:\msys64\mingw64\bin`).
- Win+R
```
SystemPropertiesAdvanced
```
- Wähle unter **"User variables 'user'"** die **"Path"**-Variable und klicke auf **Bearbeiten**.
- Klicke auf **Neu** und füge den Pfad hinzu:
```
C:\msys64\mingw64\bin
```
- Kontrolliere ob Cairo funktioniert
```
where cairo.dll
```
- Wenn Datei gefunden -> Io
