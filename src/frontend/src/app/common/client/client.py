# coding=utf-8
import json
from base64 import urlsafe_b64decode
from pathlib import Path

import requests
from cryptography.fernet import Fernet
from time import time

from src.app.common.types import Face2SearchSchema
from src.app.utils.decorator import error_handler
from src.app.config.logging_config import qt_logger


class TokenEncryptor:
    """Encrypt and decrypt tokens"""

    def __init__(self):
        self.key = self.load_or_create_key()

    def load_or_create_key(self):
        """Load or create encryption key"""
        key_path = Path(__file__).parent / 'secret.key'
        if key_path.exists():
            return key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            return key

    def encrypt_data(self, data):
        """Encrypt data"""
        f = Fernet(self.key)
        return f.encrypt(data.encode())

    def decrypt_data(self, encrypted_data):
        """Decrypt data"""
        f = Fernet(self.key)
        return f.decrypt(encrypted_data).decode()


class TokenManager(TokenEncryptor):
    def __init__(self):
        super().__init__()
        self.access_token = None
        self.refresh_token = None
        self._load_tokens()

    @property
    def is_token_expired(self) -> bool:
        """Check if token is expired"""
        time_now = round(time())
        expires_at = time_now
        has_expired = True
        if self.access_token and self.access_token.split(".")[1]:
            payload = self._decode_jwt(self.access_token)
            exp = payload.get("exp")
            if exp:
                expires_at = int(exp)
                has_expired = expires_at <= time_now
        return has_expired

    @staticmethod
    def _decode_jwt(token: str) -> dict:
        """Decode JWT"""
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("JWT is not valid: not a JWT structure")
        base64Url = parts[1]
        # Addding padding otherwise the following error happens:
        # binascii.Error: Incorrect padding
        base64UrlWithPadding = base64Url + "=" * (-len(base64Url) % 4)
        return json.loads(urlsafe_b64decode(
            base64UrlWithPadding).decode("utf-8"))

    def save_tokens(self, access_token: str, refresh_token: str):
        """Save tokens to file"""
        self.refresh_token = refresh_token
        self.access_token = access_token
        encrypted_access_token = self.encrypt_data(
            access_token)
        encrypted_refresh_token = self.encrypt_data(
            refresh_token)
        token_path = Path(__file__).parent / 'tokens.enc'
        token_path.write_bytes(
            encrypted_access_token +
            b'\n' +
            encrypted_refresh_token)

    def _load_tokens(self):
        """Load tokens from file"""
        token_path = Path(__file__).parent / 'tokens.enc'
        if token_path.exists():
            encrypted_tokens = token_path.read_bytes().split(b'\n')
            if len(encrypted_tokens) == 2:
                self.access_token = self.decrypt_data(
                    encrypted_tokens[0])
                self.refresh_token = self.decrypt_data(
                    encrypted_tokens[1])


class AuthClient:
    """Client for sending requests and handling tokens"""

    def __init__(self, base_url):
        self.base_url = base_url
        self.base_ws_url = base_url.replace("http", "ws")
        self.token_manager = TokenManager()
        self.user: dict | None = None

    def sign_up(self, face2register: Face2SearchSchema, id: str, name: str):
        url = f'{self.base_url}/auth/face-register/{id}/{name}'
        headers = {'Content-Type': 'application/json'}
        data = face2register.model_dump()
        # qt_logger.debug(f"send data:{data}")
        response = requests.post(
            url,
            json=data,
            headers=headers
        )

        return response

    @error_handler
    def login(self, email: str, password: str) -> dict | None:
        """Login with email and password"""
        url = f"{self.base_url}/auth/login"
        response = requests.post(
            url,
            json={
                "email": email,
                "password": password})

        if response.status_code == 200:
            data = response.json()
            self.user = data.get("user")
            self.token_manager.save_tokens(
                data.get("access_token"),
                data.get("refresh_token"))
            return data
        else:
            return None

    @error_handler
    def get_user_info(self):
        url = f"{self.base_url}/user/info"
        response = requests.get(url, headers=self._auth_header)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def _refresh_session(self):
        """refresh token"""
        url = f"{self.base_url}/auth/refresh-token"
        params = {"refresh_token": self.token_manager.refresh_token}
        refresh_response = requests.post(
            url, params=params)
        if refresh_response.status_code == 200:
            data = refresh_response.json()
            self.token_manager.save_tokens(
                data.get("access_token"),
                data.get("refresh_token"))
        else:
            print("failed to refresh token")

    def _auth_header(self) -> dict:
        """Authorization header with access and refresh tokens"""
        if self.token_manager.access_token is None:
            return {}
        headers = {
            "Authorization": f"Bearer {self.token_manager.access_token}",
            "Refresh-Token": self.token_manager.refresh_token}
        return headers


client = AuthClient("http://192.168.137.1:5000")
client.login(email="zhouge1831@gmail.com", password="Zz030327#")
if __name__ == "__main__":
    # 使用示例

    response = client.login("zhouge1831@gmail.com", "Zz030327#")
    token_before_refresh = client.token_manager.access_token
    client._refresh_session()
    token_after_refresh = client.token_manager.access_token
    if token_before_refresh != token_after_refresh:
        print("refresh token success")
    else:
        print("refresh token failed")

    if response["access_token"] is not None:
        print("登录成功")
    else:
        print("登录失败")
