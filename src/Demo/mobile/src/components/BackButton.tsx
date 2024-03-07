import React, { memo } from 'react';
import { TouchableOpacity, Image, StyleSheet } from 'react-native';
import { useSafeArea } from 'react-native-safe-area-context';

type Props = {
  goBack: () => void;
};

const BackButton = ({ goBack }: Props) => {
  const insets = useSafeArea();

  const styles = StyleSheet.create({
    container: {
      position: 'absolute',
      top: insets.top,
      left: 10,
    },
    image: {
      width: 24,
      height: 24,
    },
  });

  return (
    <TouchableOpacity onPress={goBack} style={styles.container}>
      <Image
        style={styles.image}
        source={require('../assets/arrow_back.png')}      
      />
    </TouchableOpacity>
  );
};  

export default memo(BackButton);
