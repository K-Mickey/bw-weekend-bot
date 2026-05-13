# API (Use‑cases)

## GetContentUseCase
```python
async def get_content(node_id: str) -> ContentResponse:
    """Возвращает список сообщений (текст/изображения/видео) и клавиатуру для указанного узла.

    Parameters
    ----------
    node_id: str
        Уникальный идентификатор узла контента.

    Returns
    -------
    ContentResponse (pydantic модель)
        messages: List[MessagePayload]
        keyboard: List[List[Button]]
    """
```

## NavigateUseCase
```python
async def navigate(current_id: str, action_label: str) -> NavigationResponse:
    """Определяет следующее состояние на основе выбранной пользователем кнопки.

    - Проверяет доступность целевого узла (`available_from`, `feature_flag`).
    - Возвращает `NavigationResponse` с новым `node_id` и готовыми сообщениями.
    """
```

## RecordInteractionUseCase
```python
def record_interaction(user_id: int, from_id: str, to_id: str) -> None:
    """Сохраняет переход пользователя в `StateStore` и инкрементирует метрику Prometheus.
    """
```

*Все функции снабжены типами и pydantic‑моделями. Скрипт `docs/gen_api.py` автоматически обновляет этот файл, извлекая сигнатуры из `src/application/*.py`.*
