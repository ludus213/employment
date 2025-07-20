import tkinter as tk
from PIL import Image, ImageTk
import pytesseract
import cv2
import numpy as np
import pyautogui
import os
import sys

# Set the path for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Ludus\scoop\apps\tesseract\5.5.0.20241111\tesseract.exe'
# Point to TESSDATA_PREFIX
os.environ['TESSDATA_PREFIX'] = r'C:\Users\Ludus\scoop\apps\tesseract\5.5.0.20241111/tessdata'
# Words to be censored
BANNED_WORDS = ["job", "employed", "work", "9-5"]

class SlurPreventer:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-disabled", True)
        self.root.wm_attributes("-transparentcolor", "white")

        self.overlay_windows = []
        self.image_path = self.resource_path("j-slur.png")
        self.pil_image = Image.open(self.image_path)
        self.tk_image = ImageTk.PhotoImage(self.pil_image)

        self.scan_screen()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def scan_screen(self):
        # Capture the screen
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        # Use pytesseract to find text
        data = pytesseract.image_to_data(screenshot_cv, output_type=pytesseract.Output.DICT)

        # Clear previous overlays
        for window in self.overlay_windows:
            window.destroy()
        self.overlay_windows.clear()

        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 60:  # Confidence threshold
                text = data['text'][i].lower()
                if any(banned_word in text for banned_word in BANNED_WORDS):
                    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    self.create_overlay(x, y, w, h)

        # Rescan after a delay
        self.root.after(1000, self.scan_screen)

    def create_overlay(self, x, y, w, h):
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.wm_attributes("-topmost", True)
        overlay.geometry(f"{w}x{h}+{x}+{y}")

        # Resize image to fit the word
        resized_pil_image = self.pil_image.resize((w, h), Image.LANCZOS)
        resized_tk_image = ImageTk.PhotoImage(resized_pil_image)

        label = tk.Label(overlay, image=resized_tk_image, bg='white')
        label.image = resized_tk_image  # Keep a reference
        label.pack()
        self.overlay_windows.append(overlay)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    app = SlurPreventer(root)
    root.mainloop()
