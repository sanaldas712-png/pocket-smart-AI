# Phase 6: Project Testing

Run from the repository root:
```powershell
pytest 6-Project-Testing-Phase
```

## Test cases
| ID | Case | Expected |
|----|------|----------|
| T1 | Generate without login | 401 |
| T2 | Home plan, valid input | 200, items returned |
| T3 | Party plan | catering, decoration, entertainment present |
| T4 | Jewelry plan | 200, items returned |
| T5 | Invalid budget / zero guests / missing occasion | 400 |
| T6 | History saved | Entry visible on `/history` |
| T7 | AI unavailable | Fallback used (`source = fallback`) |

## Manual checks (with a real API key)
Compare Gemini output against budget, platform accuracy and relevance for the three scenarios.
