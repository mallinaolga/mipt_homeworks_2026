#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

CATEGORY_SEP = "::"
_FIRST_HALF_MDAYS = (31, 28, 31, 30, 31, 30)
_SECOND_HALF_MDAYS = (31, 31, 30, 31, 30, 31)
_MONTH_DAYS = _FIRST_HALF_MDAYS + _SECOND_HALF_MDAYS
_DAY_PART_LEN = 2
_MONTH_PART_LEN = 2
_YEAR_PART_LEN = 4
_CATEGORY_PARTS_COUNT = 2

_FEBRUARY_MONTH = 2
_FLOAT_ZERO = float(_FEBRUARY_MONTH - _FEBRUARY_MONTH)
_MONTHS_PER_YEAR = 12
_DATE_PARTS_COUNT = 3
_DATE_TUPLE_LEN = 3
_THOUSAND_GROUP_WIDTH = 3
_INCOME_CMD_WORDS = 3
_COST_CATEGORIES_WORDS = 2
_COST_PURCHASE_WORDS = 4
_STATS_CMD_WORDS = 2


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


financial_transactions_storage: list[dict[str, object]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def _days_in_month(month: int, year: int) -> int:
    days = _MONTH_DAYS[month - 1]
    if month == _FEBRUARY_MONTH and is_leap_year(year):
        return 29
    return days


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")
    if len(parts) != _DATE_PARTS_COUNT:
        return None

    day_str, month_str, year_str = parts
    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        return None
    if (
        len(day_str) != _DAY_PART_LEN
        or len(month_str) != _MONTH_PART_LEN
        or len(year_str) != _YEAR_PART_LEN
    ):
        return None

    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    if month < 1 or month > _MONTHS_PER_YEAR:
        return None

    days_in_month = _days_in_month(month, year)
    if day < 1 or day > days_in_month:
        return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date_tuple = extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({})
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
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date_tuple = extract_date(cost_date)
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if not is_valid_category(category_name):
        financial_transactions_storage.append({})
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


def cost_categories_handler() -> str:
    pairs = (
        f"{common_category}::{target_category}"
        for common_category, target_categories in EXPENSE_CATEGORIES.items()
        for target_category in target_categories
    )
    return "\n".join(pairs)


def parse_amount(raw_amount: str) -> float | None:
    normalized = raw_amount.replace(",", ".")
    if not normalized:
        return None

    unsigned = normalized[1:] if normalized[0] == "-" else normalized
    is_valid = bool(unsigned)

    dots_count = 0
    for symbol in unsigned:
        if symbol == ".":
            dots_count += 1
            if dots_count > 1:
                is_valid = False
        elif not symbol.isdigit():
            is_valid = False

    if unsigned == ".":
        is_valid = False

    parts = unsigned.split(".")
    if len(parts) == _CATEGORY_PARTS_COUNT and (parts[0] == "" or parts[1] == ""):
        is_valid = False

    if not is_valid:
        return None

    return float(normalized)


def is_valid_category(category_name: str) -> bool:
    parts = category_name.split(CATEGORY_SEP)
    if len(parts) != _CATEGORY_PARTS_COUNT:
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
    return full_category_name.split(CATEGORY_SEP, 1)[1]


def format_detail_amount(amount: float) -> str:
    rounded = round(amount, 2)
    if rounded.is_integer():
        number = int(rounded)
        sign = "-" if number < 0 else ""
        absolute_number = abs(number)
        string_number = str(absolute_number)

        if len(string_number) <= _THOUSAND_GROUP_WIDTH:
            return sign + string_number

        groups = []
        while string_number:
            groups.append(string_number[-_THOUSAND_GROUP_WIDTH:])
            string_number = string_number[:-_THOUSAND_GROUP_WIDTH]
        return sign + ",".join(reversed(groups))

    return f"{rounded:.2f}"

def _extract_tx_tuple(tx: dict[str, object]) -> tuple[int, int, int] | None:
    tx_dt_raw = tx.get("date")
    if not isinstance(tx_dt_raw, tuple) or len(tx_dt_raw) != _DATE_TUPLE_LEN:
        return None

    tx_day, tx_month, tx_year = tx_dt_raw
    if not (
        isinstance(tx_day, int)
        and isinstance(tx_month, int)
        and isinstance(tx_year, int)
    ):
        return None

    return tx_year, tx_month, tx_day


def _extract_tx_amount(tx: dict[str, object]) -> float | None:
    raw_amount = tx.get("amount")
    if not isinstance(raw_amount, int | float):
        return None
    return float(raw_amount)


def _update_stats_by_transaction(
    tx: dict[str, object],
    dt: tuple[int, int, int],
    report_tuple: tuple[int, int, int],
    total_capital: float,
    month_income: float,
    month_expenses: float,
    expenses_by_cat: dict[str, float],
) -> tuple[float, float, float]:
    tx_tuple = _extract_tx_tuple(tx)
    if tx_tuple is None or tx_tuple > report_tuple:
        return total_capital, month_income, month_expenses

    amount = _extract_tx_amount(tx)
    if amount is None:
        return total_capital, month_income, month_expenses

    tx_year, tx_month, _ = tx_tuple
    is_same_month = tx_year == dt[2] and tx_month == dt[1]
    tx_type = tx.get("type")

    if tx_type == "income":
        total_capital += amount
        if is_same_month:
            month_income += amount
    elif tx_type == "cost":
        total_capital -= amount
        if is_same_month:
            month_expenses += amount
            raw_category = tx.get("category")
            if isinstance(raw_category, str):
                cat_name = get_target_category_name(raw_category)
                expenses_by_cat[cat_name] = (
                    expenses_by_cat.get(cat_name, _FLOAT_ZERO) + amount
                )

    return total_capital, month_income, month_expenses

def stats_handler(report_date: str) -> str:
    dt = extract_date(report_date)
    if dt is None:
        return INCORRECT_DATE_MSG

    report_tuple = (dt[2], dt[1], dt[0])

    total_capital = _FLOAT_ZERO
    month_income = _FLOAT_ZERO
    month_expenses = _FLOAT_ZERO
    expenses_by_cat: dict[str, float] = {}

    for tx in financial_transactions_storage:
        if not tx:
            continue

        total_capital, month_income, month_expenses = _update_stats_by_transaction(
            tx,
            dt,
            report_tuple,
            total_capital,
            month_income,
            month_expenses,
            expenses_by_cat,
        )

    result_value = month_income - month_expenses
    result_type = "profit" if result_value >= 0 else "loss"

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
        f"This month, the {result_type} amounted to {abs(result_value):.2f} rubles.",
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    if expenses_by_cat:
        for index, (name, value) in enumerate(sorted(expenses_by_cat.items()), start=1):
            lines.append(f"{index}. {name}: {format_detail_amount(value)}")

    return "\n".join(lines)

def handle_income_command(parts: list[str]) -> str:
    if len(parts) != _INCOME_CMD_WORDS:
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
    result = UNKNOWN_COMMAND_MSG

    if len(parts) == _COST_CATEGORIES_WORDS and parts[1] == "categories":
        result = cost_categories_handler()
    elif len(parts) == _COST_PURCHASE_WORDS:
        category_name = parts[1]
        amount = parse_amount(parts[2])

        if amount is None:
            result = UNKNOWN_COMMAND_MSG
        elif amount <= 0:
            result = NONPOSITIVE_VALUE_MSG
        elif extract_date(parts[3]) is None:
            result = INCORRECT_DATE_MSG
        elif not is_valid_category(category_name):
            result = f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"
        else:
            result = cost_handler(category_name, amount, parts[3])

    return result

def handle_stats_command(parts: list[str]) -> str:
    if len(parts) != _STATS_CMD_WORDS:
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
