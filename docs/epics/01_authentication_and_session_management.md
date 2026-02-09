# Epic 1: Authentication & Session Management

## Overview

LunchTogether requires user authentication so that each person can securely access their own groups, orders, and balances. Session management ensures users stay logged in across visits and can be securely logged out.

## Business Requirements

### Registration

- New users can register directly through the application.
- Users can also be invited to the platform via email — if the person is not yet registered, the invitation link should lead them to a registration flow.

### Login / Logout

- Registered users can log in to access the application.
- Users can log out, which terminates their active session.

### Session Management

- After logging in, the user's session should persist so they are not required to re-authenticate on every page visit.
- Sessions should eventually expire for security purposes.

## User Roles Context

There are two top-level application roles relevant to authentication:

- **Admin**: platform-wide administrator.
- **User**: regular application user.

Both roles authenticate through the same flow. Role-specific capabilities are handled in subsequent epics.
