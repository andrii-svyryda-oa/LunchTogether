# LunchTogether — Presentation & Demo Plan

## Presentation (14 slides)

### Slide 1 — Титульний слайд

**Візуал**: логотип або назва додатку, ваше ім'я, група, керівник.

**Текст на слайді:**

> **LunchTogether**
>
> Веб-додаток для організації спільних обідів у колективах
>
> Виконав: студент групи \_\_\_\_ ПІБ
>
> Керівник практики: \_\_\_\_
>
> 2026

---

### Slide 2 — Проблематика

**Візуал**: іконки або ілюстрація хаотичної координації (месенджер, таблиця, калькулятор).

**Текст на слайді:**

> **Проблема**
>
> - Координація замовлень через месенджери — хаотично та неструктуровано
> - Розподіл витрат на доставку вручну — помилки та конфлікти
> - Відсутність обліку хто кому скільки винен
> - Немає єдиної платформи, що поєднує групи, замовлення та баланси

---

### Slide 3 — Рішення

**Візуал**: скріншот User Dashboard (`/`).

**Текст на слайді:**

> **LunchTogether — рішення**
>
> - Створення груп для спільних обідів
> - Каталог ресторанів та страв з цінами
> - Повний життєвий цикл замовлення з автоматичним розподілом доставки
> - Система балансів — автоматичний облік хто кому винен
> - Гнучка дворівнева система дозволів

---

### Slide 4 — Технології

**Візуал**: діаграма архітектури (Client → API → DB) або дві колонки з логотипами технологій.

**Текст на слайді:**

> **Стек технологій**
>
> | Серверна частина        | Клієнтська частина        |
> | ----------------------- | ------------------------- |
> | Python 3.12             | React 19                  |
> | FastAPI                 | TypeScript                |
> | SQLAlchemy 2.0          | Redux Toolkit / RTK Query |
> | PostgreSQL              | Tailwind CSS v4           |
> | Alembic                 | shadcn/ui                 |
> | JWT (HTTP-only cookies) | React Router v7           |

---

### Slide 5 — Архітектура

**Візуал**: схема шарів архітектури (Client → API → Workflow → Repository → DB).

**Текст на слайді:**

> **Архітектура системи**
>
> - **Клієнт-серверна архітектура** з REST API
> - **Repository Pattern** — інкапсуляція доступу до бази даних, узагальнений BaseRepository з CRUD-операціями
> - **Workflow Pattern** — бізнес-логіка в окремих класах з Pydantic-моделями для вводу/виводу
> - **Dependency Injection** — автоматичне ін'єктування залежностей через FastAPI Depends()

---

### Slide 6 — База даних

**Візуал**: ER-діаграма з основними таблицями та зв'язками.

**Текст на слайді:**

> **Структура бази даних**
>
> 10 таблиць, UUID як первинні ключі, Alembic міграції
>
> - **users** — користувачі з ролями (Admin / User)
> - **groups**, **group_members** — групи та учасники
> - **group_member_permissions** — дозволи (5 типів × рівні доступу)
> - **restaurants**, **dishes** — каталог їжі
> - **orders**, **order_items** — замовлення та позиції
> - **balances**, **balance_history** — фінансовий облік

---

### Slide 7 — Автентифікація та ролі

**Візуал**: скріншот Login page (`/login`).

**Текст на слайді:**

> **Автентифікація та авторизація**
>
> - JWT-токени в HTTP-only cookies (захист від XSS)
> - Ролі на рівні додатку: **Admin** (повний доступ) та **User**
> - Ролі на рівні групи: **Admin**, **Supervisor**, **Member**
> - 5 типів групових дозволів: Members, Orders, Balances, Analytics, Restaurants
> - Кожен тип має рівні: Editor, Viewer, Initiator, Participant, None

---

### Slide 8 — Групи та навігація

**Візуал**: два скріншоти поруч — sidebar у домашньому контексті та sidebar у контексті групи.

**Текст на слайді:**

> **Групи та контекстна навігація**
>
> - Створення групи через діалог (кнопка «+» на бічній панелі)
> - Запрошення учасників за email-адресою
> - **Домашній контекст**: Home, Profile, Settings, Manage Users
> - **Контекст групи**: Dashboard, Members, Restaurants, Orders, Balances
> - Навігація автоматично перемикається залежно від обраного контексту

---

### Slide 9 — Учасники та дозволи

**Візуал**: скріншот Group Members page (`/groups/:id/members`) + мала блок-схема перевірки дозволів.

**Текст на слайді:**

> **Управління учасниками**
>
> - Запрошення за email з вибором ролі
> - Пресети ролей автоматично призначають набір дозволів
> - Алгоритм перевірки: Admin? → Учасник групи? → Має потрібний тип дозволу? → Рівень достатній?
> - До 25 учасників у групі, до 5 груп на користувача

