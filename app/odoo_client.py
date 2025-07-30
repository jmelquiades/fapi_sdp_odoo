import xmlrpc.client
from datetime import datetime

# Configuración Odoo
url = "https://criteria.odoo.com"
db = "criteria-main-11789857"
username = "api@criteria.pe"
password = "cr1t3r1425$"

# Conexión y autenticación
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if not uid:
    raise Exception("❌ Error de autenticación con Odoo")

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Mapa de estados
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

# Crear ticket y retornar también el ticket_ref generado por Odoo
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

    # Leer campos adicionales (ticket_ref) del ticket recién creado
    ticket_data = models.execute_kw(db, uid, password,
        'helpdesk.ticket', 'read',
        [[nuevo_ticket_id], ['id', 'ticket_ref']]
    )

    return ticket_data[0]

# Actualizar ticket solo si hay cambios
def actualizar_ticket_odoo(ticket_display_id_sdp, estado=None, description=None, subject=None):
    domain = [('x_studio_sdpticket', '=', ticket_display_id_sdp)]
    ids = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'search', [domain])

    if not ids:
        print(f"❌ No se encontró un ticket con SDP Display ID {ticket_display_id_sdp}")
        return None

    ticket_id = ids[0]

    datos_actuales = models.execute_kw(db, uid, password,
        'helpdesk.ticket', 'read', [[ticket_id]],
        {'fields': ['name', 'description', 'stage_id']}
    )[0]

    updates = {}
    cambios = []

    if subject and subject != datos_actuales['name']:
        updates['name'] = subject
        cambios.append('name')

    if description and description != datos_actuales['description']:
        updates['description'] = description
        cambios.append('description')

    if estado:
        nuevo_stage_id = obtener_stage_id(estado)
        if datos_actuales['stage_id'] and nuevo_stage_id != datos_actuales['stage_id'][0]:
            updates['stage_id'] = nuevo_stage_id
            cambios.append('stage_id')

    if updates:
        models.execute_kw(db, uid, password,
            'helpdesk.ticket', 'write', [[ticket_id], updates])
        print(f"✅ Ticket {ticket_display_id_sdp} actualizado con cambios: {cambios}")
    else:
        print(f"ℹ️ No hubo cambios en el ticket {ticket_display_id_sdp}")

    return {"id": ticket_id, "cambios": cambios}
