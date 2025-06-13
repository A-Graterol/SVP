import os
from flask import Flask, render_template, request, jsonify, send_file
import socket
import threading
from datetime import datetime
import ipaddress
import sqlite3
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Puerto común y descripciones
COMMON_PORTS = {
    20: "FTP - Transferencia de archivos (Datos)",
    21: "FTP - Transferencia de archivos (Control)",
    22: "SSH - Acceso remoto seguro",
    23: "Telnet - Acceso remoto no seguro",
    25: "SMTP - Correo electrónico",
    53: "DNS - Resolución de nombres",
    80: "HTTP - Navegación web",
    110: "POP3 - Recuperación de correo",
    143: "IMAP - Acceso a correo",
    443: "HTTPS - Navegación web segura",
    445: "SMB - Compartición de archivos Windows",
    3306: "MySQL - Base de datos",
    3389: "RDP - Escritorio remoto Windows",
    5900: "VNC - Escritorio remoto",
    8080: "HTTP Alt - Uso alternativo para servidores web"
}

# Vulnerabilidades asociadas a puertos comunes
VULNERABILITIES = {
    21: ["CVE-2021-1234", "Explotación en buffer overflow"],
    23: ["CVE-2020-1234", "Acceso no seguro"],
    445: ["MS08-067", "Ataque EternalBlue"],
    3389: ["CVE-2019-0708", "BlueKeep"]
}

open_ports = []
scan_in_progress = False
banner_data = {}
last_scan_data = {}  # Guardamos aquí los resultados del último escaneo

def init_db():
    if os.path.exists('database.db'):
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA table_info(scans)")
            columns = [row[1] for row in c.fetchall()]
            conn.close()

            # Si falta la columna 'vulnerabilities', eliminamos la DB y la recreamos
            if 'vulnerabilities' not in columns:
                os.remove('database.db')
                print("Base de datos eliminada. Se recreará con la nueva estructura.")

        except Exception as e:
            print("Error al verificar la estructura de la base de datos:", e)

    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE scans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT,
                        port INTEGER,
                        banner TEXT,
                        description TEXT,
                        vulnerabilities TEXT,
                        timestamp TEXT
                    )''')
        conn.commit()
        conn.close()
        print("Base de datos creada correctamente.")

def save_scan_to_db(ip, open_ports, banners, descriptions, vulns):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    timestamp = str(datetime.now())
    for port in open_ports:
        banner = banners.get(port, "")
        desc = descriptions.get(port, "Desconocido")
        vuln_list = vulns.get(port, [])
        vuln_str = ", ".join(vuln_list) if vuln_list else "Ninguna"
        c.execute("INSERT INTO scans (ip, port, banner, description, vulnerabilities, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                  (ip, port, banner, desc, vuln_str, timestamp))
    conn.commit()
    conn.close()

def get_all_scans():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM scans ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_scan(scan_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    conn.commit()
    conn.close()

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def grab_banner(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)
        sock.connect((ip, port))
        banner = sock.recv(1024).decode().strip()
        sock.close()
        return banner if banner else "Sin información"
    except:
        return "No disponible"

def scan_port(ip, port):
    global banner_data
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            banner = grab_banner(ip, port)
            open_ports.append(port)
            banner_data[port] = banner
        sock.close()
    except Exception as e:
        pass

def start_scan(ip, start_port, end_port):
    global open_ports, scan_in_progress, banner_data
    open_ports.clear()
    banner_data.clear()
    scan_in_progress = True

    threads = []
    for port in range(start_port, end_port + 1):
        thread = threading.Thread(target=scan_port, args=(ip, port,))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    scan_in_progress = False

def generate_pdf(data):
    filename = "ultimo_escaneo_exportado.pdf"
    c = canvas.Canvas(filename)

    # Agregar logo
    logo_path = "logo.png"  # Asegúrate de tener este archivo en tu carpeta
    try:
        c.drawImage(logo_path, 50, 780, width=50, height=50)
    except Exception as e:
        print(f"Error al cargar el logo: {e}")

    # Título con nombre del programa e IP
    c.setFont("Helvetica-Bold", 16)
    c.drawString(110, 780, "SVP - Escáner de Puertos")
    c.drawString(110, 800, f"Escaneo de Puertos - Última IP escaneada: {data['ip']}")

    c.setFont("Helvetica", 12)
    c.drawString(60, 760, f"Puertos abiertos: {data['total_open']}")
    c.drawString(60, 740, f"Duración: {data['duration']}")

    y = 700
    for port in data["open_ports"]:
        banner = data["banners"].get(port, "")
        desc = data["port_descriptions"].get(port, "Desconocido")
        vulns = data["vulnerabilities"].get(str(port), [])
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Puerto {port} - {desc}")
        c.setFont("Helvetica", 10)
        c.drawString(50, y - 15, f"Banner: {banner}")
        if vulns:
            c.drawString(50, y - 30, f"Vulnerabilidades: {', '.join(vulns)}")
        y -= 50
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    ip = data.get('ip')
    start_port = int(data.get('start_port'))
    end_port = int(data.get('end_port'))

    if not is_valid_ip(ip):
        return jsonify({"error": "Dirección IP inválida."}), 400

    if not (1 <= start_port <= 65535 and start_port <= end_port <= 65535):
        return jsonify({"error": "Rango de puertos inválido."}), 400

    start_time = datetime.now()
    start_scan(ip, start_port, end_port)
    end_time = datetime.now()

    results = {
        "ip": ip,
        "open_ports": sorted(open_ports),
        "banners": banner_data,
        "duration": str(end_time - start_time),
        "total_open": len(open_ports),
        "port_descriptions": COMMON_PORTS,
        "vulnerabilities": {str(p): VULNERABILITIES.get(p, []) for p in open_ports}
    }

    save_scan_to_db(ip, open_ports, banner_data, COMMON_PORTS, results["vulnerabilities"])

    # Guardar resultados para usarlos luego en /results
    global last_scan_data
    last_scan_data = results

    return jsonify(results)

@app.route('/results', methods=['GET'])
def get_results():
    global last_scan_data
    if not last_scan_data:
        return jsonify({"error": "No hay resultados disponibles. Realiza un escaneo primero."}), 400
    return jsonify(last_scan_data)

@app.route('/export/pdf', methods=['POST'])
def export_pdf():
    data = request.json
    filename = generate_pdf(data)
    return jsonify({"file": filename})

@app.route('/download_pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    return send_file(filename, as_attachment=True)

@app.route('/historial')
def historial():
    scans = get_all_scans()
    return render_template('historial.html', scans=scans)

@app.route('/delete/<int:scan_id>', methods=['POST'])
def delete(scan_id):
    delete_scan(scan_id)
    return jsonify({"message": "Registro eliminado correctamente."})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)