# 🏨 PMS-INTEGRATION-GUIDE.md - Integración con Property Management System (PMS)

Guía técnica y playbook de despliegue para la integración híbrida entre **Destino Vivo RMS** y los sistemas **PMS** (Property Management Systems) hoteleros.

---

## 📜 Módulos Registrados en el Repositorio
> **Integrador PMS (Python Engine):** [`scratch/pms_integrator.py`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/scratch/pms_integrator.py)  
> **Suite de Pruebas Automatizadas:** [`scratch/test_pms_integration.py`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/scratch/test_pms_integration.py)

---

## 1. ARQUITECTURA DE INTEGRACIÓN HÍBRIDA

```
┌─────────────────────────────────────────────────────────────┐
│                 EVENTO EN TIEMPO REAL (WEBHOOK)             │
│   PMS Hotel  ──(HTTP POST + HMAC SHA256)──> [ RMS Webhook ] │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼ (Actualización Inmediata)
┌─────────────────────────────────────────────────────────────┐
│                 POLLING PROGRAMADO (HOURLY CRON)            │
│   RMS Engine ──(HTTP GET /v1/bookings)──> [ PMS API ]       │
└─────────────────────────────────────────────────────────────┘
```

- **Frecuencia Polling:** Horario (`0 * * * *`).
- **Webhooks:** Inserción en tiempo real al crearse o cancelarse una reserva.
- **Failover:** En caso de caída de la API del PMS (`503 Service Unavailable`), RMS utiliza la última lectura de la memoria caché.

---

## 2. ESTRUCTURA DE DATOS SENSIBLES Y PRIVACIDAD (Compliance)

### Payload de Ejemplo Devuelto por PMS:
```json
{
  "hotel_id": "HOT-001",
  "occupancy": {
    "total_rooms": 100,
    "occupied": 87,
    "available": 13,
    "occupancy_pct": 87.0
  },
  "bookings": [
    {
      "id": "BK001",
      "check_in": "2026-09-15",
      "check_out": "2026-09-17",
      "room_type": "double",
      "rate": 150.00,
      "status": "confirmed",
      "guest_hash": "g_anon_4938a"
    }
  ]
}
```
*Nota de Compliance:* Los datos personales del huésped (Nombre, Teléfono) son anonimizados mediante `guest_hash` (SHA256) antes de ingresar a RMS.

---

## 3. MANEJO DE ERRORES Y RETRIES

| Código HTTP / Evento | Comportamiento en RMS |
| :--- | :--- |
| **`401 Unauthorized`** | Refresca el token OAuth 2.0 / API Key del PMS y reintenta la solicitud. |
| **`429 Rate Limited`** | Detiene peticiones adicionales, coloca la tarea en cola y aplica backoff exponencial. |
| **`503 Service Down`** | Cambia a lectura de **memoria caché local** y genera una alerta al gerente. |
| **Invalid Payload** | Descarta el registro individual con log de advertencia sin interrumpir el resto. |

---

## 4. METRICAS Y MONITOREO (SLAs)

- **Latencia de API (Target):** `< 2,000 ms` (2 segundos).
- **Tasa de Éxito (Target):** `> 99.0%`.
- **Freshness de Datos:** Máximo 1 hora de antigüedad (Alerta si el lag supera las 2 horas).

---

## 5. PLAYBOOK DE DESPLIEGUE EN ANTIGRAVITY (Deployment Steps)

1. **Configurar Credenciales:** Guardar la API Key del PMS (`$secrets.PMS_API_KEY`) y el secreto del webhook (`$secrets.PMS_WEBHOOK_SECRET`) en Antigravity Vault.
2. **Desplegar Task:** Crear la tarea orquestada de sincronización horaria.
3. **Prueba Piloto (1 Hotel):** Probar el flujo de sincronización con el hotel piloto `HOT-001`.
4. **Monitoreo (24 Horas):** Verificar latencia y tasa de éxito en el dashboard.
5. **Escalado Multi-Hotel:** Activar la sincronización para la totalidad de hoteles registrados.
