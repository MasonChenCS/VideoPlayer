import os
from datetime import datetime
import cv2
from tkinter import *
import tkinter.filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import ImageTk, Image


def make_dir(entry):
    if not os.path.exists(entry):
        os.mkdir(entry)


def show_frames():
    global showing_frames
    global is_image
    global frame_counter
    global main_label
    global cur_frame
    global slider
    global grayscale
    global mode
    global vid
    if is_image:
        ret = True
    else:
        ret, frame = vid.read()
    if ret:
        speed = slider.get()
        if not is_image:
            if mode == 'Video':
                if speed > 0:
                    frame_counter += 1
                elif speed == 0 and frame_counter < vid.get(cv2.CAP_PROP_FRAME_COUNT):
                    vid.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)
                if frame_counter >= vid.get(cv2.CAP_PROP_FRAME_COUNT):
                    if looping:
                        frame_counter = 0
                        vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    else:
                        frame_counter = vid.get(cv2.CAP_PROP_FRAME_COUNT)
                        vid.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)
        else:
            frame = vid
        frame = autoresize(frame, height_=720)
        cur_frame = frame
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY if grayscale else cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image))
        main_label.imgtk = imgtk
        main_label.configure(image=imgtk)
        showing_frames = True
        main_label.after(int(20 * (1.0 / speed if speed > 0 else 0)), show_frames)
    else:
        showing_frames = False


def get_camera_array():
    index = 0
    arr = []
    while True:
        vid_ = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not vid_.read()[0] or vid_ is None or not vid_.isOpened():
            break
        else:
            arr.append(index)
        vid_.release()
        cv2.destroyAllWindows()
        index += 1
    vid_.release()
    cv2.destroyAllWindows()
    return arr


def get_name(mode_, direction, src_dir_, cur_vid_name_, cur_cam_name_):
    global vid_empty
    global cam_empty
    vid_list = os.listdir(src_dir_)
    if mode_ == 'Video' and len(vid_list) > 0:
        vid_empty = False
        if cur_vid_name_ == 'Init':
            return vid_list[0]
        if cur_vid_name_ in vid_list:
            index = vid_list.index(cur_vid_name_)
        else:
            # print('Video not found in directory. Defaulting to 0.')
            index = 0
        if direction == 'next':
            index += 1
            if index >= len(vid_list):
                index = 0
        elif direction == 'prev':
            index -= 1
            if index < 0:
                index = len(vid_list) - 1
        return vid_list[index]
    elif mode_ == 'Video' and len(vid_list) == 0:
        vid_empty = True
        prev_button.pack_forget()
        next_button.pack_forget()
    cam_list = get_camera_array()
    if mode_ == 'Camera' and len(cam_list) > 0:
        cam_empty = False
        if cur_cam_name_ == 'Init':
            return cam_list[0]
        if cur_cam_name_ in cam_list:
            index = cam_list.index(cur_cam_name_)
        else:
            # print('Camera not found in directory. Defaulting to 0.')
            index = 0
        if direction == 'next':
            index += 1
            if index >= len(cam_list):
                index = 0
        elif direction == 'prev':
            index -= 1
            if index < 0:
                index = len(cam_list) - 1
        return cam_list[index]
    elif mode_ == 'Camera' and len(cam_list) == 0:
        cam_empty = True
        prev_button.pack_forget()
        next_button.pack_forget()
    return 'None'


def button_cycle(mode_, direction, src_dir_, cur_vid_name_, cur_cam_name_):
    global showing_frames
    global is_image
    global frame_counter
    global cur_vid_name
    global cur_cam_name
    global main_label
    global mode_button
    global warning_label_vid
    global warning_label_cam
    global vid
    frame_counter = 0
    file_name = get_name(mode_, direction, src_dir_, cur_vid_name_, cur_cam_name_)
    if file_name != 'None':
        warning_label_vid.place_forget()
        warning_label_cam.place_forget()
        main_label.pack()
        mode_button.configure(text=mode_ + " Mode: " + str(file_name))
        if cur_vid_name_ != 'Init' or cur_cam_name_ != 'Init':
            if not is_image:
                vid.release()
            cv2.destroyAllWindows()  # This line and the one above do not seem to make a difference
        if mode_ == 'Video':
            if file_name.find(".png") != -1 or file_name.find(".jpg") != -1 or file_name.find(".jpeg") != -1:
                vid = cv2.imread(os.path.join(src_dir, file_name))
                is_image = True
            else:
                vid = cv2.VideoCapture(os.path.join(src_dir, file_name))
                is_image = False
            cur_vid_name = file_name
        elif mode_ == 'Camera':
            is_image = False
            vid = cv2.VideoCapture(int(file_name),
                                   cv2.CAP_DSHOW)  # No need for os.path.join because camera names are integers
            cur_cam_name = int(file_name)
        main_label.pack()
        if not showing_frames:
            show_frames()
        # vid.set(cv2.CAP_PROP_BUFFERSIZE, 3)
    else:
        main_label.pack_forget()
        if mode_ == 'Video':
            warning_label_cam.place_forget()
            warning_label_vid.place(relx=0.5, rely=0.4, anchor=CENTER)
        elif mode_ == 'Camera':
            warning_label_vid.place_forget()
            warning_label_cam.place(relx=0.5, rely=0.4, anchor=CENTER)
        mode_button.configure(text=mode_ + " Mode: None")


