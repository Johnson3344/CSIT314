# Sprint 2 — FRA Core

## User Stories Covered
All Sprint 1 stories, plus:
| # | Story |
|---|---|
| 10 | Admin: View all FRAs |
| 12 | Fund Raiser: Create new FRA |
| 13 | Fund Raiser: View FRAs |
| 14 | Fund Raiser: Update FRA |
| 15 | Fund Raiser: Delete FRA |
| 16 | Fund Raiser: Search FRAs |
| 17 | Fund Raiser: Change FRA status |
| 18 | Fund Raiser: Set monetary goal |
| 25 | Donee: View FRA detail page |
| 37 | Platform Management: Delete category |
| 38 | Platform Management: Search categories |
| 39 | Platform Management: Review & approve FRAs |

## Running the App
```bash
pip install -r requirements.txt
python seed_data.py
flask --app app run --debug
```
Default admin: `admin@tacofundme.org` / `admin123`

## Running Tests
```bash
pytest tests/ -v
```
