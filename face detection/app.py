import cv2
import numpy as np
import time
import threading
from tkinter import *
from tkinter import messagebox, filedialog, ttk, simpledialog
from PIL import Image, ImageTk
import logging
import speech_recognition as sr
import queue
import pyttsx3
import base64
import os
import secrets
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Yüz, göz ve gülümseme tanıma modellerini yükleme
face_cascade = cv2.CascadeClassifier('../Cascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('../Cascades/haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier('../Cascades/haarcascade_smile.xml')

# Nesne tanıma modelini yükleme
object_cascade = cv2.CascadeClassifier('../Cascades/haarcascade_car.xml')

# Kamerayı başlatma
kamera = cv2.VideoCapture(0)
if not kamera.isOpened():
    messagebox.showerror("Error", "Could not open camera.")
    exit()

# Video kaydı için ayar
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# Birden fazla kamera tanımlayın
camera_ids = [0, 1]  # Örnek olarak iki kamera tanımladık, gerçek kamera ID'leriyle değiştirin gerektiğinde
cameras = [cv2.VideoCapture(id) for id in camera_ids]

# Log dosyası ayarları
logging.basicConfig(filename='detection_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# FPS hesaplama için başlangıç zamanı
start_time = time.time()
frame_count = 0
stop_thread = False
face_id = 0
face_dict = {}
roi = None

frame_queue = queue.Queue()

# Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)


def speak(text):
    engine.say(text)
    engine.runAndWait()


def detect_and_display():
    global frame_count, start_time, stop_thread, face_id, roi

    while not stop_thread:
        ret, frame = kamera.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        if roi is not None:
            x1, y1, x2, y2 = roi
            frame = frame[y1:y2, x1:x2]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(20, 30)
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 2)

            if face_id not in face_dict:
                face_dict[face_id] = (x, y, w, h)
                face_id += 1

            cv2.putText(frame, f'ID: {face_id}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            logging.info(f'Face ID: {face_id} - Coordinates: ({x}, {y}, {w}, {h})')

        # Nesne tanıma
        objects = object_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(25, 25)
        )

        for (ox, oy, ow, oh) in objects:
            cv2.rectangle(frame, (ox, oy), (ox + ow, oy + oh), (0, 255, 255), 2)
            cv2.putText(frame, 'Object', (ox, oy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time

        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, 'Press "ESC" to Exit', (10, 70), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 255), 1,
                    cv2.LINE_AA)
        cv2.putText(frame, 'Face/Eye/Smile/Object Detection', (10, 110), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                    (255, 0, 255), 1, cv2.LINE_AA)

        out.write(frame)

        frame_queue.put(frame)

    kamera.release()
    out.release()
    cv2.destroyAllWindows()


def update_frame():
    if not frame_queue.empty():
        frame = frame_queue.get()

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(image=img)

        lbl_video.imgtk = img
        lbl_video.configure(image=img)

    root.after(10, update_frame)


def start_detection():
    global stop_thread
    stop_thread = False
    thread = threading.Thread(target=detect_and_display)
    thread.start()
    speak("Detection started")


def stop_detection():
    global stop_thread
    stop_thread = True
    speak("Detection stopped")


def take_snapshot():
    if not stop_thread:
        ret, frame = kamera.read()
        if ret:
            filename = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                    filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")])
            if filename:
                if roi is not None:
                    x1, y1, x2, y2 = roi
                    frame = frame[y1:y2, x1:x2]
                cv2.imwrite(filename, frame)
                messagebox.showinfo("Snapshot", "Snapshot saved successfully!")
                speak("Snapshot saved successfully")


def open_settings():
    settings_window = Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x200")

    def save_settings():
        global roi
        x1 = int(scale_factor_entry.get())
        y1 = int(min_neighbors_entry.get())
        x2 = int(min_size_entry.get())
        y2 = int(min_size_entry2.get())
        roi = (x1
               , y1, x2, y2)
        settings_window.destroy()
        speak("Settings saved")

    lbl_scale_factor = Label(settings_window, text="ROI x1")
    lbl_scale_factor.pack(pady=5)
    scale_factor_entry = Entry(settings_window)
    scale_factor_entry.pack(pady=5)

    lbl_min_neighbors = Label(settings_window, text="ROI y1")
    lbl_min_neighbors.pack(pady=5)
    min_neighbors_entry = Entry(settings_window)
    min_neighbors_entry.pack(pady=5)

    lbl_min_size = Label(settings_window, text="ROI x2")
    lbl_min_size.pack(pady=5)
    min_size_entry = Entry(settings_window)
    min_size_entry.pack(pady=5)

    lbl_min_size2 = Label(settings_window, text="ROI y2")
    lbl_min_size2.pack(pady=5)
    min_size_entry2 = Entry(settings_window)
    min_size_entry2.pack(pady=5)

    btn_save = Button(settings_window, text="Save", command=save_settings)
    btn_save.pack(pady=10)


def detect_from_photo():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*")])
    if file_path:
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(20, 30))
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 2)

        objects = object_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(25, 25))
        for (ox, oy, ow, oh) in objects:
            cv2.rectangle(img, (ox, oy), (ox + ow, oy + oh), (0, 255, 255), 2)
            cv2.putText(img, 'Object', (ox, oy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Detected Photo", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        speak("Photo detection completed")


def detect_from_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov"), ("All files", "*.*")])
    if file_path:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open video file.")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(20, 30))
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]

                eyes = eye_cascade.detectMultiScale(roi_gray)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

                smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)
                for (sx, sy, sw, sh) in smiles:
                    cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 2)

            objects = object_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(25, 25))
            for (ox, oy, ow, oh) in objects:
                cv2.rectangle(frame, (ox, oy), (ox + ow, oy + oh), (0, 255, 255), 2)
                cv2.putText(frame, 'Object', (ox, oy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            cv2.imshow("Detected Video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        speak("Video detection completed")


def voice_command_listener():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening for voice commands...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"Voice command: {command}")

            if "start detection" in command:
                start_detection()
            elif "stop detection" in command:
                stop_detection()
            elif "take snapshot" in command:
                take_snapshot()
            elif "open settings" in command:
                open_settings()
            elif "exit" in command:
                stop_detection()
                root.quit()
                speak("Exiting the application")
                break
            elif "encrypt data" in command:
                encrypt_data_via_voice()
            elif "decrypt data" in command:
                decrypt_data_via_voice()

        except sr.UnknownValueError:
            print("Sorry, I did not understand the command.")
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service")


class CustomEncryption:
    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = self.generate_key()

    @staticmethod
    def generate_key():
        return secrets.token_bytes(32)  # 32 byte uzunluğunda bir anahtar oluştur

    def encrypt(self, data):
        iv = os.urandom(16)  # Rastgele bir IV oluştur
        encryptor = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend()).encryptor()
        cipher_text = encryptor.update(data) + encryptor.finalize()
        return iv + cipher_text

    def decrypt(self, encrypted_data):
        iv = encrypted_data[:16]  # IV, şifreli verinin başında
        decryptor = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend()).decryptor()
        decrypted_data = decryptor.update(encrypted_data[16:]) + decryptor.finalize()
        return decrypted_data

    @staticmethod
    def generate_hmac(data, key):
        hmac_algo = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        hmac_algo.update(data)
        return hmac_algo.finalize()

    @staticmethod
    def verify_hmac(data, key, mac):
        hmac_algo = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        hmac_algo.update(data)
        hmac_algo.verify(mac)


