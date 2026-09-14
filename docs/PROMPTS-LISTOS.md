# 💬 PROMPTS-LISTOS.md - Biblioteca de Prompts Operativos (Stack Autónomo)

Colección de prompts pre-construidos para agilizar el desarrollo de Destino Vivo con Antigravity y Gmail.

---

## 1. Prompt: Crear Formulario de Onboarding de Hotel

```text
Destino Vivo: Genera la especificación paso a paso para construir la pantalla de "Hotel Onboarding" en Antigravity.
Incluye los campos del formulario acorde a docs/NATIVE-DATA-SCHEMA.md (Hotels table) y la acción de envío de correo de bienvenida vía Gmail.
```

---

## 2. Prompt: Implementar Workflow "Daily Pricing Update"

```text
Destino Vivo: Ayúdame a diseñar el workflow "Daily Pricing Update" autónomo en Antigravity.
Debe ejecutarse a las 02:00 AM, leer los hoteles activos de la tabla nativa Hotels, calcular los precios mediante una función JS integrada y guardar los resultados en la tabla Price_History.
```

---

## 3. Prompt: Configurar Alertas por Gmail

```text
Destino Vivo: Escribe la configuración para el workflow de "Alert Detection" en Antigravity que detecte ocupación superior al 90% y envíe un correo electrónico formateado por Gmail al gerente del hotel.
```
