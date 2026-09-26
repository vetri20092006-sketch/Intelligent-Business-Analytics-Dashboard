/**
 * OmniMetrics AI - Prediction Studio Engine
 * Handles form validation, slider synchronizations, sample case prefilling,
 * asynchronous API requests, animated confidence gauge, and prescriptive advice.
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("prediction-form");
  if (!form) return;

  const predictBtn = document.getElementById("predict-submit-btn");
  const resetBtn = document.getElementById("reset-form-btn");
  const resultCardWrap = document.getElementById("result-card-wrap");
  const skeletonCard = document.getElementById("prediction-skeleton");

  // Sample Presets Definition
  const sampleProfiles = {
    enterprise: {
      tenure_months: 36,
      contract_length_months: 24,
      contract_type: "Multi-Year",
      service_tier: "Enterprise",
      monthly_charges: 580.0,
      total_charges: 20880.0,
      product_usage_score: 92.5,
      nps_score: 9,
      support_tickets_quarter: 1,
      payment_delay_days: 0
    },
    growth: {
      tenure_months: 11,
      contract_length_months: 12,
      contract_type: "Annual",
      service_tier: "Growth",
      monthly_charges: 220.0,
      total_charges: 2420.0,
      product_usage_score: 61.0,
      nps_score: 6,
      support_tickets_quarter: 3,
      payment_delay_days: 8
    },
    critical: {
      tenure_months: 3,
      contract_length_months: 1,
      contract_type: "Month-to-Month",
      service_tier: "Starter",
      monthly_charges: 89.0,
      total_charges: 267.0,
      product_usage_score: 24.0,
      nps_score: 2,
      support_tickets_quarter: 7,
      payment_delay_days: 21
    }
  };

  // --------------------------------------------------------------------------
  // Slider & Number Input Syncing
  // --------------------------------------------------------------------------
  function syncInputWithSlider(inputName, sliderId, badgeId, isFloat = false) {
    const input = form.elements[inputName];
    const slider = document.getElementById(sliderId);
    const badge = document.getElementById(badgeId);

    if (!input || !slider) return;

    slider.addEventListener("input", (e) => {
      const val = isFloat ? parseFloat(e.target.value).toFixed(1) : parseInt(e.target.value, 10);
      input.value = val;
      if (badge) badge.textContent = val;
      autoRecalculateTotal();
    });

    input.addEventListener("input", (e) => {
      const val = e.target.value;
      slider.value = val;
      if (badge) badge.textContent = isFloat ? parseFloat(val || 0).toFixed(1) : val;
      autoRecalculateTotal();
    });
  }

  syncInputWithSlider("product_usage_score", "slider-usage", "badge-usage", true);
  syncInputWithSlider("nps_score", "slider-nps", "badge-nps", false);
  syncInputWithSlider("support_tickets_quarter", "slider-tickets", "badge-tickets", false);
  syncInputWithSlider("payment_delay_days", "slider-delay", "badge-delay", false);

  // Auto calculate total charges estimation
  function autoRecalculateTotal() {
    const tenure = parseFloat(form.elements["tenure_months"]?.value || 0);
    const monthly = parseFloat(form.elements["monthly_charges"]?.value || 0);
    const totalInput = form.elements["total_charges"];
    if (totalInput && (!totalInput.value || totalInput.dataset.manual !== "true")) {
      const est = Math.max(10, Math.round(tenure * monthly));
      totalInput.value = est;
    }
  }

  const monthlyInput = form.elements["monthly_charges"];
  const tenureInput = form.elements["tenure_months"];
  const totalInput = form.elements["total_charges"];

  if (monthlyInput) monthlyInput.addEventListener("input", autoRecalculateTotal);
  if (tenureInput) tenureInput.addEventListener("input", autoRecalculateTotal);
  if (totalInput) {
    totalInput.addEventListener("input", () => {
      totalInput.dataset.manual = "true";
    });
  }

  // --------------------------------------------------------------------------
  // Preset Quick Fill Chips
  // --------------------------------------------------------------------------
  document.querySelectorAll(".preset-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".preset-chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");

      const presetKey = chip.getAttribute("data-preset");
      const profile = sampleProfiles[presetKey];
      if (!profile) return;

      Object.entries(profile).forEach(([key, val]) => {
        if (form.elements[key]) {
          form.elements[key].value = val;
          form.elements[key].dispatchEvent(new Event("input", { bubbles: true }));
        }
      });

      if (totalInput) totalInput.dataset.manual = "true";

      window.showToast(
        "Profile Loaded",
        `Loaded preset: ${chip.textContent.trim()}`,
        "info",
        2500
      );
    });
  });

  // --------------------------------------------------------------------------
  // Form Submission & Inference Calling
  // --------------------------------------------------------------------------
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Validation
    let isValid = true;
    const requiredNumeric = [
      "tenure_months",
      "contract_length_months",
      "monthly_charges",
      "total_charges",
      "product_usage_score",
      "nps_score",
      "support_tickets_quarter",
      "payment_delay_days"
    ];

    const payload = {};

    requiredNumeric.forEach((field) => {
      const input = form.elements[field];
      if (!input) return;
      const val = parseFloat(input.value);
      if (isNaN(val) || val < 0) {
        input.classList.add("is-invalid");
        isValid = false;
      } else {
        input.classList.remove("is-invalid");
        payload[field] = val;
      }
    });

    const contractType = form.elements["contract_type"]?.value;
    const serviceTier = form.elements["service_tier"]?.value;

    if (!contractType) {
      form.elements["contract_type"]?.classList.add("is-invalid");
      isValid = false;
    } else {
      payload["contract_type"] = contractType;
    }

    if (!serviceTier) {
      form.elements["service_tier"]?.classList.add("is-invalid");
      isValid = false;
    } else {
      payload["service_tier"] = serviceTier;
    }

    if (!isValid) {
      window.showToast("Validation Error", "Please verify highlighted form values.", "warning");
      return;
    }

    // Set UI to loading state
    predictBtn.classList.add("loading");
    predictBtn.disabled = true;
    if (skeletonCard) skeletonCard.style.display = "block";
    if (resultCardWrap) resultCardWrap.style.display = "none";

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const res = await response.json();

      if (!response.ok || res.status !== "success") {
        throw new Error(res.message || "Failed to compute prediction.");
      }

      renderPredictionResult(res);

      window.showToast(
        "Prediction Complete",
        `Risk tier assessed as ${res.prediction.risk_tier} (${res.prediction.churn_percentage}% churn probability).`,
        "success"
      );
    } catch (err) {
      console.error("Prediction API error:", err);
      window.showToast("Inference Error", err.message, "danger", 5000);
    } finally {
      predictBtn.classList.remove("loading");
      predictBtn.disabled = false;
      if (skeletonCard) skeletonCard.style.display = "none";
    }
  });

  // --------------------------------------------------------------------------
  // Render Result Function
  // --------------------------------------------------------------------------
  function renderPredictionResult(data) {
    if (!resultCardWrap) return;

    const p = data.prediction;

    // Elements
    const badgeWrap = document.getElementById("res-risk-badge");
    const headline = document.getElementById("res-risk-headline");
    const summary = document.getElementById("res-risk-summary");
    const arrVal = document.getElementById("res-arr-val");
    const riskRevVal = document.getElementById("res-risk-rev-val");
    const gaugeProgress = document.getElementById("gauge-circle-progress");
    const gaugeScoreText = document.getElementById("gauge-score-value");
    const gaugeScoreLabel = document.getElementById("gauge-score-label");
    const driversList = document.getElementById("risk-drivers-list");
    const recsList = document.getElementById("recommendations-list");

    // Colors mapping
    let colorHex = "#10b981"; // Emerald
    let badgeClass = "badge-success";

    if (p.risk_tier === "Critical Risk") {
      colorHex = "#f43f5e"; // Rose
      badgeClass = "badge-danger";
    } else if (p.risk_tier === "Moderate Risk") {
      colorHex = "#f59e0b"; // Amber
      badgeClass = "badge-warning";
    }

    // Badge and Titles
    if (badgeWrap) {
      badgeWrap.className = `badge ${badgeClass}`;
      badgeWrap.innerHTML = `<i class="fa-solid ${p.badge_icon}"></i> ${p.risk_tier} • ${p.risk_status}`;
    }

    if (headline) headline.textContent = `${p.risk_tier} (${p.churn_percentage}% Probability)`;
    if (summary) summary.textContent = p.summary;

    if (arrVal) arrVal.textContent = `$${p.financials.annual_arr.toLocaleString()}`;
    if (riskRevVal) riskRevVal.textContent = `$${p.financials.revenue_at_risk.toLocaleString()}`;

    // Animate Gauge
    const circumference = 502; // 2 * PI * r (r=80)
    const offset = circumference - (circumference * p.churn_percentage) / 100;

    if (gaugeProgress) {
      gaugeProgress.style.stroke = colorHex;
      // Trigger smooth transition
      setTimeout(() => {
        gaugeProgress.style.strokeDashoffset = offset;
      }, 50);
    }

    if (gaugeScoreText) {
      gaugeScoreText.textContent = `${p.churn_percentage}%`;
      gaugeScoreText.style.color = colorHex;
    }

    if (gaugeScoreLabel) {
      gaugeScoreLabel.textContent = "Churn Propensity";
    }

    // Populate Risk Drivers
    if (driversList) {
      driversList.innerHTML = "";
      (data.risk_drivers || []).forEach((driver) => {
        const item = document.createElement("div");
        item.className = "driver-item";
        let iconClass = "fa-circle-check text-success";
        if (driver.impact === "High Risk") iconClass = "fa-circle-xmark text-danger";
        else if (driver.impact === "Medium Risk") iconClass = "fa-triangle-exclamation text-warning";

        item.innerHTML = `
          <div class="driver-icon"><i class="fa-solid ${iconClass}"></i></div>
          <div class="driver-info">
            <h5>${escapeHtml(driver.name)} <span class="badge ${driver.impact === 'High Risk' ? 'badge-danger' : driver.impact === 'Medium Risk' ? 'badge-warning' : 'badge-success'}" style="font-size:0.65rem; padding: 2px 6px;">${driver.impact}</span></h5>
            <p>${escapeHtml(driver.detail)}</p>
          </div>
        `;
        driversList.appendChild(item);
      });
    }

    // Populate Recommendations
    if (recsList) {
      recsList.innerHTML = "";
      (data.recommendations || []).forEach((rec) => {
        const item = document.createElement("div");
        item.className = "rec-item";

        let priorityBadge = "badge-primary";
        if (rec.badge_color === "danger") priorityBadge = "badge-danger";
        if (rec.badge_color === "warning") priorityBadge = "badge-warning";
        if (rec.badge_color === "success") priorityBadge = "badge-success";

        item.innerHTML = `
          <div class="rec-header">
            <span class="rec-title">${escapeHtml(rec.title)}</span>
            <span class="badge ${priorityBadge}">${rec.priority} Priority</span>
          </div>
          <p class="rec-action">${escapeHtml(rec.action)}</p>
          <div class="rec-impact">
            <i class="fa-solid fa-arrow-trend-up"></i>
            <span>${escapeHtml(rec.impact)}</span>
          </div>
        `;
        recsList.appendChild(item);
      });
    }

    // Show result card
    resultCardWrap.style.display = "block";
    resultCardWrap.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // --------------------------------------------------------------------------
  // Form Reset
  // --------------------------------------------------------------------------
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      form.reset();
      document.querySelectorAll(".preset-chip").forEach((c) => c.classList.remove("active"));
      if (resultCardWrap) resultCardWrap.style.display = "none";

      // Reset badges
      const badgeUsage = document.getElementById("badge-usage");
      if (badgeUsage) badgeUsage.textContent = "65.0";
      const badgeNps = document.getElementById("badge-nps");
      if (badgeNps) badgeNps.textContent = "7";
      const badgeTickets = document.getElementById("badge-tickets");
      if (badgeTickets) badgeTickets.textContent = "2";
      const badgeDelay = document.getElementById("badge-delay");
      if (badgeDelay) badgeDelay.textContent = "0";

      // Reset sliders
      document.getElementById("slider-usage").value = 65;
      document.getElementById("slider-nps").value = 7;
      document.getElementById("slider-tickets").value = 2;
      document.getElementById("slider-delay").value = 0;

      window.showToast("Form Reset", "Form parameters restored to standard defaults.", "info", 2000);
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
