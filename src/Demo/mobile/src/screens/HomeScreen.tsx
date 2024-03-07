import React, { memo, useEffect, useState } from 'react';
import Background from '../components/Background';
import { Button, Card, Divider, Icon, List, Text } from 'react-native-paper';
import { StyleSheet } from 'react-native';
import CameraComponent from '../components/Camera';
import { Props } from '../types';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

const HomeScreen = ({ navigation }: Props) => {
  const isUserDataLoaded = useSelector(
    (state: RootState) => state.user.isDataLoaded
  );
  const userData = useSelector((state: RootState) => state.user.userData);
  // navigate to registration screen if user is not registered
  useEffect(() => {
    if (isUserDataLoaded && !userData) {
      navigation.navigate('RegistrationScreen');
    }
  }, [isUserDataLoaded, userData, navigation]);

  const [cameraActive, setCameraActive] = useState(false);
  const handleBack = () => {
    console.log('back');
    setCameraActive(false);
    console.log(cameraActive);
  };
  if (cameraActive) {
    return <CameraComponent onBack={handleBack} />;
  }

  return (
    <Background>
      <Card style={styles.cardStyle}>
        <Card.Title
          title="Passport"
          left={(props) => <Icon source={'passport'} {...props} />}
        />

        <List.Section style={styles.cardStyle}>
          <List.Item
            title="ID"
            right={() => <Text>{userData?.id.slice(0, 10) ?? 'N/A'}</Text>}
          />
          <Divider />
          <List.Item
            title="Name"
            right={() => <Text>{userData?.name ?? 'N/A'}</Text>}
          />
          <Divider />
          <List.Item
            title="State"
            right={() => {
              if (userData?.state) {
                return <Icon color={'green'} source="check" size={30} />;
              } else {
                return <Icon color={'red'} source="close" size={30} />;
              }
            }}
          />
          <Divider />
        </List.Section>

        <Card.Actions>
          <Button
            icon="camera"
            mode="elevated" // 'elevated' is not a valid mode. Use 'contained' for solid background
            onPress={() => console.log('Pressed')}
            buttonColor={styles.checkButton.backgroundColor}
            // This sets the button color to your theme's primary color
            textColor={styles.buttonText.color} // This sets the text color to white
          >
            check
          </Button>
          <Button
            icon="cloud-upload"
            mode="elevated" // 'elevated' is not a valid mode. Use 'contained' for solid background
            onPress={() => setCameraActive(!cameraActive)}
            buttonColor={styles.uploadButton.backgroundColor}
            // This sets the button color to your theme's primary color
            textColor={styles.buttonText.color} // This sets the text color to white
          >
            Upload
          </Button>
        </Card.Actions>
      </Card>
    </Background>
  );
};

// TODO: oncheck button pressed

const StateIcon = () => {
  // update from global state
  const state = false;

  if (state) {
    return <Icon color={'green'} source="check" size={30} />;
  } else {
    return <Icon color={'red'} source="close" size={30} />;
  }
};

const styles = StyleSheet.create({
  cardStyle: {
    marginHorizontal: 5, // 控制左右边距
    marginVertical: 5, // 控制上下边距
    padding: 5,
    // ...其他样式
  },
  button: {
    margin: 4, // Adjust margins as needed
    // Possible additional styles
  },
  cardActions: {
    justifyContent: 'space-between', // Adjusts button distribution
  },
  checkButton: {
    backgroundColor: 'green', // This is light green; you can adjust the color as needed
  },
  uploadButton: {
    backgroundColor: 'blue', // This will use your theme's primary color
  },
  buttonText: {
    color: 'white', // Sets the text color to white for all buttons
  },
});

export default memo(HomeScreen);

// TODO:  upload to server