---

### Slide 10 — Ресторани та меню

**Візуал**: два скріншоти поруч — список ресторанів (`/groups/:id/restaurants`) та деталі ресторану зі стравами.

**Текст на слайді:**

> **Каталог ресторанів та страв**
>
> - Кожна група має власний список ресторанів
> - Ресторани містять меню зі стравами (назва, опис, ціна)
> - Компонент Combobox з можливістю створення нового ресторану прямо при оформленні замовлення
> - Улюблені страви для швидкого додавання

---

### Slide 11 — Життєвий цикл замовлення

**Візуал**: діаграма станів (Initiated → Confirmed → Ordered → Finished / Cancelled).

**Текст на слайді:**

> **Життєвий цикл замовлення**
>
> - **Initiated** — створено, учасники додають свої страви
> - **Confirmed** — підтверджено, можна вказати вартість доставки
> - **Ordered** — замовлення відправлено в ресторан
> - **Finished** — завершено, баланси оновлено автоматично
> - **Cancelled** — скасовано (можливо з будь-якого стану)
>
> Вартість доставки розділяється порівну між учасниками

---

### Slide 12 — Замовлення у дії

**Візуал**: два скріншоти поруч — діалог створення замовлення з Combobox та сторінка деталей замовлення.

**Текст на слайді:**

> **Створення та управління замовленням**
>
> - Вибір ресторану через Combobox (пошук або створення нового)
> - Додавання позицій: назва, ціна, кількість
> - Кнопки зміни статусу доступні ініціатору та редакторам
> - Вартість доставки з автоматичним розподілом на кожного учасника
> - При завершенні — автоматичне оновлення балансів усіх учасників

---

### Slide 13 — Баланси та аналітика

**Візуал**: два скріншоти поруч — сторінка балансів та дашборд групи.

**Текст на слайді:**

> **Система балансів та аналітика**
>
> - Автоматичний облік після завершення замовлення
> - Ручне коригування балансу з приміткою (наприклад, оплата готівкою)
> - Повна історія змін (тип: замовлення / ручне коригування)
> - Дашборд групи: кількість замовлень, загальні витрати, середній чек, найпопулярніший ресторан
> - Банер активного замовлення для швидкого доступу

---

### Slide 14 — Висновки

**Візуал**: чистий слайд з текстом, можливо іконка або лого.

**Текст на слайді:**

> **Висновки**
>
> Розроблено повнофункціональний веб-додаток з 9 модулями:
> автентифікація, групи, учасники, дозволи, ресторани, замовлення, баланси, аналітика, адміністрування
>
> **Перспективи розвитку:**
>
> - Сповіщення в реальному часі (WebSocket)
> - Інтеграція з платіжними системами
> - Мобільний додаток (React Native)
> - Підтримка кількох мов (i18n)
>
> **Дякую за увагу!**

---

## Screenshots to Prepare (12 total)

| #   | What to capture                  | Route / State                                             |
| --- | -------------------------------- | --------------------------------------------------------- |
| 1   | User Dashboard                   | `/` (logged in, with some data)                           |
| 2   | Login page                       | `/login`                                                  |
| 3   | Sidebar — home context           | Any home page (`/`, `/profile`, `/settings`)              |
| 4   | Sidebar — group context          | Any group page (`/groups/:id/orders`)                     |
| 5   | Group Members page               | `/groups/:id/members` (with several members)              |
| 6   | Restaurant list                  | `/groups/:id/restaurants` (with 2-3 restaurants)          |
| 7   | Restaurant detail with dishes    | `/groups/:id/restaurants/:rid` (with menu items)          |
| 8   | Order creation dialog (Combobox) | `/groups/:id/orders` → click "New Order"                  |
| 9   | Order detail page                | `/groups/:id/orders/:oid` (with items, status buttons)    |
| 10  | Balances page                    | `/groups/:id/balances` (with positive/negative balances)  |
| 11  | Group dashboard                  | `/groups/:id` (with analytics cards, active order banner) |
| 12  | Settings page                    | `/settings` (showing preferences and account info)        |

---

## Diagrams to Prepare (4 total)

| #   | Diagram                                                         | For slide |
| --- | --------------------------------------------------------------- | --------- |
| 1   | Architecture layers (Client → API → Workflow → Repository → DB) | 4, 5      |
| 2   | ER diagram (10 entities with relationships)                     | 6         |
| 3   | Permission check flowchart (Admin? → Member? → Permission?)     | 9         |
| 4   | Order lifecycle state diagram (Initiated → ... → Finished)      | 11        |

---

## Demo Script (5 minutes)

