# Epic 5: Restaurants

## Overview

Each group maintains its own scope of restaurants. Restaurants represent the places from which the group orders food. Each restaurant can have a menu of dishes that group members can choose from when placing orders.

## Business Requirements

### Restaurant Management

- Each group has its own list of restaurants.
- Users with the **Restaurants Editor** permission scope can add, edit, and remove restaurants within the group.
- Users with the **Restaurants Viewer** permission scope can view restaurants but not modify them.

### Restaurant Properties

- A restaurant has a **name** (required).
- A restaurant can optionally have a **description**.

### Dishes (Restaurant Menu)

- Each restaurant can have a list of **dishes**.
- Each dish has:
  - **Name** (required)
  - **Detail** (optional additional information)
  - **Price** (required)
- Dishes can be added, edited, and removed by users with the Restaurants Editor permission scope.

### Dish Price Updates from Orders

- When an order is finished, all existing dish prices in the restaurant should be updated to match the current prices from the order if they differ.
- If new dishes appear in a finished order that don't yet exist in the restaurant, they should be stored as new dishes.
