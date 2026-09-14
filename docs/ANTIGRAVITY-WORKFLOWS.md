# ⚙️ ANTIGRAVITY-WORKFLOWS.md - Especificación de Workflows Autónomos

Este documento detalla la lógica, los triggers y la ejecución de los workflows principales en Antigravity utilizando la capacidad de procesamiento interna y la integración con Gmail.

---

## 1. Workflow: `Daily Pricing Update`

### Propósito
Recalcular las tarifas recomendadas de los próximos 30 días para todos los hoteles activos y guardar el histórico en el Data Store nativo.

### Trigger
- **Tipo:** Scheduled Trigger (Cron internal)
- **Frecuencia:** Diariamente a las 02:00 AM (UTC-3).

### Secuencia de Pasos
1. **Query Active Hotels:** Consultar la tabla `Hotels` filtrando por `status == "ACTIVE"`.
2. **Query Rules:** Obtener las reglas activas desde `Pricing_Rules`.
3. **Execute Internal JavaScript Pricing Logic:**
   - Ejecutar la lógica de ajuste de tarifas dentro del nodo de expresión JS de Antigravity:
     ```javascript
     function calculateTariffs(hotel, rules) {
       let rate = hotel.base_rate;
       for (const rule of rules) {
         if (rule.rule_type === 'OCCUPANCY_SURGE' && hotel.current_occupancy >= rule.threshold_min) {
           rate += (rule.adjustment_type === 'PERCENTAGE') 
             ? (rate * (rule.adjustment_value / 100)) 
             : rule.adjustment_value;
         }
       }
       // Enforce min and max boundaries
       return Math.min(Math.max(rate, hotel.min_rate), hotel.max_rate);
     }
     ```
4. **Save History:** Insertar los resultados calculados en la tabla `Price_History`.
5. **Send Summary via Gmail (Opcional):** Si el hotel tiene activada la notificación diaria, enviar un correo vía Gmail con el desglose de precios recomendados.

---

## 2. Workflow: `Alert Detection & Gmail Notification`

### Propósito
Monitorear variaciones de ocupación y enviar notificaciones por correo de forma inmediata mediante Gmail.

### Trigger
- **Tipo:** Event-driven (al actualizar ocupación) / Scheduled (cada 4 horas).

### Secuencia de Pasos
1. **Fetch Latest Pricing & Occupancy:** Leer los registros de `Price_History`.
2. **Evaluate Alert Conditions:**
   - Ocupación > 90% → Alerta `HIGH_DEMAND` (`CRITICAL`).
   - Ocupación < 30% en los próximos 7 días → Alerta `LOW_OCCUPANCY` (`WARNING`).
3. **Record Alert:** Guardar el registro en la tabla `Alerts_Config`.
4. **Trigger Gmail Action:**
   - Enviar un correo electrónico al correo del `HOTEL_MANAGER` registrado en `Users`:
     - **Asunto:** `[Destino Vivo Alerta] Ocupación Crítica - {{hotel_name}}`
     - **Cuerpo:** `Hola {{manager_name}}, la ocupación de {{hotel_name}} ha superado el 90% para la fecha {{target_date}}. Se recomienda ajustar tarifas.`

---

## 3. Workflow: `Hotel Onboarding`

### Propósito
Dar de alta un nuevo hotel en el Data Store nativo y enviar un correo de bienvenida confirmando la configuración.

### Trigger
- **Tipo:** Form Submission (UI Antigravity).

### Secuencia de Pasos
1. **Validate Input:** Verificar tarifa base, límites mínimos y máximos.
2. **Create Hotel Entry:** Generar registro en la tabla nativa `Hotels`.
3. **Create Default Rules:** Insertar reglas estándar en `Pricing_Rules`.
4. **Send Welcome Email:** Disparar acción de Gmail enviando mensaje de bienvenida con el resumen del alta al correo del usuario.
