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

def find_employee_rows(words, first="Ian", last="Maccarthy", y_tol=20, x_tol=20):
    firstName = None
    lastName = None

    for w in words:
        if w['text'] == first:
            firstName = w
            break

    if not firstName:
        raise ValueError("First name not found")
    
    for w in words:
        if (
            w['text'] == last
            and abs(w['x0'] - firstName['x0']) < x_tol
            and w['top'] > firstName['top']
            and abs(w['top'] - firstName['top']) < y_tol
        ):
            lastName = w
            break
    if not lastName:
        raise ValueError("last name not found")
    
    return{
        "row_min": firstName['top'],
        "row_max": lastName['top']
    }


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

def match_shift_types(shifts, words, row_bottom, row_top, y_tol=5, x_tol=50):
    results = []
    row_min = min(row_top, row_bottom) - y_tol
    row_max = max(row_top, row_bottom) + y_tol

    for shift in shifts:
        x = shift['x0']

        for w in words:
            if (
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