# Anahtar oluşturma
key = CustomEncryption.generate_key()
custom_cipher = CustomEncryption(key)

# HMAC anahtarı oluşturma
hmac_key = CustomEncryption.generate_key()


def encrypt_data():
    data = simpledialog.askstring("Input", "Enter the data to encrypt:")
    if data:
        encrypted_data = custom_cipher.encrypt(data.encode('utf-8'))
        mac = custom_cipher.generate_hmac(encrypted_data, hmac_key)
        cipher_text_base64 = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        messagebox.showinfo("Encrypted Data", f"Encrypted Data (Base64): {cipher_text_base64}")
        speak("Data encrypted successfully")


def decrypt_data():
    encrypted_data_b64 = simpledialog.askstring("Input", "Enter the Base64 encrypted data:")
    if encrypted_data_b64:
        encrypted_data = base64.urlsafe_b64decode(encrypted_data_b64)
        try:
            custom_cipher.verify_hmac(encrypted_data, hmac_key, custom_cipher.generate_hmac(encrypted_data, hmac_key))
            decrypted_data = custom_cipher.decrypt(encrypted_data).decode('utf-8')
            messagebox.showinfo("Decrypted Data", f"Decrypted Data: {decrypted_data}")
            speak("Data decrypted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")
            speak("Decryption failed")


