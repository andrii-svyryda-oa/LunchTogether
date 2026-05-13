# Рис. 2.3.1. ER-діаграма бази даних

Діаграма описує реляційну схему бази даних PostgreSQL із дванадцятьма
сутностями та зовнішніми ключами між ними. Усі сутності наслідують спільні поля
`id` (UUID), `created_at` та `updated_at`. Ключові обмеження унікальності
позначено через `UQ` у назві ключа.

**Використовується у розділах:** 2.3, 3.3.

```mermaid
erDiagram
    USERS ||--o{ GROUPS : "owns"
    USERS ||--o{ GROUP_MEMBERS : "is_member_of"
    USERS ||--o{ GROUP_INVITATIONS : "invites_or_invited"
    USERS ||--o{ ORDERS : "initiates"
    USERS ||--o{ ORDER_ITEMS : "adds"
    USERS ||--o{ BALANCES : "has"
    USERS ||--o{ FAVORITE_DISHES : "marks_favorite"
    USERS ||--o{ BALANCE_HISTORY : "created_by"

    GROUPS ||--o{ GROUP_MEMBERS : "has"
    GROUPS ||--o{ GROUP_INVITATIONS : "has"
    GROUPS ||--o{ RESTAURANTS : "has"
    GROUPS ||--o{ ORDERS : "has"
    GROUPS ||--o{ BALANCES : "has"

    GROUP_MEMBERS ||--o{ GROUP_MEMBER_PERMISSIONS : "has"

    RESTAURANTS ||--o{ DISHES : "offers"
    RESTAURANTS ||--o{ ORDERS : "fulfills"

    DISHES ||--o{ ORDER_ITEMS : "referenced_by"
    DISHES ||--o{ FAVORITE_DISHES : "favorited_as"

    ORDERS ||--o{ ORDER_ITEMS : "contains"
    ORDERS ||--o{ BALANCE_HISTORY : "triggers"

    BALANCES ||--o{ BALANCE_HISTORY : "tracks"

    USERS {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        string role
        bool is_active
        bool is_verified
        bool navigate_to_active_order
    }

    GROUPS {
        uuid id PK
        string name
        string description
        string logo_path
        uuid owner_id FK
    }

    GROUP_MEMBERS {
        uuid id PK
        uuid user_id FK
        uuid group_id FK
    }

    GROUP_MEMBER_PERMISSIONS {
        uuid id PK
        uuid group_member_id FK
        string permission_type
        string level
    }

    GROUP_INVITATIONS {
        uuid id PK
        uuid group_id FK
        uuid inviter_id FK
        string invitee_email
        uuid invitee_id FK
        string status
        string token UK
    }

    RESTAURANTS {
        uuid id PK
        string name
        string description
        uuid group_id FK
    }

    DISHES {
        uuid id PK
        string name
        string detail
        decimal price
        uuid restaurant_id FK
    }

    FAVORITE_DISHES {
        uuid id PK
        uuid user_id FK
        uuid dish_id FK
        bool is_favorite
    }

    ORDERS {
        uuid id PK
        uuid group_id FK
        uuid restaurant_id FK
        string restaurant_name
        uuid initiator_id FK
        string status
        decimal delivery_fee_total
        decimal delivery_fee_per_person
    }

    ORDER_ITEMS {
        uuid id PK
        uuid order_id FK
        uuid user_id FK
        uuid dish_id FK
        string name
        string detail
        decimal price
        int quantity
    }

    BALANCES {
        uuid id PK
        uuid user_id FK
        uuid group_id FK
        decimal amount
    }

    BALANCE_HISTORY {
        uuid id PK
        uuid balance_id FK
        decimal amount
        decimal balance_after
        string note
        string change_type
        uuid order_id FK
        uuid created_by_id FK
    }
```
