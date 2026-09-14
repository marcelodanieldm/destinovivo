# 📊 NATIVE-DATA-SCHEMA.md - Modelo de Datos Nativo Antigravity

El modelo de datos de **Destino Vivo** se gestiona de forma autónoma a través del **Data Store Nativo de Antigravity**.

---

## 1. Tabla: `Users`
Almacena la información de los usuarios del sistema y sus roles.

| Campo | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `user_id` | String (UUID) | Identificador único del usuario | `USR-1001` |
| `email` | String | Correo electrónico principal | `gerente@hotelbuenosaires.com` |
| `name` | String | Nombre completo | `Carlos Mendoza` |
| `role` | Enum | Rol en la plataforma | `ADMIN`, `HOTEL_MANAGER`, `ANALYST` |
| `hotel_ids` | Array[String] | IDs de hoteles asociados | `["HOT-001", "HOT-002"]` |
| `created_at` | DateTime | Fecha de creación ISO 8601 | `2026-09-14T10:00:00Z` |
| `status` | Enum | Estado de la cuenta | `ACTIVE`, `SUSPENDED` |

---

## 2. Tabla: `Hotels`
Información detallada de los establecimientos hoteleros registrados.

| Campo | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `hotel_id` | String (UUID) | Identificador único del hotel | `HOT-001` |
| `name` | String | Nombre comercial del hotel | `Hotel Boutique Sol` |
| `country` | String | País de ubicación | `Argentina`, `Brasil` |
| `city` | String | Ciudad | `Buenos Aires`, `Rio de Janeiro` |
| `currency` | Enum | Moneda de operación | `USD`, `ARS`, `BRL` |
| `total_rooms` | Integer | Cantidad total de habitaciones | `45` |
| `base_rate` | Float | Tarifa base por noche | `120.00` |
| `min_rate` | Float | Tarifa piso permitida | `80.00` |
| `max_rate` | Float | Tarifa techo permitida | `350.00` |
| `created_at` | DateTime | Fecha de registro | `2026-09-14T10:00:00Z` |

---

## 3. Tabla: `Pricing_Rules`
Reglas de precios dinámicos aplicables a cada hotel.

| Campo | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `rule_id` | String (UUID) | Identificador de la regla | `RUL-501` |
| `hotel_id` | String (UUID) | Hotel al que aplica | `HOT-001` |
| `rule_type` | Enum | Tipo de ajuste de precio | `OCCUPANCY_SURGE`, `SEASONAL`, `WEEKEND` |
| `threshold_min` | Float | Umbral mínimo para activar | `80.00` (80% ocupación) |
| `threshold_max` | Float | Umbral máximo | `100.00` |
| `adjustment_type` | Enum | Tipo de modificación | `PERCENTAGE`, `FIXED_AMOUNT` |
| `adjustment_value` | Float | Valor del ajuste (+15% o +20 USD) | `15.00` |
| `is_active` | Boolean | Estado de la regla | `true` / `false` |

---

## 4. Tabla: `Price_History`
Historial de recálculos de precios generados internamente por los workflows.

| Campo | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `history_id` | String (UUID) | Identificador único | `HIS-9001` |
| `hotel_id` | String (UUID) | Hotel evaluado | `HOT-001` |
| `target_date` | Date | Fecha para la cual aplica la tarifa | `2026-10-15` |
| `recommended_rate`| Float | Tarifa calculada por el sistema | `145.50` |
| `applied_rate` | Float | Tarifa aceptada por el usuario | `145.50` |
| `occupancy_pct` | Float | Porcentaje de ocupación actual | `85.00` |
| `rules_applied` | Array[String] | Reglas que afectaron el precio | `["RUL-501", "RUL-503"]` |
| `calculated_at` | DateTime | Timestamp del cálculo | `2026-09-14T02:00:00Z` |

---

## 5. Tabla: `Alerts_Config`
Registro de alertas detectadas y estado de notificación por Gmail.

| Campo | Tipo | Descripción | Ejemplo / Validación |
| :--- | :--- | :--- | :--- |
| `alert_id` | String (UUID) | Identificador de alerta | `ALT-301` |
| `hotel_id` | String (UUID) | Hotel afectado | `HOT-001` |
| `alert_type` | Enum | Tipo de anomalía | `HIGH_DEMAND`, `LOW_OCCUPANCY`, `COMPETITOR_DROP` |
| `severity` | Enum | Gravedad | `INFO`, `WARNING`, `CRITICAL` |
| `message` | String | Mensaje explicativo | `Ocupación superó 90% para el 12 de Octubre` |
| `sent_via_gmail` | Boolean | Notificación enviada por correo | `true` |
| `is_resolved` | Boolean | Resuelta por el usuario | `false` |
| `created_at` | DateTime | Fecha de disparo | `2026-09-14T08:30:00Z` |
