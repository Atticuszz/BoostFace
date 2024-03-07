import axios, { AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const baseURL = 'http://192.168.187.34:5000/auth';

const fastapiClient = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

fastapiClient.interceptors.request.use(
  async (config) => {
    const accessToken = await AsyncStorage.getItem('accessToken');
    const refreshToken = await AsyncStorage.getItem('refreshToken');
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    if (refreshToken) {
      config.headers['Refresh-Token'] = refreshToken;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const filterUserData = async (response: AxiosResponse) => {
  const { access_token, refresh_token, user } = response.data;
  // console.log('response.data:', response.data);
  const userData = {
    id: user.id,
    name: user.user_metadata?.name,
    userState: user.user_metadata?.state, // 或者根据实际情况调整
  };

  await AsyncStorage.setItem('accessToken', access_token);
  await AsyncStorage.setItem('refreshToken', refresh_token);
  await AsyncStorage.setItem('userData', JSON.stringify(userData));

  console.log('user:', userData);

  return userData; // 返回 userData 以供进一步使用
};
// login
export const login = async (email: string, password: string) => {
  try {
    const response = await fastapiClient.post('/login', { email, password });
    return await filterUserData(response); // 直接返回响应数据
  } catch (error) {
    console.error(error); // 简单打印错误信息
    return null;
  }
};

// register
export const register = async (
  email: string,
  password: string,
  username: string
) => {
  try {
    // await AsyncStorage.clear();
    const response = await fastapiClient.post('/register', {
      email,
      password,
      username,
    });

    return await filterUserData(response);
  } catch (error) {
    console.error(error); // 简单打印错误信息
    return null;
  }
};
export const faceRegister = async ({ id, name, face }) => {
  const data = {
    face_img: face.face_img,
    bbox: face.bbox, // Send as 2D array
    kps: face.kps, // Send as 2D array
    det_score: face.det_score,
    uid: face.uid,
  };
  // console.log('data:', data);
  const response = await fastapiClient.post(`/face-register/${id}/${name}`, {
    ...data,
  });
  return response.data;
};
