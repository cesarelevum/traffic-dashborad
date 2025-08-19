<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>🚚 Tráfico • KPIs Transportista</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    body{background:#f8fafc}
    .card{border:1px solid #eef1f4;border-radius:14px}
    .kpi-card{border:0;border-radius:16px;background:linear-gradient(180deg,#fff 0%,#f3f6ff 100%);box-shadow:0 6px 16px rgba(9,16,31,.06)}
    .kpi-label{color:#6c757d;font-size:.85rem}
    .kpi-value{font-size:1.9rem;font-weight:800;letter-spacing:.3px}
    .table td{vertical-align:middle}
    .alert-badge{font-size:.85rem}
  </style>
</head>
<body>
  <nav class="navbar navbar-expand bg-white border-bottom sticky-top">
    <div class="container d-flex align-items-center justify-content-between">
      <span class="navbar-brand fw-bold d-flex align-items-center gap-2">
        <i class="bi bi-speedometer2"></i> Tráfico • Dashboard KPIs
      </span>
      <button id="btnRnd" class="btn btn-sm btn-outline-primary">
        <i class="bi bi-shuffle"></i> Regenerar datos
      </button>
    </div>
  </nav>

  <main class="container py-4">

    <!-- KPIs (6 tarjetas) -->
    <div class="row g-3 mb-3" id="kpis"></div>

    <!-- Donuts + Barras -->
    <div class="row g-3 mb-3">
      <div class="col-md-4">
        <div class="card shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="mb-0">On-Time Delivery</h6>
              <span id="badgeOTD" class="badge rounded-pill text-bg-secondary">–</span>
            </div>
            <canvas id="donutOTD" height="200"></canvas>
            <div class="small text-secondary mt-2">% de entregas a tiempo vs total</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="mb-0">Utilización de Flota</h6>
              <span id="badgeUTIL" class="badge rounded-pill text-bg-secondary">–</span>
            </div>
            <canvas id="donutUTIL" height="200"></canvas>
            <div class="small text-secondary mt-2">Viajes realizados / capacidad mensual</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm">
          <div class="card-body">
            <h6 class="mb-3">Km por Unidad</h6>
            <canvas id="barKM" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Alertas -->
    <div class="card border-warning mb-3 shadow-sm">
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

    <!-- Tabla -->
    <div class="card shadow-sm">
      <div class="card-body">
        <h6 class="mb-3"><i class="bi bi-table me-1"></i> Detalle Operativo</h6>
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
    // ======== Datos aleatorios realistas + "malos" garantizados ========
    function r(min,max){return Math.random()*(max-min)+min}
    function genData(n=12){
      const idx=[...Array(n).keys()].sort(()=>0.5-Math.random())
      const lowKmIdx=idx.slice(0,3)     // 3 unidades con km < 3000
      const lowOTDIdx=idx.slice(3,6)    // 3 unidades con OTD < 80%
      const data=[]
      for(let i=0;i<n;i++){
        const km=Math.round(lowKmIdx.includes(i)? r(2200,2950): r(3000,5000))
        const eff=r(2.6,3.3)                         // km/L
        const lts=Math.round(km/eff)
        const viajes=Math.round(r(24,36))            // capacidad mensual ~36
        const tot=viajes
        const otdPct=lowOTDIdx.includes(i)? r(60,79): r(85,99)
        const onTime=Math.max(0,Math.min(tot,Math.round(tot*otdPct/100)))
        const disp=Math.round(r(86,96))
        const inc=Math.random()<0.12?1:0
        data.push({
          Unidad:`T-${101+i}`, Km_recorridos:km, Combustible_L:lts, Viajes:viajes,
          Entregas_a_tiempo:onTime, Entregas_totales:tot, Tiempo_promedio_h:+r(6.8,8.2).toFixed(1),
          Disponibilidad_pct:disp, Incidentes:inc
        })
      }
      return data
    }

    // ======== Render ========
    let charts={donutOTD:null,donutUTIL:null,barKM:null}

    function destroyCharts(){
      Object.values(charts).forEach(c=>{ if(c){c.destroy()} })
      charts={donutOTD:null,donutUTIL:null,barKM:null}
    }

    function renderKPIs(summary){
      const {utilPct,otdPct,kmTot,kmlProm,inc100k,activas} = summary
      const items=[
        {label:'Utilización flota', val:`${utilPct.toFixed(1)}%`},
        {label:'OTD (a tiempo)',   val:`${otdPct.toFixed(1)}%`},
        {label:'Km totales',       val: kmTot.toLocaleString('es-MX')},
        {label:'Rend. promedio',   val:`${kmlProm.toFixed(2)} km/L`},
        {label:'Incidentes/100k',  val:`${inc100k.toFixed(2)}`},
        {label:'Unid. activas',    val: activas }
      ]
      const row=document.getElementById('kpis')
      row.innerHTML=items.map(it=>`
        <div class="col-6 col-md-4 col-lg-2">
          <div class="card kpi-card p-3 h-100">
            <div class="kpi-label">${it.label}</div>
            <div class="kpi-value">${it.val}</div>
          </div>
        </div>`).join('')
    }

    function renderAlerts(data){
      const alerts=[]
      data.forEach(x=>{
        const otd=(x.Entregas_a_tiempo/x.Entregas_totales)*100
        if(x.Km_recorridos<3000) alerts.push(`⚠️ Cuidado: ${x.Unidad} con Km ${x.Km_recorridos} &lt; 3000`)
        if(otd<80) alerts.push(`⚠️ Cuidado: ${x.Unidad} con OTD ${otd.toFixed(1)}% &lt; 80%`)
      })
      document.getElementById('alertCount').textContent=alerts.length
      document.getElementById('alertsList').innerHTML = alerts.length
        ? alerts.map(a=>`<li>${a}</li>`).join('')
        : '<li>Sin alertas.</li>'
    }

    function renderTable(data){
      const tbody=document.getElementById('tbody')
      tbody.innerHTML=data.map(x=>{
        const kml=x.Km_recorridos/x.Combustible_L
        const otd=(x.Entregas_a_tiempo/x.Entregas_totales)*100
        const warn=(x.Km_recorridos<3000)||(otd<80)
        const trClass=warn?'class="table-warning"':''
        return `<tr ${trClass}>
          <td>${x.Unidad}</td><td>${x.Viajes}</td>
          <td>${x.Km_recorridos.toLocaleString('es-MX')}</td>
          <td>${x.Combustible_L.toLocaleString('es-MX')}</td>
          <td>${kml.toFixed(2)}</td><td>${otd.toFixed(1)}</td>
          <td>${x.Disponibilidad_pct}</td><td>${x.Incidentes}</td>
        </tr>`
      }).join('')
    }

    function renderCharts(data, summary){
      const labels=data.map(x=>x.Unidad)
      const kmData=data.map(x=>x.Km_recorridos)
      const otdData=data.map(x=>(x.Entregas_a_tiempo/x.Entregas_totales*100).toFixed(1))

      destroyCharts()

      charts.barKM = new Chart(document.getElementById('barKM'), {
        type:'bar',
        data:{labels, datasets:[{label:'Km', data:kmData}]},
        options:{responsive:true, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true}}}
      })

      const otdRest=100-summary.otdPct
      charts.donutOTD = new Chart(document.getElementById('donutOTD'), {
        type:'doughnut',
        data:{labels:['A tiempo','Fuera de tiempo'], datasets:[{data:[summary.otdPct, otdRest]}]},
        options:{responsive:true, plugins:{legend:{display:false}}, cutout:'70%'}
      })
      document.getElementById('badgeOTD').textContent = `${summary.otdPct.toFixed(1)}%`

      charts.donutUTIL = new Chart(document.getElementById('donutUTIL'), {
        type:'doughnut',
        data:{labels:['Utilizado','Libre'], datasets:[{data:[summary.utilPct, 100-summary.utilPct]}]},
        options:{responsive:true, plugins:{legend:{display:false}}, cutout:'70%'}
      })
      document.getElementById('badgeUTIL').textContent = `${summary.utilPct.toFixed(1)}%`
    }

    function summarize(data){
      const kmTot = data.reduce((a,x)=>a+x.Km_recorridos,0)
      const litros= data.reduce((a,x)=>a+x.Combustible_L,0)
      const otdOk = data.reduce((a,x)=>a+x.Entregas_a_tiempo,0)
      const otdTot= data.reduce((a,x)=>a+x.Entregas_totales,0)
      const incTot= data.reduce((a,x)=>a+x.Incidentes,0)
      const kmlProm = kmTot/litros
      const otdPct  = otdTot? (otdOk/otdTot*100):0
      // Utilización: viajes realizados vs capacidad mensual (36 por unidad)
      const viajesReal = data.reduce((a,x)=>a+x.Viajes,0)
      const capacidad  = data.length*36
      const utilPct    = capacidad? (viajesReal/capacidad*100):0
      const inc100k    = kmTot? (incTot/kmTot*100000):0
      const activas    = data.filter(x=>x.Viajes>0).length
      return {kmTot,kmlProm,otdPct,utilPct,inc100k,activas}
    }

    function renderAll(data){
      const summary=summarize(data)
      renderKPIs(summary)
      renderAlerts(data)
      renderTable(data)
      renderCharts(data,summary)
    }

    // ======== Bootstrap ========
    function start(){
      const data=genData(12)
      renderAll(data)
      document.getElementById('btnRnd').onclick=()=>renderAll(genData(12))
    }
    start()
  </script>
</body>
</html>
