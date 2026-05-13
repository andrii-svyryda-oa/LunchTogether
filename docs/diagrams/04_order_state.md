# Рис. 3.5.1. Діаграма станів життєвого циклу замовлення

Діаграма ілюструє валідні переходи між станами замовлення, що визначені у
`OrderLifecycleWorkflow` ([backend/app/workflows/order/lifecycle.py](../../backend/app/workflows/order/lifecycle.py))
константою `VALID_TRANSITIONS`. Усі переходи доступні лише ініціатору
замовлення, користувачу з рівнем дозволу `Orders:Editor` або системному
адміністратору. Перехід у термінальний стан `Finished` автоматично запускає
перерахунок балансів учасників.

**Використовується у розділах:** 1.4, 2.4, 3.5.

```mermaid
stateDiagram-v2
    [*] --> Initiated : create_order
    Initiated --> Confirmed : confirm
    Initiated --> Cancelled : cancel
    Confirmed --> Ordered : mark_as_ordered
    Confirmed --> Cancelled : cancel
    Ordered --> Finished : mark_as_finished<br/>(перерахунок балансів)
    Ordered --> Cancelled : cancel
    Finished --> [*]
    Cancelled --> [*]

    note right of Initiated
        Учасники додають свої
        позиції до замовлення.
    end note

    note right of Confirmed
        Ініціатор/Editor може
        задати вартість доставки.
        Позиції стають недоступними
        для звичайних учасників.
    end note

    note right of Ordered
        Замовлення передано до
        ресторану. Очікується
        отримання.
    end note

    note right of Finished
        Для кожного учасника
        обчислюється сума позицій
        + його частка доставки,
        balance.amount зменшується
        на цю суму, додається
        запис у balance_history.
        Список страв ресторану
        оновлюється з фактичних
        позицій замовлення.
    end note
```
