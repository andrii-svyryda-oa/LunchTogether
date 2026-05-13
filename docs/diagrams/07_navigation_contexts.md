# Рис. 4.5.1. Перемикання контекстів бічної навігації

Двопанельна бічна навігація (`Sidebar` у
[frontend/src/components/common/Layout/Sidebar.tsx](../../frontend/src/components/common/Layout/Sidebar.tsx))
автоматично перемикається між двома контекстами на основі поточного маршруту.
Ліва вузька панель з іконками завжди показує домашню кнопку, список груп та
кнопку створення групи. Права (контекстна) панель показує підрозділи,
релевантні поточному контексту.

**Використовується у розділах:** 4.5, 4.7.

```mermaid
flowchart TD
    Path[pathname]

    Path --> Check{Перевірка<br/>pathname}

    Check -->|"pathname є /, /profile,<br/>/settings або /users/*"| HomeCtx[Домашній контекст]
    Check -->|"pathname починається з<br/>/groups/:groupId/*"| GroupCtx[Контекст групи]
    Check -->|"інше"| Empty[Контекстна панель<br/>прихована]

    subgraph IconBar [Ліва панель з іконками - завжди видима]
        HomeBtn[Home іконка]
        GroupIcons[Іконки всіх груп користувача<br/>useGetGroupsQuery]
        AddGroup[Кнопка плюс<br/>відкриває діалог створення групи]
    end

    subgraph HomeNav [Підрозділи домашнього контексту]
        Home[Home /]
        Profile[Profile /profile]
        Settings[Settings /settings]
        AdminBlock[Тільки для admin:<br/>Manage Users /users]
    end

    subgraph GroupNav [Підрозділи контексту групи]
        Dashboard[Dashboard /groups/:id]
        Members[Members /groups/:id/members]
        Restaurants[Restaurants /groups/:id/restaurants]
        Orders[Orders /groups/:id/orders]
        Balances[Balances /groups/:id/balances]
    end

    HomeCtx --> HomeNav
    GroupCtx --> GroupNav
```
