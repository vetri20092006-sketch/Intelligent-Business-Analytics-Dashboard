/**
 * OmniMetrics AI - Model Performance & Diagnostics
 * Initializes Chart.js for ROC Curve, Confusion Matrix, and Feature Importance.
 */

document.addEventListener("DOMContentLoaded", () => {
  const perfContainer = document.getElementById("performance-page-container");
  if (!perfContainer) return;

  let rocChartInstance = null;
  let featChartInstance = null;

  async function loadPerformanceData() {
    try {
      const response = await fetch("/api/model-info");
      const res = await response.json();

      if (!response.ok || res.status !== "success") {
        throw new Error(res.message || "Failed to load model metrics.");
      }

      const m = res.data;
      updateKpis(m);
      renderRocCurve(m.roc_curve, m.roc_auc);
      renderConfusionMatrix(m.confusion_matrix);
      renderFeatureImportance(m.feature_importance);
      renderModelParameters(m);

    } catch (err) {
      console.error("Error loading model performance:", err);
      window.showToast("Metrics Error", "Could not load model diagnostics data.", "danger");
    }
  }

  function updateKpis(m) {
    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    setVal("kpi-acc", `${(m.accuracy * 100).toFixed(1)}%`);
    setVal("kpi-prec", `${(m.precision * 100).toFixed(1)}%`);
    setVal("kpi-rec", `${(m.recall * 100).toFixed(1)}%`);
    setVal("kpi-f1", `${(m.f1_score * 100).toFixed(1)}%`);
    setVal("kpi-auc", m.roc_auc.toFixed(3));
  }

  function getThemeColors() {
    const isDark = document.documentElement.getAttribute("data-theme") !== "light";
    return {
      textColor: isDark ? "#94a3b8" : "#475569",
      gridColor: isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(15, 23, 42, 0.06)",
      primary: "#6366f1",
      secondary: "#06b6d4",
      bgFill: isDark ? "rgba(99, 102, 241, 0.15)" : "rgba(99, 102, 241, 0.1)"
    };
  }

  function renderRocCurve(points, auc) {
    const ctx = document.getElementById("rocChart")?.getContext("2d");
    if (!ctx) return;

    if (rocChartInstance) rocChartInstance.destroy();

    const colors = getThemeColors();

    const labels = points.map((p) => p.x);
    const dataPoints = points.map((p) => p.y);

    rocChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: `Random Forest Model (AUC = ${auc.toFixed(3)})`,
            data: dataPoints,
            borderColor: colors.primary,
            backgroundColor: colors.bgFill,
            borderWidth: 3,
            fill: true,
            tension: 0.25,
            pointRadius: 2,
            pointHoverRadius: 6,
            pointBackgroundColor: colors.secondary
          },
          {
            label: "Random Baseline (AUC = 0.500)",
            data: labels.map((x) => x),
            borderColor: "#64748b",
            borderWidth: 1.5,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false
        },
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: colors.textColor, font: { family: "Inter", size: 12 } }
          },
          tooltip: {
            callbacks: {
              label: (context) => `TPR: ${context.parsed.y.toFixed(3)} | FPR: ${labels[context.dataIndex]}`
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: "False Positive Rate (1 - Specificity)", color: colors.textColor },
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor, maxTicksLimit: 6 }
          },
          y: {
            title: { display: true, text: "True Positive Rate (Sensitivity / Recall)", color: colors.textColor },
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor },
            min: 0,
            max: 1
          }
        }
      }
    });
  }

  function renderConfusionMatrix(cm) {
    const tnEl = document.getElementById("cm-tn");
    const fpEl = document.getElementById("cm-fp");
    const fnEl = document.getElementById("cm-fn");
    const tpEl = document.getElementById("cm-tp");

    if (tnEl) tnEl.textContent = cm.true_negative.toLocaleString();
    if (fpEl) fpEl.textContent = cm.false_positive.toLocaleString();
    if (fnEl) fnEl.textContent = cm.false_negative.toLocaleString();
    if (tpEl) tpEl.textContent = cm.true_positive.toLocaleString();

    const total = cm.total_test_samples || 1000;
    const tnRate = document.getElementById("cm-tn-rate");
    const fpRate = document.getElementById("cm-fp-rate");
    const fnRate = document.getElementById("cm-fn-rate");
    const tpRate = document.getElementById("cm-tp-rate");

    if (tnRate) tnRate.textContent = `${((cm.true_negative / total) * 100).toFixed(1)}% of test set`;
    if (fpRate) fpRate.textContent = `${((cm.false_positive / total) * 100).toFixed(1)}% of test set`;
    if (fnRate) fnRate.textContent = `${((cm.false_negative / total) * 100).toFixed(1)}% of test set`;
    if (tpRate) tpRate.textContent = `${((cm.true_positive / total) * 100).toFixed(1)}% of test set`;
  }

  function renderFeatureImportance(featList) {
    const ctx = document.getElementById("featChart")?.getContext("2d");
    if (!ctx) return;

    if (featChartInstance) featChartInstance.destroy();

    const colors = getThemeColors();

    // Top 8 features
    const topFeats = (featList || []).slice(0, 8);
    const labels = topFeats.map((f) => f.display_name);
    const dataValues = topFeats.map((f) => f.percentage);

    featChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Feature Importance (%)",
            data: dataValues,
            backgroundColor: [
              "rgba(99, 102, 241, 0.85)",
              "rgba(6, 182, 212, 0.85)",
              "rgba(16, 185, 129, 0.85)",
              "rgba(245, 158, 11, 0.85)",
              "rgba(147, 51, 234, 0.85)",
              "rgba(236, 72, 153, 0.85)",
              "rgba(59, 130, 246, 0.85)",
              "rgba(100, 116, 139, 0.85)"
            ],
            borderRadius: 6,
            borderSkipped: false
          }
        ]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => ` Relative Influence: ${context.parsed.x.toFixed(1)}%`
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: "Gini Importance Percentage (%)", color: colors.textColor },
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor }
          },
          y: {
            grid: { display: false },
            ticks: { color: colors.textColor, font: { family: "Inter", size: 12, weight: 600 } }
          }
        }
      }
    });
  }

  function renderModelParameters(m) {
    const list = document.getElementById("model-params-table");
    if (!list || !m.parameters) return;

    list.innerHTML = "";
    const params = [
      { label: "Algorithm Architecture", val: m.model_type },
      { label: "Ensemble Estimators", val: m.parameters.n_estimators },
      { label: "Tree Max Depth", val: m.parameters.max_depth },
      { label: "Min Samples Leaf", val: m.parameters.min_samples_leaf },
      { label: "Class Weighting Strategy", val: m.parameters.class_weight },
      { label: "Validation Methodology", val: m.parameters.cross_validation },
      { label: "Feature Scaler", val: m.parameters.scaler },
      { label: "Categorical Encoding", val: m.parameters.encoder },
      { label: "Training Split Size", val: `${m.training_samples.toLocaleString()} samples (80%)` },
      { label: "Test Split Size", val: `${m.test_samples.toLocaleString()} samples (20%)` }
    ];

    params.forEach((p) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td style="font-weight: 600; color: var(--text-primary);">${p.label}</td>
        <td style="font-family: var(--font-mono); color: var(--brand-secondary);">${p.val}</td>
      `;
      list.appendChild(row);
    });
  }

  // Handle dynamic theme changes
  window.addEventListener("themeChanged", () => {
    loadPerformanceData();
  });

  loadPerformanceData();
});
