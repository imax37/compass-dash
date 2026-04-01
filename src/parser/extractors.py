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
        "shiftTimeRow": firstName['top'],
        "shiftTypeRow": lastName['top']
    }

SHIFT_PATTERN = re.compile(r"\d{4}-\d{4}")

def get_employee_shifts(words, employee_y, tolerance=20):
    shifts = []

    for w in words:
        if SHIFT_PATTERN.match(w['text']):

            if abs(w['top'] - employee_y) < tolerance:
                shifts.append(w)

    return shifts

def match_shift_types(shifts, words, shift_type_y, y_tol=20, x_tol=20):
    results = []

    for shift in shifts:
        x = shift['x0']

        for w in words:
            if (
                abs(w['top'] - shift_type_y) < y_tol and 
                abs(w['x0'] - x) < x_tol and
                not SHIFT_PATTERN.match(w['text'])
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