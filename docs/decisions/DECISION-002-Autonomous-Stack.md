# ADR-002: Transición a Stack Autónomo (Sin Google Sheets ni Google Cloud)

- **Estado:** Aprobado
- **Fecha:** 2026-09-14
- **Autores:** Equipo Destino Vivo

---

## Contexto
Para reducir la complejidad operacional, eliminar dependencias de infraestructura Cloud pagada o externa (GCP) y evitar limitaciones de cuotas de API de Google Sheets, se decide simplificar el stack del MVP.

## Decisión
1. Reemplazar **Google Sheets** como base de datos por el **Data Store nativo de Antigravity** (tablas internas / almacenamiento JSON estructurado).
2. Reemplazar **Google Cloud Functions** por expresiones y lógica en JavaScript ejecutadas dentro de los Workflows de Antigravity.
3. Utilizar **Gmail** (vía conexión nativa SMTP / API) únicamente para notificaciones, alertas de ocupación y resúmenes ejecutivos por correo electrónico.

## Consecuencias
- **Positivas:** 
  - Cero dependencias de infraestructura en Google Cloud (no se requiere configurar GCP Projects, Cloud Functions ni OAuth complejo).
  - Mayor velocidad de respuesta al ejecutar los algoritmos de pricing dentro del mismo motor de Antigravity.
  - Almacenamiento directo e integrado sin riesgo de cuotas de lectura/escritura de Sheets.
- **Limitaciones:**
  - Las notificaciones se limitan al alcance de entrega de correo de Gmail.
