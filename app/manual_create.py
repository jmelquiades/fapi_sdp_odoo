# app/manual_create.py

from sdp_client import refrescar_token, obtener_id_por_display_id, obtener_detalle_ticket
from odoo_client import crear_ticket_odoo, models, db, uid, password
from datetime import datetime

def convertir_fecha_sdp(valor):
    if isinstance(valor, dict) and "value" in valor:
        timestamp_ms = int(valor["value"])
        fecha = datetime.utcfromtimestamp(timestamp_ms / 1000)
        return fecha.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(valor, str):
        return valor
    return None

def crear_ticket_desde_sdp(display_id):
    print("🟡 Autenticando...")
    refrescar_token()
    print("✅ Token actualizado.")

    print(f"\n🔍 Buscando ticket SDP con display_id = {display_id}...")
    ticket_id = obtener_id_por_display_id(display_id)
    if not ticket_id:
        print("❌ Ticket no encontrado.")
        return

    t = obtener_detalle_ticket(ticket_id)
    print("📄 Asunto:", t.get("subject"))
    print("📝 Descripción:", t.get("description", "")[:100], "...")
    print("⏰ Fecha creación (UTC):", convertir_fecha_sdp(t.get("created_time")))

    ticket_id_odoo = crear_ticket_odoo(
        subject=t.get("subject", "Sin asunto"),
        description=t.get("description", ""),
        estado=t.get("status", {}).get("name", "Nuevo"),
        fecha_creacion_sdp=convertir_fecha_sdp(t.get("created_time")),
        ticket_id_sdp=str(t.get("display_id"))  # ✅ usamos display_id
    )

    ticket_data = models.execute_kw(db, uid, password,
        'helpdesk.ticket', 'read', [[ticket_id_odoo]], {'fields': ['ticket_ref']})
    ticket_ref = ticket_data[0].get('ticket_ref', 'N/A')

    print(f"\n✅ Ticket creado en Odoo: 🎫 {ticket_ref} (ID interno: {ticket_id_odoo})")
    print(f"🔗 SDP display_id registrado: {t.get('display_id')}")

if __name__ == "__main__":
    crear_ticket_desde_sdp("225")
