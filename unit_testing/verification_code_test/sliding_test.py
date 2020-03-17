"""
破解极验验证码
"""
# -*- coding:utf-8 -*-
import time

from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

__author__ = 'Evan'


class SliderSpider(object):

    def __init__(self):
        self.url = 'https://www.geetest.com/demo/slide-popup.html'
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 8)

    def __del__(self):
        self.browser.close()

    def login(self):
        """
        :return:
        """
        self.browser.get(self.url)

    def click_button(self):
        """
        点击按钮，弹出滑动验证码
        :return:
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        button.click()

    def get_page_screenshot(self):
        """
        获取网页全屏截图
        :return:
        """
        pageScreenshot = self.browser.get_screenshot_as_png()
        # self.browser.save_screenshot('name.png')
        pageScreenshot = Image.open(BytesIO(pageScreenshot))

        return pageScreenshot

    def get_position(self):
        """
        获取验证码背景图的坐标位置
        :return:    返回左上右下四个值。左上，右下分别是图片左上角和图片右下角的坐标
        """
        image = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_bg')))

        location = image.location
        size = image.size
        # print('location:', location)
        # print('size:', size)
        left, upper, right, lower = location['x'], location['y'], location['x'] + size['width'], location['y'] + size[
            'height']
        print('背景图片的位置：', left, upper, right, lower)
        return left, upper, right, lower

    def get_bg_picture(self, name):
        """
        下载图片
        :param name: 保存图片的名字
        :return: 图片对象
        """
        left, upper, right, lower = self.get_position()
        pageScreenshot = self.get_page_screenshot()
        bg_img = pageScreenshot.crop((left, upper, right, lower))
        bg_img.save(name)
        return bg_img

    def hide_slider(self):
        """
        执行js代码,隐藏滑块;两句js代码用法一样，但有些小差别
        :return:
        """
        js = 'document.querySelectorAll("canvas")[2].style=""'  # 获取文档中 第二个class="canvax" 的style=''元素
        # js = 'document.getElementsByClassName("geetest_canvas_slice geetest_absolute")[0].style="display:none;"'
        self.browser.execute_script(js)

    def get_gap(self, img1, img2):
        """
        获取缺口偏移量
        :param img1: 不带缺口图片
        :param img2: 带缺口图
        :return: 缺口偏移量
        """
        left = 60
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i
                    return left
        return left

    def is_pixel_equal(self, img1, img2, x, y):
        """
        判断两个像素是否相同
        :param img1: 不带缺口图片
        :param img2: 带缺口图
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 获取图片指定位置的像素点
        pixel1 = img1.load()[x, y]
        pixel2 = img2.load()[x, y]
        threshold = 50
        # 如果x-x的值小于50的阈值，对比两张图片的像素值，找出差距过大的位置
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold and abs(pixel1[3] - pixel2[3]) < threshold:
            return True
        else:
            return False

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 缺口偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        distance += 15
        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 1.5
            else:
                # 加速度为负3
                a = -2
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def get_back_track(self):
        """
        模拟滑动超出15像素后的往回滑动
        :return:
        """
        tracks = [-1, -1, -1, -2, -2, -3, -2, -2, -1]
        for x in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()

    def mouse_shake(self):
        """
        模拟释放鼠标手抖了一个机灵
        :return:
        """
        ActionChains(self.browser).move_by_offset(xoffset=3, yoffset=0).perform()
        ActionChains(self.browser).move_by_offset(xoffset=-3, yoffset=0).perform()

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def move_slider(self, slider, track):
        """
        模拟人为滑动
        :param slider: 滑块位置
        :param track: 滑动轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()

        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        self.get_back_track()
        time.sleep(0.1)
        self.mouse_shake()
        time.sleep(0.2)
        ActionChains(self.browser).release().perform()

    def main(self):
        try:
            self.login()
            self.click_button()
            img1 = self.get_bg_picture('slider_test.png')
            self.hide_slider()
            img2 = self.get_bg_picture('no_slider_test.png')
            gap_distance = self.get_gap(img1, img2)
            print('缺口的位置为:', gap_distance)
            gap_distance -= 6
            track = self.get_track(gap_distance)
            slider = self.get_slider()
            self.move_slider(slider, track)

            result = self.wait.until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
            print('登录成功情况：', result)

        except:
            print('Login failed, try again!!!')
            self.main()


if __name__ == '__main__':
    slider = SliderSpider()
    slider.main()
