// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';

const store = configureStore({
  reducer: {
    user: userReducer,
    // ...其他 reducers ...
  },
});

export type RootState = ReturnType<typeof store.getState>;
export default store;
