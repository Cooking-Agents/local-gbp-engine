/*
 * Local GBP Engine — checkout wiring.
 *
 * The live Stripe Payment Link is NOT hardcoded here (it must be created by a human
 * on a real Stripe account). This script reads the link from the injected
 * window.GBP_ENGINE_CHECKOUT_URL (set in config.js, which the operator fills in).
 *
 * If no real link is configured, the buttons are left non-functional and a clear
 * notice is shown — the site NEVER fabricates a checkout URL or pretends to sell.
 */
(function () {
  var checkoutUrl =
    (window.GBP_ENGINE_CHECKOUT_URL && window.GBP_ENGINE_CHECKOUT_URL.trim()) || "";

  var statusEl = document.getElementById("checkout-status");
  var triggers = document.querySelectorAll("[data-checkout-trigger]");

  if (checkoutUrl) {
    triggers.forEach(function (el) {
      el.addEventListener("click", function (ev) {
        // Allow in-page anchor fallback only if href is a real #section and not checkout
        ev.preventDefault();
        window.location.href = checkoutUrl;
      });
    });
    if (statusEl) {
      statusEl.textContent = "Secure checkout powered by Stripe.";
    }
  } else {
    triggers.forEach(function (el) {
      el.addEventListener("click", function (ev) {
        // If the trigger is also an in-page anchor (href="#..."), let it scroll.
        var href = el.getAttribute("href") || "";
        if (href.charAt(0) === "#" && href.length > 1) {
          return; // normal anchor navigation
        }
        ev.preventDefault();
      });
    });
    if (statusEl) {
      statusEl.textContent =
        "Checkout is being configured — contact us to book a pilot location.";
    }
  }

  // Footer year
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
})();
