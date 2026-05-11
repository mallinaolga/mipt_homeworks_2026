#!/usr/bin/env python

import sys

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


def _has_valid_date_part_lengths(
    day_str: str,
    month_str: str,
    year_str: str,
) -> bool:
    date_parts = (
        day_str,
        month_str,
        year_str,
    )
    expected_lengths = (
        _DAY_PART_LEN,
        _MONTH_PART_LEN,
        _YEAR_PART_LEN,
    )

    for date_part, expected_length in zip(date_parts, expected_lengths, strict=True):
        if len(date_part) != expected_length:
            return False

    return True


def _has_only_digit_date_parts(
    day_str: str,
    month_str: str,
    year_str: str,
) -> bool:
    return day_str.isdigit() and month_str.isdigit() and year_str.isdigit()


def _has_valid_date_parts(
    day_str: str,
    month_str: str,
    year_str: str,
) -> bool:
    return _has_valid_date_part_lengths(
        day_str,
        month_str,
        year_str,
    ) and _has_only_digit_date_parts(day_str, month_str, year_str)


def _is_valid_month(month: int) -> bool:
    return 1 <= month <= _MONTHS_PER_YEAR


def _is_valid_day(day: int, month: int, year: int) -> bool:
    return 1 <= day <= _days_in_month(month, year)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    date_tuple = None
    parts = maybe_dt.split("-")

    if len(parts) == _DATE_PARTS_COUNT:
        day_str, month_str, year_str = parts

        if _has_valid_date_parts(day_str, month_str, year_str):
            day = int(day_str)
            month = int(month_str)
            year = int(year_str)

            if _is_valid_month(month) and _is_valid_day(day, month, year):
                date_tuple = day, month, year

    return date_tuple


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
        },
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
        },
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    pairs = (
        f"{common_category}::{target_category}"
        for common_category, target_categories in EXPENSE_CATEGORIES.items()
        for target_category in target_categories
    )
    return "\n".join(pairs)


def _has_valid_amount_chars(unsigned_amount: str) -> bool:
    dots_count = 0
    is_valid = bool(unsigned_amount)

    for symbol in unsigned_amount:
        if symbol == ".":
            dots_count += 1
            is_valid = is_valid and dots_count <= 1
        else:
            is_valid = is_valid and symbol.isdigit()

    return is_valid


def _has_valid_amount_parts(unsigned_amount: str) -> bool:
    parts = unsigned_amount.split(".")
    has_empty_decimal_part = len(parts) == _CATEGORY_PARTS_COUNT and "" in parts
    return unsigned_amount != "." and not has_empty_decimal_part


def _is_valid_unsigned_amount(unsigned_amount: str) -> bool:
    return _has_valid_amount_chars(unsigned_amount) and _has_valid_amount_parts(
        unsigned_amount,
    )


def parse_amount(raw_amount: str) -> float | None:
    normalized = raw_amount.replace(",", ".")
    amount = None

    if normalized:
        unsigned = normalized[1:] if normalized[0] == "-" else normalized

        if _is_valid_unsigned_amount(unsigned):
            amount = float(normalized)

    return amount


def is_valid_category(category_name: str) -> bool:
    parts = category_name.split(CATEGORY_SEP)
    is_valid = False

    if len(parts) == _CATEGORY_PARTS_COUNT:
        common_category, target_category = parts
        target_categories = EXPENSE_CATEGORIES.get(common_category)
        is_valid = target_categories is not None and target_category in target_categories

    return is_valid


def parse_date_to_tuple(date_str: str) -> tuple[int, int, int] | None:
    date_tuple = extract_date(date_str)
    parsed_date = None

    if date_tuple is not None:
        day, month, year = date_tuple
        parsed_date = year, month, day

    return parsed_date


def get_target_category_name(full_category_name: str) -> str:
    return full_category_name.split(CATEGORY_SEP, 1)[1]


def format_detail_amount(amount: float) -> str:
    rounded = round(amount, 2)
    if rounded.is_integer():
        return _format_integer_amount(int(rounded))

    return f"{rounded:.2f}"


def _format_integer_amount(amount: int) -> str:
    sign = "-" if amount < 0 else ""
    string_number = str(abs(amount))

    if len(string_number) <= _THOUSAND_GROUP_WIDTH:
        return sign + string_number

    return sign + _format_thousand_groups(string_number)


