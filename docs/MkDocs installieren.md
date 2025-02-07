# MkDocs installieren
# Use ov MkDocs
---

- If MkDocs is installed inside a **virtual environment**, activate it first:
```Powershel
venv\Scripts\Activate
```
- Then Rund
```Powershel
mkdocs serve
```
# Installation
---
## Make a new respository
- Go to Github and Create a new respository. Name it. Chose **.gitignare template Python**  and **GNU General Public Licences v3.0**. Then create it.
## Cloce the respository
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
## Instal MkDocscode .
```
pip install mkdocs-material
```
## Visual studio code
- open visual studio code
```
code .
```
## Create MkDocs
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
### Chanche the Yaml file
- See this yaml file
# Debugging
---
## OSError: no library called "cairo-2" was found
#### **Option 1: Installiere Cairo über MSYS2 (empfohlen)**

1. Lade **MSYS2** von der offiziellen Seite herunter:  
    👉 [https://www.msys2.org/](https://www.msys2.org/)
2. Installiere MSYS2 und öffne die **MSYS2 MinGW 64-bit Shell**.
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
