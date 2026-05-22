import os
from dataclasses import dataclass
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass
class Config:
    api_key: str
    api_host: str
    limit_messages: int
    limit_chars: int
    temperature: float
    system_prompt: str | None
    model_name: str


def _read_yaml_config(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {}

    with open(path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        return {}

    return data


def _get_str_value(
    env_name: str,
    config_data: dict[str, Any],
    config_name: str,
    default: str,
) -> str:
    env_value = os.environ.get(env_name)

    if env_value is not None:
        return env_value

    value = config_data.get(config_name, default)

    if value is None:
        return default

    return str(value)


def _get_optional_str_value(
    env_name: str,
    config_data: dict[str, Any],
    config_name: str,
) -> str | None:
    env_value = os.environ.get(env_name)

    if env_value is not None:
        return env_value

    value = config_data.get(config_name)

    if value is None:
        return None

    return str(value)


def _get_int_value(
    env_name: str,
    config_data: dict[str, Any],
    config_name: str,
    default: int,
) -> int:
    env_value = os.environ.get(env_name)

    if env_value is not None:
        return int(env_value)

    return int(config_data.get(config_name, default))


def _get_float_value(
    env_name: str,
    config_data: dict[str, Any],
    config_name: str,
    default: float,
) -> float:
    env_value = os.environ.get(env_name)

    if env_value is not None:
        return float(env_value)

    return float(config_data.get(config_name, default))


def load_config() -> Config:
    load_dotenv()

    config_data = _read_yaml_config('config.yaml')

    return Config(
        api_key=_get_str_value('API_KEY', config_data, 'api_key', ''),
        api_host=_get_str_value('API_HOST', config_data, 'api_host', ''),
        limit_messages=_get_int_value(
            'LIMIT_MESSAGES',
            config_data,
            'limit_messages',
            10,
        ),
        limit_chars=_get_int_value(
            'LIMIT_CHARS',
            config_data,
            'limit_chars',
            8000,
        ),
        temperature=_get_float_value(
            'TEMPERATURE',
            config_data,
            'temperature',
            0.7,
        ),
        system_prompt=_get_optional_str_value(
            'SYSTEM_PROMPT',
            config_data,
            'system_prompt',
        ),
        model_name=_get_str_value(
            'MODEL_NAME',
            config_data,
            'model_name',
            'gpt-4o-mini',
        ),
    )


def validate_config(cfg: Config) -> None:
    errors: list[str] = []

    if not cfg.api_key:
        errors.append('Не задан API_KEY или api_key в config.yaml.')

    if not cfg.api_host:
        errors.append('Не задан API_HOST или api_host в config.yaml.')

    if cfg.limit_messages <= 0:
        errors.append('limit_messages должен быть положительным числом.')

    if cfg.limit_chars <= 0:
        errors.append('limit_chars должен быть положительным числом.')

    if not 0 <= cfg.temperature <= 2:
        errors.append('temperature должен быть в диапазоне от 0 до 2.')

    if not cfg.model_name:
        errors.append('model_name не может быть пустым.')

    if errors:
        print('Ошибка конфигурации:')
        for error in errors:
            print(f'- {error}')
        raise SystemExit(1)
