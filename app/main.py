from fastapi import FastAPI
from pydantic import BaseModel
from app.odoo_client import crear_ticket_odoo, actualizar_ticket_odoo
from datetime import datetime
import pytz

app = FastAPI()

class TicketData(BaseModel):
    subject: str
    description: str
    estado: str
    fecha_creacion: str
    ticket_ref: str  # Este es el display_id del ticket en SDP

@app.get("/")
def inicio():
    return {"message": "FastAPI está corriendo correctamente"}

#@app.post("/crear-ticket")
#def crear_ticket(ticket: TicketData):
    try:
        # Convertir la fecha enviada (hora Lima) a UTC
        lima = pytz.timezone("America/Lima")
        fecha_local = datetime.strptime(ticket.fecha_creacion, "%Y-%m-%d %H:%M:%S")
        fecha_local = lima.localize(fecha_local)
        fecha_utc = fecha_local.astimezone(pytz.utc)
        fecha_formateada = fecha_utc.strftime("%Y-%m-%d %H:%M:%S")

        # Crear ticket en Odoo
        nuevo_ticket = crear_ticket_odoo(
            subject=ticket.subject,
            description=ticket.description,
            estado=ticket.estado,
            fecha_creacion_sdp=fecha_formateada,
            ticket_display_id_sdp=ticket.ticket_ref
        )

        return {
            "mensaje": "🎫 Ticket creado correctamente en Odoo",
            "id_interno_odoo": nuevo_ticket["id"],
            "ticket_ref_odoo": nuevo_ticket["ticket_ref"]
        }

    except Exception as e:
        return {"detail": f"❌ Error al crear ticket: {str(e)}"}

@app.post("/crear-ticket")
def crear_ticket(ticket: TicketData):
    try:
        # Convertir la fecha enviada (puede ser en dos formatos) a UTC
        lima = pytz.timezone("America/Lima")

        try:
            # Formato preferido: "2025-07-29 22:18:00"
            fecha_local = datetime.strptime(ticket.fecha_creacion, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # Formato alternativo: "Jul 29, 2025 01:59 AM"
                fecha_local = datetime.strptime(ticket.fecha_creacion, "%b %d, %Y %I:%M %p")
            except ValueError as e:
                raise ValueError(f"Formato de fecha inválido: {ticket.fecha_creacion}") from e

        fecha_local = lima.localize(fecha_local)
        fecha_utc = fecha_local.astimezone(pytz.utc)
        fecha_formateada = fecha_utc.strftime("%Y-%m-%d %H:%M:%S")

        # Crear ticket en Odoo
        nuevo_ticket = crear_ticket_odoo(
            subject=ticket.subject,
            description=ticket.description,
            estado=ticket.estado,
            fecha_creacion_sdp=fecha_formateada,
            ticket_display_id_sdp=ticket.ticket_ref
        )

        return {
            "mensaje": "🎫 Ticket creado correctamente en Odoo",
            "id_interno_odoo": nuevo_ticket["id"],
            "ticket_ref_odoo": nuevo_ticket["ticket_ref"]
        }

    except Exception as e:
        return {"detail": f"❌ Error al crear ticket: {str(e)}"}


@app.put("/actualizar-ticket")
def actualizar_ticket(data: TicketData):
    try:
        resultado = actualizar_ticket_odoo(
            ticket_display_id_sdp=data.ticket_ref,
            estado=data.estado,
            subject=data.subject,
            description=data.description
        )

        if resultado:
            return {
                "mensaje": "✅ Ticket actualizado correctamente en Odoo",
                "ticket_ref_actualizado": data.ticket_ref,
                "cambios_aplicados": resultado["cambios"]
            }
        else:
            return {
                "mensaje": "⚠️ Ticket no encontrado o no se aplicaron cambios",
                "ticket_ref_intentado": data.ticket_ref
            }

    except Exception as e:
        return {"detail": f"❌ Error al actualizar ticket: {str(e)}"}
