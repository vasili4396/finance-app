import calendar


def get_month_boundaries(date):
    start_of_month = date.replace(day=1)
    _, days_in_month = calendar.monthrange(date.year, date.month)
    end_of_month = date.replace(day=days_in_month)

    return start_of_month, end_of_month
