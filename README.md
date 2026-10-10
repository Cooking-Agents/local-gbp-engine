# Local GBP Engine

Productized, done-for-you **white-label Google Business Profile fulfillment** for local SEO
agencies. Per location, per month we produce and publish **4 optimized GBP posts**, draft
**every review reply in your client's voice**, and send a **branded monthly report** — all under
*your* agency's brand. You resell it; we're invisible.

**$199 / location / month.** Undercuts the documented $349/mo white-label floor — you still keep a
50%+ margin reselling at $300–500/location.

## What you get (per location, per month)
- 4 published GBP posts (What's New / seasonal / offer / reminder) via the free GBP API, with
  photos and a CTA button.
- Review replies drafted in your client's tone, queued for your approval, then published.
- One branded monthly report (your logo): posts published, reviews answered, profile
  completeness, impression trend — ready to forward to your client.
- Truly white-label: your brand everywhere, no mention of us, ever.

## Who this is for
Local SEO agencies and white-label fulfillment shops already selling a GBP / citations / review
line item and paying $349–$1,000/client/mo to fulfill it. You own the client relationship and the
margin; we do the monthly grind.

## Live offer
Landing page: https://gist.githubusercontent.com/Cooking-Agents/1a6e6095b02d1ebe3bd92c7505da7068/raw/index.html

## Delivery pipeline
`pipeline/gbp_engine.py` — a CLI with three stages:
- `generate` — 4 GBP post drafts + report skeleton for a location.
- `report` — the branded monthly report JSON.
- `publish` — publishes approved posts via the free GBP API. **Human-gated**: requires Google
  OAuth credentials (see the build notes). Never fakes a publish.

## Status / honesty note
The marketing site and delivery pipeline are real and verified. The live Stripe checkout is
configured but not yet activated (needs a real Stripe account), and post publishing is gated on
Google OAuth credentials a human must create — both are flagged, never faked.
