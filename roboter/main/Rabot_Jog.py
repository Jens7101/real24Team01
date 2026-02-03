import socket
import time
import keyboard         #pip install keyboard

# Funktionen für REST-Kommunikation
def send_rest_command(ip, index, subindex, hex_value):
    path = f"/od/{index:04X}/{subindex:02X}"
    body = f'"{hex_value}"'
    headers = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {ip}\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{body}"
    )
    try:
        with socket.create_connection((ip, 80), timeout=2) as sock:
            sock.sendall(headers.encode())
            sock.recv(4096)
    except Exception as e:
        print(f"{ip} → Fehler: {e}")

def read_signed_rpm(ip, index, subindex):
    path = f"/od/{index:04X}/{subindex:02X}"
    headers = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {ip}\r\n"
        "Accept: application/json\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    try:
        with socket.create_connection((ip, 80), timeout=2) as sock:
            sock.sendall(headers.encode())
            response = sock.recv(4096).decode()
            if '"' in response:
                hex_value = response.split('"')[1]
                value = int(hex_value, 16)
                if value > 0x7FFFFFFF:
                    value -= 0x100000000
                return value
    except Exception as e:
        print(f"{ip} → Fehler beim Lesen: {e}")
    return None

def dec_to_hex_8(value):
    return f"{value & 0xFFFFFFFF:08X}"

def clamp_rpm(value):
    if abs(value) < 150:
        return 0
    return max(-3000, min(3000, value))

def clamp_acc_dcc(value):
    return max(100, min(8000, value))

# IP-Adressen
left_crawler = "192.168.7.10"
right_crawler = "192.168.7.11"
crawler_ips = [left_crawler, right_crawler]
# Bürsten IPs
front_brush = "192.168.7.12"
rear_brush = "192.168.7.13"

brushes_ips = [front_brush]                     # Nur eine Bürste (als Liste)
#brushes_ips = [front_brush, rear_brush]        # Mit beiden Bürsten

# Crawler-Parameter
crawler_rpm = 750
crawler_acc = 5000
crawler_dcc = 5000
brake_active = False

# Auto-Modus Parameter
auto_sequence_running = False
auto_sequence_cycles = 0  # Zählt durchgeführte Durchläufe
auto_sequence_target = 3  # Anzahl gewünschter Durchläufe

# Sequenz-Parameter (einfach änderbar)
seq_straight_speed = 500   # Geschwindigkeit beim Geradeausfahren (einfach anpassen)
seq_turn_speed = 250       # Geschwindigkeit bei Drehungen (wie gewünscht)
seq_sec_5 = 5.0
seq_sec_2 = 2.0
seq_sec_6 = 6.0
seq_turn = 1.5
seq_pause = 0.2           # Pause bei jeder Änderung

# Bürsten-Parameter
brush_rpm = 1000
brush_acc = 5000
brush_dcc = 5000
brush_running = False

# Streckenmessung
measuring = False
distance = {left_crawler: 0.0, right_crawler: 0.0}
last_time = time.time()
wheel_circumference = 0.009  # z. B. 10 cm Durchmesser

def update_crawler_acc_dcc():
    global crawler_acc, crawler_dcc
    crawler_acc = clamp_acc_dcc(crawler_acc)
    crawler_dcc = clamp_acc_dcc(crawler_dcc)
    for ip in crawler_ips:
        send_rest_command(ip, 0x6083, 0x00, dec_to_hex_8(crawler_acc))
        send_rest_command(ip, 0x6084, 0x00, dec_to_hex_8(crawler_dcc))

def set_crawler_rpm(left_rpm, right_rpm):
    left_rpm = clamp_rpm(left_rpm)
    right_rpm = clamp_rpm(right_rpm)
    send_rest_command(left_crawler, 0x60FF, 0x00, dec_to_hex_8(left_rpm))
    send_rest_command(right_crawler, 0x60FF, 0x00, dec_to_hex_8(right_rpm))

def stop_crawlers():
    set_crawler_rpm(0, 0)

def set_brush_rpm(rpm_value):
    rpm_value = clamp_rpm(rpm_value)
    for ip in brushes_ips:
        send_rest_command(ip, 0x60FF, 0x00, dec_to_hex_8(rpm_value))

# Initialisierung
update_crawler_acc_dcc()
for ip in crawler_ips:
    send_rest_command(ip, 0x6060, 0x00, "03")
    send_rest_command(ip, 0x6040, 0x00, "0006")
    send_rest_command(ip, 0x6040, 0x00, "0007")
    send_rest_command(ip, 0x6040, 0x00, "000F")
    time.sleep(0.2)


