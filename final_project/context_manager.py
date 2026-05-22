from typing import Final

ROLE_KEY: Final[str] = 'role'
CONTENT_KEY: Final[str] = 'content'

SYSTEM_ROLE: Final[str] = 'system'
USER_ROLE: Final[str] = 'user'
ASSISTANT_ROLE: Final[str] = 'assistant'

Message = dict[str, str]


class ContextManager:
    def __init__(
        self,
        limit_messages: int,
        limit_chars: int,
        system_prompt: str | None = None,
    ) -> None:
        self.limit_messages = limit_messages
        self.limit_chars = limit_chars
        self.history: list[Message] = []

        if system_prompt:
            self.history.append(
                {
                    ROLE_KEY: SYSTEM_ROLE,
                    CONTENT_KEY: system_prompt,
                },
            )

    def add_message(self, role: str, content: str) -> None:
        if role not in {SYSTEM_ROLE, USER_ROLE, ASSISTANT_ROLE}:
            raise ValueError(f'Неизвестная роль сообщения: {role}')

        if len(content) > self.limit_chars:
            content = content[-self.limit_chars :]

        self.history.append(
            {
                ROLE_KEY: role,
                CONTENT_KEY: content,
            },
        )

        self._apply_limits()

    def reset(self) -> None:
        system_message = self._get_system_message()
        self.history = [system_message] if system_message else []

    def _get_system_message(self) -> Message | None:
        if self.history and self.history[0].get(ROLE_KEY) == SYSTEM_ROLE:
            return self.history[0]

        return None

    def _system_offset(self) -> int:
        if self.history and self.history[0].get(ROLE_KEY) == SYSTEM_ROLE:
            return 1

        return 0

    def _apply_limits(self) -> None:
        system_offset = self._system_offset()

        while len(self.history) - system_offset > self.limit_messages:
            self.history.pop(system_offset)

        while self._total_chars() > self.limit_chars:
            if len(self.history) <= system_offset:
                break

            self.history.pop(system_offset)

    def _total_chars(self) -> int:
        return sum(len(message[CONTENT_KEY]) for message in self.history)
