# Epic 2: Permissions System

## Overview

LunchTogether uses a layered permissions model. At the application level there are two roles (Admin and User). Within each group, members have fine-grained permission scopes that control what they can see and do.

## Application-Level Roles

- **Admin**: can observe all groups and users, can edit all groups and users, can create new groups and users.
- **User**: can see only their own groups, cannot see all users, can create a limited number of groups.

## Group-Level Permission Scopes

Each group member is assigned a permission level per feature area. The feature areas and their possible scopes are:

| Feature Area | Available Scopes |
|---|---|
| Members | Editor, Viewer, None |
| Orders | Editor, Initiator, Participant |
| Balances | Editor, Viewer, None |
| Analytics | Viewer, None |
| Restaurants | Editor, Viewer |

## Group-Level Roles (Presets)

To simplify assignment, there are predefined roles that set all scopes at once. After selecting a role, individual scopes can still be adjusted.

- **Admin**: highest permission level in every feature area.
- **SupervisorMember**: Viewer permission in every feature area.
- **Member**: lowest permission level in every feature area.

## Protection Rules

- Users with the Members Editor permission scope cannot perform any actions on the group owner. The group owner is always protected from modification by other members.
