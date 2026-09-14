# 🚀 FASE 0: Plan de 2 Semanas - Destino Vivo MVP

> **Objetivo:** Establecer la infraestructura base no-code en Antigravity, validar la conexión con Google Sheets y ejecutar la prueba de concepto del algoritmo de cálculo dinámico de precios.

---

## 📅 Semana 1: Configuración de Base de Datos y Autenticación

### Día 1: Inicialización del Repositorio y Entorno
- [x] Estructurar repositorio local y remoto en GitHub.
- [x] Crear documentación base (`README.md`, `CLAUDE.md`, schemas y specs).
- [ ] Configurar proyecto Google Cloud con credenciales OAuth 2.0 y habilitar Google Sheets API.

### Día 2: Creación de la Base de Datos en Google Sheets
- [ ] Crear la hoja de cálculo maestra en Google Sheets.
- [ ] Crear pestañas: `Users`, `Hotels`, `Pricing_Rules`, `Price_History`, `Alerts_Config`.
- [ ] Aplicar validación de datos, formato condicional y restricciones de encabezado según [`GOOGLE-SHEETS-SCHEMA.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/GOOGLE-SHEETS-SCHEMA.md).

### Día 3: Onboarding y Conexión de Antigravity
- [ ] Configurar conectores de Google Sheets en Antigravity.
- [ ] Implementar la pantalla UI de Login / Autenticación.
- [ ] Diseñar el formulario de alta de nuevo hotel (`Hotel Onboarding Workflow`).

### Día 4: Gestión de Reglas de Precios
- [ ] Construir la interfaz de carga y edición de `Pricing_Rules` en Antigravity.
- [ ] Validar reglas de precios (tarifa mínima, tarifa máxima, multiplicador fin de semana).

### Día 5: Verificación de Semana 1
- [ ] Prueba integral de flujo: Alta de usuario → Registro de hotel → Definición de reglas → Verificación en Sheets.

---

## 📅 Semana 2: Workflows de Precios y Alertas

### Día 6-7: Workflow "Daily Pricing Update"
- [ ] Implementar trigger cron / programado en Antigravity para recálculo nocturno.
- [ ] Integrar llamada a Cloud Function de pricing o evaluación de reglas.
- [ ] Registrar histórico en la pestaña `Price_History`.

### Día 8-9: Workflow "Alert Detection"
- [ ] Implementar el workflow de monitoreo de ocupación y variaciones.
- [ ] Generar registros de alerta en la pestaña `Alerts_Config`.
- [ ] Configurar notificaciones por correo o dashboard.

### Día 10: Retrospectiva y Preparación para Fase 1 (MVP)
- [ ] Exportar configuraciones de Antigravity a `antigravity/workflows/` y `antigravity/pages/`.
- [ ] Realizar auditoría de calidad de datos y estabilidad del flujo.
- [ ] Tag de versión `v0.1.0-phase0` en GitHub.
