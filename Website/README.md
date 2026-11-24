# Tech 2 Go website prototype

Open `index.html` in your browser, or serve this folder from the repository root:

```sh
python3 -m http.server 4173 --directory website
```

Visit http://localhost:4173. No build step, API keys or application dependencies.
Optional Google Fonts load over the network; local system fonts provide a fallback.

For a single HTML file that can be downloaded and opened directly:

```sh
python3 scripts/package_website.py
```

This creates `output/tech2go-prototype.html` and `output/tech2go-website.zip`.
The ZIP includes the portable file and editable source files.

## Implemented

- Tech 2 Go branding and responsive desktop/mobile design.
- Today/tomorrow/next-day stop board with sample Lancaster, Palmdale and Quartz Hill
  stops, sample hours and illustrative map. Dates use America/Los_Angeles.
- Clickable device categories, call/text controls and appointment request form.
- Required inputs, phone/date validation, request preview and return-to-edit flow.
- No personal data storage or transmission. Submitted text is rendered safely.

This is a frontend prototype. The sample stop list repeats relative to the date of
viewing and is not an operational schedule or GPS feed. Before launch, replace it
with date-specific verified stops and confirmed parking addresses, plus a fallback
when there is no published stop. Time windows are preferences, not actual availability.

The requested placeholder phone is `(111) 111-1111`. Clicking call/text explains
that it is a demo number, rather than attempting a call. In `config.js`, replace
`phone` with the real booking number and set `phoneIsPlaceholder: false` to enable
`tel:` and `sms:` links; these open the customer's dialer/messaging app and do not
send messages automatically. Edit `stops` to change sample locations and hours.
The pin coordinates are percentage positions on an illustrative map, not GPS.

To accept real appointments, a future implementation needs a server endpoint,
request storage, staff notifications/confirmation, booking availability and
appropriate customer consent/privacy wording. No request is sent to the supplier
SQLite database. The existing database workflow remains separate and unchanged.

Sites returned “Sites is not yet enabled for this workspace,” so this version is
provided as a local/browser prototype, not a hosted production website.

## Verification

The existing supplier database validation still passes. Browser checks cover stop
switching, city preselection, demo contact guard, phone validation, request preview,
editing, safe text rendering, no personal data persistence, no runtime errors and
horizontal overflow at widths 320, 390, 768 and 1440 pixels. Desktop/mobile screenshots
were captured for review.

For developers with Playwright and Chromium installed, start the preview server,
create `output/` if needed, and run:

```sh
node tests/validate_website.cjs
```

The browser check uses `/usr/bin/chromium`. Set `TECH2GO_PREVIEW_URL` to test the
portable HTML served over HTTP or a different preview URL. The managed browser
blocks file URLs; local browser opening is supported by the file’s inline assets. No dependency is needed
to view or use the prototype itself.
