from pathlib import Path

from PIL import Image, ImageFilter


def create_image_with_center_icon(icon_path, output_path, image_size=(960, 440), icon_size=(256, 256)):
    """
    创建一个带有中心图标的透明背景图像。

    :param icon_path: 图标的文件路径。
    :param output_path: 输出图像的文件路径。
    :param image_size: 输出图像的尺寸（宽度，高度），默认为 960x540。
    :param icon_size: 图标的尺寸（宽度，高度），默认为 64x64。
    """
    # 创建一个透明背景的图像
    image = Image.new("RGBA", image_size, (0, 0, 0, 0))

    # 加载图标
    icon = Image.open(icon_path)
    icon = icon.resize(icon_size, Image.ANTIALIAS)

    # 计算图标的位置（居中）
    icon_x = (image_size[0] - icon_size[0]) // 2
    icon_y = (image_size[1] - icon_size[1]) // 2

    # 将图标放置在图像中心
    image.paste(icon, (icon_x, icon_y), icon)
    # 显示图像
    image.show()
    # 保存图像
    image.save(output_path, "PNG")


def add_acrylic_effect(image_path, output_path, blur_radius=8, tint_color=(105, 114, 168, 102)):
    """
    对图像添加亚克力效果。

    :param image_path: 输入图像的路径。
    :param output_path: 输出图像的路径。
    :param blur_radius: 高斯模糊的半径。
    :param tint_color: 要叠加的半透明色彩，RGBA 格式。
    """
    # 打开原始图像
    original = Image.open(image_path)

    # 应用高斯模糊
    blurred = original.filter(ImageFilter.GaussianBlur(blur_radius))

    # 创建一个透明画布
    tint = Image.new("RGBA", original.size, tint_color)

    # 将模糊图像与色彩层叠加
    acrylic = Image.alpha_composite(blurred.convert("RGBA"), tint)

    # 保存和展示图像
    acrylic.save(output_path, "PNG")
    acrylic.show()


if __name__ == '__main__':
    src_dir = Path(r"C:\Users\18317\python\BoostFace_pyqt6\src\app\resource\images")
    placeholder = src_dir / "background.jpg"
    output = src_dir / "Acrylic_background.png"
    add_acrylic_effect(placeholder, output)
    # create_image_with_center_icon(src_dir.joinpath('logo.png'), placeholder)
