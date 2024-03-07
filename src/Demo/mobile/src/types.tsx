import { FaceFeature, Image } from 'expo-face-detector';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';
import * as ImageManipulator from 'expo-image-manipulator';
import { faceRegister } from './services/api';
import { CameraCapturedPicture } from 'expo-camera/src/Camera.types';

export type Navigation = {
  navigate: (scene: string) => void;
};
export type Props = {
  navigation: Navigation;
};
// Define types for any complex structures used in the User
// For instance, if you have UserIdentity and Factor as complex types, you should define them as well.

// Assuming UserIdentity and Factor are like this:
interface UserIdentity {
  /*...*/
}

interface Factor {
  /*...*/
}

export interface UserData {
  id: string;
  app_metadata: Record<string, any>;
  user_metadata: Record<string, any>;
  aud: string;
  confirmation_sent_at?: Date | null;
  recovery_sent_at?: Date | null;
  email_change_sent_at?: Date | null;
  new_email?: string | null;
  invited_at?: Date | null;
  action_link?: string | null;
  email?: string | null;
  phone?: string | null;
  created_at: Date;
  confirmed_at?: Date | null;
  email_confirmed_at?: Date | null;
  phone_confirmed_at?: Date | null;
  last_sign_in_at?: Date | null;
  role?: string | null;
  updated_at?: Date | null;
  identities?: UserIdentity[] | null;
  factors?: Factor[] | null;
}

type Kps = [
  [number, number],
  [number, number],
  [number, number],
  [number, number],
  [number, number],
];
type Bbox = [
  [number, number],
  [number, number],
  [number, number],
  [number, number],
];
//
//{bounds: FaceFeatureBounds, smilingProbability?: number, leftEarPosition?: Point, rightEarPosition?: Point, leftEyePosition?: Point, leftEyeOpenProbability?: number, rightEyePosition?: Point, rightEyeOpenProbability?: number, leftCheekPosition?: Point, rightCheekPosition?: Point, leftMouthPosition?: Point, ...}
//
// TODO: github issue
// LOG  faceFeature {"BOTTOM_MOUTH": {"x": 182.98733139038086, "y": 481.19232177734375}, "LEFT_CHEEK": {"x": 255.1856689453125, "y": 467.2674255371094}, "LEFT_EAR"
// : {"x": 272.3841304779053, "y": 509.7964782714844}, "LEFT_EYE": {"x": 258.8485450744629, "y": 371.7942810058594}, "LEFT_MOUTH": {"x": 222.5811424255371, "y": 487
// .8376159667969}, "NOSE_BASE": {"x": 197.65894317626953, "y": 366.27337646484375}, "RIGHT_CHEEK": {"x": 141.28985595703125, "y": 400.6094970703125}, "RIGHT_EAR":
// {"x": 131.4392852783203, "y": 391.97344970703125}, "RIGHT_EYE": {"x": 179.35741424560547, "y": 330.4447021484375}, "RIGHT_MOUTH": {"x": 148.9053955078125, "y": 4
// 49.0743408203125}, "bounds": {"origin": {"x": 124.6875, "y": 299}, "size": {"height": 295.75, "width": 170.25}}, "leftEyeOpenProbability": 0.7024589776992798, "rightEyeOpenProbability": 0.623405933380127, "rollAngle": 22.676862716674805, "smilingProbability": 0.17023080587387085, "yawAngle": 355.01377296447754}
//  not bottomMouthPosition attr
export class FaceFeatureValidator {
  //  for face identify or face register
  bounds: Bbox | null;
  kps: Kps | null;
  face_img: string | undefined;
  uid: string;
  det_score: number;
  // face validate
  yaw_angle: number | null;
  roll_angle: number | null;
  eys_close: [number, number] | null;

  constructor() {
    this.bounds = null;
    this.kps = null;
    this.face_img = null;
    this.uid = ''; // 全局变量，用户id
    this.det_score = 0.8;
    this.roll_angle = null;
    this.yaw_angle = null;
    this.eys_close = null;
  }

  normal_position() {
    const no_yaw = !this.yawed_right() && !this.yawed_left();
    console.log('no_yaw', no_yaw);

    const no_roll = !this.roll_right() && !this.roll_left();
    console.log('no_roll', no_roll);

    return no_yaw && no_roll;
  }

