# 🐘 SUPABASE-DATABASE-GUIDE.md - Configuración & Estrategia Supabase RMS

Guía completa de arquitectura de base de datos PostgreSQL en Supabase para **Destino Vivo RMS**.

---

## 📜 Script SQL de Migración Listo para Ejecutar
> **Archivo SQL Principal:** [`docs/SUPABASE-RMS-COMPLETE-SCHEMA.sql`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/SUPABASE-RMS-COMPLETE-SCHEMA.sql)

---

## 1. TABLAS PRINCIPALES (7 Tablas)

1. **`hotels`**: Registro de establecimientos, países (`MX`, `BR`, `AR`), total de habitaciones, referencias PMS y especificación de tipos de cuarto en JSONB.
2. **`bookings`**: Reservas sincronizadas desde PMS u OTAs (Directo, Booking.com, Expedia), fechas `check_in`/`check_out`, estados y precios.
3. **`daily_prices`**: Tarifas calculadas diariamente a nivel de fecha y tipo de cuarto. Compara `price_rule_based`, `price_ml` y `price_hybrid`, con bandera `accepted` y valor `overridden_to` para modificaciones manuales.
4. **`forecasts`**: Predicciones de demanda proyectada a 1d, 7d y 30d utilizando modelos ARIMA, Prophet, LSTM o Ensemble, incluyendo métricas MAPE y grado de confianza.
5. **`variables_daily`**: Variables internas, externas (clima, festivos) y derivadas utilizadas por los modelos de pricing.
6. **`competitive_data`**: Datos rascados de la competencia, precios observados e índice de competitividad (`our_price / competitor_price`).
7. **`api_logs`**: Registro de auditoría de integración con servicios externos (PMS, OTAs, OpenWeather), tiempos de respuesta en ms y mensajes de error.

---

## 2. ÍNDICES DE RENDIMIENTO (Performance Indexes)

- `idx_bookings_hotel_checkin` → `(hotel_id, check_in)`
- `idx_daily_prices_hotel_date` → `(hotel_id, date)`
- `idx_forecasts_hotel_date` → `(hotel_id, forecast_date)`
- `idx_variables_hotel_date` → `(hotel_id, date)`
- `idx_competitive_hotel_scraped` → `(hotel_id, scraped_at DESC)`

---

## 3. FUNCIONES SQL ALMACENADAS (KPIs de Revenue Management)

### 3.1 `calculate_occupancy(p_hotel_id, p_date)`
Calcula el porcentaje de ocupación en tiempo real para una fecha dada:
$$\text{Occupancy \%} = \frac{\text{Habitaciones Reservadas Confirmadas}}{\text{Total Habitaciones del Hotel}} \times 100$$

### 3.2 `calculate_adr(p_hotel_id, p_date)`
Calcula la tarifa promedio diaria (Average Daily Rate):
$$\text{ADR} = \frac{\text{Ingreso Total por Tarifas de Reservas}}{\text{Habitaciones Vendidas}}$$

### 3.3 `calculate_revpar(p_hotel_id, p_date)`
Calcula el ingreso por habitación disponible (Revenue Per Available Room):
$$\text{RevPAR} = \text{ADR} \times \left(\frac{\text{Occupancy \%}}{100}\right)$$

---

## 4. ESTRATEGIA DE BACKUP & PITR (Point-In-Time Recovery)

### 4.1 Respaldos Automatizados Diarios (Automated Backups)
- **Frecuencia:** Copia de seguridad física completa cada 24 horas a las 03:00 UTC.
- **Retención:** 7 días garantizados en el plan Supabase Pro / Enterprise.

### 4.2 Restauración a un Punto en el Tiempo (PITR)
- Supabase escribe los logs WAL (Write-Ahead Logs) en tiempo real en Cloud Storage.
- En caso de corrupción de datos accidental o fallo grave, se puede restaurar la base de datos exactamente al segundo anterior al incidente desde **Supabase Console > Database > Backups > Restore to PITR**.
