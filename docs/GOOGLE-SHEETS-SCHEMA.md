# 📊 GOOGLE-SHEETS-SCHEMA.md - Modelo de Datos Destino Vivo

El modelo de datos de **Destino Vivo** reside en una hoja de cálculo maestra de Google Sheets compuesta por 5 pestañas principales.

---

## 1. Pestaña: `Users`
Almacena la información de los usuarios del sistema y sus roles.

| Columna | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `user_id` | String (UUID) | Identificador único del usuario | `USR-1001` |
| `email` | String | Correo electrónico principal | `gerente@hotelbuenosaires.com` |
| `name` | String | Nombre completo | `Carlos Mendoza` |
| `role` | Enum | Rol del usuario en la plataforma | `ADMIN`, `HOTEL_MANAGER`, `ANALYST` |
| `hotel_ids` | String (CSV) | IDs de hoteles asociados | `HOT-001,HOT-002` |
| `created_at` | DateTime | Fecha de creación ISO 8601 | `2026-09-14T10:00:00Z` |
| `status` | Enum | Estado de la cuenta | `ACTIVE`, `SUSPENDED` |

---

## 2. Pestaña: `Hotels`
Información detallada de los establecimientos hoteleros registrados.

| Columna | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `hotel_id` | String (UUID) | Identificador único del hotel | `HOT-001` |
| `name` | String | Nombre comercial del hotel | `Hotel Boutique Sol` |
| `country` | String | País de ubicación | `Argentina`, `Brasil` |
| `city` | String | Ciudad | `Buenos Aires`, `Rio de Janeiro` |
| `currency` | Enum | Moneda de operación | `USD`, `ARS`, `BRL` |
| `total_rooms` | Integer | Cantidad total de habitaciones | `45` |
| `base_rate` | Number | Tarifa base por noche | `120.00` |
| `min_rate` | Number | Tarifa piso permitida | `80.00` |
| `max_rate` | Number | Tarifa techo permitida | `350.00` |
| `created_at` | DateTime | Fecha de registro | `2026-09-14T10:00:00Z` |

---

## 3. Pestaña: `Pricing_Rules`
Reglas de precios dinámicos aplicables a cada hotel.

| Columna | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `rule_id` | String (UUID) | Identificador de la regla | `RUL-501` |
| `hotel_id` | String (UUID) | Hotel al que aplica | `HOT-001` |
| `rule_type` | Enum | Tipo de ajuste de precio | `OCCUPANCY_SURGE`, `SEASONAL`, `WEEKEND` |
| `threshold_min` | Number | Umbral mínimo para activar | `80.00` (80% ocupación) |
| `threshold_max` | Number | Umbral máximo | `100.00` |
| `adjustment_type` | Enum | Tipo de modificación | `PERCENTAGE`, `FIXED_AMOUNT` |
| `adjustment_value` | Number | Valor del ajuste (+15% o +20 USD) | `15.00` |
| `is_active` | Boolean | Estado de la regla | `TRUE` / `FALSE` |

---

## 4. Pestaña: `Price_History`
Historial de recálculos de precios generados por el algoritmo o workflows.

| Columna | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `history_id` | String (UUID) | Identificador único | `HIS-9001` |
| `hotel_id` | String (UUID) | Hotel evaluado | `HOT-001` |
| `target_date` | Date | Fecha para la cual aplica la tarifa | `2026-10-15` |
| `recommended_rate`| Number | Tarifa calculada por el sistema | `145.50` |
| `applied_rate` | Number | Tarifa aceptada y enviada al PMS | `145.50` |
| `occupancy_pct` | Number | Porcentaje de ocupación actual | `85.00` |
| `rules_applied` | String (CSV) | Reglas que afectaron el precio | `RUL-501,RUL-503` |
| `calculated_at` | DateTime | Timestamp del cálculo | `2026-09-14T02:00:00Z` |

---

## 5. Pestaña: `Alerts_Config`
Registro de alertas detectadas por el sistema.

| Columna | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `alert_id` | String (UUID) | Identificador de alerta | `ALT-301` |
| `hotel_id` | String (UUID) | Hotel afectado | `HOT-001` |
| `alert_type` | Enum | Tipo de anomalía | `HIGH_DEMAND`, `LOW_OCCUPANCY`, `COMPETITOR_DROP` |
| `severity` | Enum | Gravedad | `INFO`, `WARNING`, `CRITICAL` |
| `message` | String | Mensaje explicativo | `Ocupación superó 90% para el 12 de Octubre` |
| `is_resolved` | Boolean | Resuelta por el usuario | `FALSE` |
| `created_at` | DateTime | Fecha de disparo | `2026-09-14T08:30:00Z` |
