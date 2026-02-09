# Epic 4: Groups

## Overview

Groups are the central organizing unit in LunchTogether. A group represents a set of people (friends, colleagues, family) who organize regular meals together. This epic covers group creation, listing, member management, invitations, and group-level permissions assignment.

## Business Requirements

### Group Properties

- A group has a **name** and **description**.
- A group can optionally have a **logo**.

### Group Creation & Limits

- Any user can create groups, subject to a limit of **5 groups per user**.
- Each group can have up to **25 participants**.

### Group Listing & Visibility

- Users can only see groups they belong to.
- The main (left) navigation menu should follow a Discord-like layout:
  - The first square is a button leading to the user's home page (with analytics and navigation to settings).
  - Each subsequent square represents one of the user's groups.
- Admins can see all groups on the platform (covered in Epic 3).

### Group Home Page

- When a user enters a group page, the behavior depends on user preferences:
  - If there is an **active order** and the user has configured to navigate to active orders, they are redirected to the active order.
  - Otherwise, the user lands on the **group home page**.
  - This navigation preference should be configurable in user settings.
- The group home page displays (subject to permissions): analytics, order history, and the user's balance with history.

### Group Members Management

- Users with the **Members Editor** permission scope can manage group members.
- Members Editors can change other members' permission scopes/roles.
- Members Editors **cannot** perform any actions on the group owner — the owner is always protected.

### Group Permission Assignment

- When adding or editing a member, their permissions are set by choosing a **role preset** (Admin, SupervisorMember, Member) which fills all scopes at once.
- After selecting a preset, individual scopes can be **adjusted** per feature area:
  - Members: Editor, Viewer, None
  - Orders: Editor, Initiator, Participant
  - Balances: Editor, Viewer, None
  - Analytics: Viewer, None
  - Restaurants: Editor, Viewer

### Invitations

- Group members can invite others to join a group.
- **In-app invitation**: if the person is already registered, they receive an in-app invite.
- **Email invitation**: if the person is not registered, an email is sent with a registration link. Upon registering, they join the group.
- Users can invite friends who are already on the platform to their groups.
