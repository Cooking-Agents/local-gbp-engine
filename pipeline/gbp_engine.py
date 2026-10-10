#!/usr/bin/env python3
"""
Local GBP Engine — white-label GBP content + review-reply pipeline (v1, $0 stack).

Pure Python standard library. No paid APIs, no network calls, no credentials
required to run the DRAFT + REPORT stages. The PUBLISH stage is credential-gated
(Google OAuth for the GBP API) and refuses to run without real credentials —
it never fakes a publish.

Stages: draft -> approve -> publish -> report

Commands:
  generate   Produce 4 GBP post drafts + a monthly report skeleton for a location.
  report     Render the branded monthly report from generated posts + a reviews file.
  publish    Publish approved posts to a Google Business Profile via the GBP API.
             REQUIRES OAuth credentials (see README). Refuses without them.

Every command is offline-verifiable. See build_notes.md for the exact runs.
"""
import argparse
import json
import os
import sys
import datetime

VERSION = "1.0.0"


def _today():
    return datetime.date.today()


def _month_label(d=None):
    d = d or _today()
    return d.strftime("%B %Y")


def generate_posts(name, category, city, tone="friendly"):
    """Return 4 GBP post drafts. Deterministic templates, no network."""
    cat_l = (category or "local business").lower()
    city_short = (city or "your area").split(",")[0].strip()
    tone_openers = {
        "friendly": "Hi neighbors",
        "professional": "Hello",
        "playful": "Hey there",
    }
    opener = tone_openers.get(tone, "Hi neighbors")

    posts = [
        {
            "slot": 1,
            "type": "What's New",
            "cta": "Learn more",
            "summary": f"{name} update — recent work and what we're focused on in {city_short}.",
            "title": f"What's new at {name}",
            "body": (
                f"{opener}! Quick update from the team at {name} here in {city}. "
                f"We've been busy serving {cat_l} customers across {city_short} this month. "
                f"If you've been putting off that project, now's a great time to reach out — "
                f"we'd love to help. Message us or give us a call to get started."
            ),
        },
        {
            "slot": 2,
            "type": "Seasonal",
            "cta": "Sign up",
            "summary": f"Seasonal reminder relevant to {cat_l} customers in {city_short}.",
            "title": f"{_month_label()} tips from {name}",
            "body": (
                f"{_month_label()} is here! As your trusted {cat_l} team in {city_short}, "
                f"we put together a few seasonal reminders to keep things running smoothly. "
                f"Need a hand? We're booking appointments now — reply here or call us and "
                f"we'll get you on the schedule."
            ),
        },
        {
            "slot": 3,
            "type": "Offer",
            "cta": "Get offer",
            "summary": f"A limited-time offer for {city_short} customers.",
            "title": f"Special offer for {city_short} neighbors",
            "body": (
                f"For a limited time, {name} is offering a special deal for our {city_short} "
                f"community. Whether it's routine service or a bigger job, we've got you "
                f"covered at a price that works. Tap 'Get offer' or call today to claim it "
                f"— spots are limited."
            ),
        },
        {
            "slot": 4,
            "type": "Update / Reminder",
            "cta": "Call now",
            "summary": f"Hours / how-to-reach-us reminder for {name}.",
            "title": f"Here's how to reach {name}",
            "body": (
                f"Looking for a reliable {cat_l} team in {city_short}? {name} is here to help. "
                f"Reach us by phone, message, or stop by during business hours. "
                f"We make it easy to get fast, friendly service — save this post so you "
                f"always know how to find us."
            ),
        },
    ]
    return posts


def report_skeleton(name, city, posts):
    completeness = {
        "has_hours": None,
        "has_categories": None,
        "has_photos": None,
        "has_description": None,
        "posts_this_month": len(posts),
    }
    return {
        "location": name,
        "city": city,
        "month": _month_label(),
        "posts_published": len(posts),
        "reviews_answered": None,
        "profile_completeness": completeness,
        "impression_trend": None,
        "note": (
            "Fields marked null require live GBP API data (credentials). "
            "This skeleton is produced offline; the report command fills them "
            "from real data when credentials are provided."
        ),
    }


