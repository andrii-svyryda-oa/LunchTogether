import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { Nullable } from "@/types";

interface UserState {
  selectedUserId: Nullable<string>;
  searchQuery: string;
  currentPage: number;
}

const initialState: UserState = {
  selectedUserId: null,
  searchQuery: "",
  currentPage: 1,
};

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    setSelectedUserId(state, action: PayloadAction<Nullable<string>>) {
      state.selectedUserId = action.payload;
    },
    setSearchQuery(state, action: PayloadAction<string>) {
      state.searchQuery = action.payload;
      state.currentPage = 1;
    },
    setCurrentPage(state, action: PayloadAction<number>) {
      state.currentPage = action.payload;
    },
    resetUserFilters(state) {
      state.searchQuery = "";
      state.currentPage = 1;
    },
  },
});

export const {
  setSelectedUserId,
  setSearchQuery,
  setCurrentPage,
  resetUserFilters,
} = userSlice.actions;

// Selectors
export const selectSelectedUserId = (state: { user: UserState }) =>
  state.user.selectedUserId;
export const selectSearchQuery = (state: { user: UserState }) =>
  state.user.searchQuery;
export const selectCurrentPage = (state: { user: UserState }) =>
  state.user.currentPage;

export default userSlice.reducer;
