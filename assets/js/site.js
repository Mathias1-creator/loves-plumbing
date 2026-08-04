/* Love's Plumbing and Drains — progressive enhancement only.
   Every page works with JS disabled: the nav falls back to visible links,
   FAQ answers render open, and gallery images are plain images. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------- mobile nav --- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });

    // Close when a link is chosen or focus leaves the header
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
        toggle.focus();
      }
    });
  }

  /* --------------------------------------------------------- FAQ ----- */
  // Answers ship open (no-JS readable); collapse them once JS is running.
  document.querySelectorAll(".faq-q").forEach(function (btn) {
    var panel = document.getElementById(btn.getAttribute("aria-controls"));
    if (!panel) return;

    btn.setAttribute("aria-expanded", "false");
    panel.classList.remove("is-open");
    panel.hidden = true;

    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      panel.hidden = open;
      panel.classList.toggle("is-open", !open);
    });
  });

  /* ------------------------------------------------- scroll reveal --- */
  var revealables = document.querySelectorAll(".reveal");
  if (reduced || !("IntersectionObserver" in window)) {
    revealables.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ---------------------------------------------------- lightbox ----- */
  var lb = document.getElementById("lightbox");
  var triggers = Array.prototype.slice.call(document.querySelectorAll("[data-lb]"));
  if (!lb || !triggers.length) return;

  var lbImg = lb.querySelector(".lb-img");
  var lbCounter = lb.querySelector(".lb-counter");
  var btnPrev = lb.querySelector(".lb-prev");
  var btnNext = lb.querySelector(".lb-next");
  var btnClose = lb.querySelector(".lb-close");
  var index = 0;
  var lastFocused = null;

  function show(i) {
    index = (i + triggers.length) % triggers.length;
    var t = triggers[index];
    var img = t.querySelector("img");

    lbImg.src = t.getAttribute("data-lb-src") || img.currentSrc || img.src;
    lbImg.srcset = t.getAttribute("data-lb-srcset") || "";
    lbImg.sizes = "100vw";
    // The description carries over as the image's alt attribute — it stays the
    // enlarged photo's accessible name, it just is not rendered as visible text.
    lbImg.alt = img.getAttribute("alt") || "";
    lbCounter.textContent = index + 1 + " / " + triggers.length;
  }

  function open(i) {
    lastFocused = document.activeElement;
    show(i);
    lb.classList.add("is-open");
    lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    btnClose.focus();
  }

  function close() {
    lb.classList.remove("is-open");
    lb.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    lbImg.removeAttribute("src");
    lbImg.removeAttribute("srcset");
    if (lastFocused) lastFocused.focus();
  }

  triggers.forEach(function (t, i) {
    t.addEventListener("click", function (e) {
      e.preventDefault();
      open(i);
    });
  });

  btnClose.addEventListener("click", close);
  btnPrev.addEventListener("click", function () { show(index - 1); });
  btnNext.addEventListener("click", function () { show(index + 1); });

  // Click the backdrop (but not the image or controls) to dismiss
  lb.addEventListener("click", function (e) {
    if (e.target === lb) close();
  });

  document.addEventListener("keydown", function (e) {
    if (!lb.classList.contains("is-open")) return;

    if (e.key === "Escape") { close(); return; }
    if (e.key === "ArrowLeft") { e.preventDefault(); show(index - 1); return; }
    if (e.key === "ArrowRight") { e.preventDefault(); show(index + 1); return; }

    // Keep Tab inside the dialog while it is open
    if (e.key === "Tab") {
      var focusable = [btnClose, btnPrev, btnNext];
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });

  // Swipe between images on touch devices
  var startX = null;
  lb.addEventListener("touchstart", function (e) { startX = e.changedTouches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", function (e) {
    if (startX === null) return;
    var dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 45) show(index + (dx < 0 ? 1 : -1));
    startX = null;
  }, { passive: true });
})();
