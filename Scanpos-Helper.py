from tkinter import StringVar, filedialog, messagebox
import tkinter as tk
from PIL import ImageTk, Image, ImageEnhance, ImageFilter, ImageGrab
import ctypes
from pynput import keyboard
from pynput import mouse

try:  # Windows 8.1 and later
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception as e:
    pass

image_contrast_float = 1.0
filter_pre_enhance = True
remove_white = False
window_alpha = 0.5


def prepareImage(filepath, contrast_float):
    nxtimage = Image.open(filepath)
    if filter_pre_enhance:
        nxtimage = nxtimage.filter(ImageFilter.EDGE_ENHANCE_MORE)
    enhancer = ImageEnhance.Contrast(nxtimage)
    nxtimage = enhancer.enhance(contrast_float)
    if not filter_pre_enhance:
        nxtimage = nxtimage.filter(ImageFilter.EDGE_ENHANCE_MORE)
    if remove_white:
        limage = nxtimage.convert("L")
        source = limage
        mask = source.point(lambda i: i < 150 and i)
        mask = mask.point(lambda i: i != 0 and 255)
        nxtimage = mask
    image = ImageTk.PhotoImage(nxtimage)
    return image


def showLoadSaveDialog():
    window = tk.Tk()
    window.geometry("750x250+10+100")
    window.attributes("-topmost", "true")
    file_path_load = StringVar()
    file_path_load.set("-")
    file_path_save = StringVar()
    file_path_save.set("-")

    def filedialogopen():
        file_path_load.set(filedialog.askopenfilename())
        if (file_path_load.get() and len(file_path_load.get()) > 1):
            window.destroy()

    def filedialogsave():
        window.attributes("-alpha", 0)
        file_path_save.set(
            filedialog.asksaveasfilename(defaultextension="bmp"))
        if (file_path_save.get() and len(file_path_save.get()) > 1):
            ss = ImageGrab.grab()
            ss.save(file_path_save.get(), "bmp")
            messagebox.showinfo("Fertig!", "Screenshot gespeichert!")
            window.destroy()
        else:
            window.attributes("-alpha", 1)

    ipadding = {'ipadx': 10, 'ipady': 10, "padx": 0, "pady": 0}
    tk.Label(
        window,
        text="Falls erste Messung eines Artefaktes: Screenshot aufnehmen!",
        anchor=tk.W,
        bg="white").pack(**ipadding,
                         fill=tk.X)
    tk.Label(window,
             text="Falls folgende Messung: Screenshot laden!",
             anchor=tk.W,
             bg="white").pack(**ipadding,
                              fill=tk.X)
    tk.Button(window,
              text='Screenshot laden!',
              command=filedialogopen).pack(**ipadding,
                                           fill=tk.X)
    tk.Button(window,
              text='Screenshot aufnehmen!',
              command=filedialogsave).pack(**ipadding,
                                           fill=tk.X)
    window.mainloop()
    return (file_path_load.get(), file_path_save.get())


"""
def get_curr_screen_geometry():
    """ """
    Workaround to get the size of the current screen in a multi-screen setup.

    Returns:
        geometry (str): The standard Tk geometry string.
            [width]x[height]+[left]+[top]
    """ """
    root = Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    geometry = root.winfo_geometry()
    root.destroy()
    return geometry
"""


def makeOverlayWindow(filepath):

    def on_release(key):
        global image_contrast_float, image, filter_pre_enhance, remove_white, window_alpha
        print('{0} released'.format(key))
        if key == keyboard.Key.esc:
            window.deiconify()
            window.destroy()
            return False
        if key == keyboard.Key.up:
            image_contrast_float = image_contrast_float + 1.0
            image = prepareImage(filepath, image_contrast_float)
            canvas.itemconfig(image_container, image=image)
        if key == keyboard.Key.down:
            image_contrast_float = image_contrast_float - 1.0
            image = prepareImage(filepath, image_contrast_float)
            canvas.itemconfig(image_container, image=image)
        if key == keyboard.Key.left:
            filter_pre_enhance = not filter_pre_enhance
            image = prepareImage(filepath, image_contrast_float)
            canvas.itemconfig(image_container, image=image)
        if key == keyboard.Key.right:
            remove_white = not remove_white
            image = prepareImage(filepath, image_contrast_float)
            canvas.itemconfig(image_container, image=image)
        if key == keyboard.Key.page_up:
            window_alpha = window_alpha + 0.05
            window.attributes("-alpha", window_alpha)
        if key == keyboard.Key.page_down:
            window_alpha = window_alpha - 0.05
            window.attributes("-alpha", window_alpha)

    # ...or, in a non-blocking fashion:"""
    listener = keyboard.Listener(on_release=on_release)
    listener.start()

    #creating window
    window = tk.Tk()
    #getting screen width and height of display
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    #setting tkinter window size
    window.geometry("%dx%d" % (width, height))
    window.geometry("+0+0")
    window.overrideredirect(True)
    window.attributes("-alpha", window_alpha)
    window.attributes('-topmost', 'true')
    canvas = tk.Canvas(window, width=width, height=height)
    canvas.pack()

    image = prepareImage(filepath, image_contrast_float)
    image_container = canvas.create_image(0, 0, anchor=tk.NW, image=image)

    window.mainloop()


filepaths = showLoadSaveDialog()
if (filepaths[0] and len(filepaths[0]) > 1):
    makeOverlayWindow(filepaths[0])