  async finished(image: CameraCapturedPicture,target_size: { width: number; height: number }) {
    // console.log( 'image', image)
    const face_img = await cropFaceFromImage(image.uri, this.bounds,target_size);
    // FIXME: kps not change
    // this.face_img = `data:image/jpg;base64,${base64}`;
    this.face_img = face_img.base64
    const userData = await AsyncStorage.getItem('userData');
    const { id, name } = JSON.parse(userData);
    this.uid = id;
    await this.registerFace(id, name);
  }

  async registerFace(userId: string, userName: string) {
    try {
      const response = await faceRegister({
        id: userId,
        name: userName,
        face: {
          face_img: this.face_img, // Base64 encoded image data
          bbox: this.bounds, // Bounding box coordinates, assuming it's already a 2D array
          kps: this.kps, // Keypoints, assuming it's already a 2D array
          det_score: this.det_score, // Detection score
          uid: this.uid, // Face ID
        },
      });
      console.log("registerFace",response); // Response handling
    } catch (error) {
      console.error('Face registration failed:', error);
    }
  }

  update_attr(faceFeature: FaceFeature) {
    // console.log('faceFeature', faceFeature);
    // FIXME: feature wrong
    let { width, height } = faceFeature.bounds.size;
    let { x, y } = faceFeature.bounds.origin;
    this.bounds = [
      [x, y], // 左上角
      [x + width, y], // 右上角
      [x, y + height], // 左下角
      [x + width, y + height], // 右下角
    ];

    this.kps = [
      [faceFeature.LEFT_EYE.x, faceFeature.LEFT_EYE.y],
      [faceFeature.RIGHT_EYE.x, faceFeature.RIGHT_EYE.y],
      [faceFeature.NOSE_BASE.x, faceFeature.NOSE_BASE.y],
      [faceFeature.LEFT_MOUTH.x, faceFeature.LEFT_MOUTH.y],
      [faceFeature.RIGHT_MOUTH.x, faceFeature.RIGHT_MOUTH.y],
    ];
    this.face_img = null;
    this.uid = ''; // 全局变量，用户id
    this.det_score = 0.8;
    this.yaw_angle = faceFeature.yawAngle;
    this.roll_angle = faceFeature.rollAngle;
    this.eys_close = [
      faceFeature.leftEyeOpenProbability,
      faceFeature.rightEyeOpenProbability,
    ];
  }

  yawed_left() {
    console.log('this.yaw_angle', this.yaw_angle);
    return this.yaw_angle < 330 && this.yaw_angle > 290;
  }

  yawed_right() {
    console.log('this.yaw_angle', this.yaw_angle);
    return this.yaw_angle > 40 && this.yaw_angle < 90;
  }

  roll_right() {
    console.log('this.roll_angle', this.roll_angle);
    return this.roll_angle > 30 && this.roll_angle < 90;
  }

  roll_left() {
    console.log('this.roll_angle', this.roll_angle);
    return this.roll_angle < 350 && this.roll_angle > 290;
  }

  eys_blink() {
    console.log('this.eys_close', this.eys_close);
    return this.eys_close[0] < 0.2 && this.eys_close[1] < 0.2;
  }
}

async function cropFaceFromImage(imageUri, bbox,tar_size: { width: number; height: number }) {
  console.log("bbox",bbox)
  console.log( "tar_size", tar_size)
  const minX = Math.min(bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]);
  const minY = Math.min(bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]);
  const maxX = Math.max(bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]);
  const maxY = Math.max(bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]);

  const width = maxX - minX;
  const height = maxY - minY;

  const cropConfig = {
    originX: minX,
    originY: minY,
    width: width,
    height: height,
  };
  const croppedImage = await ImageManipulator.manipulateAsync(
    imageUri,
    [{resize:tar_size},{ crop: cropConfig }],
    { compress: 1, format: ImageManipulator.SaveFormat.JPEG ,base64:true}
  );
  console.log( 'croppedImage', croppedImage.height, croppedImage.width)
  return croppedImage;
}

export type ActionType = {
  name: string;
  check: (validator: FaceFeatureValidator) => boolean;
};

export interface UserData {
  id: string;
  name: string;
  state: string; // 根据您的需求调整这个字段
}
