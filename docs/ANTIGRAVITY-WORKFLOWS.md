# ⚙️ ANTIGRAVITY-WORKFLOWS.md - Especificación de Workflows

Este documento detalla la lógica, los triggers, las llamadas a API y los pasos de ejecución de los workflows principales en Antigravity.

---

## 1. Workflow: `Daily Pricing Update`

### Propósito
Recalcular las tarifas recomendadas de los próximos 30 días para todos los hoteles activos y registrar los resultados en `Price_History`.

### Trigger
- **Tipo:** Cron / Scheduled Trigger
- **Frecuencia:** Diariamente a las 02:00 AM (Hora Local del Hotel / UTC-3).

### Secuencia de Pasos
1. **Fetch Hotels:** Consultar la pestaña `Hotels` filtrando por `status = ACTIVE`.
2. **Fetch Rules:** Para cada hotel activo, obtener las reglas en `Pricing_Rules` donde `is_active = TRUE`.
3. **Execute Pricing Calculation:**
   - Enviar payload JSON a Google Cloud Function `calculatePricing`:
     ```json
     {
       "hotel_id": "HOT-001",
       "base_rate": 120.00,
       "min_rate": 80.00,
       "max_rate": 350.00,
       "rules": [...]
     }
     ```
4. **Append History:** Insertar las nuevas tarifas recomendadas en la pestaña `Price_History`.
5. **Log Summary:** Registrar métricas del flujo (hoteles procesados, errores).

---

## 2. Workflow: `Alert Detection`

### Propósito
Detectar cambios bruscos de ocupación o desvíos de precios de competidores para generar notificaciones preventivas.

### Trigger
- **Tipo:** Event-driven / Scheduled (cada 4 horas).

### Secuencia de Pasos
1. **Query Occupancy & Rates:** Consultar últimos registros en `Price_History`.
2. **Evaluate Thresholds:**
   - Si `occupancy_pct > 90%` → Generar alerta `HIGH_DEMAND` (`CRITICAL`).
   - Si `occupancy_pct < 30%` en los próximos 7 días → Generar alerta `LOW_OCCUPANCY` (`WARNING`).
3. **Write Alert:** Insertar registro en `Alerts_Config`.
4. **Notify User:** Enviar notificación push o correo al manager del hotel.

---

## 3. Workflow: `Hotel Onboarding`

### Propósito
Permitir a un administrador dar de alta un hotel, asociar reglas por defecto y crear sus credenciales iniciales.

### Trigger
- **Tipo:** Form Submission (UI Antigravity).

### Secuencia de Pasos
1. **Validate Input:** Verificar campos requeridos (nombre, moneda, tarifa base, tarifa mínima/máxima).
2. **Generate Identifiers:** Asignar `hotel_id` único (ej. `HOT-002`).
3. **Write to Sheets:**
   - Crear fila en `Hotels`.
   - Crear reglas por defecto en `Pricing_Rules`.
4. **Confirm Success:** Mostrar pantalla de confirmación en la UI.
