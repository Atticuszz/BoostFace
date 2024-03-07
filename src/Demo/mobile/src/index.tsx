import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import { HomeScreen, RegistrationScreen } from './screens';
import { useDispatch } from 'react-redux';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { setDataLoaded, setUserData } from './store/userSlice';

const Stack = createStackNavigator();
function RootStack() {
  return (
    <Stack.Navigator
      initialRouteName="HomeScreen"
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="HomeScreen" component={HomeScreen} />
      <Stack.Screen name="RegistrationScreen" component={RegistrationScreen} />
    </Stack.Navigator>
  );
}

export default function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    const initializeAppState = async () => {
      // await AsyncStorage.clear();
      try {
        const userDataString = await AsyncStorage.getItem('userData');
        if (userDataString) {
          const userData = JSON.parse(userDataString);
          dispatch(setUserData(userData));
        }
        dispatch(setDataLoaded(true));
      } catch (error) {
        console.error('Failed to load user data:', error);
      }
    };

    initializeAppState();
  }, [dispatch]);

  return (
    <NavigationContainer>
      <RootStack />
    </NavigationContainer>
  );
}
