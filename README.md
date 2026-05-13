# Sprint 4 — Analytics & Polish

## User Stories Covered
All Sprint 3 stories, plus:
| # | Story |
|---|---|
| 21 | Fund Raiser: Respond to comments |
| 22 | Fund Raiser: Filter completed FRA history |
| 31 | Donee: Report suspicious FRA |
| 34 | Donee: Filter donation history |
| 40 | Platform Management: Filter/search FRA reports |
| 41 | Platform Management: Generate daily/weekly/monthly reports |

This is the **complete final release** of TACOFundMe.
All 41 user stories are implemented.

## Running the App
```bash
pip install -r requirements.txt
python seed_data.py
flask --app app run --debug
```

## Running Tests
```bash
pytest tests/ -v
```
