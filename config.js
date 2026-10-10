// Local GBP Engine — deployment configuration.
//
// ACTION FOR THE OPERATOR (one-time, $0): create a Stripe Payment Link for the
// $199/location/mo pilot, then paste the link below. Without it, the page is a
// complete, working marketing site with a functional CTA that requests contact
// — it does NOT fake a checkout.
//
// To get a free Stripe Payment Link:
//   1. dashboard.stripe.com -> Payments -> Payment Links -> New
//   2. Product: "Local GBP Engine — pilot location", price $199/mo, recurring
//   3. Copy the link (https://buy.stripe.com/...) and paste it below.
window.GBP_ENGINE_CHECKOUT_URL = ""; // <- paste your Stripe Payment Link here