def encrypt_data_via_voice():
    data = simpledialog.askstring("Input", "Enter the data to encrypt via voice command:")
    if data:
        encrypted_data = custom_cipher.encrypt(data.encode('utf-8'))
        mac = custom_cipher.generate_hmac(encrypted_data, hmac_key)
        cipher_text_base64 = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        messagebox.showinfo("Encrypted Data", f"Encrypted Data (Base64): {cipher_text_base64}")
        speak("Data encrypted successfully via voice command")


def decrypt_data_via_voice():
    encrypted_data_b64 = simpledialog.askstring("Input", "Enter the Base64 encrypted data via voice command:")
    if encrypted_data_b64:
        encrypted_data = base64.urlsafe_b64decode(encrypted_data_b64)
        try:
            custom_cipher.verify_hmac(encrypted_data, hmac_key, custom_cipher.generate_hmac(encrypted_data, hmac_key))
            decrypted_data = custom_cipher.decrypt(encrypted_data).decode('utf-8')
            messagebox.showinfo("Decrypted Data", f"Decrypted Data: {decrypted_data}")
            speak("Data decrypted successfully via voice command")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")
            speak("Decryption failed via voice command")


def view_log():
    log_window = Toplevel(root)
    log_window.title("Detection Log")
    log_window.geometry("600x400")

    with open('detection_log.txt', 'r') as file:
        log_content = file.read()

    log_text = Text(log_window)
    log_text.insert(1.0, log_content)
    log_text.pack(expand=True, fill=BOTH)

    log_window.mainloop()


root = Tk()
root.title("Face Detection with OpenCV and Tkinter")
root.geometry("900x700")
root.configure(bg='lightblue')

style = ttk.Style()
style.configure('TButton', font=('Arial', 12, 'bold'), padding=10)
style.configure('TLabel', font=('Arial', 12), background='lightblue')
style.configure('TFrame', background='lightgray')

lbl_title = ttk.Label(root, text="Real-Time Detection and Analysis", font=('Arial', 20, 'bold'))
lbl_title.pack(pady=10)

lbl_video = Label(root, bg='black')
lbl_video.pack(fill=BOTH, expand=YES, padx=10, pady=10)

frame_controls = ttk.Frame(root)
frame_controls.pack(fill=X, pady=10)

btn_start = ttk.Button(frame_controls, text="Start Detection", command=start_detection)
btn_start.pack(side=LEFT, padx=10, pady=10)

btn_stop = ttk.Button(frame_controls, text="Stop Detection", command=stop_detection)
btn_stop.pack(side=LEFT, padx=10, pady=10)

btn_snapshot = ttk.Button(frame_controls, text="Take Snapshot", command=take_snapshot)
btn_snapshot.pack(side=LEFT, padx=10, pady=10)

btn_settings = ttk.Button(frame_controls, text="Settings", command=open_settings)
btn_settings.pack(side=LEFT, padx=10, pady=10)

btn_detect_photo = Button(root, text="Detect from Photo", command=detect_from_photo)
btn_detect_photo.pack(pady=10)

btn_detect_video = Button(root, text="Detect from Video", command=detect_from_video)
btn_detect_video.pack(pady=10)

btn_encrypt = ttk.Button(frame_controls, text="Encrypt Data", command=encrypt_data)
btn_encrypt.pack(side=LEFT, padx=10, pady=10)

btn_decrypt = ttk.Button(frame_controls, text="Decrypt Data", command=decrypt_data)
btn_decrypt.pack(side=LEFT, padx=10, pady=10)

btn_view_log = ttk.Button(frame_controls, text="View Log", command=view_log)
btn_view_log.pack(side=LEFT, padx=10, pady=10)

btn_exit = ttk.Button(frame_controls, text="Exit", command=root.quit)
btn_exit.pack(side=LEFT, padx=10, pady=10)

lbl_info = ttk.Label(root, text="Press 'ESC' to exit the video display.")
lbl_info.pack(pady=5)

status_var = StringVar()
status_var.set("Ready")
status_label = ttk.Label(root, textvariable=status_var, relief=SUNKEN, anchor=W)
status_label.pack(fill=X, side=BOTTOM, ipady=2)


def on_esc(event):
    stop_detection()
    root.quit()


root.bind('<Escape>', on_esc)

# Start the frame update loop
root.after(10, update_frame)

# Start the voice command listener in a separate thread
voice_thread = threading.Thread(target=voice_command_listener)
voice_thread.daemon = True
voice_thread.start()

root.mainloop()
