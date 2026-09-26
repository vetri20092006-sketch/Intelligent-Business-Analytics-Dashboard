/**
 * OmniMetrics AI - Dataset Explorer & Data Dictionary
 * Manages paginated interactive table, live search filtering, and Chart.js distribution charts.
 */

document.addEventListener("DOMContentLoaded", () => {
  const datasetContainer = document.getElementById("dataset-page-container");
  if (!datasetContainer) return;

  let currentPage = 1;
  let currentLimit = 10;
  let currentSearch = "";
  let currentSortBy = "customer_id";
  let currentSortOrder = "asc";

  let targetChartInstance = null;
  let contractChartInstance = null;

  // Search input with debounce
  const searchInput = document.getElementById("table-search-input");
  let debounceTimer;

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        currentSearch = e.target.value.trim();
        currentPage = 1;
        fetchTableData();
      }, 300);
    });
  }

  // Limit select
  const limitSelect = document.getElementById("table-limit-select");
  if (limitSelect) {
    limitSelect.addEventListener("change", (e) => {
      currentLimit = parseInt(e.target.value, 10);
      currentPage = 1;
      fetchTableData();
    });
  }

  // Pagination buttons
  const prevBtn = document.getElementById("page-prev-btn");
  const nextBtn = document.getElementById("page-next-btn");

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      if (currentPage > 1) {
        currentPage--;
        fetchTableData();
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      currentPage++;
      fetchTableData();
    });
  }

  // Column header sorting
  document.querySelectorAll(".data-table th.sortable").forEach((th) => {
    th.addEventListener("click", () => {
      const col = th.getAttribute("data-sort");
      if (currentSortBy === col) {
        currentSortOrder = currentSortOrder === "asc" ? "desc" : "asc";
      } else {
        currentSortBy = col;
        currentSortOrder = "asc";
      }

      // Update UI sort indicators
      document.querySelectorAll(".data-table th.sortable i").forEach((icon) => {
        icon.className = "fa-solid fa-sort";
      });
      const icon = th.querySelector("i");
      if (icon) {
        icon.className = currentSortOrder === "asc" ? "fa-solid fa-sort-up" : "fa-solid fa-sort-down";
      }

      fetchTableData();
    });
  });

  // Fetch Table Data
  async function fetchTableData() {
    const tableBody = document.getElementById("dataset-table-body");
    const countInfo = document.getElementById("table-count-info");
    const pageIndicator = document.getElementById("current-page-num");

    if (tableBody) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="10" style="text-align: center; padding: 2rem;">
            <div class="skeleton-text" style="width: 60%; margin: 0 auto;"></div>
          </td>
        </tr>
      `;
    }

    try {
      const params = new URLSearchParams({
        page: currentPage,
        limit: currentLimit,
        search: currentSearch,
        sort_by: currentSortBy,
        sort_order: currentSortOrder
      });

      const response = await fetch(`/api/dataset-sample?${params.toString()}`);
      const res = await response.json();

      if (!response.ok || res.status !== "success") {
        throw new Error(res.message || "Failed to load table rows.");
      }

      const { records, pagination } = res.data;

      // Update table rows
      if (tableBody) {
        tableBody.innerHTML = "";

        if (records.length === 0) {
          tableBody.innerHTML = `
            <tr>
              <td colspan="10" style="text-align:center; padding: 2rem; color: var(--text-muted);">
                <i class="fa-solid fa-magnifying-glass" style="font-size: 1.5rem; margin-bottom: 0.5rem; display:block;"></i>
                No customer records found matching "${currentSearch}".
              </td>
            </tr>
          `;
          return;
        }

        records.forEach((row) => {
          const tr = document.createElement("tr");

          const churnBadge =
            row.has_churned === 1
              ? `<span class="badge badge-danger"><i class="fa-solid fa-xmark"></i> Churned</span>`
              : `<span class="badge badge-success"><i class="fa-solid fa-check"></i> Retained</span>`;

          const tierBadge =
            row.service_tier === "Enterprise"
              ? `<span class="badge badge-primary">Enterprise</span>`
              : row.service_tier === "Growth"
              ? `<span class="badge badge-cyan">Growth</span>`
              : `<span class="badge" style="background:var(--bg-tertiary); color:var(--text-secondary);">Starter</span>`;

          tr.innerHTML = `
            <td style="font-family: var(--font-mono); font-weight: 700; color: var(--text-primary);">${row.customer_id}</td>
            <td>${tierBadge}</td>
            <td>${row.contract_type} (${row.contract_length_months}m)</td>
            <td>${row.tenure_months} mos</td>
            <td style="font-family: var(--font-mono);">$${row.monthly_charges.toFixed(2)}</td>
            <td style="font-family: var(--font-mono);">$${row.total_charges.toLocaleString()}</td>
            <td>
              <div style="display:flex; align-items:center; gap:0.5rem;">
                <div style="flex:1; height:6px; background:var(--bg-tertiary); border-radius:99px; overflow:hidden; min-width:40px;">
                  <div style="width:${row.product_usage_score}%; height:100%; background:var(--brand-primary);"></div>
                </div>
                <span style="font-family:var(--font-mono); font-size:0.75rem;">${row.product_usage_score}</span>
              </div>
            </td>
            <td style="font-family: var(--font-mono);">${row.nps_score}/10</td>
            <td>${row.support_tickets_quarter}</td>
            <td>${churnBadge}</td>
          `;

          tableBody.appendChild(tr);
        });
      }

      // Update Pagination state
      if (pageIndicator) pageIndicator.textContent = `Page ${pagination.page} of ${pagination.total_pages}`;
      if (countInfo) {
        const start = (pagination.page - 1) * pagination.limit + 1;
        const end = Math.min(pagination.page * pagination.limit, pagination.total_records);
        countInfo.textContent = `Showing ${start.toLocaleString()} - ${end.toLocaleString()} of ${pagination.total_records.toLocaleString()} customer records`;
      }

      if (prevBtn) prevBtn.disabled = !pagination.has_prev;
      if (nextBtn) nextBtn.disabled = !pagination.has_next;
      currentPage = pagination.page;

    } catch (err) {
      console.error("Dataset table fetch error:", err);
      if (tableBody) {
        tableBody.innerHTML = `<tr><td colspan="10" style="text-align:center; color:var(--color-danger); padding:1.5rem;">Error loading data: ${err.message}</td></tr>`;
      }
    }
  }

  // Fetch Dataset Distribution Charts
  async function loadDistributionCharts() {
    try {
      const response = await fetch("/api/dataset-stats");
      const res = await response.json();

      if (!response.ok || res.status !== "success") return;
      const s = res.data;

      // Update KPI chips
      const totalRecEl = document.getElementById("ds-total-records");
      const retainedPctEl = document.getElementById("ds-retained-pct");
      const churnPctEl = document.getElementById("ds-churn-pct");

      if (totalRecEl) totalRecEl.textContent = s.total_records.toLocaleString();
      if (retainedPctEl) retainedPctEl.textContent = `${s.retained_pct}%`;
      if (churnPctEl) churnPctEl.textContent = `${s.churned_pct}%`;

      renderTargetDonut(s.retained_count, s.churned_count);
      renderContractDistribution(s.contract_type_churn);

    } catch (err) {
      console.error("Dataset stats fetch error:", err);
    }
  }

  function getThemeColors() {
    const isDark = document.documentElement.getAttribute("data-theme") !== "light";
    return {
      textColor: isDark ? "#94a3b8" : "#475569",
      gridColor: isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(15, 23, 42, 0.06)"
    };
  }

  function renderTargetDonut(retained, churned) {
    const ctx = document.getElementById("targetDistChart")?.getContext("2d");
    if (!ctx) return;

    if (targetChartInstance) targetChartInstance.destroy();
    const colors = getThemeColors();

    targetChartInstance = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Active / Retained", "Churned Accounts"],
        datasets: [
          {
            data: [retained, churned],
            backgroundColor: ["#10b981", "#f43f5e"],
            borderColor: "transparent",
            hoverOffset: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "70%",
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: colors.textColor, font: { family: "Inter", size: 12 } }
          }
        }
      }
    });
  }

  function renderContractDistribution(contractData) {
    const ctx = document.getElementById("contractDistChart")?.getContext("2d");
    if (!ctx || !contractData) return;

    if (contractChartInstance) contractChartInstance.destroy();
    const colors = getThemeColors();

    const labels = contractData.map((d) => d.contract_type);
    const churnRates = contractData.map((d) => d.churn_rate);

    contractChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Churn Rate (%)",
            data: churnRates,
            backgroundColor: ["#f43f5e", "#f59e0b", "#10b981"],
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => ` Churn Rate: ${context.parsed.y}%`
            }
          }
        },
        scales: {
          y: {
            title: { display: true, text: "Churn Rate (%)", color: colors.textColor },
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor },
            max: 100
          },
          x: {
            grid: { display: false },
            ticks: { color: colors.textColor }
          }
        }
      }
    });
  }

  window.addEventListener("themeChanged", () => {
    loadDistributionCharts();
  });

  fetchTableData();
  loadDistributionCharts();
});
