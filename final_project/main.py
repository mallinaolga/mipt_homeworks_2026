import os
from collections.abc import Iterable
from typing import Any, Final, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.config import Config, load_config, validate_config
from src.context_manager import ContextManager
from src.file_utils import get_chunks, process_file_tags

EXIT_COMMAND: Final[str] = r'\q'
RESET_COMMAND: Final[str] = '/reset'
CHUNK_COMMAND: Final[str] = '/file_chunk'


def parse_chunk_args(command: str) -> tuple[str, int]:

    mode = 'paragraph'
    value = 1

    parts = command.split()

    for part in parts:
        if part.startswith('len='):
            mode = 'len'
            value = int(part.removeprefix('len='))
        elif part.startswith('paragraph='):
            mode = 'paragraph'
            value = int(part.removeprefix('paragraph='))

    if value <= 0:
        raise ValueError('Размер чанка должен быть положительным числом.')

    return mode, value


def build_client(cfg: Config) -> OpenAI:
    return OpenAI(
        api_key=cfg.api_key,
        base_url=cfg.api_host,
    )


def handle_chunks(command: str, client: OpenAI, cfg: Config) -> None:

    try:
        mode, value = parse_chunk_args(command)
    except ValueError as exc:
        print(f'Ошибка в параметрах команды: {exc}')
        return

    path = input('Введите путь до файла: ').strip()

    if not os.path.exists(path):
        print('Файл не найден.')
        return

    user_prompt = input('User prompt для каждого фрагмента: ').strip()

    if not user_prompt:
        print('Промпт не может быть пустым.')
        return

    auto_mode = '-y' in command.split()

    print('Начинаю обработку файла.')

    for index, chunk in enumerate(get_chunks(path, mode, value), start=1):
        if not auto_mode:
            input('\nНажмите Enter для обработки следующего чанка...')

        messages: list[ChatCompletionMessageParam] = [
            {
                'role': 'user',
                'content': f'{user_prompt}\n\nФрагмент файла #{index}:\n{chunk}',
            },
        ]

        try:
            response = client.chat.completions.create(
                model=cfg.model_name,
                messages=messages,
                temperature=cfg.temperature,
            )
        except Exception as exc:
            print(f'Ошибка при обращении к LLM: {exc}')
            return

        answer = response.choices[0].message.content or ''

        print(f'\n--- Ответ на чанк #{index} ---')
        print(answer)

    print('\nОбработка завершена.')


def stream_ai_response(client: OpenAI, cfg: Config, ctx: ContextManager) -> str:
    """
    Отправляет историю сообщений в LLM и печатает ответ потоково.
    """
    try:
        response_stream = client.chat.completions.create(
            model=cfg.model_name,
            messages=cast(Iterable[ChatCompletionMessageParam], ctx.history),
            temperature=cfg.temperature,
            stream=True,
        )
    except KeyboardInterrupt:
        print(r'\nГенерация ответа прервана. Для выхода используйте команду \q.')
        return ''
    except Exception as exc:
        print(f'Ошибка при обращении к LLM: {exc}')
        return ''

    full_response = ''

    print('Assistant: ', end='', flush=True)

    try:
        for chunk in cast(Iterable[Any], response_stream):
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if delta.content:
                print(delta.content, end='', flush=True)
                full_response += delta.content

    except KeyboardInterrupt:
        print(r'\nГенерация ответа прервана. Для выхода используйте команду \q.')
        return full_response

    print()
    return full_response


def handle_user_command(
    user_input: str,
    ctx: ContextManager,
    client: OpenAI,
    cfg: Config,
) -> bool:

    if user_input == RESET_COMMAND:
        ctx.reset()
        os.system('cls' if os.name == 'nt' else 'clear')
        print('История сообщений очищена.')
        return True

    if user_input.startswith(CHUNK_COMMAND):
        handle_chunks(user_input, client, cfg)
        return True

    return False


def process_iteration(client: OpenAI, cfg: Config, ctx: ContextManager) -> bool:

    try:
        user_input = input('\n>>> ').strip()
    except (EOFError, KeyboardInterrupt):
        print(r'\nДля выхода используйте команду \q.')
        return True

    if not user_input:
        return True

    if user_input == EXIT_COMMAND:
        return False

    if handle_user_command(user_input, ctx, client, cfg):
        return True

    processed_text = process_file_tags(user_input)
    ctx.add_message('user', processed_text)

    full_response = stream_ai_response(client, cfg, ctx)

    if full_response:
        ctx.add_message('assistant', full_response)

    return True


def print_help() -> None:
    print('GigaVibeMiptCode AI Assistant запущен.')
    print(r'Введите \q для выхода.')
    print('Введите /reset для очистки истории.')
    print('Можно вставлять файлы в сообщение через тег: @::path/to/file.txt::')
    print('Команда обработки файла чанками:')
    print('  /file_chunk len=1000')
    print('  /file_chunk paragraph=3')
    print('  /file_chunk -y len=1000')


def main() -> None:
    cfg = load_config()
    validate_config(cfg)

    client = build_client(cfg)
    ctx = ContextManager(
        limit_messages=cfg.limit_messages,
        limit_chars=cfg.limit_chars,
        system_prompt=cfg.system_prompt,
    )

    print_help()

    while True:
        should_continue = process_iteration(client, cfg, ctx)

        if not should_continue:
            print('Завершение работы.')
            break


if __name__ == '__main__':
    main()