mode = "manual"  # oder "auto"
def print_mode_hint():
    if mode == "manual":
        print("""
╔════════════════════════════════════════════════════════════╗
║ MANUELLER MODUS                                            ║
╠════════════════════════════════════════════════════════════╣
║ ↑ ↓ ← → → Fahren (Richtung)                                ║
║ A / D → Raupen-RPM verringern / erhöhen                    ║
║ Q / E → Raupen-ACC/DCC verringern / erhöhen                ║
║ B → Bremse toggeln                                         ║
║ G → Drehzahl anzeigen                                      ║
║ J → Distanzmessung starten / stoppen                       ║
║ K → Distanz zurücksetzen                                   ║
║ L → Distanz anzeigen                                       ║
║ O → Bürste starten / stoppen                               ║
║ M → Modus wechseln                                         ║
║ ESC → Programm beenden                                     ║
╚════════════════════════════════════════════════════════════╝
""")
    else:
        print("""
╔════════════════════════════════════════════════════════════╗
║ AUTOMATISCHER MODUS                                        ║
╠════════════════════════════════════════════════════════════╣
║ SPACE → Ablauf starten                                     ║
║ M → Modus wechseln                                         ║
║ ESC → Programm beenden                                     ║
╚════════════════════════════════════════════════════════════╝
""")

print_mode_hint()

