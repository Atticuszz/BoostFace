import React, { memo, useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Background from '../components/Background';
import Logo from '../components/Logo';
import Header from '../components/Header';
import Button from '../components/Button';
import TextInput from '../components/TextInput';
import { theme } from '../core/theme';
import { Navigation } from '../types';
import {
  emailValidator,
  passwordValidator,
  nameValidator,
} from '../core/utils';
import { Snackbar } from 'react-native-paper';
import { register } from '../services/api';
import { useDispatch, useSelector } from 'react-redux';
import { store } from '../store';
import { setUserData } from '../store/userSlice';

type Props = {
  navigation: Navigation;
};

const RegisterScreen = ({ navigation }: Props) => {
  const dispatch = useDispatch();
  const [name, setName] = useState({ value: '', error: '' });
  const [email, setEmail] = useState({ value: '', error: '' });
  const [password, setPassword] = useState({ value: '', error: '' });
  const [snackbarVisible, setSnackbarVisible] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const _onSignUpPressed = async () => {
    setLoading(true);
    const nameError = nameValidator(name.value);
    const emailError = emailValidator(email.value);
    const passwordError = passwordValidator(password.value);

    if (emailError || passwordError || nameError) {
      setName({ ...name, error: nameError });
      setEmail({ ...email, error: emailError });
      setPassword({ ...password, error: passwordError });
      return;
    }

    const response = await register(email.value, password.value, name.value);
    if (response) {
      dispatch(setUserData(response));
      console.log('Registration successful');
      setSnackbarMessage('Registration successful!');
      setSnackbarVisible(true);
      setTimeout(() => {
        navigation.navigate('HomeScreen');
      }, 1000);
    } else {
      console.log('Registration failed');
      setSnackbarMessage('Registration failed. Please try again.');
      setSnackbarVisible(true);
    }
    setLoading(false);
  };

  return (
    <Background>
      {/*<BackButton goBack={() => navigation.navigate('Dashboard')} />*/}

      <Logo />

      <Header>Create Account</Header>

      <TextInput
        label="Name"
        returnKeyType="next"
        value={name.value}
        onChangeText={(text) => setName({ value: text, error: '' })}
        error={!!name.error}
        errorText={name.error}
      />

      <TextInput
        label="Email"
        returnKeyType="next"
        value={email.value}
        onChangeText={(text) => setEmail({ value: text, error: '' })}
        error={!!email.error}
        errorText={email.error}
        autoCapitalize="none"
        autoComplete="email"
        textContentType="emailAddress"
        keyboardType="email-address"
      />

      <TextInput
        label="Password"
        returnKeyType="done"
        value={password.value}
        onChangeText={(text) => setPassword({ value: text, error: '' })}
        error={!!password.error}
        errorText={password.error}
        secureTextEntry
      />

      <Button
        mode="elevated"
        onPress={_onSignUpPressed}
        style={styles.button}
        loading={loading}
      >
        Sign Up
      </Button>

      {/*<View style={styles.row}>*/}
      {/*  <Text style={styles.label}>Already have an account? </Text>*/}
      {/*  <TouchableOpacity onPress={() => navigation.navigate('LoginScreen')}>*/}
      {/*    <Text style={styles.link}>Login</Text>*/}
      {/*  </TouchableOpacity>*/}
      {/*</View>*/}
      <Snackbar
        visible={snackbarVisible}
        onDismiss={() => setSnackbarVisible(false)}
        duration={Snackbar.DURATION_SHORT}
      >
        {snackbarMessage}
      </Snackbar>
    </Background>
  );
};

const styles = StyleSheet.create({
  label: {
    color: theme.colors.secondary,
  },
  button: {
    marginTop: 24,
  },
  row: {
    flexDirection: 'row',
    marginTop: 4,
  },
  link: {
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
});

export default memo(RegisterScreen);
