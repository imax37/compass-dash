from .pdf_reader import extract_words_from_pdf
from .extractors import(
    get_date_columns,
    find_employee_rows,
    get_employee_shifts,
    match_shift_types,
    assign_dates
)

def parse_pdf(pdf_path, first_name, last_name):
    all_results = []

    for words in extract_words_from_pdf(pdf_path):

        date_columns = get_date_columns(words)
        employee_rows = find_employee_rows(words, first_name, last_name)

        shifts = get_employee_shifts(
            words, employee_rows['row_min'], employee_rows['row_max']
            )
        shifts_w_type = match_shift_types(
            shifts, words, employee_rows['row_min'], employee_rows['row_max'], last_name
            )
        results = assign_dates(shifts_w_type, date_columns)

        all_results.extend(results)

    return all_results