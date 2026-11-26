# Tech 2 Go content garage

A local content planner for turning real repair work into useful posts and repair
inquiries. It includes a pipeline board, date-based calendar, editable story briefs,
primary-channel results tracking and CSV/JSON exports. It does **not** connect to
social accounts, schedule uploads, send messages or publish anything.

Open `index.html` with its sibling files present, or run from the repository root:

```sh
python3 -m http.server 4176 --directory content_planner
```

Visit http://localhost:4176. No application packages or internet connection are
needed to use the planner. To create a portable single-file copy and ZIP:

```sh
python3 scripts/package_content_planner.py
```

Outputs: `output/tech2go-content-planner.html` and
`output/tech2go-content-planner.zip`. The portable HTML can be downloaded and
opened in a browser without a server. Browser storage behavior for local files
varies, so export JSON after each session.

## Start here

1. Review the 12 starter stories. Dates from November 30 to December 25, 2026 are
   suggested slots, in Pacific Time, not scheduled posts. Reschedule around actual
   repairs, your launch timing and holidays.
2. Open a story to edit its hook, outline, shot list, owner, city, date and channel.
   Related `S101`–`S126` IDs refer to `pricing/services.csv`. They are sourcing links
   for planning, not permission to advertise a fixed price or a proven capability.
3. Move the stage as work happens: **Idea → Planned → Filmed → Editing → Review →
   Ready → Published**. Filming and editing are manual. Ready/Published require a
   permission basis plus privacy, technical and call-to-action checks. These are
   staff-entered attestations, not automated verification or a legal consent form.
4. Publish manually after checking the actual footage and platform requirements.
   To record Published, enter the actual primary-channel post URL and date. The
   planner rejects future actual publication dates. It cannot verify a URL is live.
5. Record results about seven days later, then write one lesson and one next test.
   Use a separate story for each channel-specific publication; do not merge results
   from a Reel and a Short as if their audiences were distinct people.

## What to make

Use three weekly slots as a sustainable starting assumption:

- **Education/trust:** a useful symptom explanation or backup lesson.
- **Repair process:** honest before/process/after footage, when a real job allows it.
- **Decision/local:** repair-versus-replace, component choices or an actual van update.

Phone content leads the first week, then laptop and desktop stories broaden the
catalog. Data-access stories distinguish copying accessible data from recovery of
permanently deleted data. The local city tags identify the intended audience; they
do not claim the van is parked there. No customer cases, performance improvements,
reviews, current appointments or confirmed stops are invented in the seed plan.

## Capture once, reuse thoughtfully

During an authorized repair or a clearly labeled shop demonstration, collect a
vertical master clip with clean audio, uncluttered closeups and room for captions.
Capture five short sections: symptom, diagnosis explanation, relevant part/process,
actual test and one next action. Explain the decision rather than filming every
screw. Use the template in `story_template.txt`.

From that footage, create a short process clip, an explanation clip or a still
checklist when each adds value. Keep a clean master; adapt the opening, captions,
cover and closing for the channel. Check current platform specifications before
exporting. This planner does not promise reach or use a supposedly optimal posting
time. A proposed 45–60 minute filming block is an operating assumption, not a repair
time or a reason to interrupt customer work.

Keep customer authorization separate from ordinary repair approval. Record the
actual filming permission outside this app using a non-identifying job reference.
Use owned/demo devices whenever practical. Crop notifications, account details,
serial/IMEI numbers, license plates and faces unless specifically authorized. Do
not paste consent documents, credentials, customer names or recovered data here.
Review all footage, including audio and reflections, before posting.

Tech 2 Go's website is still a prototype and `(111) 111-1111` is not a booking
number. The starter CTA and review notes deliberately require a confirmed channel.
Do not publish a fake van stop, booking link or customer success story. Any price
needs an approved quote basis and clear exclusions; repair-model estimates are not
live advertised offers. No recovery guarantees or unsafe energized repair demos.

## Measure useful results

Metrics are entered manually for one primary-channel post, as of a measurement
date: views, saves, shares, attributed repair inquiries and confirmed bookings.
Blank means unmeasured; zero means measured zero. Inquiry rate = inquiries / views
× 100, shown only when both are recorded and views exceed zero. It is a rough
post-level indicator, not a unique-person conversion rate or causal proof.

Once a week ask:

- Which story brought relevant questions or an attributed repair inquiry?
- Did it explain a problem that Tech 2 Go can actually assess or repair?
- Which opening, demonstration or CTA should be tested next?

Change one variable at a time. Example: keep the device topic and CTA, but replace
a generic introduction with the symptom. Compare similarly aged posts and retain
what brings qualified inquiries; do not judge solely by raw views. No starter
metrics, testimonials or bookings have been fabricated.

## Save and portability

Edits are saved to this browser's local storage, not GitHub, SQLite or other devices.
A private browser, cleared storage or a different URL may show a fresh starter plan.
If storage fails, changes exist only in memory and the planner warns you.

- **Back up JSON** preserves all rows for later **Restore JSON**. Restore validates
  the complete file, then asks before replacing the current browser's plan. Keep a
  backup first. It does not silently merge stories or publish imported records.
- **Export CSV** gives a spreadsheet copy of all rows, including hidden/filtered
  stories. Formula-leading text is escaped for spreadsheet safety. CSV export is
  one-way; use JSON to restore app state.
- `content_plan.csv` is the editable starter source. Edit it and rerun the packaging
  script to update `seed.js`. Existing browser edits take precedence over new seeds.
  Use a different browser profile/origin to inspect a clean starter plan without
  replacing saved work. Never commit customer metrics or permissions accidentally.

The starter plan is intentionally generic. Store production footage in your own
controlled media folders; a suggested arrangement is `C001/raw`, `C001/edit`,
`C001/exports`, with permission records separately restricted. This is a one-person
local planner, not a shared multiuser CMS or a social-platform scheduler.

## Verification

`tests/validate_content_planner.cjs` checks the board, calendar, editing, local
persistence, publication checks, manual results and export/import flow, plus layout
at common mobile/desktop widths. It requires Playwright and `/usr/bin/chromium` in
the development environment, not on the user's machine. With the server running:

```sh
node tests/validate_content_planner.cjs
```

Set `TECH2GO_CONTENT_URL` to test another served URL, such as the portable HTML.
