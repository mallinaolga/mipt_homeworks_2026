#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"


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
    if len(parts) != 3:
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
    financial_transactions_storage.append({"type": "income", "amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append(
        {"type": "cost", "category": category_name, "amount": amount, "date": income_date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories = []
    for common_category in sorted(EXPENSE_CATEGORIES):
        for target_category in EXPENSE_CATEGORIES[common_category]:
            categories.append(f"{common_category}::{target_category}")
    return "\n".join(categories)


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
    if len(parts) != 2:
        return False
    common_category, target_category = parts
    if common_category not in EXPENSE_CATEGORIES:
        return False
    return target_category in EXPENSE_CATEGORIES[common_category]


def parse_date_to_tuple(date_str: str) -> tuple[int, int, int]:
    day, month, year = extract_date(date_str)
    return year, month, day


def get_target_category_name(full_category_name: str) -> str:
    return full_category_name.split("::", 1)[1]


def format_detail_amount(amount: float) -> str:
    if amount == int(amount):
        return str(int(amount))
    return f"{amount:.2f}"


def stats_handler(report_date: str) -> str:
    report_date_tuple = parse_date_to_tuple(report_date)

    total_capital = 0.0
    current_month_income = 0.0
    current_month_expenses = 0.0
    expenses_by_category: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        transaction_date_tuple = parse_date_to_tuple(transaction["date"])
        if transaction_date_tuple > report_date_tuple:
            continue

        amount = transaction["amount"]
        if transaction["type"] == "income":
            total_capital += amount
        else:
            total_capital -= amount

        if transaction_date_tuple[0] == report_date_tuple[0] and transaction_date_tuple[1] == report_date_tuple[1]:
            if transaction["type"] == "income":
                current_month_income += amount
            else:
                current_month_expenses += amount
                target_category = get_target_category_name(transaction["category"])
                if target_category not in expenses_by_category:
                    expenses_by_category[target_category] = 0.0
                expenses_by_category[target_category] += amount

    month_result = current_month_income - current_month_expenses
    month_result_type = "profit" if month_result >= 0 else "loss"

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
        f"This month, the {month_result_type} amounted to {abs(month_result):.2f} rubles.",
        f"Income: {current_month_income:.2f} rubles",
        f"Expenses: {current_month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    sorted_categories = sorted(expenses_by_category.items(), key=lambda item: item[0])
    for index, (category_name, amount) in enumerate(sorted_categories, start=1):
        lines.append(f"{index}. {category_name}: {format_detail_amount(amount)}")

    return "\n".join(lines)


def handle_income_command(parts: list[str]) -> str:
    if len(parts) != 3:
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
    if len(parts) == 2 and parts[1] == "categories":
        return cost_categories_handler()

    if len(parts) != 4:
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
    if len(parts) != 2:
        return UNKNOWN_COMMAND_MSG
    if extract_date(parts[1]) is None:
        return INCORRECT_DATE_MSG
    return stats_handler(parts[1])


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
