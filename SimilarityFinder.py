#Author: Stan Yin
#GitHub Name: SomeB1oody
#This project is based on CC 4.0 BY, please mention my name if you use it.
#This project requires opencv, os and wxWidgets.
import cv2
import os
import wx

global max_num
max_num = 0

def match_point(path1, path2):
    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)
    if img1 is None or img2 is None:
        wx.MessageBox("Cannot load image", "Error", wx.OK | wx.ICON_ERROR)
        return
    sift = cv2.SIFT()
    kp1, description1 = sift.detectAndCompute(img1, None)
    kp2, description2 = sift.detectAndCompute(img2, None)

    flann = cv2.FlannBasedMatcher()
    matches = flann.knnMatch(description1, description2, k=2)

    match_ = []
    for m, n in matches:
        if m.distance < 0.8 * n.distance:
            match_.append(m)

    num = len(match_)
    return num

def match_id(path1, database, match_point_number):
    global max_num
    for file in os.listdir(database):
        model = os.path.join(database, file)
        num = match_point(path1, model)

        if num > max_num:
            max_num = num
            name = file

    ID = name if name else None

    if max_num < match_point_number and ID is not None:
        ID = None

    return ID

class SimilarityFinder(wx.Frame):
    def __init__(self, *args, **kw):
        super(SimilarityFinder, self).__init__(*args, **kw)

        panel = wx.Panel(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        # 输入路径
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.file_button = wx.Button(panel, label="Select image")
        self.Bind(wx.EVT_BUTTON, self.on_select_file, self.file_button)
        self.hbox.Add(self.file_button,flag=wx.ALL, border=5)
        self.input_path_text = wx.StaticText(panel, label="Click \"Select image\" first")
        self.hbox.Add(self.input_path_text, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox, flag=wx.EXPAND)
        # 输入匹配点数
        self.vbox.Add(wx.StaticText(panel, label=
        "Enter min number of match point:"), flag=wx.ALL, border=5)
        self.match_point_number = wx.TextCtrl(panel)
        self.vbox.Add(self.match_point_number, flag=wx.EXPAND | wx.ALL, border=5)
        # 数据库的目录
        self.vbox.Add(wx.StaticText(panel, label="Database path:"), flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label="Example:C:\\Wallpaper\\"), flag=wx.ALL, border=5)
        self.database_path = wx.TextCtrl(panel)
        self.vbox.Add(self.database_path, flag=wx.EXPAND | wx.ALL, border=5)
        # 展示输入图片
        empty_image = wx.Image(300, 300)  # 创建一个空白的 wx.Image
        empty_image.Replace(0, 0, 0, 255, 255, 255)  # 将所有像素设为白色
        empty_bitmap = wx.Bitmap(empty_image)  # 将 wx.Image 转换为 wx.Bitmap
        self.vbox.Add(wx.StaticText(panel, label="Input image:"), flag=wx.ALL, border=5)
        self.image_area = wx.StaticBitmap(panel, bitmap=empty_bitmap)
        self.vbox.Add(self.image_area, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        # 按钮
        self.find_button = wx.Button(panel, label="Find")
        self.find_button.Bind(wx.EVT_BUTTON, self.on_find)
        self.vbox.Add(self.find_button, flag=wx.ALL, border=5)
        # 匹配项名字输出
        self.name_text = wx.StaticText(panel, label=
        "Please click \"Find\" button first to show best matched image")
        self.vbox.Add(self.name_text, flag=wx.ALL, border=5)
        # 展示匹配图片
        self.img_text = wx.StaticText(panel, label="")
        self.vbox.Add(self.img_text, flag=wx.ALL, border=5)
        self.image_area_matched = wx.StaticBitmap(panel, bitmap=empty_bitmap)
        self.vbox.Add(self.image_area_matched, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        # 设置面板的布局管理器
        panel.SetSizer(self.vbox)
        panel.Layout()

    def on_select_file(self, event):
        with wx.FileDialog(None, "Select a image", wildcard="所有文件 (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.input_path_text.SetLabel(f"{dialog.GetPath()}")
                self.selected_file = dialog.GetPath()


    def on_find(self, event):
        path = self.selected_file
        database_path = self.database_path.GetValue()
        match_point_number = self.match_point_number.GetValue()
        # 判断输入是否有效
        if not path:
            wx.MessageBox("Please enter image path", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not os.path.exists(path):
            wx.MessageBox(f"File path '{path}' does not exist",'Error', wx.OK | wx.ICON_ERROR)
            return
        if not os.path.isfile(path):
            wx.MessageBox(f"Cannot find file in path '{path}'",'Error', wx.OK | wx.ICON_ERROR)
            return
        if not match_point_number.isdigit():
            wx.MessageBox("Input must be a number that is greater than zero.",
            'Error', wx.OK | wx.ICON_ERROR)
            return
        #展示输入图片
        try:
            img = wx.Image(path, wx.BITMAP_TYPE_ANY)
            width = img.GetWidth() * (300 // img.GetHeight())
            img = img.Scale(width, 300, wx.IMAGE_QUALITY_HIGH)
            bitmap = wx.Bitmap(img)
            self.image_area.SetBitmap(bitmap)
            self.Refresh()
        except Exception as e:
            wx.MessageBox(f"Fail to show image: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
        # 寻找匹配图片
        id_ = match_id(path, database_path, match_point_number)
        if id_ is None:
            self.name_text.SetLabel("No image meets requirements.")
            return
        else:
            self.name_text.SetLabel(f"Best matched image is: {id_}")
            try:
                img_ = wx.Image(f"{database_path}{id_}", wx.BITMAP_TYPE_ANY)
                width_ = img_.GetWidth() * (300 // img_.GetHeight())
                img_ = img_.Scale(width_, 300, wx.IMAGE_QUALITY_HIGH)
                bitmap = wx.Bitmap(img_)
                self.image_area_matched.SetBitmap(bitmap)
            except Exception as e:
                self.img_text.SetLabel(f"Fail to show image: {str(e)}")
        self.Refresh()


if __name__ == "__main__":
    app = wx.App()
    frame = SimilarityFinder(None)
    frame.SetTitle('SimilarityFinder')
    frame.SetSize((700, 1000))
    frame.Show()
    app.MainLoop()
