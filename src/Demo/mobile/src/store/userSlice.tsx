// store/userSlice.js
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { UserData } from '../types';

interface UserState {
  userData: UserData | null;
  isDataLoaded: boolean;
}

const initialState: UserState = {
  userData: null,
  isDataLoaded: false,
};

export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUserData: (state, action: PayloadAction<UserData>) => {
      state.userData = action.payload;
      state.isDataLoaded = true; // 数据加载完成
    },
    clearUserData: (state) => {
      state.userData = null;
      state.isDataLoaded = false; // 数据未加载
    },
    // 可选：提供一个单独的 action 来设置加载状态
    setDataLoaded: (state, action: PayloadAction<boolean>) => {
      state.isDataLoaded = action.payload;
    },
  },
});

export const { setUserData, clearUserData, setDataLoaded } = userSlice.actions;

export default userSlice.reducer;
