import os
import subprocess
import sys
import threading

import wx
from PIL import Image

# example: http://www.java2s.com/Tutorial/Python/0380__wxPython/AddBitmaptoImageList.htm


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(1024, 768))
        self.image_paths = {}
        self.init_ui()

    def init_ui(self):
        self.panel = wx.Panel(self)

        self.folder_select_button = wx.Button(self.panel, label="Select Folder")
        self.folder_select_button.Bind(wx.EVT_BUTTON, self.on_select_folder)

        self.image_list_ctrl = wx.ListCtrl(
            self.panel, style=wx.LC_ICON | wx.LC_AUTOARRANGE
        )
        self.images = wx.ImageList(100, 100)
        self.image_list_ctrl.SetImageList(self.images, wx.IMAGE_LIST_NORMAL)
        self.image_list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_image_activated)

        self.loading_text = wx.StaticText(
            self.panel, label="Loading...", style=wx.ALIGN_CENTER
        )

        # Hide the loading text initially
        self.loading_text.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.folder_select_button, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.loading_text, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.image_list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(self.sizer)

        # Initially, the image list is not shown until images are loaded
        self.image_list_ctrl.Hide()

    def on_select_folder(self, event):
        dialog = wx.DirDialog(self, "Choose a directory:")

        if dialog.ShowModal() == wx.ID_OK:
            self.loading_text.Show()
            self.image_list_ctrl.Hide()
            self.image_paths.clear()

            self.update_ui()

            threading.Thread(
                target=self.load_thumbnails, args=(dialog.GetPath(),), daemon=True
            ).start()

        dialog.Destroy()

    def load_thumbnails(self, folderPath):
        wx.CallAfter(self.images.RemoveAll)
        wx.CallAfter(self.image_list_ctrl.DeleteAllItems)

        for filename in os.listdir(folderPath):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                image_path = os.path.join(folderPath, filename)

                img = Image.open(image_path)
                img.thumbnail((100, 100))
                img_wx = wx.Bitmap.FromBuffer(*img.size, img.tobytes())
                wx.CallAfter(self.add_image_to_list, img_wx, image_path)

        wx.CallAfter(self.finalize_loading)

    def add_image_to_list(self, img_wx, image_path):
        img_index = self.images.Add(img_wx)
        item_index = self.image_list_ctrl.InsertItem(
            self.image_list_ctrl.GetItemCount(), "", img_index
        )
        self.image_paths[item_index] = image_path

    def finalize_loading(self):
        self.loading_text.Hide()
        self.image_list_ctrl.Show()
        self.update_ui()

    def update_ui(self):
        self.panel.Layout()
        self.sizer.Layout()
        self.Refresh()

    def on_image_activated(self, event):
        # Open image
        index = event.GetIndex()
        image_path = self.image_paths.get(index)

        if image_path:
            if os.name == "nt":
                # Windows
                os.startfile(image_path)
            else:
                # macOS, Linux
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.run([opener, image_path])


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Image Browser with Thumbnails")
        frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
