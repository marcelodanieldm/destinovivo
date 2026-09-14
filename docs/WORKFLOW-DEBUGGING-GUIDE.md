# 🛠️ WORKFLOW-DEBUGGING-GUIDE.md - Protocolo de Diagnóstico de Errores

Guía paso a paso para identificar, aislar y solucionar errores en la ejecución de los Workflows de Antigravity e integraciones con Supabase.

---

## 🔍 Matriz de Diagnóstico por Código HTTP

| Código HTTP | Tipo de Error | Causa Raíz Frecuente | Solución Inmediata |
| :--- | :--- | :--- | :--- |
| **`400 Bad Request`** | Error en Payload | Tipo de dato incorrecto (ej. texto enviado a campo `NUMERIC` o fecha mal formateada). | Inspeccionar el JSON del Body. Asegurar formato ISO 8601 (`YYYY-MM-DD`). |
| **`401 Unauthorized`** | Error de Credencial | Header `apikey` faltante o expirado, o token Bearer inválido. | Verificar que los headers incluyan la `SUPABASE_SERVICE_ROLE_KEY` en los cron workflows. |
| **`403 Forbidden`** | Bloqueo por RLS | La política de Row Level Security bloquea la lectura/escritura del rol actual. | Crear o modificar la política RLS en Supabase o usar la `SERVICE_ROLE_KEY`. |
| **`404 Not Found`** | Recurso Inexistente | La tabla o endpoint especificado en la URL no existe en el esquema. | Ejecutar el script DDL de [`docs/SUPABASE-POSTGRESQL-SCHEMA.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/SUPABASE-POSTGRESQL-SCHEMA.md). |
| **`409 Conflict`** | Restricción Unicidad | Intento de insertar una clave primaria o campo `UNIQUE` duplicado (ej. `email` existente). | Capturar la excepción en el workflow o actualizar el registro usando `PATCH`. |
| **`429 Rate Limit`** | Límite de Cuota | Exceso de solicitudes a APIs externas (ej. OpenWeather API key en plan free). | Activar `"ignoreError": true` en el paso de la API externa o configurar retries. |

---

## 🧪 1. Cómo Hacer una Solicitud de Prueba Aislada (cURL)

Para aislar si el error se origina en Supabase o en el motor de Antigravity, ejecuta la petición directa desde la terminal o Postman:

```bash
# Probar lectura directa con Service Role Key (Saltea RLS):
curl -X GET "https://[YOUR_PROJECT_ID].supabase.co/rest/v1/hotels?status=eq.ACTIVE" \
  -H "apikey: [YOUR_SUPABASE_ANON_KEY]" \
  -H "Authorization: Bearer [YOUR_SUPABASE_SERVICE_ROLE_KEY]"

# Probar inserción directa en price_history:
curl -X POST "https://[YOUR_PROJECT_ID].supabase.co/rest/v1/price_history" \
  -H "apikey: [YOUR_SUPABASE_ANON_KEY]" \
  -H "Authorization: Bearer [YOUR_SUPABASE_SERVICE_ROLE_KEY]" \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": "HOT-001",
    "target_date": "2026-09-14",
    "recommended_rate": 138.00,
    "applied_rate": 138.00,
    "occupancy_pct": 85.00,
    "decision_source": "rule_based"
  }'
```

---

## 🔐 2. Cómo Verificar y Solucionar Bloqueos de RLS (`403 Forbidden`)

1. **Diagnóstico:** Abre la consola de Supabase > **SQL Editor** y ejecuta la consulta simulación con el rol del usuario:
   ```sql
   SET ROLE authenticated;
   SELECT * FROM public.hotels WHERE hotel_id = 'HOT-001';
   ```
2. **Solución:** Si la consulta retorna 0 filas o lanza error de permisos, aplica la política permitida:
   ```sql
   -- Otorgar permiso de lectura al rol autenticado sobre su propio hotel
   CREATE POLICY "Allow select for hotel admin" ON public.hotels
   FOR SELECT TO authenticated
   USING (
     hotel_id IN (SELECT UNNEST(hotel_ids) FROM public.users WHERE user_id = auth.uid())
   );
   ```

---

## 🩹 3. Recetas de Reparación Rápida para "Daily Pricing Update"

- **Fallo: "Cannot read property 'base_rate' of undefined"**
  - *Causa:* La consulta `GET /hotels` devolvió un array vacío porque no hay hoteles en estado `ACTIVE`.
  - *Arreglo:* Inserta un hotel activo de prueba utilizando [`antigravity/exports/seed-data.json`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/antigravity/exports/seed-data.json).
- **Fallo: "OpenWeather API Key Invalid"**
  - *Causa:* Cuota de OpenWeather expirada.
  - *Arreglo:* Antigravity continuará la ejecución utilizando el multiplicador de reserva `1.0x` gracias al parámetro `"ignoreError": true`.