def mode_cycle(mode_, mode_list_):
    global mode
    if mode_ in mode_list_:
        index = mode_list_.index(mode_)
    else:
        # print('Mode not found in mode list. Defaulting to 0.')
        index = 0
    index += 1
    if index >= len(mode_list_):
        index = 0
    mode = mode_list_[index]


def grayscale_cycle():
    global grayscale
    if grayscale:
        grayscale = False
    else:
        grayscale = True


def autoresize(image, width_=None, height_=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width_ is None and height_ is None:
        return image
    if width_ is None:
        r = height_ / float(h)
        dim = (int(w * r), height_)
    else:
        r = width_ / float(w)
        dim = (width_, int(h * r))
    return cv2.resize(image, dim, interpolation=inter)


def add_braces(entry):
    if entry.find(" ") != -1:
        return "{" + entry + "}"
    return entry


def drop_listbox(event):
    update_listbox(event.data)


def update_listbox(entry):
    global listbox
    global src_dir
    global mode
    if entry.rfind("/") != "-1":
        if entry.find("{") != -1 and len(entry) > 2:
            entry = entry[entry.find("{") + 1:entry.find("}")]
        elif entry.find("{") == -1 and entry.find(" ") != -1:
            entry = entry[:entry.find(" ")]
        file_name = entry[entry.rfind("/") + 1:]
        listbox.insert("end", file_name)
        src_dir = entry[:entry.rfind("/")]
        mode = 'Video'
        button_cycle(mode, '', src_dir, file_name, '')
    else:
        listbox.insert("end", "Error locating file.")


def pause_or_resume():
    global pause_button
    global slider
    speed = slider.get()
    if speed == 0:
        slider.set(1)
        pause_button.configure(text="⏸")
    elif speed != 0:
        slider.set(0)
        pause_button.configure(text="▶")
    slider.update()


def take_screenshot():
    global save_dir
    global cur_frame
    global vid_empty
    global cam_empty
    global mode
    if (not vid_empty and mode == 'Video') or (not cam_empty and mode == 'Camera'):
        now = datetime.now()
        cv2.imwrite(os.path.join(save_dir, str(now.date())+"-"+str(now.hour)+"-"+str(now.minute)+"-"+str(now.second)+"-"+str(now.microsecond)+".png"), cur_frame)
    else:
        print("Could not take screenshot.")


src_dir = 'Source'
save_dir = 'Screenshots'
mode_list = ['Video', 'Camera']
mode = 'Video'
cur_vid_name = 'Init'
cur_cam_name = 'Init'
vid_empty = True
cam_empty = True
showing_frames = False
looping = True
grayscale = False
is_image = False
make_dir(src_dir)
make_dir(save_dir)
width = 1280
height = 720 + 250
label_font_size = 40
button_font_size = 20
listbox_font_size = 10
max_speed = 5
bg_color = "black"
button_color1 = "mediumpurple3"
button_color2 = "mediumpurple4"
window = TkinterDnD.Tk()
window.title("Video Player")
window.configure(background=bg_color)
window.geometry("%dx%d+%d+%d" % (width, height, window.winfo_screenwidth() / 2 - width / 2, window.winfo_screenheight() / 2 - height * 11 / 20))
window.resizable(False, False)

main_label = Label(width=1280, height=720, highlightthickness=0, bg=bg_color, borderwidth=0)
main_label.pack()
warning_label_vid = Label(text="No videos in source folder!", font=("Arial", label_font_size, "bold"), fg="white",
                          width=76, height=26, highlightthickness=0, bg=bg_color, borderwidth=0)
warning_label_vid.place(relx=0.5, rely=0.4, anchor=CENTER)
warning_label_vid.place_forget()
warning_label_cam = Label(text="No cameras connected!", font=("Arial", label_font_size, "bold"), fg="white", width=76,
                          height=26, highlightthickness=0, bg=bg_color, borderwidth=0)
warning_label_cam.place(relx=0.5, rely=0.4, anchor=CENTER)
warning_label_cam.place_forget()
pause_button = Button(text="⏸", font=("Arial", button_font_size, "bold"), fg="white",
                      activeforeground="white", width=12, height=2, bg=button_color1, activebackground=button_color2,
                      borderwidth=5, relief="raised", command=pause_or_resume)
pause_button.pack()
pause_button.place(x=width / 2 - 220 / 2, y=height - 220 / 2 - 70)
pause_button.update()
prev_button = Button(text="⏪", font="Arial 20 bold", fg="white", activeforeground="white", width=12, height=2,
                     bg=button_color1, activebackground=button_color2, borderwidth=5, relief="raised",
                     command=lambda: button_cycle(mode, 'prev', src_dir, cur_vid_name, cur_cam_name))
prev_button.pack()
prev_button.place(x=pause_button.winfo_x() - 230, y=pause_button.winfo_y())
prev_button.update()
next_button = Button(text="⏩", font=("Arial", button_font_size, "bold"), fg="white", activeforeground="white",
                     width=12, height=2,
                     bg=button_color1, activebackground=button_color2, borderwidth=5, relief="raised",
                     command=lambda: button_cycle(mode, 'next', src_dir, cur_vid_name, cur_cam_name))
next_button.pack()
next_button.place(x=pause_button.winfo_x() + 230, y=pause_button.winfo_y())
next_button.update()
mode_button = Button(text=mode+" Mode: None", font=("Arial", 16, "bold"), fg="white", width=51,
                     activeforeground="white",
                     bg=button_color1, activebackground=button_color2, borderwidth=5, relief="raised",
                     command=lambda: [mode_cycle(mode, mode_list),
                                      button_cycle(mode, '', src_dir, cur_vid_name, cur_cam_name)])
mode_button.pack()
mode_button.place(relx=0.5, y=pause_button.winfo_y() - 35, anchor=CENTER)
mode_button.update()
slider = Scale(from_=0, to=max_speed, resolution=0.1, orient=HORIZONTAL, font=("Arial", button_font_size, "bold"), fg="white",
               length=678, sliderlength=50, highlightthickness=2, highlightcolor="white", bg=button_color2,
               troughcolor="lavender", borderwidth=0)
slider.set(1)
slider.pack()
slider.place(relx=0.5, y=pause_button.winfo_y() + pause_button.winfo_height() + 40, anchor=CENTER)
slider.update()
listbox = Listbox(selectmode=tkinter.SINGLE, font=("Arial", listbox_font_size, "bold"), fg="white", width=35, height=9,
                  highlightthickness=2, highlightcolor="white", bg=button_color2, borderwidth=0)
listbox.insert(1, "Drag and drop files here...")
listbox.drop_target_register(DND_FILES)
listbox.dnd_bind("<<Drop>>", drop_listbox)
listbox.pack()
listbox.place(x=140, y=pause_button.winfo_y() + 80, anchor=CENTER)
listbox.update()
upload_button = Button(text="Upload File", font=("Arial", 16, "bold"), fg="white", activeforeground="white", width=18,
                       height=1, bg=button_color1, activebackground=button_color2, borderwidth=5, relief="raised",
                       command=lambda: update_listbox(add_braces(tkinter.filedialog.askopenfilename())))
upload_button.pack()
upload_button.place(x=mode_button.winfo_x() - 286, y=mode_button.winfo_y())
upload_button.update()
screenshot_button = Button(text="📸", font=("Arial", 54, "bold"), fg="white", activeforeground="white", width=5,
                           height=1, bg=button_color1, activebackground=button_color2, borderwidth=5, relief="raised",
                           command=take_screenshot)
screenshot_button.pack()
screenshot_button.place(x=mode_button.winfo_x() + mode_button.winfo_width() + 36, y=mode_button.winfo_y())
screenshot_button.update()
restart_button = Button(text="🔁", font=("Arial", button_font_size, "bold"), fg="white", activeforeground="white", width=5,
                           height=1, bg=button_color1, activebackground=button_color2, borderwidth=5, relief="raised",
                           command=lambda: button_cycle(mode, '', src_dir, cur_vid_name, cur_cam_name))
restart_button.pack()
restart_button.place(x=screenshot_button.winfo_x(), y=screenshot_button.winfo_y()+screenshot_button.winfo_height()+12)
restart_button.update()
gray_button = Button(text="Gray", font=("Arial", 20, "bold"), fg="white", activeforeground="white", width=5,
                     height=1, bg=button_color1, activebackground=button_color2, borderwidth=5, relief="raised",
                     command=grayscale_cycle)
gray_button.pack()
gray_button.place(x=screenshot_button.winfo_x()+screenshot_button.winfo_width()/2+16, y=screenshot_button.winfo_y()+screenshot_button.winfo_height()+12)
gray_button.update()

frame_counter = 0
vid = ''
cur_frame = ''
button_cycle(mode, '', src_dir, cur_vid_name, cur_cam_name)

if not showing_frames and ((not vid_empty and mode == 'Video') or (not cam_empty and mode == 'Camera')):
    show_frames()
window.mainloop()  # mainloop is an infinite loop. Nothing executes past this line until the program terminates.
if not is_image and vid != '':
    vid.release()
cv2.destroyAllWindows()