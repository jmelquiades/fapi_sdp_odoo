# app/manual_test.py

from sdp_client import refrescar_token, obtener_id_por_display_id, obtener_detalle_ticket
from odoo_client import crear_ticket_odoo, actualizar_ticket_odoo
from odoo_client import models, db, uid, password
from datetime import datetime

# Convierte la fecha de SDP (UTC) al formato correcto para Odoo
def convertir_fecha_sdp(valor):
    if isinstance(valor, dict) and "value" in valor:
        timestamp_ms = int(valor["value"])
        fecha = datetime.utcfromtimestamp(timestamp_ms / 1000)  # ✅ usar UTC
        return fecha.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(valor, str):
        return valor
    return None

# Prueba completa con ticket fijo (display_id = 225)
def prueba_integracion_manual():
    print("🟡 Paso 1: Autenticación y refresco de token...")
    try:
        refrescar_token()
        print("✅ Token refrescado correctamente.")
    except Exception as e:
        print("❌ Error al refrescar token:", e)
        return

    print("\n🟡 Paso 2: Buscar ticket SDP con display_id = 225...")
    try:
        ticket_id = obtener_id_por_display_id("225")
        if not ticket_id:
            print("❌ No se encontró el ticket con display_id 225.")
            return
        print(f"✅ ID interno SDP encontrado: {ticket_id}")
    except Exception as e:
        print("❌ Error al buscar el ticket:", e)
        return

    print("\n🟡 Paso 3: Obtener detalle completo del ticket SDP...")
    try:
        t = obtener_detalle_ticket(ticket_id)
        print("📄 Asunto:", t.get("subject"))
        print("📝 Descripción:", t.get("description", "")[:100], "...")
        print("⏰ Fecha de creación SDP (UTC):", convertir_fecha_sdp(t.get("created_time")))
    except Exception as e:
        print("❌ Error al obtener detalle del ticket:", e)
        return

    print("\n🟡 Paso 4: Crear ticket en Odoo...")
    try:
        ticket_id_odoo = crear_ticket_odoo(
            subject=t.get("subject", "Sin asunto"),
            description=t.get("description", ""),
            estado=t.get("status", {}).get("name", "Nuevo"),
            fecha_creacion_sdp=convertir_fecha_sdp(t.get("created_time")),
            ticket_id_sdp=t.get("id")
        )

        ticket_data = models.execute_kw(db, uid, password,
            'helpdesk.ticket', 'read', [[ticket_id_odoo]], {'fields': ['ticket_ref']})
        ticket_ref = ticket_data[0].get('ticket_ref', 'N/A')

        print(f"✅ Ticket creado en Odoo: 🎫 {ticket_ref} (ID interno: {ticket_id_odoo})")

    except Exception as e:
        print("❌ Error al crear ticket en Odoo:", e)
        return

    print("\n🟡 Paso 5: Simular actualización en Odoo desde ticket de SDP...")
    try:
        nuevo_estado = "Cerrado"
        actualizar_ticket_odoo(t.get("id"), estado=nuevo_estado)
        print("✅ Ticket en Odoo actualizado a estado:", nuevo_estado)
    except Exception as e:
        print("❌ Error al actualizar ticket en Odoo:", e)
        return

    print("\n🎉 Prueba completada exitosamente.")

# Ejecutar manualmente
if __name__ == "__main__":
    prueba_integracion_manual()
