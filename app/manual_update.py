# app/manual_update.py

from sdp_client import refrescar_token, obtener_id_por_display_id, obtener_detalle_ticket
from odoo_client import actualizar_ticket_odoo, models, db, uid, password
from datetime import datetime

# Mapear estado de SDP a ID de etapa en Odoo
ESTADOS_ODP = {
    "Nuevo": 1,
    "Asignado": 7,
    "En progreso": 1,
    "En Pausa": 3,
    "Resuelto": 6,
    "Cerrado": 4,
    "Cancelado": 5
}

def convertir_fecha_sdp(valor):
    if isinstance(valor, dict) and "value" in valor:
        timestamp_ms = int(valor["value"])
        fecha = datetime.fromtimestamp(timestamp_ms / 1000)
        return fecha.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(valor, str):
        return valor
    return None

def manual_update_ticket(display_id_sdp):
    print("🟡 Paso 1: Autenticación...")
    refrescar_token()

    print(f"\n🟡 Paso 2: Buscar ticket SDP con display_id #{display_id_sdp}...")
    id_interno = obtener_id_por_display_id(display_id_sdp)
    if not id_interno:
        print("❌ No se encontró el ticket en SDP.")
        return

    ticket_sdp = obtener_detalle_ticket(id_interno)
    if not ticket_sdp:
        print("❌ No se pudo obtener detalle del ticket.")
        return

    print("✅ Ticket encontrado. Analizando diferencias...")

    # Buscar en Odoo el ticket por x_studio_sdpticket = display_id
    domain = [('x_studio_sdpticket', '=', str(display_id_sdp))]
    fields = ['id', 'name', 'description', 'stage_id']
    resultados = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'search_read', [domain], {'fields': fields})

    if not resultados:
        print("⚠️ Ticket no encontrado en Odoo.")
        return

    ticket_odoo = resultados[0]
    ticket_id = ticket_odoo['id']

    # Obtener datos desde SDP
    nuevo_subject = ticket_sdp.get("subject", "Sin asunto")
    nueva_description = ticket_sdp.get("description", "")
    nuevo_estado = ticket_sdp.get("status", {}).get("name", "Nuevo")
    nuevo_stage_id = ESTADOS_ODP.get(nuevo_estado, 1)

    cambios = {}

    if ticket_odoo['name'] != nuevo_subject:
        cambios['name'] = nuevo_subject
    if ticket_odoo['description'] != nueva_description:
        cambios['description'] = nueva_description
    if ticket_odoo['stage_id'][0] != nuevo_stage_id:
        cambios['stage_id'] = nuevo_stage_id

    if cambios:
        print("🔁 Cambios detectados:", cambios)
        models.execute_kw(db, uid, password, 'helpdesk.ticket', 'write', [[ticket_id], cambios])
        print("✅ Ticket actualizado en Odoo.")
    else:
        print("👌 El ticket ya está sincronizado. No se realizaron cambios.")

if __name__ == "__main__":
    manual_update_ticket(225)  # Aquí puedes cambiar el número de ticket SDP (display_id)
