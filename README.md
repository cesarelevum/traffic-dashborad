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
  </style>
</head>
<body>
<nav class="navbar bg-white border-bottom">
  <div class="container">
    <span class="navbar-brand fw-bold">🚚 Tráfico • Dashboard</span>
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
async function main(){
  const res = await fetch('./data.json');     // lee el JSON del repo
  const data = await res.json();

  // KPIs
  const kmTot = data.reduce((a,x)=>a+x.Km_recorridos,0);
  const litros = data.reduce((a,x)=>a+x.Combustible_L,0);
  const ontime = data.reduce((a,x)=>a+x.Entregas_a_tiempo,0);
  const totEnt = data.reduce((a,x)=>a+x.Entregas_totales,0);
  const unidAct = data.filter(x=>x.Viajes>0).length;
  const kmlProm = kmTot/litros;
  const inc100k = (data.reduce((a,x)=>a+x.Incidentes,0)/kmTot)*100000;
  const util = (unidAct/data.length)*100;

  document.getElementById('kpiKm').textContent = kmTot.toLocaleString('es-MX');
  document.getElementById('kpiKml').textContent = kmlProm.toFixed(2);
  document.getElementById('kpiOTD').textContent = ((ontime/totEnt)*100).toFixed(1)+'%';
  document.getElementById('kpiInc').textContent = inc100k.toFixed(2);
  document.getElementById('kpiUtil').textContent = util.toFixed(1)+'%';
  document.getElementById('kpiAct').textContent = unidAct;

  // Tabla
  const tbody = document.getElementById('tbody');
  tbody.innerHTML = data.map(x=>{
    const kml = x.Km_recorridos / x.Combustible_L;
    const otd = (x.Entregas_a_tiempo/x.Entregas_totales)*100;
    return `<tr>
      <td>${x.Unidad}</td><td>${x.Viajes}</td><td>${x.Km_recorridos.toLocaleString('es-MX')}</td>
      <td>${x.Combustible_L.toLocaleString('es-MX')}</td>
      <td>${kml.toFixed(2)}</td><td>${otd.toFixed(1)}</td>
      <td>${x.Disponibilidad_pct}</td><td>${x.Incidentes}</td>
    </tr>`
  }).join('');

  // Gráficas
  const labels = data.map(x=>x.Unidad);
  const kmData = data.map(x=>x.Km_recorridos);
  const otdData = data.map(x=>(x.Entregas_a_tiempo/x.Entregas_totales*100).toFixed(1));

  new Chart(document.getElementById('kmChart'), {
    type:'bar', data:{labels, datasets:[{label:'Km', data:kmData}]},
    options:{responsive:true, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true}}}
  });
  new Chart(document.getElementById('otdChart'), {
    type:'bar', data:{labels, datasets:[{label:'OTD %', data:otdData}]},
    options:{responsive:true, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true, max:100}}}
  });
}
main();
</script>
</body>
</html>
