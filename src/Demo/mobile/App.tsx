// App.tsx
import React from 'react';
import { Provider as ReduxProvider } from 'react-redux';
import store from './src/store'; // 确保路径正确
import { Provider as PaperProvider } from 'react-native-paper';
import { theme } from './src/core/theme'; // 确保路径正确
import { SafeAreaProvider } from 'react-native-safe-area-context';
import App from './src'; // 确保路径正确

const Main: React.FC = () => {
  return (
    <ReduxProvider store={store}>
      <PaperProvider theme={theme}>
        <SafeAreaProvider>
          <App />
        </SafeAreaProvider>
      </PaperProvider>
    </ReduxProvider>
  );
};

export default Main;
