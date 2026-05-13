# Рис. 2.1.1. Шарова архітектура системи LunchTogether

Діаграма ілюструє основні шари клієнт-серверного додатку та напрямки залежностей
між ними. Запити користувача проходять зверху вниз: від React-клієнта через
HTTP/REST до серверної частини на FastAPI, далі через бізнес-логіку (Workflow)
до шару доступу до даних (Repository), що працює із PostgreSQL через
SQLAlchemy.

**Використовується у розділах:** 2.1, 2.6.

```mermaid
flowchart TD
    User([Користувач])

    subgraph Client [Клієнтська частина React+TypeScript]
        UI[Сторінки та компоненти<br/>shadcn/ui + Tailwind CSS]
        Routing[React Router<br/>ProtectedRoute]
        State[Redux Toolkit + RTK Query<br/>Кеш + інвалідація тегів]
        UI --> Routing
        UI --> State
    end

    HTTP[/REST через HTTPS<br/>JSON, HTTP-only cookie/]

    subgraph Server [Серверна частина FastAPI]
        Middleware[Middleware<br/>CORS, логування, обробка помилок]
        Endpoints[API endpoints<br/>APIRouter, Depends, response_model]
        AuthDep[Залежності автентифікації<br/>get_current_user, get_current_admin]
        Workflows[Workflow-класи<br/>бізнес-логіка та правила]
        Repositories[Repository-класи<br/>доступ до даних]
        ORM[SQLAlchemy 2.0<br/>декларативні моделі та сесії]

        Middleware --> Endpoints
        Endpoints --> AuthDep
        Endpoints --> Workflows
        Workflows --> Repositories
        Endpoints -. простi запити .-> Repositories
        Repositories --> ORM
    end

    DB[(PostgreSQL<br/>uuid-ossp, 12 таблиць)]

    User --> Client
    Client --> HTTP
    HTTP --> Middleware
    ORM --> DB
```
