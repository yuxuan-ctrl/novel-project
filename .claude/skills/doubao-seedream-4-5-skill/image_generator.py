import requests
import json
import base64
from PIL import Image
from io import BytesIO
import os

# API配置
API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1"

def generate_image_doubao(prompt, model="doubao-seedream-4-0-250828", size="1024x1024",
                         watermark=False, response_format="url", image=None,
                         sequential_image_generation="disabled", multiple_images=False):
    """
    使用豆包API生成图片或图生图

    Args:
        prompt: 图片描述文本
        model: 模型名称，默认doubao-seedream-4-0-250828
        size: 图片尺寸
        watermark: 是否添加水印
        response_format: 返回格式，url或b64_json
        image: 基础图片URL或本地路径（用于图生图）
    """
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "response_format": response_format,
        "watermark": watermark
    }

    # 如果有图片，添加到数据中
    if image:
        # 如果是本地路径，需要先上传或转换为base64
        if os.path.exists(image):
            # 读取本地图片并转换为base64
            with open(image, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            # 这里简化处理，实际可能需要先上传获取URL
            data["image"] = f"data:image/png;base64,{image_data}"
        else:
            data["image"] = image

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()

        # 显示响应信息
        if 'created' in result:
            print(f"生成时间: {result['created']}")
        if 'usage' in result:
            usage = result['usage']
            print(f"Token使用: 总计={usage.get('total_tokens')}, 输出={usage.get('output_tokens')}")

        # 处理返回的图片
        for i, img_data in enumerate(result['data']):
            if response_format == "b64_json" and 'b64_json' in img_data:
                # 处理base64格式
                image_data = base64.b64decode(img_data['b64_json'])
                image = Image.open(BytesIO(image_data))
                filename = f"doubao_generated_{i+1}.png"
                image.save(filename)
                print(f"图片已保存: {filename}")
            elif 'url' in img_data:
                # 返回URL
                print(f"图片URL: {img_data['url']}")
                return img_data['url']

            # 显示修订后的提示词（如果有）
            if 'revised_prompt' in img_data:
                print(f"修订后的提示词: {img_data['revised_prompt']}")

        return result['data']
    else:
        print(f"错误: {response.status_code} - {response.text}")
        return None

# 保存图片从URL
def save_image_from_url(url, filename):
    """从URL保存图片到本地"""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"图片已保存: {filename}")
        return filename
    else:
        print(f"下载失败: {response.status_code}")
        return None

if __name__ == "__main__":
    # 测试示例
    prompt = "中国动画电影风格，英俊青年跪在石台上，铁链束缚，天空阴沉，电影级光照"
    image_url = generate_image_doubao(prompt)

    if image_url:
        save_image_from_url(image_url, "test_doubao.png")