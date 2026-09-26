/**
 * OmniMetrics AI - Global Client Application Script
 * Theme Toggle, Mobile Navigation, Toast Notification System, Scroll-to-Top
 */

(function () {
  "use strict";

  // --------------------------------------------------------------------------
  // Theme Management (Obsidian Dark vs Crisp Light)
  // --------------------------------------------------------------------------
  const THEME_STORAGE_KEY = "omnimetrics_theme";
  const themeToggleBtn = document.getElementById("theme-toggle-btn");

  function getPreferredTheme() {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored) return stored;
    return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);

    if (themeToggleBtn) {
      const icon = themeToggleBtn.querySelector("i");
      if (icon) {
        if (theme === "light") {
          icon.className = "fa-solid fa-moon";
          themeToggleBtn.setAttribute("title", "Switch to Dark Mode");
          themeToggleBtn.setAttribute("aria-label", "Switch to Dark Mode");
        } else {
          icon.className = "fa-solid fa-sun";
          themeToggleBtn.setAttribute("title", "Switch to Light Mode");
          themeToggleBtn.setAttribute("aria-label", "Switch to Light Mode");
        }
      }
    }

    // Dispatch custom event for Chart.js instances to re-render colors if needed
    window.dispatchEvent(new CustomEvent("themeChanged", { detail: { theme } }));
  }

  // Initialize theme
  const initialTheme = getPreferredTheme();
  applyTheme(initialTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      showToast("Theme Updated", `Switched to ${next} theme mode.`, "info", 2500);
    });
  }

  // --------------------------------------------------------------------------
  // Mobile Drawer Navigation
  // --------------------------------------------------------------------------
  const mobileToggleBtn = document.getElementById("mobile-nav-toggle");
  const mobileDrawer = document.getElementById("mobile-drawer");

  if (mobileToggleBtn && mobileDrawer) {
    mobileToggleBtn.addEventListener("click", () => {
      const isOpen = mobileDrawer.classList.contains("open");
      if (isOpen) {
        mobileDrawer.classList.remove("open");
        mobileToggleBtn.innerHTML = '<i class="fa-solid fa-bars"></i>';
      } else {
        mobileDrawer.classList.add("open");
        mobileToggleBtn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
      }
    });

    // Close when clicking link
    mobileDrawer.querySelectorAll(".nav-link").forEach((link) => {
      link.addEventListener("click", () => {
        mobileDrawer.classList.remove("open");
        mobileToggleBtn.innerHTML = '<i class="fa-solid fa-bars"></i>';
      });
    });
  }

  // --------------------------------------------------------------------------
  // Global Toast Notification Manager
  // --------------------------------------------------------------------------
  window.showToast = function (title, message, type = "info", duration = 4000) {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let iconClass = "fa-circle-info";
    if (type === "success") iconClass = "fa-circle-check";
    if (type === "warning") iconClass = "fa-triangle-exclamation";
    if (type === "danger") iconClass = "fa-circle-exclamation";

    toast.innerHTML = `
      <i class="fa-solid ${iconClass} toast-icon"></i>
      <div class="toast-body">
        <div class="toast-title">${escapeHtml(title)}</div>
        <div class="toast-message">${escapeHtml(message)}</div>
      </div>
      <button class="toast-close" aria-label="Close Notification">
        <i class="fa-solid fa-xmark"></i>
      </button>
    `;

    const closeBtn = toast.querySelector(".toast-close");
    closeBtn.addEventListener("click", () => removeToast(toast));

    container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(toast);
      }, duration);
    }
  };

  function removeToast(toast) {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 250);
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

  // --------------------------------------------------------------------------
  // Scroll to Top Button
  // --------------------------------------------------------------------------
  const scrollTopBtn = document.getElementById("scroll-top-btn");
  if (scrollTopBtn) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 300) {
        scrollTopBtn.classList.add("visible");
      } else {
        scrollTopBtn.classList.remove("visible");
      }
    });

    scrollTopBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // --------------------------------------------------------------------------
  // Navbar scroll background enhancement
  // --------------------------------------------------------------------------
  const header = document.querySelector(".site-header");
  if (header) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 20) {
        header.style.boxShadow = "var(--shadow-md)";
      } else {
        header.style.boxShadow = "none";
      }
    });
  }
})();
