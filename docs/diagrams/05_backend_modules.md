# Рис. 3.1.1. Структура модулів серверної частини

Діаграма відображає основні пакети директорії `backend/app/` та напрямки
імпортів між ними. Стрілка `A --> B` означає «модуль A залежить від модуля B».
Структура реалізує шарову архітектуру: верхні шари (API) можуть викликати
нижні (Workflow → Repository → Models), але не навпаки.

**Використовується у розділах:** 3.1.

```mermaid
flowchart TD
    Main[main.py<br/>create_app, Sentry, middleware]
    Config[config.py<br/>Settings BaseSettings]
    Database[database.py<br/>AsyncEngine, get_db]
    Deps[dependencies.py<br/>фабрики DI для всіх шарів]

    subgraph Api [api/]
        ApiRouter[router.py]
        AuthApi[auth.py]
        UsersApi[users.py]
        GroupsApi[groups.py]
        RestApi[restaurants.py]
        OrdersApi[orders.py]
        BalancesApi[balances.py]
        AnalyticsApi[analytics.py]
        ApiRouter --> AuthApi
        ApiRouter --> UsersApi
        ApiRouter --> GroupsApi
        ApiRouter --> RestApi
        ApiRouter --> OrdersApi
        ApiRouter --> BalancesApi
        ApiRouter --> AnalyticsApi
    end

    subgraph Workflows [workflows/]
        WfUser[user/<br/>register, login]
        WfGroup[group/<br/>create, invite, manage_members]
        WfOrder[order/<br/>create, lifecycle]
        WfBalance[balance/<br/>adjust]
    end

    subgraph Repositories [repositories/]
        RepBase[base.py<br/>BaseRepository Generic]
        RepUser[user.py]
        RepGroup[group.py]
        RepRest[restaurant.py]
        RepOrder[order.py]
        RepBalance[balance.py]
    end

    subgraph Schemas [schemas/]
        ScBase[base.py<br/>PaginatedResponse, MessageResponse]
        ScUser[user.py]
        ScGroup[group.py]
        ScOrder[order.py]
        ScRest[restaurant.py]
        ScBalance[balance.py]
        ScAnalytics[analytics.py]
    end

    subgraph Models [models/]
        MdBase[base.py<br/>Base, BaseModel UUID + audit]
        MdEnums[enums.py<br/>UserRole, OrderStatus, presets]
        MdUser[user.py]
        MdGroup[group.py]
        MdOrder[order.py]
        MdRest[restaurant.py]
        MdBalance[balance.py]
    end

    subgraph Core [core/]
        CoreSec[security.py<br/>JWT, bcrypt]
        CoreExc[exceptions.py<br/>AppException ієрархія]
        CoreMid[middleware.py<br/>RequestLogging, ErrorHandling]
        CoreMail[email.py<br/>EmailService SMTP]
        CoreStor[storage.py<br/>uploads]
    end

    Main --> Config
    Main --> Api
    Main --> CoreMid
    Api --> Deps
    Deps --> Workflows
    Deps --> Repositories
    Deps --> Database
    Deps --> CoreMail
    Workflows --> Repositories
    Workflows --> Schemas
    Workflows --> CoreExc
    Workflows --> CoreSec
    Repositories --> Models
    Repositories --> Schemas
    Schemas --> Models
    Models --> MdEnums
```
