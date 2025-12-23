import requests
import json
import base64
from PIL import Image
from io import BytesIO
import os

# API配置
API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1"

def generate_image_doubao_v2(prompt, model="doubao-seedream-4-0-250828", size="1024x1024",
                            watermark=False, response_format="url", image=None,
                            multiple_images=False):
    """
    使用豆包API生成图片，支持文生图、图生图和多图融合

    Args:
        prompt: 图片描述文本
        model: 模型名称，默认doubao-seedream-4-0-250828
        size: 图片尺寸
        watermark: 是否添加水印
        response_format: 返回格式，url 或 b64_json
        image: 基础图片URL或本地路径（用于图生图），可以是列表（多图融合）
        multiple_images: 是否启用多图融合模式
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

    # 处理图片输入
    if image:
        if multiple_images and isinstance(image, list):
            # 多图融合模式
            data["sequential_image_generation"] = "disabled"
            image_list = []
            for img_path in image:
                if os.path.exists(img_path):
                    with open(img_path, "rb") as f:
                        img_data = base64.b64encode(f.read()).decode('utf-8')
                    image_list.append(f"data:image/png;base64,{img_data}")
                else:
                    image_list.append(img_path)
            data["image"] = image_list
            print(f"使用多图融合模式，图片数量：{len(image_list)}")
        else:
            # 单图模式
            if os.path.exists(image):
                with open(image, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                data["image"] = f"data:image/png;base64,{image_data}"
                print("使用单图生图模式")
            else:
                data["image"] = image
                print("使用图片URL")

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

# 测试多图融合
if __name__ == "__main__":
    # 多图融合示例
    prompt = "保持图1的面容特征，生成在斩仙台上的场景，身穿破烂囚衣，铁链束缚"
    images = [
        "character_images/linxuan.png",  # 角色参考
        # 可以添加更多参考图片，如服装、场景等
    ]

    result = generate_image_doubao_v2(
        prompt=prompt,
        image=images,
        multiple_images=True,
        watermark=False
    )

    if result and 'url' in result[0]:
        save_image_from_url(result[0]['url'], "test_multi_fusion.png")