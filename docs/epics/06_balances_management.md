# Epic 6: Balances Management

## Overview

Each person in a group has a group-specific virtual balance. The application handles only the management and tracking of these balances — there is no payment system integration. Balances are adjusted manually by authorized members or automatically when orders are finished.

## Business Requirements

### Group-Specific Balances

- Every member of a group has their own balance within that group.
- Balances are scoped per group — the same user has independent balances in different groups.

### Manual Balance Adjustments

- Users with the **Balances Editor** permission scope can apply adjustments to balances of other participants in the group.
- An adjustment can be **positive** (adding funds) or **negative** (subtracting funds).
- An adjustment can include an optional **note** describing the reason.
- Every adjustment creates a **record in the balance history**.

### Automatic Balance Updates from Orders

- When an order reaches the **Finished** state, the balances of all participating members are automatically updated.
- This automatic update also creates a record in the balance history.

### Balance History

- Each balance has a full history of all changes (both manual adjustments and order-driven updates).
- The balance history is visible on the group home page (subject to the user's Balances permission scope).

### Permission Scopes

- **Editor**: can view balances and apply adjustments to other members' balances.
- **Viewer**: can view balances and balance history but cannot make adjustments.
- **None**: no access to balance information.
