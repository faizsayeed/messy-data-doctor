<script>
const stats = {{ analytics.stats | tojson }};
const missing = {{ analytics.missing | tojson }};
const variance = {{ analytics.variance | tojson }};
const outliers = {{ analytics.outliers | tojson }};
const corr = {{ analytics.correlation | tojson }};
const columns = Object.keys(stats);

/* 1️⃣ BAR: MIN / MEAN / MAX */
new Chart(barChart, {
  type: "bar",
  data: {
    labels: columns,
    datasets: [
      { label: "Min", data: columns.map(c => stats[c].min) },
      { label: "Mean", data: columns.map(c => stats[c].mean) },
      { label: "Max", data: columns.map(c => stats[c].max) }
    ]
  },
  options: { responsive:true, maintainAspectRatio:false }
});

/* 2️⃣ HISTOGRAM (SIMULATED) */
new Chart(histChart, {
  type: "line",
  data: {
    labels: columns,
    datasets: [{
      label: "Mean Distribution",
      data: columns.map(c => stats[c].mean),
      tension: 0.4
    }]
  },
  options: { responsive:true, maintainAspectRatio:false }
});

/* 3️⃣ VARIANCE */
new Chart(varianceChart, {
  type: "bar",
  data: {
    labels: columns,
    datasets: [{
      label: "Variance",
      data: columns.map(c => variance[c])
    }]
  },
  options: { responsive:true, maintainAspectRatio:false }
});

/* 4️⃣ MISSING VALUES */
new Chart(missingChart, {
  type: "bar",
  data: {
    labels: columns,
    datasets: [{
      label: "Missing Values",
      data: columns.map(c => missing[c])
    }]
  },
  options: { responsive:true, maintainAspectRatio:false }
});

/* 5️⃣ OUTLIERS */
new Chart(outlierChart, {
  type: "bar",
  data: {
    labels: columns,
    datasets: [{
      label: "Outliers",
      data: columns.map(c => outliers[c])
    }]
  },
  options: { responsive:true, maintainAspectRatio:false }
});

/* 6️⃣ HEATMAP */
const heatLabels = Object.keys(corr);
const heatData = [];
heatLabels.forEach((x,i) => {
  heatLabels.forEach((y,j) => {
    heatData.push({x:i,y:j,v:corr[x][y]});
  });
});

new Chart(heatmap, {
  type:"scatter",
  data:{datasets:[{data:heatData,pointRadius:10}]},
  options:{
    responsive:true,
    maintainAspectRatio:false,
    scales:{
      x:{ticks:{callback:v=>heatLabels[v]}},
      y:{ticks:{callback:v=>heatLabels[v]}}
    }
  }
});
</script>
