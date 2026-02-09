# Epic 8: Group Dashboard & Analytics

## Overview

The group home page serves as a dashboard providing an at-a-glance view of group activity. It shows analytics, order history, and the current user's balance — all subject to the user's permission scopes within the group.

## Business Requirements

### Group Home Page Content

When a user navigates to the group home page, they should see (based on their permissions):

- **Analytics** (requires Analytics Viewer permission): group-level analytics about ordering activity, spending, and participation.
- **Order History**: a list of past orders for the group.
- **User's Balance with History** (requires Balances Viewer or Editor permission): the current user's balance within the group along with the history of balance changes.

### Analytics Permission

- **Viewer**: can see group analytics.
- **None**: analytics section is not visible.

### Navigation Behavior

- When entering a group page, the user is either redirected to the **active order** (if one exists and the user has configured this preference) or lands on the group home page.
- This preference is configurable per user in their settings.