try:
    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        # Sofortiger Abbruch mit ESC — unabhängig vom Modus
        if keyboard.is_pressed("esc"):
            print("Beende Steuerung...")
            break
        if measuring:
            for ip in crawler_ips:
                rpm_val = read_signed_rpm(ip, 0x606C, 0x00)
                if rpm_val is not None:
                    rps = rpm_val / 60.0
                    distance[ip] += rps * wheel_circumference * dt
        if keyboard.is_pressed("m"):
            mode = "auto" if mode == "manual" else "manual"
            print_mode_hint()
            time.sleep(0.3)
        # Bürstensteuerung immer prüfen (funktioniert in beiden Modi)
        if keyboard.is_pressed("o"):
            brush_running = not brush_running
            if brush_running:
                print("Bürste gestartet.")
                for ip in brushes_ips:
                    send_rest_command(ip, 0x6060, 0x00, "03")
                    send_rest_command(ip, 0x6040, 0x00, "0006")
                    send_rest_command(ip, 0x6040, 0x00, "0007")
                    send_rest_command(ip, 0x6040, 0x00, "000F")
                set_brush_rpm(brush_rpm)
            else:
                print("Bürste gestoppt.")
                for ip in brushes_ips:
                    send_rest_command(ip, 0x60FF, 0x00, dec_to_hex_8(0))
            time.sleep(0.2)
        elif keyboard.is_pressed("y"):
            brush_rpm = min(3000, brush_rpm + 100)
            print(f"Bürsten-RPM erhöht: {brush_rpm}")
            if brush_running:
                set_brush_rpm(brush_rpm)
            time.sleep(0.2)
        elif keyboard.is_pressed("c"):
            brush_rpm = max(150, brush_rpm - 100)
            print(f"Bürsten-RPM verringert: {brush_rpm}")
            if brush_running:
                set_brush_rpm(brush_rpm)
            time.sleep(0.2)
        if mode == "manual":
            # Crawler-Steuerung
            if keyboard.is_pressed("up") and keyboard.is_pressed("right"):
                set_crawler_rpm(crawler_rpm, max(150, int(crawler_rpm * 0.5)))
            elif keyboard.is_pressed("up") and keyboard.is_pressed("left"):
                set_crawler_rpm(max(150, int(crawler_rpm * 0.5)), crawler_rpm)
            elif keyboard.is_pressed("down") and keyboard.is_pressed("right"):
                set_crawler_rpm(-crawler_rpm, -max(150, int(crawler_rpm * 0.5)))
            elif keyboard.is_pressed("down") and keyboard.is_pressed("left"):
                set_crawler_rpm(-max(150, int(crawler_rpm * 0.5)), -crawler_rpm)
            elif keyboard.is_pressed("up"):
                set_crawler_rpm(crawler_rpm, crawler_rpm)
            elif keyboard.is_pressed("down"):
                set_crawler_rpm(-crawler_rpm, -crawler_rpm)
            elif keyboard.is_pressed("left"):
                set_crawler_rpm(-crawler_rpm, crawler_rpm)
            elif keyboard.is_pressed("right"):
                set_crawler_rpm(crawler_rpm, -crawler_rpm)
            else:
                stop_crawlers()

            # Crawler-RPM
            if keyboard.is_pressed("a"):
                crawler_rpm = max(150, crawler_rpm - 100)
                print(f"Crawler-RPM verringert: {crawler_rpm}")
                time.sleep(0.2)
            elif keyboard.is_pressed("d"):
                crawler_rpm = min(3000, crawler_rpm + 100)
                print(f"Crawler-RPM erhöht: {crawler_rpm}")
                time.sleep(0.2)

            # Crawler-ACC/DCC
            elif keyboard.is_pressed("q"):
                crawler_acc = max(100, crawler_acc - 250)
                crawler_dcc = max(100, crawler_dcc - 250)
                update_crawler_acc_dcc()
                print(f"Crawler-ACC/DCC verringert: {crawler_acc}")
                time.sleep(0.2)
            elif keyboard.is_pressed("e"):
                crawler_acc = min(8000, crawler_acc + 250)
                crawler_dcc = min(8000, crawler_dcc + 250)
                update_crawler_acc_dcc()
                print(f"Crawler-ACC/DCC erhöht: {crawler_acc}")
                time.sleep(0.2)

            # Bremse
            elif keyboard.is_pressed("b"):
                brake_active = not brake_active
                if brake_active:
                    print("Bremse aktiviert!")
                    for ip in crawler_ips:
                        send_rest_command(ip, 0x6040, 0x00, "0002")
                else:
                    print("Bremse gelöst!")
                    for ip in crawler_ips:
                        send_rest_command(ip, 0x6040, 0x00, "0006")
                        send_rest_command(ip, 0x6040, 0x00, "0007")
                        send_rest_command(ip, 0x6040, 0x00, "000F")
                time.sleep(0.2)


                
        elif mode == "auto":
            # Start/Stop des automatischen Ablaufs
            if keyboard.is_pressed("space"):
                if auto_sequence_running:
                    print("Automatischer Ablauf gestoppt.")
                    auto_sequence_running = False
                    stop_crawlers()
                else:
                    print(f"Starte automatischen Ablauf ({auto_sequence_target} Durchläufe)...")
                    auto_sequence_running = True
                    auto_sequence_cycles = 0
                    for ip in crawler_ips:
                        send_rest_command(ip, 0x6040, 0x00, "0006")
                        send_rest_command(ip, 0x6040, 0x00, "0007")
                        send_rest_command(ip, 0x6040, 0x00, "000F")
                time.sleep(0.3)
            
            # Hier kommt dein automatischer Ablauf hin
            if auto_sequence_running:
                # Prüfe auf Space-Taste während des Ablaufs (so kann jederzeit abgebrochen werden)
                if keyboard.is_pressed("space"):
                    print("Automatischer Ablauf manuell unterbrochen.")
                    auto_sequence_running = False
                    stop_crawlers()
                    time.sleep(0.3)
                    continue

                if auto_sequence_cycles >= auto_sequence_target:
                    print(f"Automatischer Ablauf beendet ({auto_sequence_target} Durchläufe abgeschlossen).")
                    auto_sequence_running = False
                    stop_crawlers()
                else:
                    # Sequenz: die gewünschte Abfolge mit zusammenfassbaren Zeiten
                    # Jede Aktion ist ein Tupel (action, duration)
                    seq = [
                        ("forward", seq_sec_5),
                        ("pause", seq_pause),
                        ("turn_right", seq_turn),
                        ("pause", seq_pause),
                        ("forward", seq_sec_2),
                        ("pause", seq_pause),
                        ("turn_right", seq_turn),
                        ("pause", seq_pause),
                        ("forward", seq_sec_5),
                        ("pause", seq_pause),
                        ("turn_left", seq_turn),
                        ("pause", seq_pause),
                        ("forward", seq_sec_2),
                        ("pause", seq_pause),
                        ("turn_left", seq_turn),
                        ("pause", seq_pause),
                        ("forward", seq_sec_5),
                        ("pause", seq_pause),
                        ("turn_right", seq_turn),
                        ("pause", seq_pause),
                        ("forward", seq_sec_2),
                        ("pause", seq_pause),
                        ("turn_right", seq_turn),
                        ("pause", seq_pause),
                        ("forward", seq_sec_5),
                        ("pause", seq_pause),
                        ("turn_right", seq_turn),
                        ("pause", seq_pause),
                        ("forward", seq_sec_6),
                        ("pause", seq_pause),
                        ("turn_right", seq_turn),
                    ]

                    # Unterteile jede Aktion in kleine Schritte (100ms) und prüfe Space
                    step_time = 0.1
                    aborted = False
                    for action, duration in seq:
                        # Rechne Schleifendurchläufe
                        loops = max(1, int(duration / step_time))

                        # Setze Motoren entsprechend der Aktion
                        if action == "forward":
                            set_crawler_rpm(seq_straight_speed, seq_straight_speed)
                        elif action == "turn_right":
                            set_crawler_rpm(seq_turn_speed, -seq_turn_speed)
                        elif action == "turn_left":
                            set_crawler_rpm(-seq_turn_speed, seq_turn_speed)
                        elif action == "pause":
                            set_crawler_rpm(0, 0)

                        for _ in range(loops):
                            if keyboard.is_pressed("space"):
                                print("Automatischer Ablauf manuell unterbrochen.")
                                auto_sequence_running = False
                                stop_crawlers()
                                aborted = True
                                break
                            time.sleep(step_time)

                        if aborted:
                            break

                    if not aborted:
                        auto_sequence_cycles += 1

        # Drehzahl anzeigen
        elif keyboard.is_pressed("g"):
            for ip in crawler_ips:
                rpm_val = read_signed_rpm(ip, 0x606C, 0x00)
                if rpm_val is not None:
                    print(f"{ip} → aktuelle Drehzahl: {rpm_val} RPM")
                    if measuring:
                        print(f"{ip} → Strecke: {distance[ip]:.3f} m")
                else:
                    print(f"{ip} → keine Drehzahl gelesen")
            time.sleep(0.2)

        # Streckenmessung
        elif keyboard.is_pressed("j"):
            measuring = not measuring
            print(f"Streckenmessung {'gestartet' if measuring else 'gestoppt'}.")
            time.sleep(0.3)
        elif keyboard.is_pressed("k"):
            distance = {left_crawler: 0.0, right_crawler: 0.0}
            print("Streckenmessung zurückgesetzt.")
            time.sleep(0.3)
        elif keyboard.is_pressed("l"):
            for ip in crawler_ips:
                print(f"{ip} → Strecke: {distance[ip]:.3f} m")
            time.sleep(0.3)

        # Bürstensteuerung       
        elif keyboard.is_pressed("o"):
            brush_running = not brush_running
            if brush_running:
                print("Bürste gestartet.")
                for ip in brushes_ips:
                    send_rest_command(brushes_ips, 0x6060, 0x00, "03")
                    send_rest_command(brushes_ips, 0x6040, 0x00, "0006")
                    send_rest_command(brushes_ips, 0x6040, 0x00, "0007")
                    send_rest_command(brushes_ips, 0x6040, 0x00, "000F")
                set_brush_rpm(brush_rpm)
            else:
                print("Bürste gestoppt.")
                set_brush_rpm(0)
                for ip in brushes_ips:
                    send_rest_command(brushes_ips, 0x60FF, 0x00, dec_to_hex_8(0))
                    #send_rest_command(brushes_ips, 0x6040, 0x00, "0006")
                    send_rest_command(brushes_ips, 0x6040, 0x00, "0002")
            time.sleep(0.2)
        elif keyboard.is_pressed("y"):
            brush_rpm = min(3000, brush_rpm + 100)
            print(f"Bürsten-RPM erhöht: {brush_rpm}")
            if brush_running:
                set_brush_rpm(brush_rpm)
            time.sleep(0.2)
        elif keyboard.is_pressed("c"):
            brush_rpm = max(150, brush_rpm - 100)
            print(f"Bürsten-RPM verringert: {brush_rpm}")
            if brush_running:
                set_brush_rpm(brush_rpm)
            time.sleep(0.2)
        
        elif keyboard.is_pressed("p"):
            for ip in brushes_ips:
                send_rest_command(ip, 0x6040, 0x00, "0006")
            
            time.sleep(0.3)
        elif keyboard.is_pressed("esc"):
            print("Beende Steuerung...")
            break

        time.sleep(0.05)

finally:
    stop_crawlers()
    set_brush_rpm(0)
    for ip in crawler_ips:
        send_rest_command(ip, 0x6040, 0x00, "0006")
    for ip in brushes_ips:
        send_rest_command(ip, 0x6040, 0x00, "0006")


