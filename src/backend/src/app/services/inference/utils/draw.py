import cv2


def draw_bbox(dimg, bbox, bbox_color):
    """
    only draw the bbox beside the corner,and the corner is round
    :param dimg: img to draw bbox on
    :param bbox: face bboxes
    :param bbox_color: bbox color
    :return: no return
    """
    # 定义矩形的四个角的坐标
    pt1 = tuple(map(int, (bbox[0], bbox[1])))
    pt2 = tuple(map(int, (bbox[2], bbox[3])))
    bbox_thickness = 2
    # 定义直角附近线段的长度
    line_len = int(0.08 * (pt2[0] - pt1[0]) + 0.06 * (pt2[1] - pt1[1]))
    inner_line_len = int(
        line_len *
        0.718) if bbox_color != (
        0,
        0,
        255) else line_len

    def draw_line(_pt1, _pt2):
        cv2.line(dimg, _pt1, _pt2, bbox_color, bbox_thickness)

    draw_line((pt1[0], pt1[1]), (pt1[0] + inner_line_len, pt1[1]))
    draw_line((pt1[0], pt1[1]), (pt1[0], pt1[1] + line_len))
    draw_line((pt2[0], pt1[1]), (pt2[0] - inner_line_len, pt1[1]))
    draw_line((pt2[0], pt1[1]), (pt2[0], pt1[1] + line_len))
    draw_line((pt1[0], pt2[1]), (pt1[0] + inner_line_len, pt2[1]))
    draw_line((pt1[0], pt2[1]), (pt1[0], pt2[1] - line_len))
    draw_line((pt2[0], pt2[1]), (pt2[0] - inner_line_len, pt2[1]))
    draw_line((pt2[0], pt2[1]), (pt2[0], pt2[1] - line_len))


def draw_text(dimg, box, name):
    # 文字信息显示
    font_scale = 1
    # 设置文本的位置，将文本放在人脸框的下方
    text_position = tuple(map(int, (box[0], box[3] + 22)))
    # ft2 = cv2.freetype.createFreeType2()
    # ft2.loadFontData(fontFileName='simhei.ttf', id=0)
    # ft2.putText(img=dimg,
    #             text=name,
    #             org=text_position,
    #             fontHeight=20,
    #             color=color,
    #             thickness=-1,
    #             line_type=cv2.LINE_AA,
    #             bottomLeftOrigin=True)
    # 添加文本  中文问题还没有解决
    cv2.putText(img=dimg,
                text=name,
                org=text_position,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=font_scale,
                color=(0, 255, 0),
                thickness=2,
                lineType=cv2.LINE_AA)