def _format_thousand_groups(string_number: str) -> str:
    groups = []

    while string_number:
        groups.append(string_number[-_THOUSAND_GROUP_WIDTH:])
        string_number = string_number[:-_THOUSAND_GROUP_WIDTH]

    return ",".join(reversed(groups))


def _extract_tx_tuple(tx: dict[str, object]) -> tuple[int, int, int] | None:
    tx_tuple = None
    tx_dt_raw = tx.get("date")

    if isinstance(tx_dt_raw, tuple) and len(tx_dt_raw) == _DATE_TUPLE_LEN:
        tx_day, tx_month, tx_year = tx_dt_raw

        if _is_valid_tx_date_tuple(tx_day, tx_month, tx_year):
            tx_tuple = tx_year, tx_month, tx_day

    return tx_tuple


def _is_valid_tx_date_tuple(
    tx_day: object,
    tx_month: object,
    tx_year: object,
) -> bool:
    return all(
        isinstance(tx_part, int)
        for tx_part in (
            tx_day,
            tx_month,
            tx_year,
        )
    )


def _extract_tx_amount(tx: dict[str, object]) -> float | None:
    raw_amount = tx.get("amount")
    amount = None

    if isinstance(raw_amount, int | float):
        amount = float(raw_amount)

    return amount


def _is_same_month(
    tx_tuple: tuple[int, int, int],
    report_date: tuple[int, int, int],
) -> bool:
    tx_year, tx_month, _ = tx_tuple
    _, report_month, report_year = report_date
    return tx_year == report_year and tx_month == report_month


def _apply_income_transaction(
    amount: float,
    totals: tuple[float, float, float],
    *,
    is_same_month: bool,
) -> tuple[float, float, float]:
    total_capital, month_income, month_expenses = totals
    total_capital += amount

    if is_same_month:
        month_income += amount

    return total_capital, month_income, month_expenses


def _apply_cost_transaction(
    tx: dict[str, object],
    amount: float,
    totals: tuple[float, float, float],
    expenses_by_cat: dict[str, float],
    *,
    is_same_month: bool,
) -> tuple[float, float, float]:
    total_capital, month_income, month_expenses = totals
    total_capital -= amount

    if is_same_month:
        month_expenses += amount
        _update_category_expenses(tx, amount, expenses_by_cat)

    return total_capital, month_income, month_expenses


def _update_category_expenses(
    tx: dict[str, object],
    amount: float,
    expenses_by_cat: dict[str, float],
) -> None:
    raw_category = tx.get("category")

    if isinstance(raw_category, str):
        cat_name = get_target_category_name(raw_category)
        expenses_by_cat[cat_name] = expenses_by_cat.get(cat_name, _FLOAT_ZERO) + amount


def _update_stats_by_transaction(
    tx: dict[str, object],
    dt: tuple[int, int, int],
    report_tuple: tuple[int, int, int],
    totals: tuple[float, float, float],
    expenses_by_cat: dict[str, float],
) -> tuple[float, float, float]:
    updated_totals = totals
    tx_tuple = _extract_tx_tuple(tx)

    if tx_tuple is not None and tx_tuple <= report_tuple:
        updated_totals = _update_stats_by_valid_transaction(
            tx,
            dt,
            tx_tuple,
            totals,
            expenses_by_cat,
        )

    return updated_totals


def _update_stats_by_valid_transaction(
    tx: dict[str, object],
    dt: tuple[int, int, int],
    tx_tuple: tuple[int, int, int],
    totals: tuple[float, float, float],
    expenses_by_cat: dict[str, float],
) -> tuple[float, float, float]:
    updated_totals = totals
    amount = _extract_tx_amount(tx)

    if amount is not None:
        is_same_month = _is_same_month(tx_tuple, dt)
        updated_totals = _apply_transaction_amount(
            tx,
            amount,
            totals,
            expenses_by_cat,
            is_same_month=is_same_month,
        )

    return updated_totals


def _apply_transaction_amount(
    tx: dict[str, object],
    amount: float,
    totals: tuple[float, float, float],
    expenses_by_cat: dict[str, float],
    *,
    is_same_month: bool,
) -> tuple[float, float, float]:
    tx_type = tx.get("type")
    updated_totals = totals

    if tx_type == "income":
        updated_totals = _apply_income_transaction(
            amount,
            totals,
            is_same_month=is_same_month,
        )
    elif tx_type == "cost":
        updated_totals = _apply_cost_transaction(
            tx,
            amount,
            totals,
            expenses_by_cat,
            is_same_month=is_same_month,
        )

    return updated_totals


