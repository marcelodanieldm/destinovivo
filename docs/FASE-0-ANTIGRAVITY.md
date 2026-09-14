# 🚀 FASE 0: Plan de 2 Semanas - Destino Vivo MVP (Stack Autónomo)

> **Objetivo:** Establecer la infraestructura no-code autónoma en Antigravity con Data Store nativo, motor de precios interno y alertas por Gmail.

---

## 📅 Semana 1: Data Store Nativo y Onboarding

### Día 1: Inicialización del Repositorio y Arquitectura
- [x] Estructurar repositorio local y remoto en GitHub.
- [x] Definir arquitectura autónoma sin dependencias Cloud en [`STACK-ANTIGRAVITY.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/STACK-ANTIGRAVITY.md) y [`ADR-002`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/decisions/DECISION-002-Autonomous-Stack.md).

### Día 2: Configuración del Data Store Nativo
- [ ] Crear las tablas nativas en Antigravity: `Users`, `Hotels`, `Pricing_Rules`, `Price_History`, `Alerts_Config` según [`NATIVE-DATA-SCHEMA.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/NATIVE-DATA-SCHEMA.md).
- [ ] Configurar los tipos de datos y relaciones primarias.

### Día 3: Onboarding y Conexión Gmail
- [ ] Configurar el conector/servicio de Gmail para notificaciones.
- [ ] Implementar la pantalla UI de Login.
- [ ] Diseñar el formulario de alta de nuevo hotel (`Hotel Onboarding Workflow`).

### Día 4: Gestión de Reglas de Precios
- [ ] Construir la interfaz de carga y edición de `Pricing_Rules` en Antigravity.
- [ ] Validar reglas de precios (tarifa mínima, tarifa máxima, multiplicador fin de semana).

### Día 5: Verificación de Semana 1
- [ ] Prueba integral de flujo: Alta de usuario → Registro de hotel → Definición de reglas → Correo de bienvenida por Gmail.

---

## 📅 Semana 2: Workflows de Precios e Integración Gmail

### Día 6-7: Workflow "Daily Pricing Update"
- [ ] Implementar el Scheduled Trigger en Antigravity para recálculo nocturno.
- [ ] Configurar el nodo de expresión JS interna para el cálculo de tarifas.
- [ ] Guardar el historial en `Price_History`.

### Día 8-9: Workflow "Alert Detection & Gmail Notification"
- [ ] Implementar el workflow de monitoreo de ocupación.
- [ ] Registrar alertas en la tabla `Alerts_Config`.
- [ ] Configurar el envío automático de correos de alerta mediante Gmail.

### Día 10: Retrospectiva y Preparación para Fase 1 (MVP)
- [ ] Exportar configuraciones de Antigravity a `antigravity/workflows/` y `antigravity/pages/`.
- [ ] Realizar auditoría de estabilidad del flujo.
- [ ] Tag de versión `v0.2.0-autonomous` en GitHub.
