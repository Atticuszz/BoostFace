import React, { useEffect, useRef, useState } from 'react';
import {
  Dimensions,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { Camera } from 'expo-camera';
import { Snackbar } from 'react-native-paper';
import MaskedView from '@react-native-masked-view/masked-view';
import * as FaceDetector from 'expo-face-detector';
import { ActionType, FaceFeatureValidator } from '../types';
import BackButton from './BackButton';

function CameraDeviceError({ message }) {
  const [snackbarVisible, setSnackbarVisible] = useState(true);

  return (
    <Snackbar
      visible={snackbarVisible}
      onDismiss={() => setSnackbarVisible(false)}
      duration={Snackbar.DURATION_SHORT}
    >
      {message}
    </Snackbar>
  );
}

type Props = {
  onBack: () => void; // ... other props
};
const CameraComponent = ({ onBack }: Props) => {
  const cameraRef = useRef<Camera>(null);
  const [hasPermission, setHasPermission] = useState(null);
  const [type, setType] = useState(Camera.Constants.Type.front);
  const [faces, setFaces] = useState([]);
  const [isDetecting, setIsDetecting] = useState(false);
  const [instruction, setInstruction] = useState('');

  // flash as detecting
  const [flashColor, setFlashColor] = useState('white');
  const colors = ['white', 'red', 'orange', 'blue', 'yellow'];
  useEffect(() => {
    let colorIndex = 0;
    let interval;
    if (isDetecting) {
      interval = setInterval(() => {
        setFlashColor(colors[colorIndex % colors.length]);
        colorIndex++;
      }, 500); // 每 500ms 改变颜色
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isDetecting]); // 依赖于 isDetecting 状态

  // permission?
  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  //  actions
  const faceFeatureValidator = useRef(new FaceFeatureValidator()).current;
  const [currentActions, setCurrentActions] = useState([]);
  const [currentActionIndex, setCurrentActionIndex] = useState(0);
  const possibleActions: ActionType[] = [
    {
      name: 'Yawed Left',
      check: (validator) => validator.yawed_left(),
    },
    { name: 'Yawed Right', check: (validator) => validator.yawed_right() },
    {
      name: 'Eyes Blink',
      check: (validator) => validator.eys_blink(),
    },
  ];

  // start facedetect and select actions
  const startFaceDetection = () => {
    setIsDetecting(true);
    // 随机选择两个动作
    const shuffled = possibleActions.sort(() => 0.5 - Math.random());
    setCurrentActions(shuffled.slice(0, 2));
    setCurrentActionIndex(0);
    // first action
    setInstruction('Please perform: ' + shuffled[0].name);
  };

  // Function to capture image from the camera
  const captureImage = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 1,
        base64: true,
      });
      return photo; // This should be the image object expected by DetectionResult
    }
    return null;
  };

  // face detect and validate

  const handleFacesDetected = async ({ faces}) => {
    // logic of handle face detect

    setFaces(faces);
    // pre-conditions
    console.log('length', faces.length);
    // must have one face
    if (faces.length === 0) {
      setInstruction('No face detected');
    } else if (faces.length > 1) {
      setInstruction('More than one face detected');
    } else {
      faceFeatureValidator.update_attr(faces[0]);

      // 检测到一个面部时，检查当前动作是否成功
      if (currentActionIndex < 2) {
        //  pre actions
        setInstruction(
          'Please perform: ' + currentActions[currentActionIndex].name
        );

        const currentAction = currentActions[currentActionIndex];
        if (currentAction && currentAction.check(faceFeatureValidator)) {
          // success action
          setTimeout(() => {
            setInstruction('Great! You did it!');
          }, 1000);
          setCurrentActionIndex(currentActionIndex + 1);
        } // failed do nothing
      } else {
        // final action
        setInstruction(
          'Please make sure your face is directly facing the screen and not tilted'
        );
        if (faceFeatureValidator.normal_position()) {
          setIsDetecting(false);
          setInstruction('All actions completed!');
          const image = await captureImage();
          await faceFeatureValidator.finished(image,styles.camera);
          setInstruction('registering!');
        }
      }
    }
  };

  if (hasPermission === null) {
    return <CameraDeviceError message="Requesting camera permission..." />;
  }
  if (!hasPermission) {
    return <CameraDeviceError message="No permission to access your camera" />;
  }

  return (
    <View style={[styles.container, { backgroundColor: flashColor }]}>
      {/*go back*/}
      {/*<TouchableOpacity*/}
      {/*  style={styles.backButton}*/}
      {/*  onPress={() => {*/}
      {/*    setIsDetecting(false);*/}
      {/*    navigation.navigate('Dashboard');*/}
      {/*  }}*/}
      {/*>*/}
      {/*  <Text style={styles.backButtonText}>{'< Back'}</Text>*/}
      {/*</TouchableOpacity>*/}

      <MaskedView
        style={StyleSheet.absoluteFill}
        maskElement={
          <View style={styles.maskContainer}>
            <View style={styles.mask}></View>
          </View>
        }
      >
        <Camera
          ref={cameraRef}
          style={styles.camera}
          type={type}
          onFacesDetected={isDetecting ? handleFacesDetected : undefined}
          pictureSize="1920x1080"
          ratio="16:9"
          faceDetectorSettings={{
            mode: FaceDetector.FaceDetectorMode.accurate,
            detectLandmarks: FaceDetector.FaceDetectorLandmarks.all,
            runClassifications: FaceDetector.FaceDetectorClassifications.all,
            minDetectionInterval: 10,
            tracking: true,
          }}
        />
      </MaskedView>

      {/* start face detect */}
      <TouchableOpacity
        style={styles.startButton}
        onPress={() => startFaceDetection()}
      >
        <Text style={styles.startButtonText}>Start Detection</Text>
      </TouchableOpacity>

      {instruction !== '' && (
        <View style={styles.instructionContainer}>
          <Text style={styles.instructionText}>{instruction}</Text>
        </View>
      )}

      {/* face state */}
      {faces.length > 0 && (
        <View style={styles.faceTextContainer}>
          <Text style={styles.faceText}>Detected {faces.length} face(s)</Text>
        </View>
      )}
      <BackButton goBack={onBack} />
    </View>
  );
};