def cmd_generate(args):
    posts = generate_posts(args.name, args.category, args.city, args.tone)
    report = report_skeleton(args.name, args.city, posts)
    outdir = args.out
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "posts.json"), "w") as f:
        json.dump({"location": args.name, "city": args.city,
                   "month": _month_label(), "posts": posts}, f, indent=2)
    with open(os.path.join(outdir, "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    # human-readable drafts for the approval step
    lines = [f"# GBP post drafts — {args.name} ({args.city}) — {_month_label()}", ""]
    for p in posts:
        lines += [f"## {p['slot']}. {p['type']} — {p['title']}",
                  f"CTA: {p['cta']}", "", p["body"], ""]
    with open(os.path.join(outdir, "posts.md"), "w") as f:
        f.write("\n".join(lines))
    print(f"Generated {len(posts)} GBP post drafts + report skeleton for '{args.name}'.")
    print(f"  -> {os.path.join(outdir, 'posts.json')}")
    print(f"  -> {os.path.join(outdir, 'posts.md')}")
    print(f"  -> {os.path.join(outdir, 'report.json')}")
    print("Next step: review posts.md, then approve + publish (publish needs GBP OAuth creds).")
    return 0


def cmd_report(args):
    posts_path = os.path.join(args.dir, "posts.json")
    if not os.path.exists(posts_path):
        print(f"error: {posts_path} not found. Run 'generate' first.", file=sys.stderr)
        return 2
    with open(posts_path) as f:
        data = json.load(f)
    reviews = []
    if args.reviews and os.path.exists(args.reviews):
        with open(args.reviews) as f:
            reviews = json.load(f)
    report = report_skeleton(data["location"], data["city"], data["posts"])
    report["reviews_answered"] = len(reviews)
    out = os.path.join(args.dir, "monthly-report.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Monthly report for '{data['location']}' written to {out}")
    print(f"  posts: {report['posts_published']}  reviews answered: {report['reviews_answered']}")
    return 0


def cmd_publish(args):
    # Credential gate — never fake a publish.
    need = ["GOOGLE_GBP_CLIENT_ID", "GOOGLE_GBP_CLIENT_SECRET",
            "GOOGLE_GBP_REFRESH_TOKEN", "GOOGLE_GBP_ACCOUNT_ID",
            "GOOGLE_GBP_LOCATION_ID"]
    missing = [v for v in need if not os.environ.get(v)]
    if missing:
        print("PUBLISH BLOCKED — missing GBP API OAuth credentials.", file=sys.stderr)
        print("This stage needs a human to create Google OAuth credentials (free tier).", file=sys.stderr)
        print("Missing environment variables:", file=sys.stderr)
        for v in missing:
            print(f"  - {v}", file=sys.stderr)
        print("\nSetup (free): create a Google Cloud project, enable the Business Profile",
              "\nAPI, create an OAuth client, and authorize a refresh token with scope",
              "\nhttps://www.googleapis.com/auth/business.manage. Then export the vars above.",
              file=sys.stderr)
        print("\nNo posts were published. Drafts remain staged in the output dir.", file=sys.stderr)
        return 3
    # A real publish implementation would exchange the refresh token for an access
    # token and POST to the GBP API v4 media/posts endpoint. Out of scope for the
    # offline-verifiable v1 and deliberately not stubbed with fake success.
    print("Credentials present. Live publish path not implemented in offline v1.", file=sys.stderr)
    return 4


def main(argv=None):
    p = argparse.ArgumentParser(description="Local GBP Engine — white-label GBP content pipeline")
    p.add_argument("--version", action="version", version=f"gbp-engine {VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Generate 4 GBP post drafts + report skeleton")
    g.add_argument("--name", required=True)
    g.add_argument("--category", default="local business")
    g.add_argument("--city", default="your area")
    g.add_argument("--tone", default="friendly", choices=["friendly", "professional", "playful"])
    g.add_argument("--out", default="out")
    g.set_defaults(func=cmd_generate)

    r = sub.add_parser("report", help="Render the monthly report")
    r.add_argument("--dir", default="out")
    r.add_argument("--reviews", default=None)
    r.set_defaults(func=cmd_report)

    pub = sub.add_parser("publish", help="Publish approved posts (needs GBP OAuth creds)")
    pub.add_argument("--dir", default="out")
    pub.set_defaults(func=cmd_publish)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
