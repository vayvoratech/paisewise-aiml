# Phase 2 new endpoints

- `POST /ai/sip-coach` — SIP progress, projection, monthly requirement and 1,000-run Monte Carlo summary.
- `GET /ai/stock-discovery/{userId}` — up to 5 educational stocks, based on learning level, sector familiarity and risk match.
- `GET /features/{userId}` — full current feature vector plus feature version.
- `POST /ai/features/refresh/{userId}` — triggers feature pipeline refresh and returns latest features.
