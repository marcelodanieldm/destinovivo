# 🏨 OTA-INTEGRATION-GUIDE.md - Integración Multi-Canal OTA & Paridad de Tarifas

Guía técnica y de arquitectura para la sincronización multi-canal con **Booking.com, Expedia, Agoda, Google Hotels y Venta Directa** en Destino Vivo RMS.

---

## 📜 Modulos Registrados en el Repositorio
> **Motor de Integración OTA (Python):** [`scratch/ota_manager.py`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/scratch/ota_manager.py)  
> **Suite de Pruebas Unitarias y Carga:** [`scratch/test_ota_integration.py`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/scratch/test_ota_integration.py)

---

## 1. ARQUITECTURA & MATRIZ DE CANALES

| Canal | Participación Objetivo (Share) | Comisión % | Límite API / min | Endpoint de Sincronización |
| :--- | :--- | :--- | :--- | :--- |
| **Venta Directa** | `15%` | `0%` | `1000 requests/min` | `https://api.destinovivo.com/v1/direct/rates` |
| **Google Hotels** | `10%` | `10%` | `600 requests/min` | `https://www.google.com/travel/hotels/api/v1/rates` |
| **Booking.com** | `30%` | `15%` | `300 requests/min` | `https://api.booking.com/pms/v1/rates` |
| **Agoda** | `20%` | `18%` | `200 requests/min` | `https://api.agoda.com/pms/v1/rates` |
| **Expedia** | `25%` | `20%` | `250 requests/min` | `https://api.expedia.com/v1/rates` |

---

## 2. REGLAS Y VALIDACIÓN DE PARIDAD DE TARIFAS (Rate Parity)

### 🏆 Regla de Oro (Golden Rule):
$$\text{Tarifa Directa} \le \text{Tarifa OTA} \times (1 - \text{Comisión \%})$$

### Ejemplo de Cálculo:
- **Tarifa Base Directa:** `$100.00 USD`
- **Comisión Booking.com (15%):**  
  $$\text{Tarifa Booking.com} = \frac{100.00}{1 - 0.15} = \$117.65\text{ USD}$$
- **Comisión Expedia (20%):**  
  $$\text{Tarifa Expedia} = \frac{100.00}{1 - 0.20} = \$125.00\text{ USD}$$

### Validación Previa a la Sincronización:
El módulo [`RateParityValidator`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/scratch/ota_manager.py#L42) evalúa la paridad antes de enviar las tarifas a las OTAs. Si una OTA intenta vender por debajo de la tarifa directa neta, la sincronización se **cancela inmediatamente** y dispara una alerta.

---

## 3. ALGORITMO DE ASIGNACIÓN DINÁMICA DE INVENTARIO

Dado un total de habitaciones disponibles (ej. 100 cuartos), el motor [`InventoryAllocator`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/scratch/ota_manager.py#L82) distribuye el inventario priorizando los canales de mayor margen neto (Venta Directa).

### Estrategia de Asignación:
- **Demanda Alta (Forecast >= 90%):** Se aumenta la ponderación de Venta Directa (+50%) y Google Hotels (+20%), reduciendo el inventario expuesto en canales de alta comisión como Expedia.
- **Prevención de Overbooking (Stop-Sell Trigger al 98%):**
  - Si la ocupación alcanza el **98% o quedan 1-2 habitaciones**, se activa el **Stop-Sell automático** para todas las OTAs intermediarias, asignando el 100% de los cuartos restantes al canal **Directo**.

---

## 4. ESTRATEGIA DE REINTENTOS CON BACKOFF EXPONENCIAL

Si un canal externo responde con un fallo temporal (`503 Service Unavailable` o `429 Too Many Requests`):
1. **Reintento 1:** Espera `2s`.
2. **Reintento 2:** Espera `4s`.
3. **Reintento 3:** Espera `8s`.
4. Si la OTA no responde tras 3 intentos, se registra en `api_logs`, se notifica al equipo por email y el pipeline continúa sin bloquear a las demás OTAs.
