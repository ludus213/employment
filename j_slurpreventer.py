#!/usr/bin/env python3
import tkinter as tk
from PIL import Image, ImageTk
import pytesseract
import cv2
import numpy as np
import os
import sys
import mss

# Set the path for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Ludus\scoop\apps\tesseract\5.5.0.20241111\tesseract.exe'
# Point to TESSDATA_PREFIX
os.environ['TESSDATA_PREFIX'] = r'C:\Users\Ludus\scoop\apps\tesseract\5.5.0.20241111/tessdata'
# Words to be censored
BANNED_WORDS = ["job", "employed", "work", "9-5", "employment", "employee", "employ"]

class SlurPreventer:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-disabled", True)
        self.root.wm_attributes("-transparentcolor", "white")

        self.image_path = self.resource_path("j-slur.png")
        self.pil_image = Image.open(self.image_path)

        self.sct = mss.mss()

        # Create a single overlay window
        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.wm_attributes("-topmost", True)
        self.overlay.wm_attributes("-transparentcolor", "white")
        monitor = self.sct.monitors[0]
        self.overlay.geometry(f"{monitor['width']}x{monitor['height']}+{monitor['left']}+{monitor['top']}")

        self.canvas = tk.Canvas(self.overlay, bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.tk_images = []

        self.scan_screen()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def scan_screen(self):
        # Capture the screen
        monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_BGRA2GRAY)

        # Use pytesseract to find text
        config = "--oem 3 --psm 11"
        data = pytesseract.image_to_data(screenshot_cv, config=config, output_type=pytesseract.Output.DICT)

        # Clear previous overlays
        self.canvas.delete("all")
        self.tk_images.clear()

        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 75:  # Confidence threshold
                text = data['text'][i].lower()
                if text in BANNED_WORDS:
                    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])

                    # Resize image to fit the word
                    resized_pil_image = self.pil_image.resize((w, h), Image.LANCZOS)
                    resized_tk_image = ImageTk.PhotoImage(resized_pil_image)
                    self.tk_images.append(resized_tk_image)

                    # Draw image on canvas
                    self.canvas.create_image(x, y, image=resized_tk_image, anchor=tk.NW)

        # Rescan after a delay
        self.root.after(250, self.scan_screen)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    app = SlurPreventer(root)
    root.mainloop()