def stats_handler(report_date: str) -> str:
    dt = extract_date(report_date)
    result = INCORRECT_DATE_MSG

    if dt is not None:
        result = _build_stats_response(report_date, dt)

    return result


def _build_stats_response(report_date: str, dt: tuple[int, int, int]) -> str:
    report_tuple = (dt[2], dt[1], dt[0])
    expenses_by_cat: dict[str, float] = {}
    totals = _collect_stats(dt, report_tuple, expenses_by_cat)

    return _format_stats_response(report_date, totals, expenses_by_cat)


def _collect_stats(
    dt: tuple[int, int, int],
    report_tuple: tuple[int, int, int],
    expenses_by_cat: dict[str, float],
) -> tuple[float, float, float]:
    totals = (_FLOAT_ZERO, _FLOAT_ZERO, _FLOAT_ZERO)

    for tx in financial_transactions_storage:
        if tx:
            totals = _update_stats_by_transaction(
                tx,
                dt,
                report_tuple,
                totals,
                expenses_by_cat,
            )

    return totals


def _format_stats_response(
    report_date: str,
    totals: tuple[float, float, float],
    expenses_by_cat: dict[str, float],
) -> str:
    total_capital, month_income, month_expenses = totals
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

    lines.extend(_format_expense_details(expenses_by_cat))
    return "\n".join(lines)


def _format_expense_details(expenses_by_cat: dict[str, float]) -> list[str]:
    return [
        f"{index}. {name}: {format_detail_amount(value)}"
        for index, category_item in enumerate(sorted(expenses_by_cat.items()), start=1)
        for name, value in (category_item,)
    ]


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


def _is_cost_categories_command(parts: list[str]) -> bool:
    return len(parts) == _COST_CATEGORIES_WORDS and parts[1] == "categories"


def _is_cost_purchase_command(parts: list[str]) -> bool:
    return len(parts) == _COST_PURCHASE_WORDS


def handle_cost_command(parts: list[str]) -> str:
    result = UNKNOWN_COMMAND_MSG

    if _is_cost_categories_command(parts):
        result = cost_categories_handler()
    elif _is_cost_purchase_command(parts):
        result = _handle_cost_purchase_command(parts)

    return result


def _handle_cost_purchase_command(parts: list[str]) -> str:
    category_name = parts[1]
    amount = parse_amount(parts[2])
    result = UNKNOWN_COMMAND_MSG

    if amount is not None:
        result = _handle_valid_cost_amount(category_name, amount, parts[3])

    return result


def _handle_valid_cost_amount(
    category_name: str,
    amount: float,
    cost_date: str,
) -> str:
    result = NONPOSITIVE_VALUE_MSG

    if amount > 0:
        result = _handle_positive_cost_amount(category_name, amount, cost_date)

    return result


def _handle_positive_cost_amount(
    category_name: str,
    amount: float,
    cost_date: str,
) -> str:
    result = INCORRECT_DATE_MSG

    if extract_date(cost_date) is not None:
        result = _handle_valid_cost_date(category_name, amount, cost_date)

    return result


def _handle_valid_cost_date(
    category_name: str,
    amount: float,
    cost_date: str,
) -> str:
    if is_valid_category(category_name):
        return cost_handler(category_name, amount, cost_date)

    return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"


def handle_stats_command(parts: list[str]) -> str:
    if len(parts) != _STATS_CMD_WORDS:
        return UNKNOWN_COMMAND_MSG
    if extract_date(parts[1]) is None:
        return INCORRECT_DATE_MSG
    return stats_handler(parts[1])


def _handle_command(parts: list[str]) -> str:
    handlers = {
        "income": handle_income_command,
        "cost": handle_cost_command,
        "stats": handle_stats_command,
    }
    handler = handlers.get(parts[0])
    result = UNKNOWN_COMMAND_MSG

    if handler is not None:
        result = handler(parts)

    return result


def main() -> None:
    for raw_command in sys.stdin:
        command = raw_command.strip()

        if command:
            print(_handle_command(command.split()))


if __name__ == "__main__":
    main()
