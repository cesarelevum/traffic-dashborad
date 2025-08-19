<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>KPIs de Tráfico • Transportista</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    body{background:#f8fafc}
    .kpi{border:1px solid #e9ecef;border-radius:14px}
    .kpi .label{color:#6c757d;font-size:.85rem}
    .table td{vertical-align:middle}
    .alert-badge{font-size:.85rem}
  </style>
</head>
<body>
<nav class="navbar bg-white border-bottom">
  <div class="container d-flex align-items-center justify-content-between">
    <span class="navbar-brand fw-bold">🚚 Tráfico • Dashboard</span>
    <button id="btnRnd" class="btn btn-sm btn-outline-primary">🔁 Regenerar datos</button>
  </div>
</nav>

<main class="container py-4">
  <!-- KPIs -->
  <div class="row g-3 mb-3">
    <div class="col-6 col-md-2"><div class="card kpi"><div class="card-body">
      <div class="label">Utilización flota</div><div id="kpiUtil" class="fs-4 fw-bold">–</div>
    </div></div></div>
    <div class="col-6 col-md-2"><div class="card kpi"><div class="card-body">
      <div class="label">OTD (a tiempo)</div><div id="kpiOTD" class="fs-4 fw-bold">–</div>
    </div></div></div>
    <div class="col-6 col-md-2"><div class="card kpi"><div class="card-body">
      <div class="label">Km totales</div><div id="kpiKm" class="fs-4 fw-bold">–</div>
    </div></div></div>
    <div class="col-6 col-md-2"><div class="card kpi"><div class="card-body">
      <div class="label">Rend. prom. (km/L)</div><div id="kpiKml" class="fs-4 fw-bold">–</div>
    </div></div></div>
    <div class="col-6 col-md-2"><div class="card kpi"><div class="card-body">
      <div class="label">Incidentes/100k km</div><div id="kpiInc" class="fs-4 fw-bold">–</div>
    </div></div></div>
    <div class="col-6 col-md-2"><div class="card kpi"><div class="card-body">
      <div class="label">Unid. activas</div><div id="kpiAct" class="fs-4 fw-bold">–</div>
    </div></div></div>
  </div>

  <!-- ALERTAS -->
  <div class="card border-warning mb-4">
    <div class="card-body">
      <div class="d-flex align-items-center justify-content-between">
        <h6 class="mb-0">
          <span class="badge text-bg-warning alert-badge me-2">⚠️ Alertas</span>
          Unidades con <b>Km &lt; 3000</b> o <b>OTD &lt; 80%</b>
        </h6>
        <span id="alertCount" class="badge text-bg-secondary">0</span>
      </div>
      <ul id="alertsList" class="mb-0 mt-2"></ul>
    </div>
  </div>

  <!-- Charts -->
  <div class="row g-3 mb-4">
    <div class="col-md-6">
      <div class="card"><div class="card-body">
        <h6 class="mb-3">Km por unidad</h6>
        <canvas id="kmChart" height="120"></canvas>
      </div></div>
    </div>
    <div class="col-md-6">
      <div class="card"><div class="card-body">
        <h6 class="mb-3">On-Time por unidad (%)</h6>
        <canvas id="otdChart" height="120"></canvas>
      </div></div>
    </div>
  </div>

  <!-- Tabla -->
  <div class="card">
    <div class="card-body">
      <h6 class="mb-3">Detalle operativo</h6>
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th>Unidad</th><th>Viajes</th><th>Km</th><th>Combustible (L)</th>
              <th>km/L</th><th>OTD %</th><th>Disp. %</th><th>Incidentes</th>
            </tr>
          </thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
    </div>
  </div>
</main>

<script>
const USE_RANDOM = true; // pon en false si quieres volver a leer data.json

let kmChart, otdChart;

function rand(min, max){ return Math.random()*(max-min)+min; }
function pick(arr){ return arr[Math.floor(Math.random()*arr.length)]; }

function generateRandomData(n=12){
  const data = [];
  // Elegimos aleatoriamente 3 índices "malos" para Km y 3 para OTD
  const idx = [...Array(n).keys()];
  idx.sort(()=>0.5-Math.random());
  const lowKmIdx  = idx.slice(0, 3);
  const lowOTDIdx = idx.slice(3, 6);

  for(let i=0;i<n;i++){
    // Km: si es "malo" entre 2200-2950, si no entre 3000-4800
    const km = Math.round(lowKmIdx.includes(i) ? rand(2200, 2950) : rand(3000, 4800));
    // Eficiencia entre 2.6 y 3.2 km/L
    const eff = rand(2.6, 3.2);
    const lts = Math.round(km / eff);
    // Viajes 24–36
    const viajes = Math.round(rand(24, 36));
    const tot = viajes;
    // OTD: si es "malo" 60–79%, si no 85–99%
    const otdPct = lowOTDIdx.includes(i) ? rand(60, 79) : rand(85, 99);
    const onTime = Math.max(0, Math.min(tot, Math.round(tot*otdPct/100)));
    // Disponibilidad 86–96%
    const disp = Math.round(rand(86, 96));
    // Incidentes: 15% de probabilidad 0/1
    const inc = Math.random() < 0.15 ? 1 : 0;

    data.push({
      Unidad: `T-${101+i}`,
      Km_recorridos: km,
      Combustible_L: lts,
      Viajes: viajes,
      Entregas_a_tiempo: onTime,
      Entregas_totales: tot,
      Tiempo_promedio_h: +(rand(6.8, 8.2)).toFixed(1),
      Disponibilidad_pct: disp,
      Incidentes: inc
    });
  }
  return data;
}

async function loadData(){
  if (USE_RANDOM) return generateRandomData(12);
  const res = await fetch('./data.json'); // fallback si no quieres aleatorio
  return await res.json();
}

function destroyCharts(){
  if (kmChart) { kmChart.destroy(); kmChart = null; }
  if (otdChart){ otdChart.destroy(); otdChart = null; }
}

function render(data){
  // KPIs
  const kmTot = data.reduce((a,x)=>a+x.Km_recorridos,0);
  const litros = data.reduce((a,x)=>a+x.Combustible_L,0);
  const ontime = data.reduce((a,x)=>a+x.Entregas_a_tiempo,0);
  const totEnt = data.reduce((a,x)=>a+x.Entregas_totales,0);
  const unidAct = data.filter(x=>x.Viajes>0).length;
  const kmlProm = kmTot/litros;
  const inc100k = (data.reduce((a,x)=>a+x.Incidentes,0)/kmTot)*100000;
  const util = (unidAct/data.length)*100;

  document.getElementById('kpiKm').textContent  = kmTot.toLocaleString('es-MX');
  document.getElementById('kpiKml').textContent = kmlProm.toFixed(2);
  document.getElementById('kpiOTD').textContent = ((ontime/totEnt)*100).toFixed(1)+'%';
  document.getElementById('kpiInc').textContent = inc100k.toFixed(2);
  document.getElementById('kpiUtil').textContent= util.toFixed(1)+'%';
  document.getElementById('kpiAct').textContent = unidAct;

  // ALERTAS
  const alerts = [];
  data.forEach(x=>{
    const otd = (x.Entregas_a_tiempo/x.Entregas_totales)*100;
    if (x.Km_recorridos < 3000) alerts.push(`⚠️ Cuidado: ${x.Unidad} con Km ${x.Km_recorridos} < 3000`);
    if (otd < 80) alerts.push(`⚠️ Cuidado: ${x.Unidad} con OTD ${otd.toFixed(1)}% < 80%`);
  });
  document.getElementById('alertCount').textContent = alerts.length;
  document.getElementById('alertsList').innerHTML = alerts.length
    ? alerts.map(a=>`<li>${a}</li>`).join('')
    : '<li>Sin alertas.</li>';

  // TABLA
  const tbody = document.getElementById('tbody');
  tbody.innerHTML = data.map(x=>{
    const kml = x.Km_recorridos / x.Combustible_L;
    const otd = (x.Entregas_a_tiempo/x.Entregas_totales)*100;
    const warn = (x.Km_recorridos < 3000) || (otd < 80);
    const trClass = warn ? 'class="table-warning"' : '';
    return `<tr ${trClass}>
      <td>${x.Unidad}</td><td>${x.Viajes}</td>
      <td>${x.Km_recorridos.toLocaleString('es-MX')}</td>
      <td>${x.Combustible_L.toLocaleString('es-MX')}</td>
      <td>${kml.toFixed(2)}</td><td>${otd.toFixed(1)}</td>
      <td>${x.Disponibilidad_pct}</td><td>${x.Incidentes}</td>
    </tr>`;
  }).join('');

  // CHARTS
  const labels = data.map(x=>x.Unidad);
  const kmData = data.map(x=>x.Km_recorridos);
  const otdData = data.map(x=>(x.Entregas_a_tiempo/x.Entregas_totales*100).toFixed(1));

  destroyCharts();
  kmChart = new Chart(document.getElementById('kmChart'), {
    type:'bar', data:{labels, datasets:[{label:'Km', data:kmData}]},
    options:{responsive:true, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true}}}
  });
  otdChart = new Chart(document.getElementById('otdChart'), {
    type:'bar', data:{labels, datasets:[{label:'OTD %', data:otdData}]},
    options:{responsive:true, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true, max:100}}}
  });
}

async function bootstrap(){
  const data = await loadData();
  render(data);
  document.getElementById('btnRnd').onclick = async ()=>{
    const rnd = generateRandomData(12);
    render(rnd);
  };
}

bootstrap();
</script>
</body>
</html>
