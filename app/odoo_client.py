# imports
from bs4 import BeautifulSoup
import xmlrpc.client
import json
from datetime import datetime

# conexión (esto lo mantenemos igual)
url = "https://criteria.odoo.com"
db = "criteria-main-11789857"
username = "api@criteria.pe"
password = "cr1t3r1425$"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if not uid:
    raise Exception("❌ Error de autenticación con Odoo")

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# función de mapeo de estados
def obtener_stage_id(nombre_estado: str) -> int:
    mapa_estados = {
        "Nuevo": 1,
        "Asignado": 7,
        "En progreso": 2,
        "En Pausa": 3,
        "Resuelto": 6,
        "Cerrado": 4,
        "Cancelado": 5
    }
    return mapa_estados.get(nombre_estado.strip(), 1)

# ✅ mantener la función que ya estaba funcionando
def crear_ticket_odoo(subject, description, estado, fecha_creacion_sdp, ticket_display_id_sdp):
    stage_id = obtener_stage_id(estado)
    
    nuevo_ticket_id = models.execute_kw(db, uid, password,
        'helpdesk.ticket', 'create',
        [{
            'team_id': 1,
            'name': subject,
            'description': description,
            'stage_id': stage_id,
            'x_studio_sdpticket': ticket_display_id_sdp,
            'x_studio_fecha_de_creacin': fecha_creacion_sdp
        }]
    )

    ticket_data = models.execute_kw(db, uid, password,
        'helpdesk.ticket', 'read',
        [[nuevo_ticket_id], ['id', 'ticket_ref']]
    )

    return ticket_data[0]

# ✅ nueva función: actualizar
def actualizar_ticket_odoo(ticket_display_id_sdp, estado=None, description=None, subject=None):
    domain = [('x_studio_sdpticket', '=', ticket_display_id_sdp)]
    ids = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'search', [domain])

    if not ids:
        print(f"❌ No se encontró un ticket con SDP Display ID {ticket_display_id_sdp}")
        return {"error": f"No se encontró un ticket con ref SDP: {ticket_display_id_sdp}"}

    ticket_id = ids[0]

    datos_actuales = models.execute_kw(db, uid, password,
        'helpdesk.ticket', 'read', [[ticket_id]],
        {'fields': ['name', 'description', 'stage_id']}
    )[0]

    updates = {}
    cambios = []

    if subject and subject.strip() != datos_actuales['name']:
        updates['name'] = subject.strip()
        cambios.append('name')

    descripcion_limpia = BeautifulSoup(description or "", "html.parser").get_text()
    if descripcion_limpia and descripcion_limpia.strip() != (datos_actuales['description'] or "").strip():
        updates['description'] = descripcion_limpia.strip()
        cambios.append('description')

    if estado:
        try:
            estado_obj = json.loads(estado) if isinstance(estado, str) else estado
            nombre_estado = estado_obj.get("name", "").strip()
        except:
            nombre_estado = estado.strip()

        nuevo_stage_id = obtener_stage_id(nombre_estado)

        if datos_actuales['stage_id'] and nuevo_stage_id != datos_actuales['stage_id'][0]:
            updates['stage_id'] = nuevo_stage_id
            cambios.append('stage_id')

    if updates:
        models.execute_kw(db, uid, password,
            'helpdesk.ticket', 'write', [[ticket_id], updates])
        print(f"✅ Ticket {ticket_display_id_sdp} actualizado con cambios: {cambios}")
        return {
            "mensaje": "✅ Ticket actualizado correctamente en Odoo",
            "ticket_ref_actualizado": ticket_display_id_sdp,
            "cambios_aplicados": cambios
        }
    else:
        print(f"ℹ️ No hubo cambios en el ticket {ticket_display_id_sdp}")
        return {
            "mensaje": "ℹ️ Ticket sin cambios",
            "ticket_ref_actualizado": ticket_display_id_sdp
        }
