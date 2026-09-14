# 🧪 END-TO-END-TEST-PLAN.md - Plan de Pruebas Integrales (Escenario Nuevo Hotel)

Plan de pruebas E2E para verificar el ciclo de vida completo de un nuevo hotel en **Destino Vivo RMS MVP**.

---

## 📋 Datos de Prueba Iniciales (Test Data)

- **Nombre del Hotel:** `Hotel Oasis LatAm`
- **Ciudad / País:** `São Paulo, Brasil`
- **Total Habitaciones:** `50`
- **Correo Electrónico:** `admin@hoteloasis.com`
- **Contraseña:** `OasisSecure2026!`
- **Tarifa Base:** `$100.00 USD` | **Mínima:** `$70.00 USD` | **Máxima:** `$300.00 USD`

---

## 🔄 Escenarios y Verificaciones por Paso

### STEP 1: SIGNUP & ONBOARDING (Alta de Hotel)
- **Acción:** Enviar formulario de registro en `/register`.
- **Resultados Esperados:**
  - [x] Fila creada en la tabla `hotels` con `subscription_tier = 'free'`.
  - [x] Usuario creado en `users` con rol `hotel_admin`.
  - [x] 3 Reglas por defecto en `pricing_rules` (Base, +30% Ocupación Alta, -20% Ocupación Baja).
  - [x] 2 Alertas automáticas en `alerts_config`.
  - [x] Correo de bienvenida enviado a `admin@hoteloasis.com`.
- **Cómo Verificar:** Consultar `GET /hotels?name=eq.Hotel Oasis LatAm` en Supabase.

---

### STEP 2: LOGIN & AUTH (Autenticación)
- **Acción:** Ingresar credenciales en `/login`.
- **Resultados Esperados:**
  - [x] Respuesta HTTP `200 OK` desde `/auth/v1/token`.
  - [x] Token JWT `sb-access-token` guardado en `Session Storage`.
  - [x] Redirección automática a `/dashboard`.
- **Cómo Verificar:** Inspeccionar `Application > LocalStorage` en las DevTools del navegador.

---

### STEP 3: VIEW PRICING DASHBOARD & RLS
- **Acción:** Cargar la pantalla `/pricing`.
- **Resultados Esperados:**
  - [x] Muestra ocupación actual y precio base de `$100.00 USD`.
  - [x] **Aislamiento RLS:** El hotelero de *Hotel Oasis LatAm* solo visualiza la información de su propio establecimiento.

---

### STEP 4: TRIGGER ALERT (Prueba de Alertas)
- **Acción:** Simular ocupación al `25%` y ejecutar el workflow `Alert Detection`.
- **Resultados Esperados:**
  - [x] Registro insertado en `alerts_log` con estado `SENT`.
  - [x] La alerta aparece destacada en rojo en el dashboard `/alerts`.
  - [x] Notificación enviada por Gmail/SendGrid.

---

### STEP 5: RUN DAILY PRICING UPDATE
- **Acción:** Ejecutar manualmente el workflow `Daily Pricing Update`.
- **Resultados Esperados:**
  - [x] Motor JS evalúa las reglas y clima local.
  - [x] Nueva fila insertada en `price_history`.
  - [x] La tarifa recomendada en el dashboard se actualiza automáticamente.

---

### STEP 6: BACKOFFICE VIEW (Administrador de Plataforma)
- **Acción:** Iniciar sesión en `/backoffice/login` con la cuenta `admin@destinovivo.com`.
- **Resultados Esperados:**
  - [x] Acceso al panel multi-tenant `/backoffice/dashboard`.
  - [x] Visualización de *Hotel Oasis LatAm* en la lista global de establecimientos.
  - [x] Inspección de 5 pestañas en `/backoffice/hotel/{hotel_id}`.
