#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

COST_CATEGORIES_COMMAND_LEN = 2
INCOME_COMMAND_LEN = 3
COST_COMMAND_LEN = 4
STATS_COMMAND_LEN = 2
CATEGORY_PARTS_COUNT = 2

DATE_PARTS_COUNT = 3
DAY_STR_LEN = 2
MONTH_STR_LEN = 2
YEAR_STR_LEN = 4
MONTHS_IN_YEAR = 12

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None

    day_str, month_str, year_str = parts
    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        return None
    if len(day_str) != 2 or len(month_str) != 2 or len(year_str) != 4:
        return None

    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    if month < 1 or month > 12:
        return None

    days_in_month = {
        1: 31,
        2: 29 if is_leap_year(year) else 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }

    if day < 1 or day > days_in_month[month]:
        return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            "type": "income",
            "amount": amount,
            "date": date_tuple,
        }
    )
    return OP_SUCCESS_MSG



def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date_tuple = extract_date(cost_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    if not is_valid_category(category_name):
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {
            "type": "cost",
            "category": category_name,
            "amount": amount,
            "date": date_tuple,
        }
    )
    return OP_SUCCESS_MSG


def parse_amount(raw_amount: str) -> float | None:
    normalized = raw_amount.replace(",", ".")
    if not normalized:
        return None

    dots_count = 0
    for symbol in normalized:
        if symbol == ".":
            dots_count += 1
            if dots_count > 1:
                return None
        elif not symbol.isdigit():
            return None

    if normalized == ".":
        return None

    parts = normalized.split(".")
    if len(parts) == 2 and (parts[0] == "" or parts[1] == ""):
        return None

    return float(normalized)


def is_valid_category(category_name: str) -> bool:
    parts = category_name.split("::")
    if len(parts) != CATEGORY_PARTS_COUNT:
        return False
    common_category, target_category = parts
    if common_category not in EXPENSE_CATEGORIES:
        return False
    return target_category in EXPENSE_CATEGORIES[common_category]


def parse_date_to_tuple(date_str: str) -> tuple[int, int, int] | None:
    date_tuple = extract_date(date_str)
    if date_tuple is None:
        return None

    day, month, year = date_tuple
    return year, month, day

def get_target_category_name(full_category_name: str) -> str:
    return full_category_name.split("::", 1)[1]


def format_detail_amount(amount: float) -> str:
    if amount == int(amount):
        return str(int(amount))
    return f"{amount:.2f}"


def stats_handler(report_date: str) -> str:
    dt = extract_date(report_date)
    if dt is None:
        return INCORRECT_DATE_MSG

    report_tuple = (dt[2], dt[1], dt[0])

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    expenses_by_cat: dict[str, float] = {}

    for tx in financial_transactions_storage:
        tx_dt = tx["date"]
        tx_tuple = (tx_dt[2], tx_dt[1], tx_dt[0])

        if tx_tuple > report_tuple:
            continue

        amt = tx["amount"]
        if tx["type"] == "income":
            total_capital += amt
            if tx_dt[2] == dt[2] and tx_dt[1] == dt[1]:
                month_income += amt
        else:
            total_capital -= amt
            if tx_dt[2] == dt[2] and tx_dt[1] == dt[1]:
                month_expenses += amt
                cat_name = tx["category"].split("::")[1]
                expenses_by_cat[cat_name] = expenses_by_cat.get(cat_name, 0.0) + amt

    res_val = month_income - month_expenses
    res_type = "profit" if res_val >= 0 else "loss"

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
        f"This month, the {res_type} amounted to {abs(res_val):.2f} rubles.",
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    for index, (name, value) in enumerate(sorted(expenses_by_cat.items()), start=1):
        if value == int(value):
            formatted_value = str(int(value))
        else:
            formatted_value = f"{value:.2f}"
        lines.append(f"{index}. {name}: {formatted_value}")

    return "\n".join(lines)


def handle_income_command(parts: list[str]) -> str:
    if len(parts) != INCOME_COMMAND_LEN:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(parts[1])
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if extract_date(parts[2]) is None:
        return INCORRECT_DATE_MSG

    return income_handler(amount, parts[2])

def handle_cost_command(parts: list[str]) -> str:
    if len(parts) == COST_CATEGORIES_COMMAND_LEN and parts[1] == "categories":
        return cost_categories_handler()

    if len(parts) != COST_COMMAND_LEN:
        return UNKNOWN_COMMAND_MSG

    category_name = parts[1]
    amount = parse_amount(parts[2])
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if extract_date(parts[3]) is None:
        return INCORRECT_DATE_MSG

    if not is_valid_category(category_name):
        return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"

    return cost_handler(category_name, amount, parts[3])


def handle_stats_command(parts: list[str]) -> str:
    if len(parts) != STATS_COMMAND_LEN:
        return UNKNOWN_COMMAND_MSG
    if extract_date(parts[1]) is None:
        return INCORRECT_DATE_MSG
    return stats_handler(parts[1])

def cost_categories_handler() -> str:
    categories = []
    for common_category in EXPENSE_CATEGORIES:
        for target_category in EXPENSE_CATEGORIES[common_category]:
            categories.append(f"{common_category}::{target_category}")
    return "\n".join(categories)

def main() -> None:
    while True:
        raw_command = input()
        command = raw_command.strip()
        if not command:
            continue

        parts = command.split()
        action = parts[0]

        if action == "income":
            print(handle_income_command(parts))
        elif action == "cost":
            print(handle_cost_command(parts))
        elif action == "stats":
            print(handle_stats_command(parts))
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()