const { width, height } = Dimensions.get('window');
const maskRadius = Math.min(width, height) / 2.2; // 根据需要调整这个半径
// 假设相机的宽高比是 16:9
const aspectRatio = 16 / 9;

// 计算相机视图的高度以保持 16:9 比例
const cameraHeight = width * aspectRatio;
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  }, //  camera view is not same as the picture size that camera takes
  camera: {
    width: width,
    height: cameraHeight, // opacity: 0.05,
  }, // mask view
  maskedView: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },

  // location of the mask
  maskContainer: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'transparent',
    justifyContent: 'center',
    alignItems: 'center',
  },
  mask: {
    width: maskRadius * 2,
    height: maskRadius * 2,
    borderRadius: maskRadius,
    backgroundColor: 'black',
  },

  startButton: {
    position: 'absolute',
    bottom: 30,
    alignSelf: 'center',
    backgroundColor: '#4CAF50',
    padding: 20,
    borderRadius: 10,
  },
  startButtonText: {
    color: '#fff',
    fontSize: 16,
  },
  backButton: {
    position: 'absolute',
    top: 45,
    left: 20,
    padding: 10,
    borderRadius: 5,
  },
  backButtonText: {
    fontSize: 18,
    color: 'black',
  },
  faceTextContainer: {
    position: 'absolute',
    bottom: 10,
    left: 10,
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 10,
    borderRadius: 5,
  },
  faceText: {
    color: '#fff',
  },
  instructionContainer: {
    position: 'absolute',
    top: '16%',
    alignSelf: 'center',
    backgroundColor: 'rgba(0,0,0,0.6)',
    padding: 10,
    borderRadius: 5,
  },
  instructionText: {
    color: '#fff',
    fontSize: 18,
    textAlign: 'center',
  },
});

export default CameraComponent;
