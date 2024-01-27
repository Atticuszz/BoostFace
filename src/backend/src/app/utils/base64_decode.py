"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 25/12/2023
@Description  :
"""
import base64


def decode_base64(data):
    # 如果有数据URI前缀，去除它
    if data.startswith('data:image'):
        # 查找Base64实际数据开始的位置
        base64_start = data.find('base64,') + 7
        data = data[base64_start:]
    # 确保字符串长度是4的倍数
    padding_needed = len(data) % 4
    if padding_needed:
        data += '=' * (4 - padding_needed)
    return base64.b64decode(data)
