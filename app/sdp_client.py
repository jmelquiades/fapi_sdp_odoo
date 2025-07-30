# app/sdp_client.py

import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Credenciales de Zoho SDP
CLIENT_ID = "1000.NDBH7MG7K7M4WVAZWFVRSY6M736Z2D"
CLIENT_SECRET = "31d25e6384eab2fba1473d717c7b62f378c95fc8d3"
REFRESH_TOKEN = "1000.64c7178d01de2f632cd3629d84bcf163.e9906c7a4bee20e59e1094715372a7f3"
ACCESS_TOKEN = ""  # Será actualizado automáticamente

BASE_URL = "https://sdpondemand.manageengine.com"
PORTAL = "itdesk"

# Refrescar token
def refrescar_token():
    global ACCESS_TOKEN
    url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    data = urlencode(params).encode()
    request = Request(url, data=data, method="POST")
    try:
        with urlopen(request) as response:
            content = json.loads(response.read().decode())
            ACCESS_TOKEN = content["access_token"]
            print("🔄 Token actualizado correctamente.")
    except HTTPError as e:
        print("❌ Error al refrescar token:")
        print(e.read().decode())

# Encabezados
def get_headers():
    return {
        "Accept": "application/vnd.manageengine.sdp.v3+json",
        "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

# Obtener ID interno desde display_id
def obtener_id_por_display_id(display_id):
    url = f"{BASE_URL}/app/{PORTAL}/api/v3/requests"
    input_data = json.dumps({
        "list_info": {
            "row_count": "50",
            "start_index": "1",
            "sort_field": "created_time",
            "sort_order": "desc"
        }
    })
    url += "?" + urlencode({"input_data": input_data})
    request = Request(url, headers=get_headers())
    try:
        with urlopen(request) as response:
            contenido = json.loads(response.read().decode())
            for ticket in contenido["requests"]:
                if str(ticket.get("display_id")) == str(display_id):
                    return ticket.get("id")
    except HTTPError as e:
        print("❌ Error al buscar ticket:")
        print(e.read().decode())
    return None

# Leer un ticket por ID interno
def obtener_detalle_ticket(ticket_id):
    url = f"{BASE_URL}/app/{PORTAL}/api/v3/requests/{ticket_id}"
    print(f"📡 Consultando URL: {url}")
    request = Request(url, headers=get_headers())

    try:
        with urlopen(request) as response:
            detalle = json.loads(response.read().decode())["request"]
            return detalle  # incluye id, display_id, status, etc.
    except HTTPError as e:
        print("❌ Error al obtener ticket:")
        print(e.read().decode())
        return None

# Función temporal para depuración
def listar_display_ids():
    url = f"{BASE_URL}/app/{PORTAL}/api/v3/requests"
    input_data = json.dumps({
        "list_info": {
            "row_count": "50",
            "start_index": "1",
            "sort_field": "created_time",
            "sort_order": "desc"
        }
    })
    url += "?" + urlencode({"input_data": input_data})
    request = Request(url, headers=get_headers())
    try:
        with urlopen(request) as response:
            contenido = json.loads(response.read().decode())
            print("📋 Últimos display_id:")
            for ticket in contenido["requests"]:
                print(f"  • #{ticket.get('display_id')} → ID Interno: {ticket.get('id')}")
    except HTTPError as e:
        print("❌ Error al listar tickets:")
        print(e.read().decode())

# Leer lista de tickets básicos (opcional para pruebas múltiples)
def leer_tickets(limit=5):
    url = f"{BASE_URL}/app/{PORTAL}/api/v3/requests"
    input_data = json.dumps({
        "list_info": {
            "row_count": str(limit),
            "start_index": "1",
            "sort_field": "created_time",
            "sort_order": "desc"
        }
    })
    url += "?" + urlencode({"input_data": input_data})
    request = Request(url, headers=get_headers())

    try:
        with urlopen(request) as response:
            contenido = json.loads(response.read().decode())
            tickets = contenido.get("requests", [])
            resultado = []

            for t in tickets:
                resultado.append({
                    "subject": t.get("subject", "Sin asunto"),
                    "description": t.get("description", ""),
                    "status": t.get("status", {}).get("name", "Nuevo"),
                    "created_time": t.get("created_time"),
                    "request_id": t.get("id"),
                    "display_id": t.get("display_id")
                })

            return resultado

    except HTTPError as e:
        print("❌ Error al leer tickets:")
        print(e.read().decode())
        return []
