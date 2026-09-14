const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

// Load seed data for preview
let seedData = {};
try {
  seedData = JSON.parse(fs.readFileSync(path.join(__dirname, '../antigravity/exports/seed-data.json'), 'utf8'));
} catch (e) {
  console.error("Could not load seed data:", e);
}

function renderHtml(title, activeRoute, contentHtml) {
  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} - Destino Vivo RMS</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
    .bg-dark-slate { background-color: #0f172a; }
  </style>
</head>
<body class="bg-gray-50 text-gray-800 min-h-screen flex flex-col">

  <!-- TOP NAVBAR -->
  <header class="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <a href="/" class="flex items-center space-x-2 font-bold text-xl tracking-tight text-blue-400">
          <i class="fa-solid fa-hotel text-2xl text-blue-500"></i>
          <span>Destino Vivo <span class="text-xs bg-blue-600/30 text-blue-300 px-2 py-0.5 rounded border border-blue-500/30">RMS MVP</span></span>
        </a>
      </div>

      <nav class="hidden md:flex items-center space-x-1 text-sm font-medium">
        <a href="/" class="px-3 py-2 rounded-md ${activeRoute === '/' ? 'bg-slate-800 text-white font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-800'}">Inicio</a>
        <a href="/login" class="px-3 py-2 rounded-md ${activeRoute === '/login' ? 'bg-slate-800 text-white font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-800'}">Login Hotel</a>
        <a href="/dashboard" class="px-3 py-2 rounded-md ${activeRoute === '/dashboard' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-800'}">Dashboard</a>
        <a href="/pricing" class="px-3 py-2 rounded-md ${activeRoute === '/pricing' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-800'}">Tarifas (30d)</a>
        <a href="/alerts" class="px-3 py-2 rounded-md ${activeRoute === '/alerts' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-800'}">Alertas & Gmail</a>
        <a href="/settings" class="px-3 py-2 rounded-md ${activeRoute === '/settings' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-800'}">Configuración</a>
        <a href="/backoffice/login" class="px-3 py-2 rounded-md bg-purple-950/80 text-purple-200 border border-purple-800 hover:bg-purple-900 font-semibold ml-4">
          <i class="fa-solid fa-user-shield mr-1"></i> Backoffice
        </a>
      </nav>
    </div>
  </header>

  <!-- MAIN CONTENT CONTAINER -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">
    ${contentHtml}
  </main>

  <!-- FOOTER -->
  <footer class="bg-white border-t border-gray-200 py-6 text-center text-xs text-gray-500 mt-auto">
    <p>Destino Vivo RMS — Sistema Autónomo de Revenue Management para Hoteles en LatAm y Brasil</p>
    <p class="mt-1 text-gray-400">Antigravity Native Storage + Gmail Integration | Preview Local (Port ${PORT})</p>
  </footer>

</body>
</html>`;
}

function handleRequest(req, res) {
  const url = req.url;

  if (url === '/') {
    const html = renderHtml('Bienvenido', '/', `
      <div class="py-12 md:py-20 text-center max-w-3xl mx-auto">
        <span class="bg-blue-100 text-blue-800 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">Fase 0 MVP Autónomo</span>
        <h1 class="text-4xl md:text-5xl font-extrabold text-gray-900 mt-4 tracking-tight">Optimiza las Tarifas de tu Hotel en LatAm</h1>
        <p class="text-lg text-gray-600 mt-4">Sistema inteligente de Revenue Management con motor de reglas dinámicas, storage nativo y notificaciones por Gmail.</p>
        <div class="mt-8 flex justify-center gap-4">
          <a href="/login" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold shadow-md transition">Iniciar Sesión Hotel</a>
          <a href="/dashboard" class="bg-gray-900 hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-semibold shadow-md transition">Ver Demo Dashboard</a>
        </div>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (url === '/login') {
    const html = renderHtml('Iniciar Sesión', '/login', `
      <div class="max-w-md mx-auto my-8 bg-white p-8 rounded-xl shadow-lg border border-gray-100">
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">Destino Vivo RMS</h2>
          <p class="text-sm text-gray-500 mt-1">Ingresa tus credenciales para acceder</p>
        </div>

        <form action="/dashboard" method="GET" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico</label>
            <input type="email" value="gerente@hotelboutiquesol.com" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input type="password" value="••••••••" required minlength="8" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none">
          </div>
          <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-lg font-semibold shadow transition">Iniciar Sesión (Supabase Auth)</button>
        </form>

        <div class="mt-6 border-t border-gray-100 pt-4 text-center">
          <a href="/register" class="text-sm text-blue-600 hover:underline">¿No tienes cuenta? Crear cuenta</a>
        </div>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (url === '/register') {
    const html = renderHtml('Crear Cuenta', '/register', `
      <div class="max-w-md mx-auto my-8 bg-white p-8 rounded-xl shadow-lg border border-gray-100">
        <h2 class="text-2xl font-bold text-gray-900 text-center">Registrar Nuevo Hotel</h2>
        <p class="text-sm text-gray-500 text-center mt-1">Completa los datos para iniciar tu prueba gratis</p>
        <form action="/dashboard" method="GET" class="space-y-4 mt-6">
          <div><label class="block text-sm font-medium text-gray-700">Nombre Completo</label><input type="text" value="Carlos Mendoza" class="w-full px-4 py-2 border rounded-lg"></div>
          <div><label class="block text-sm font-medium text-gray-700">Nombre del Hotel</label><input type="text" value="Hotel Boutique Sol" class="w-full px-4 py-2 border rounded-lg"></div>
          <div><label class="block text-sm font-medium text-gray-700">Correo Electrónico</label><input type="email" value="gerente@hotelboutiquesol.com" class="w-full px-4 py-2 border rounded-lg"></div>
          <div><label class="block text-sm font-medium text-gray-700">Contraseña</label><input type="password" value="••••••••" class="w-full px-4 py-2 border rounded-lg"></div>
          <button type="submit" class="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold">Completar Onboarding</button>
        </form>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (url.startsWith('/dashboard')) {
    const hotel = (seedData.Hotels && seedData.Hotels[0]) || { name: 'Hotel Boutique Sol' };
    const html = renderHtml('Dashboard Home', '/dashboard', `
      <div class="space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Bienvenido, ${hotel.name}</h1>
            <p class="text-sm text-gray-500 mt-0.5">Resumen de ocupación, tarifas optimizadas y alertas del día</p>
          </div>
          <div class="flex gap-2">
            <a href="/pricing" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium shadow hover:bg-blue-700">Pricing Dashboard</a>
            <a href="/alerts" class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50">Alerts Dashboard</a>
            <a href="/settings" class="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-200"><i class="fa-solid fa-gear"></i></a>
          </div>
        </div>

        <!-- QUICK STATS GRID -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Hoteles Activos</span>
            <div class="text-3xl font-extrabold text-gray-900 mt-1">1</div>
            <span class="text-xs text-emerald-600 font-medium mt-1 inline-block"><i class="fa-solid fa-circle-check"></i> Estado Normal</span>
          </div>
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Ocupación Promedio</span>
            <div class="text-3xl font-extrabold text-gray-900 mt-1">85%</div>
            <span class="text-xs text-blue-600 font-medium mt-1 inline-block">+4% vs semana pasada</span>
          </div>
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Tarifa Actual</span>
            <div class="text-3xl font-extrabold text-blue-600 mt-1">$138.00 <span class="text-sm font-normal text-gray-500">USD</span></div>
            <span class="text-xs text-gray-500 font-medium mt-1 inline-block">Tarifa base: $120.00 (+15%)</span>
          </div>
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Alertas Gmail</span>
            <div class="text-3xl font-extrabold text-amber-500 mt-1">1</div>
            <span class="text-xs text-amber-600 font-medium mt-1 inline-block">1 Pendiente de confirmación</span>
          </div>
        </div>

        <!-- RECENT PRICING TABLE -->
        <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="p-4 border-b border-gray-100 flex justify-between items-center">
            <h3 class="font-bold text-gray-900">Últimas Tarifas Recomendadas</h3>
            <a href="/pricing" class="text-xs text-blue-600 font-semibold hover:underline">Ver historial de 30 días &rarr;</a>
          </div>
          <table class="w-full text-left text-sm">
            <thead class="bg-gray-50 text-gray-500 uppercase text-xs">
              <tr><th class="p-3">Hotel</th><th class="p-3">Fecha Tarifa</th><th class="p-3">Ocupación %</th><th class="p-3">Tarifa Rec.</th><th class="p-3">Origen</th></tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr>
                <td class="p-3 font-medium">HOT-001 (Boutique Sol)</td>
                <td class="p-3">2026-09-14</td>
                <td class="p-3"><span class="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded font-semibold">85.0%</span></td>
                <td class="p-3 font-bold text-blue-600">$138.00 USD</td>
                <td class="p-3 text-xs bg-gray-100 rounded inline-block my-1 font-mono">RULE_BASED (+15%)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (url.startsWith('/pricing')) {
    const html = renderHtml('Pricing Dashboard', '/pricing', `
      <div class="space-y-6">
        <h1 class="text-2xl font-bold text-gray-900">Pricing & Revenue Dashboard (30 Días)</h1>

        <!-- TABS BAR -->
        <div class="flex border-b border-gray-200 space-x-6 text-sm font-semibold">
          <button class="pb-3 text-blue-600 border-b-2 border-blue-600">Current Pricing</button>
          <button class="pb-3 text-gray-500 hover:text-gray-700">Price History (30 días)</button>
          <button class="pb-3 text-gray-500 hover:text-gray-700">Pricing Rules</button>
        </div>

        <!-- TAB 1 CONTENT -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm"><span class="text-xs text-gray-400 font-semibold uppercase">Precio Base</span><div class="text-2xl font-bold text-gray-900 mt-1">$120.00 USD</div></div>
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm"><span class="text-xs text-gray-400 font-semibold uppercase">Precio Final Optimizado</span><div class="text-2xl font-bold text-emerald-600 mt-1">$138.00 USD</div></div>
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm"><span class="text-xs text-gray-400 font-semibold uppercase">Ocupación Actual</span><div class="text-2xl font-bold text-blue-600 mt-1">85.0%</div></div>
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm"><span class="text-xs text-gray-400 font-semibold uppercase">Origen Decisión</span><div class="text-2xl font-bold text-purple-600 mt-1">RULE_BASED</div></div>
        </div>

        <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h3 class="font-bold text-gray-900 mb-4">Simulación de Gráfico Recharts (Tarifa vs Ocupación)</h3>
          <div class="h-48 bg-slate-900 rounded-lg flex items-center justify-center text-slate-400 text-sm">
            <i class="fa-solid fa-chart-line text-3xl mr-3 text-blue-400"></i>
            Gráfico de dispersión Recharts: Muestra $138.00 USD vs 85% de ocupación
          </div>
        </div>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (url.startsWith('/alerts')) {
    const html = renderHtml('Centro de Alertas', '/alerts', `
      <div class="space-y-6">
        <h1 class="text-2xl font-bold text-gray-900">Centro de Alertas & Notificaciones Gmail</h1>

        <!-- SECTION 1: URGENT ACTIVE ALERTS (RED THEME) -->
        <div class="bg-red-50 border-2 border-red-500 rounded-xl p-5 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-red-900 font-extrabold flex items-center gap-2">
              <i class="fa-solid fa-triangle-exclamation text-red-600 text-xl"></i>
              Active Alerts (Urgente)
            </h3>
            <span class="bg-red-600 text-white text-xs px-2.5 py-1 rounded-full font-bold">1 ALERTA CRÍTICA</span>
          </div>

          <div class="bg-white border border-red-200 rounded-lg p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <span class="bg-red-100 text-red-800 text-xs font-bold px-2 py-0.5 rounded">HIGH_DEMAND</span>
              <p class="font-semibold text-gray-900 mt-1">Ocupación crítica (85%) detectada para el 15 de Octubre</p>
              <p class="text-xs text-gray-500 mt-0.5">Disparado: 2026-09-14 08:30:00 UTC | Correo enviado por Gmail</p>
            </div>
            <button onclick="alert('Alerta reconocida!')" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-bold shadow transition">Acknowledge (Reconocer)</button>
          </div>
        </div>

        <!-- SECTION 2: CONFIGURATION & HISTORY -->
        <div class="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <h3 class="font-bold text-gray-900 mb-3">Alert History (Últimas 24 Horas)</h3>
          <table class="w-full text-left text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr><th class="p-3">Fecha / Hora</th><th class="p-3">Destinatario</th><th class="p-3">Estado</th></tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr>
                <td class="p-3">2026-09-14 08:30:00</td>
                <td class="p-3">gerente@hotelboutiquesol.com</td>
                <td class="p-3"><span class="bg-red-100 text-red-800 text-xs font-bold px-2 py-0.5 rounded">SENT (Gmail)</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (url.startsWith('/settings')) {
    const html = renderHtml('Configuración', '/settings', `
      <div class="space-y-6 max-w-4xl">
        <h1 class="text-2xl font-bold text-gray-900">Configuración del Hotel & Integraciones</h1>

        <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-6">
          <h3 class="font-bold text-gray-900 border-b pb-2">1. Información del Hotel (Sólo Lectura)</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div><span class="text-xs text-gray-400 block">Nombre</span><span class="font-semibold text-gray-800">Hotel Boutique Sol</span></div>
            <div><span class="text-xs text-gray-400 block">Ciudad / País</span><span class="font-semibold text-gray-800">Buenos Aires, Argentina</span></div>
            <div><span class="text-xs text-gray-400 block">Habitaciones</span><span class="font-semibold text-gray-800">45 cuartos</span></div>
            <div><span class="text-xs text-gray-400 block">Suscripción</span><span class="font-semibold text-blue-600">Fase 0 MVP</span></div>
          </div>

          <h3 class="font-bold text-gray-900 border-b pb-2">2. Configuración de Precios (Editable)</h3>
          <form class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div><label class="block text-xs font-semibold text-gray-700">Tarifa Base ($ USD)</label><input type="number" value="120" class="w-full mt-1 px-3 py-2 border rounded-lg"></div>
            <div><label class="block text-xs font-semibold text-gray-700">Tarifa Mínima ($ USD)</label><input type="number" value="80" class="w-full mt-1 px-3 py-2 border rounded-lg"></div>
            <div><label class="block text-xs font-semibold text-gray-700">Tarifa Máxima ($ USD)</label><input type="number" value="350" class="w-full mt-1 px-3 py-2 border rounded-lg"></div>
            <div class="md:col-span-3"><button type="button" onclick="alert('Guardado!')" class="bg-blue-600 text-white px-5 py-2 rounded-lg font-semibold">Guardar Cambios</button></div>
          </form>
        </div>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (url.startsWith('/backoffice/login')) {
    const html = renderHtml('Backoffice Admin Login', '/backoffice/login', `
      <div class="max-w-md mx-auto my-12 bg-slate-900 text-white p-8 rounded-2xl shadow-2xl border border-slate-800">
        <div class="text-center mb-6">
          <span class="bg-purple-600/30 text-purple-300 text-xs px-3 py-1 rounded-full border border-purple-500/30 uppercase font-bold tracking-wider">Acceso Restringido</span>
          <h2 class="text-2xl font-extrabold mt-3">Destino Vivo Backoffice</h2>
          <p class="text-xs text-slate-400 mt-1">Portal interno de administración de plataforma</p>
        </div>

        <form action="/backoffice/dashboard" method="GET" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-300 mb-1">Correo Admin Interno</label>
            <input type="email" value="admin@destinovivo.com" required class="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none">
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-300 mb-1">Contraseña</label>
            <input type="password" value="••••••••" required class="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none">
          </div>
          <button type="submit" class="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg font-bold shadow-lg transition">Ingresar al Backoffice Admin</button>
        </form>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (url.startsWith('/backoffice/dashboard')) {
    const html = renderHtml('Backoffice Admin Dashboard', '/backoffice/dashboard', `
      <div class="space-y-6">
        <div class="bg-slate-900 text-white p-6 rounded-xl border border-slate-800 shadow-md">
          <h1 class="text-2xl font-extrabold">Destino Vivo Platform Backoffice</h1>
          <p class="text-sm text-slate-400 mt-0.5">Vista global multi-tenant para el equipo de administración interna</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm"><span class="text-xs font-bold text-gray-400 uppercase">Total Hoteles</span><div class="text-3xl font-extrabold text-gray-900 mt-1">1</div></div>
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm"><span class="text-xs font-bold text-gray-400 uppercase">Hoteles Activos</span><div class="text-3xl font-extrabold text-emerald-600 mt-1">100%</div></div>
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm"><span class="text-xs font-bold text-gray-400 uppercase">Alertas Disparadas</span><div class="text-3xl font-extrabold text-blue-600 mt-1">1</div></div>
          <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm"><span class="text-xs font-bold text-gray-400 uppercase">MRR Estimado</span><div class="text-3xl font-extrabold text-purple-600 mt-1">$0.00 (MVP)</div></div>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="p-4 border-b font-bold text-gray-900">Todos los Hoteles Registrados en LatAm</div>
          <table class="w-full text-left text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr><th class="p-3">ID</th><th class="p-3">Nombre</th><th class="p-3">Ciudad / País</th><th class="p-3">Habitaciones</th><th class="p-3">Estado</th><th class="p-3">Acción</th></tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr>
                <td class="p-3 font-mono text-xs">HOT-001</td>
                <td class="p-3 font-bold text-gray-900">Hotel Boutique Sol</td>
                <td class="p-3">Buenos Aires, Argentina</td>
                <td class="p-3">45 cuartos</td>
                <td class="p-3"><span class="bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-0.5 rounded">ACTIVE</span></td>
                <td class="p-3"><a href="/backoffice/hotel/HOT-001" class="bg-purple-600 text-white text-xs px-3 py-1.5 rounded font-semibold hover:bg-purple-700">Inspeccionar Hotel</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (url.startsWith('/backoffice/hotel/')) {
    const html = renderHtml('Inspector de Hotel', '/backoffice/dashboard', `
      <div class="space-y-6">
        <div class="bg-slate-900 text-white p-6 rounded-xl border border-slate-800">
          <div class="flex justify-between items-center">
            <div>
              <span class="bg-purple-600 text-white text-xs px-2.5 py-0.5 rounded font-mono font-bold">HOT-001</span>
              <h1 class="text-2xl font-extrabold mt-1">Inspeccionando: Hotel Boutique Sol</h1>
              <p class="text-sm text-slate-400">Buenos Aires, Argentina | 45 habitaciones | Plan: Fase 0 MVP</p>
            </div>
            <a href="/backoffice/dashboard" class="bg-slate-800 text-slate-300 hover:text-white px-4 py-2 rounded-lg text-sm">&larr; Volver al Backoffice</a>
          </div>
        </div>

        <div class="flex border-b border-gray-200 space-x-6 text-sm font-semibold">
          <button class="pb-3 text-purple-600 border-b-2 border-purple-600">Overview</button>
          <button class="pb-3 text-gray-500">Pricing Decisions (30d)</button>
          <button class="pb-3 text-gray-500">Alerts Fired</button>
          <button class="pb-3 text-gray-500">Users / Staff</button>
          <button class="pb-3 text-gray-500">Pricing Rules</button>
        </div>

        <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
          <h3 class="font-bold text-gray-900">Personal y Staff Registrado</h3>
          <table class="w-full text-left text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr><th class="p-3">Email</th><th class="p-3">Nombre</th><th class="p-3">Rol</th><th class="p-3">Estado</th><th class="p-3">Acción Admin</th></tr>
            </thead>
            <tbody>
              <tr>
                <td class="p-3 font-medium">gerente@hotelboutiquesol.com</td>
                <td class="p-3">Carlos Mendoza</td>
                <td class="p-3 font-mono text-xs">HOTEL_MANAGER</td>
                <td class="p-3"><span class="bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-0.5 rounded">ACTIVE</span></td>
                <td class="p-3"><button onclick="alert('Usuario suspendido!')" class="bg-red-100 text-red-700 hover:bg-red-200 text-xs px-3 py-1 rounded font-bold">Suspender Acceso</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  // 404
  const html = renderHtml('Página no encontrada', '', `<div class="py-20 text-center"><h1 class="text-4xl font-bold">404</h1><p class="mt-2 text-gray-500">Página no encontrada</p></div>`);
  res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(html);
}

const server = http.createServer(handleRequest);

server.listen(PORT, () => {
  console.log(`\n==========================================================`);
  console.log(`  🚀 SERVIDOR PREVIEW HTML LOCAL INICIADO CON ÉXITO        `);
  console.log(`==========================================================`);
  console.log(`  Abre tu navegador web e ingresa a cualquiera de las URLs:`);
  console.log(`  👉 http://localhost:${PORT}/                  (Landing Home)`);
  console.log(`  👉 http://localhost:${PORT}/login             (Login Hotel)`);
  console.log(`  👉 http://localhost:${PORT}/dashboard         (Dashboard Principal)`);
  console.log(`  👉 http://localhost:${PORT}/pricing           (Pricing 30 Días)`);
  console.log(`  👉 http://localhost:${PORT}/alerts            (Alertas & Gmail)`);
  console.log(`  👉 http://localhost:${PORT}/settings          (Configuración)`);
  console.log(`  👉 http://localhost:${PORT}/backoffice/login   (Login Admin Backoffice)`);
  console.log(`  👉 http://localhost:${PORT}/backoffice/dashboard (Backoffice General)`);
  console.log(`==========================================================\n`);
});
