# Архитектура проекта (Clean Architecture + DDD)

## 1. Слои
- **Presentation (Adapters)** – `telegram_adapter.py`, `vk_adapter.py`.
- **Application (Use‑cases)** – `get_content.py`, `navigate.py`, `record_interaction.py`.
- **Domain (Entities, Value Objects, Services)** – все бизнес‑сущности находятся в едином модуле `src/domain/domain.py`.  Он содержит базовый класс ``ContentNode`` с общей валидацией, конкретные типы ``PostNode``, ``PhotoNode``, ``VideoNode`` и ``TextNode``, а также вспомогательные value‑object‑ы (``Media``, ``KeyboardButton``) и фабрику ``node_factory``.
- **Infrastructure (Gateways)** – `content_repository.py`, `state_store.py`, `logger.py`, `metrics.py`.

## 2. Диаграмма
```plantuml
@startuml
!include architecture.puml
@enduml
```

## 3. Поток обработки запросов
1. Пользователь отправляет сообщение → **Adapter** (Telegram/VK).
2. Adapter вызывает **NavigateUseCase**.
3. Use‑case запрашивает **ContentRepository**.
4. Полученный **ContentNode** (созданный фабрикой) преобразуется в **MessagePayload** (текст, изображения, клавиатура).
5. Adapter отправляет сформированное сообщение пользователю.

---
*Все уровни работают независимо, что облегчает тестирование и замену компонентов.*