### 0:00–0:20 — Introduction

> "Доброго дня. Я представляю веб-додаток LunchTogether — систему для організації спільних обідів у робочих колективах. Зараз я продемонструю основні можливості додатку."

### 0:20–0:40 — Login & Dashboard

1. Open the app in the browser — you're on the **Login page**.
2. Enter credentials and log in.
3. Show the **User Dashboard** — point out analytics cards: total groups, orders participated, total spent, average order value, favorite restaurant.
   > "Після входу користувач потрапляє на особистий дашборд з аналітикою: кількість груп, замовлень, загальна сума витрат та улюблений ресторан."

### 0:40–1:10 — Navigation & Group Creation

1. Point out the **left sidebar**: Home icon highlighted, sub-navigation shows Home, Profile, Settings.
2. Click the **"+" button** at the bottom of group icons.
3. In the dialog, enter a group name and description → **Create**.
4. Group icon appears in the sidebar. Click it.
5. Sub-navigation switches to group context: Dashboard, Members, Restaurants, Orders, Balances.
   > "Навігація є контекстно-залежною. При виборі домашньої сторінки відображаються персональні розділи. Після створення групи та входу в неї — навігація перемикається на розділи цієї групи."

### 1:10–1:40 — Members & Permissions

1. Go to **Members** page.
2. Click **Invite** — enter an email address, select role "Member" from the Combobox.
3. Show existing members with their roles and permission badges.
   > "На сторінці учасників можна запрошувати нових за email-адресою, обирати роль та бачити дозволи кожного учасника. Система підтримує п'ять типів дозволів з різними рівнями."

### 1:40–2:10 — Restaurants & Dishes

1. Go to **Restaurants** page.
2. Show existing restaurants. Click on one.
3. On the **Restaurant Detail** page, show the dish list.
4. Add a new dish: enter name, price → save.
   > "Кожна група має свій каталог ресторанів зі стравами. Учасники можуть додавати нові ресторани та страви з цінами."

### 2:10–3:10 — Order Lifecycle (key demo)

1. Go to **Orders** page. Click **"New Order"**.
2. In the creation dialog, use the **Combobox** to search for a restaurant. Type a name that doesn't exist — show the **"Create …"** option. Select an existing restaurant instead → **Create**.
3. The order is created in **Initiated** status. You're on the **Order Detail** page.
4. **Add an item**: enter dish name, price, quantity → save. Show the item in the list.
5. Click **"Confirm Order"** — status changes to **Confirmed**.
6. Set **delivery fee** (e.g., 120 ₴) — show it's split equally among participants.
7. Click **"Mark as Ordered"** — status changes to **Ordered**.
8. Click **"Mark as Finished"** — status changes to **Finished**. Mention that balances are now auto-updated.
   > "Це ключова функція — повний життєвий цикл замовлення. Ініціатор створює замовлення, учасники додають свої страви, після підтвердження вказується вартість доставки, яка розділяється порівну. Після завершення баланси оновлюються автоматично."

### 3:10–3:40 — Balances

1. Go to **Balances** page.
2. Show member balances — some positive (owed money), some negative (owe money).
3. Click the **"+"** button next to a member — make a manual adjustment (e.g., +50 ₴ with note "Готівкою").
4. Expand a member's **history** — show entries with types (Order / Manual) and amounts.
   > "Система балансів автоматично відстежує хто кому скільки винен. Також можна робити ручні коригування, наприклад при оплаті готівкою. Вся історія зберігається."

### 3:40–4:10 — Group Dashboard & Analytics

1. Go to the **Group Dashboard** page.
2. Point out analytics: total orders, total spent, number of members, average order, most popular restaurant.
3. Show the **active order banner** (if visible) or mention it appears when there's an active order.
4. Show **"My balance"** card.
   > "Дашборд групи показує аналітику: загальну кількість замовлень, витрати, найпопулярніший ресторан. Якщо є активне замовлення — відображається банер з посиланням."

### 4:10–4:30 — Settings & Admin

1. Quickly navigate to **Settings** — show preferences (auto-navigate to active order toggle).
2. If time permits, quickly show **Manage Users** page (admin-only) with user list.
   > "У налаштуваннях можна ввімкнути автоматичний перехід до активного замовлення при вході в групу. Адміністратор також має доступ до управління всіма користувачами системи."

### 4:30–5:00 — Summary

> "Підсумовуючи: LunchTogether — це повнофункціональний веб-додаток з дев'ятьма функціональними модулями. Серверна частина побудована на FastAPI з PostgreSQL, клієнтська — на React з TypeScript та shadcn/ui. Система підтримує гнучку дворівневу авторизацію та повний цикл управління замовленнями. Дякую за увагу, готовий відповісти на запитання."
