---
name: account-legitimacy-vetting
description: "Use when asked if a profile or account is legit."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Verification, OSINT, LinkedIn, Scams, DueDiligence]
    related_skills: [blocked-page-recovery, grounded-citations]
---

# Account Legitimacy Vetting

## When to Use

Use when the user asks whether a person, profile, account, recruiter or seller is
legitimate — "is this LinkedIn account real", "is this recruiter legit", "this seller/DM
contacted me", "can I trust this profile" — or when they forward a suspicious message
and want to know whether to engage. Also use when an account is presented as
evidence of a business relationship (vendor, hire, partner).

Not for: verifying a company's product claims (see `product-teardown`), or checking a
news story (`grounded-citations`).

The deliverable is a decision, not a dossier.

## Output contract

- **Line 1 is the verdict**: `Legit` / `Likely legit` / `Cannot verify` / `Likely fake`.
  "Cannot verify" is a real verdict and the most common one — an unverifiable account
  is not a fake one, and calling it fake without evidence is as dishonest as vouching
  for it.
- Then a **verified / could-not-verify split**, so the user can see which half of the
  answer is evidence and which half is absence of it.
- Then **ranked flags** (green / yellow / red), each with the mechanism, not just the
  label. "327 connections is low for institutional sales" beats "few connections".
- Then **3–5 checks the user can run** from inside their logged-in session: mutual
  connections, LinkedIn Verify badge, work email + calendar invite, switchboard call
  to the company's real office.
- End by **asking for the message text or a screenshot**. Wording is the fastest intent
  signal, and a screenshot hands you the photo and experience fields that guest access
  cannot fetch.
- Verdict first, no preamble, no hedging paragraphs. The user reads for the answer.

## Procedure

1. **Separate three questions that fail independently**: identity (is this a real
   person), affiliation (do they work where they claim), intent (is the approach a
   scam). A real person's identity can be cloned into a fake account; a real employee
   can be a fraudster; a fake account can be doing no harm. Never let a pass on one
   imply a pass on another, and say which one you are answering.
2. **Harvest the index card before attempting a fetch.** A search-backend query on the
   exact profile URL and on `"Full Name" <platform>` returns the public metadata card
   (headline, location, connection count) and post URLs even when the page is walled.
   One call, and often all the identity data that is publicly visible.
3. **Date the account from its activity IDs** (LinkedIn: top 41 bits of the activity
   URN are the post timestamp — decoder in `references/linkedin-profile-recon.md`).
   Years of dated posts vs two weeks of posts is the single most useful history signal
   available from outside.
4. **Corroborate the claimed employer independently**: company team page, press
   releases, award coverage, conference speaker lists, B2B contact databases
   (ZoomInfo / RocketReach / SignalHire / The Org). Absence from all of them is a
   yellow flag, not proof — plenty of real employees are invisible to all five.
5. **Test the name separately from the profile.** A bare-name search (drop the platform
   from the query) that surfaces old forum posts, a Facebook or SoundCloud account, and
   unrelated mentions proves the *name* is real and in use. It does not prove this
   profile belongs to that person. State that distinction explicitly rather than letting
   the user infer it.
6. **Score network size against the claimed role**, not against a universal number.
   A few hundred connections is low for sales, BD, or recruiting (those networks run
   1,500–5,000+) and unremarkable for engineers or accounts outside the West.
7. **Check for name-space pollution.** Sibling accounts under the same name that look
   fabricated — template headline, implausible tenure ("38 years" at a firm founded
   later), zero activity — do not convict this account, but they show the name is being
   used by more than one persona. Report it as context.

## Flags that actually carry weight

**Green**: an established network with mutuals; a dated posting history that tracks
real, independently verifiable events; a consistent photo across platforms; a work
email on the company's real domain that accepts a calendar invite.

**Yellow**: low connection count for the claimed seniority; no footprint outside the
platform; public visibility set so low that nothing can be checked; employer not
confirmable anywhere; headline that reads like a job description rather than a job.

**Red**: photo reused from a stock/other-person source; work history with impossible
dates or companies that do not exist; the same "person" appearing under several
near-identical accounts; account created recently but claiming a long career.

## Reading the message (intent)

Red regardless of how good the profile is: investment or crypto "signals" and returns;
a job offer requiring the user to buy equipment, pay a fee, or receive-and-forward
funds; pressure to move to WhatsApp/Telegram for "compliance" or "security"; requests
for ID, passport, or a selfie; romance framing; urgency plus secrecy; any "verification"
link that needs a login.

Green-ish: specifics the user can independently check — a named mutual contact, a role
that exists on the company's careers page, a real event the person can be tied to.

## Pitfalls

- **Never upgrade a verdict because the posts look real.** Fake personas repost genuine
  industry news precisely because it looks checkable. Content quality is not provenance.
- **Don't read a locked-down public profile as concealment.** Note it as a blocker to
  verification and move on; the visibility setting is one toggle, not a tell.
- **Don't burn calls on a proxy ladder for a walled social profile** — one archive
  attempt, then ask the logged-in user for a screenshot. They have better data than any
  fetch can return. See `blocked-page-recovery`.
- **Do the searching yourself.** "You could Google them" is not an answer; report what
  the searches returned, including that they returned nothing.
- **The user may be mid-conversation with this person.** Give a decision aid, not an
  accusation, and never script a "test" that tips the other party off.
- **State the timestamp of the evidence.** "Active as of <last post date>" — an account
  that went quiet is a different risk than one posting this week.
