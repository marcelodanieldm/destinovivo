// Simulation script for Destino Vivo Pricing Engine & Alert Detection Logic

const seedData = require('../antigravity/exports/seed-data.json');

console.log("=== 1. SIMULATING DAILY PRICING UPDATE ENGINE ===");
const hotels = seedData.Hotels;
const rules = seedData.Pricing_Rules;
const pricingResults = [];

for (const hotel of hotels) {
  let rate = hotel.base_rate;
  const hotelRules = rules.filter(r => r.hotel_id === hotel.hotel_id);
  
  for (const rule of hotelRules) {
    if (rule.rule_type === 'OCCUPANCY_SURGE') {
      rate += (rule.adjustment_type === 'PERCENTAGE') 
        ? (rate * (rule.adjustment_value / 100)) 
        : rule.adjustment_value;
    }
  }
  
  const finalRate = Math.min(Math.max(rate, hotel.min_rate), hotel.max_rate);
  
  pricingResults.push({
    history_id: 'HIS-' + Date.now() + '-' + hotel.hotel_id,
    hotel_id: hotel.hotel_id,
    target_date: new Date().toISOString().split('T')[0],
    recommended_rate: finalRate,
    applied_rate: finalRate,
    occupancy_pct: 85.0,
    calculated_at: new Date().toISOString()
  });
}

console.log("Pricing Calculation Results:", JSON.stringify(pricingResults, null, 2));

console.log("\n=== 2. SIMULATING ALERT DETECTION & GMAIL TRIGGER ===");
const history = pricingResults;
const users = seedData.Users;
const alertsToCreate = [];
const emailsToSend = [];

for (const record of history) {
  if (record.occupancy_pct >= 80.0) {
    const alertId = 'ALT-' + Date.now() + '-' + record.hotel_id;
    const manager = users.find(u => u.hotel_ids.includes(record.hotel_id)) || { email: 'admin@destinovivo.com', name: 'Administrador' };
    
    alertsToCreate.push({
      alert_id: alertId,
      hotel_id: record.hotel_id,
      alert_type: 'HIGH_DEMAND',
      severity: 'CRITICAL',
      message: `Ocupación crítica (${record.occupancy_pct}%) detectada para la fecha ${record.target_date}`,
      sent_via_gmail: true,
      is_resolved: false,
      created_at: new Date().toISOString()
    });
    
    emailsToSend.push({
      to: manager.email,
      subject: `[Destino Vivo Alerta CRÍTICA] Alta Ocupación en Hotel ${record.hotel_id}`,
      body: `Hola ${manager.name},\n\nSe ha detectado una ocupación del ${record.occupancy_pct}% para la fecha ${record.target_date}.\nTarifa recomendada calculada: $${record.recommended_rate}.\n\n--\nDestino Vivo System`
    });
  }
}

console.log("Alerts Generated:", JSON.stringify(alertsToCreate, null, 2));
console.log("Emails Prepared for Gmail:", JSON.stringify(emailsToSend, null, 2));
console.log("\nSUCCESS: All internal logic executed cleanly without errors!");
