import re

DATE_PATTERN = re.compile(r"\d{2}-[A-Za-z]{3}")

def get_date_columns(words):
    date_columns = []

    for w in words:
        if DATE_PATTERN.match(w["text"]):
            date_columns.append({
                "date": w["text"],
                "x": w["x0"]
            })

    date_columns = sorted(date_columns, key=lambda d: d["x"])

    return date_columns

def find_employee_rows(words, first="Ian", last="Maccarthy", y_tol=20, x_tol=50):
    first=first.lower()
    last=last.lower()

    row_top = None

    for w in words:
        if w['text'].lower() == first:
            row_top = w['top']
            break

    if not row_top:
        raise ValueError("First name not found")
    
    row_words = [x for x in words if abs(x['top'] - row_top) < y_tol]

    for x in row_words:
        if x['text'].lower() == last:

            return{
                "row_min": row_top,
                "row_max": x['top']
            }

    raise ValueError("last name not found")

SHIFT_PATTERN = re.compile(r"(\d{4}-\d{4})")

def get_employee_shifts(words, row_bottom, row_top, tolerance=5):
    shifts = []
    row_min = min(row_top, row_bottom) - tolerance
    row_max = max(row_top, row_bottom) + tolerance

    for w in words:
        
        if row_min <= w['top'] <= row_max:

            match = SHIFT_PATTERN.search(w['text'])
            if match:
                shifts.append(w)
    
    return shifts

def match_shift_types(shifts, words, row_bottom, row_top, last_name, y_tol=5, x_tol=40):
    results = []
    row_min = min(row_top, row_bottom) - y_tol
    row_max = max(row_top, row_bottom) + y_tol

    for shift in shifts:
        x = shift['x0']

        for w in words:
            if (
                w['text'].lower() != last_name.lower() and 
                row_min <= w['top'] <= row_max and 
                abs(w['x0'] - x) < x_tol and
                not SHIFT_PATTERN.search(w['text'])
            ):
                results.append({
                    'x': x,
                    'time': shift['text'],
                    'type': w['text']
                })
                break

    return results

def assign_dates(shifts, date_columns):

    results = []

    for shift in shifts:
        x = shift["x"]

        closest = min(
            date_columns,
            key=lambda d: abs(d['x']-x)
        )

        results.append({
            "date": closest["date"],
            "time": shift["time"],
            "type": shift["type"]
        })

    return results