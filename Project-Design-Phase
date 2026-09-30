# Phase 3: Project Design

## Architecture
```
Browser (HTML/CSS/JS)
   | fetch(FormData)
Flask backend (app.py)  ->  validators.py  ->  gemini_service.py  ->  Gemini API
   |                                              | on error / over budget
SQLite (users, history)                        mock_data.py (fallback catalog)
```

## Components
| Component | Description |
|-----------|-------------|
| Frontend UI | Forms for budget, preferences and images; renders recommendations |
| Flask Backend | Sessions, routes, validation, history storage |
| Gemini AI Layer | Builds prompts, requests JSON, parses and validates output |
| Fallback Layer | Budget-share allocation over a mock catalog |

## Data model
- `users(id, username, password_hash)`
- `history(id, user_id, planner, budget, total, result JSON, created_at)`

## Pages
Home, Login, Register, User Dashboard, Home/Party/Jewelry planner, History.

## API contract
`POST /generate-<kind>` (multipart form) -> `{summary, items[{category,name,platform,price,reason}], budget, total, remaining, over_budget, source}`
