# Epic 7: Orders

## Overview

Orders are the core operational feature of LunchTogether. A group member initiates an order, participants add their dishes, and the order progresses through a lifecycle until it is finished or cancelled. Completed orders affect balances and can update restaurant dish information.

## Business Requirements

### Order Creation

- Users with the **Orders Editor** or **Orders Initiator** permission scope can create a new order within a group.

### Permission-Based Capabilities

- **Editor**: can add, edit, and remove dishes in the order for any participant, at any point during the editable stages.
- **Initiator**: can initiate an order, add their own dishes, wait for participants to add theirs, and then confirm or decline the order.
- **Participant**: can only add, edit, and remove their own dishes in an order.

### Order Dishes

- Each dish added to an order has:
  - **Name** (required)
  - **Detail** (optional)
  - **Price** (required)
- An order dish does **not** require a mandatory link to an existing restaurant dish — it can be entered freely as just a name, detail, and price. This is important for maintaining accurate historical records.

### Favorite Dishes

- A user can mark a dish as a **favorite**.
- When a user adds a position to a new order from a restaurant, their favorite dishes from that restaurant are **suggested**.
- The user can select from favorites or enter a new dish manually.

### Order Lifecycle

An order progresses through the following states:

1. **Initiated**: The order is created by the initiator. Participants can add their dishes.
2. **Confirmed**: The order is confirmed and becomes **non-editable**. At this point, the initiator is expected to place the order with the external source. The person who orders can manage **packing/delivery fees** — either by adding a specific amount to each participant or by entering a total amount that is divided equally among all participants.
3. **Ordered**: All dishes have been ordered and most likely paid for externally.
4. **Finished**: The order is complete — all dishes are delivered and paid. Upon entering this state:
   - **Balances** of all participating members are updated automatically.
   - Existing restaurant **dish prices** are updated if they differ from the order.
   - New dishes from the order are **stored** in the restaurant.
5. **Cancelled**: The order is cancelled by the initiator or by all participants leaving.

### Delivery / Packing Fees

- At the **Confirmed** stage, the person managing the order can handle delivery or packing fees in one of two ways:
  - Add a specific amount of money to each individual participant.
  - Enter a total fee amount that gets **divided equally** between all participants.
