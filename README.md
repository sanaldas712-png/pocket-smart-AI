# Phase 7: Project Documentation

## User guide
1. Register and log in.
2. Pick a planner on the dashboard.
3. Enter budget and preferences (jewelry: optionally upload an outfit image).
4. Click **Generate Recommendations**; review items, total and remaining budget.
5. Revisit past plans under **History**.

## Configuration
| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Google AI Studio key (without it, fallback mode runs) |
| `GEMINI_MODEL` | Model name, default `gemini-2.5-flash` |
| `SECRET_KEY` | Flask session secret |

## Known limitations
- Prices are AI-estimated or mock data, not live listings.
- SQLite is for demo scale only.
