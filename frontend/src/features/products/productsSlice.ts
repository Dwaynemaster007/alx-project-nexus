import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface ProductFilters {
  category_slug?: string;
  min_price?: number;
  max_price?: number;
}

/**
 * UI state shared by the navbar (search), the sidebar (filters),
 * the sort dropdown and the product grid (pagination).
 */
interface ProductState {
  isSidebarOpen: boolean;
  currentSort: string;
  filters: ProductFilters;
  search: string;
  offset: number;
}

const initialState: ProductState = {
  isSidebarOpen: false,
  currentSort: '-created_at', // Default sort (newest first)
  filters: {},
  search: '',
  offset: 0,
};

export const productsSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.isSidebarOpen = !state.isSidebarOpen;
    },
    // Changing sort, filters or search starts again from the first page
    setSort: (state, action: PayloadAction<string>) => {
      state.currentSort = action.payload;
      state.offset = 0;
    },
    setFilters: (state, action: PayloadAction<ProductFilters>) => {
      state.filters = action.payload;
      state.offset = 0;
    },
    setSearch: (state, action: PayloadAction<string>) => {
      state.search = action.payload;
      state.offset = 0;
    },
    setOffset: (state, action: PayloadAction<number>) => {
      state.offset = action.payload;
    },
  },
});

export const { toggleSidebar, setSort, setFilters, setSearch, setOffset } = productsSlice.actions;

export default productsSlice.reducer;
