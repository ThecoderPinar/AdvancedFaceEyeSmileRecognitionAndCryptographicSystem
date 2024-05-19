# 😊 Face Detection Application with OpenCV and Tkinter 🎉

Welcome to the Face Detection Application! This application leverages OpenCV for real-time face, eye, smile, and object detection. It also includes advanced features such as voice commands, encryption, and decryption. Below, you'll find a detailed explanation of the functionalities and features implemented.

## 📦 Features

1. **Real-Time Detection**
   - Detects faces, eyes, smiles, and objects using pre-trained Haar Cascades.
   - Displays detection results on the video stream from the webcam.
   - Calculates and displays the frames per second (FPS).

2. **Snapshot Capture 📸**
   - Take snapshots of the current video frame and save them as JPEG images.

3. **Voice Commands 🎤**
   - Control the application using voice commands to start/stop detection, take snapshots, open settings, encrypt/decrypt data, and exit the application.

4. **Encryption/Decryption 🔒**
   - Encrypt and decrypt data using AES encryption with a generated key.
   - Generate and verify HMAC for data integrity.

5. **Settings Configuration ⚙️**
   - Configure Region of Interest (ROI) for detection via a settings window.

6. **Log Viewing 📜**
   - View detection logs that record face detection events with timestamps and coordinates.

7. **Detect from Photo and Video 📷🎥**
   - Detect faces, eyes, smiles, and objects from static images and video files.

## Purpose and Goals 🎯

### Purpose
The purpose of this project is to develop a robust face detection application using OpenCV and Tkinter, integrated with advanced features such as voice command recognition, data encryption, and photo/video processing.

### Goals
- Implement real-time face, eye, smile, and object detection using Haar cascades.
- Provide an intuitive user interface with Tkinter for easy interaction.
- Enable voice commands for starting/stopping detection, taking snapshots, and other actions.
- Implement AES encryption for secure data storage and transmission.
- Allow users to configure regions of interest (ROIs) for detection.
- Provide options to reduce the size of photos and videos to save storage space.
- Implement logging for tracking detection events.

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- OpenCV
- Tkinter
- PIL (Pillow)
- SpeechRecognition
- Pyttsx3
- Cryptography

Install the required libraries using pip:

```sh
pip install opencv-python-headless tk pillow SpeechRecognition pyttsx3 cryptography
```

## Running the Application 🏃‍♂️

### Clone the Repository 📂

```sh
git clone https://github.com/your-repo/face-detection-app.git
cd face-detection-app
```

### Run the Application ▶️
```sh
python face detection/app.py
```

# 🛠️ Detailed Explanation
## Main Components 🔧
### Haar Cascades 📸
Loaded using OpenCV to detect faces, eyes, smiles, and objects.
```sh
face_cascade = cv2.CascadeClassifier('../Cascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('../Cascades/haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier('../Cascades/haarcascade_smile.xml')
object_cascade = cv2.CascadeClassifier('../Cascades/haarcascade_car.xml')
```

### Camera Setup 🎥
Initializes the webcam for real-time video capture.
```sh
kamera = cv2.VideoCapture(0)
if not kamera.isOpened():
    messagebox.showerror("Error", "Could not open camera.")
    exit()
```
### Detection and Display 👀
Continuously captures frames from the webcam, performs detection, and displays the results.
```sh
def detect_and_display():
    while not stop_thread:
        ret, frame = kamera.read()
        ...
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(20, 30))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            ...
        frame_queue.put(frame)
    kamera.release()
    out.release()
    cv2.destroyAllWindows()
```

### Voice Commands 🎤
Uses the SpeechRecognition library to capture and interpret voice commands.

```sh
def detect_and_display():def voice_command_listener():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    ...
    try:
        command = recognizer.recognize_google(audio).lower()
        ...
        if "start detection" in command:
            start_detection()
        ...
    except sr.UnknownValueError:
        print("Sorry, I did not understand the command.")
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service")
```

### Encryption/Decryption 🔐
Implements AES encryption and decryption using the Cryptography library.

```sh
class CustomEncryption:
    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = self.generate_key()
    ...
    def encrypt(self, data):
        iv = os.urandom(16)
        encryptor = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend()).encryptor()
        cipher_text = encryptor.update(data) + encryptor.finalize()
        return iv + cipher_text
    ...
    def decrypt(self, encrypted_data):
        iv = encrypted_data[:16]
        decryptor = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend()).decryptor()
        decrypted_data = decryptor.update(encrypted_data[16:]) + decryptor.finalize()
        return decrypted_data
```

### GUI with Tkinter 🎨
The application interface is built using Tkinter, with buttons for different functionalities and a video display area.

```sh
root = Tk()
root.title("Face Detection with OpenCV and Tkinter")
root.geometry("900x700")
root.configure(bg='lightblue')
...
lbl_video = Label(root, bg='black')
lbl_video.pack(fill=BOTH, expand=YES, padx=10, pady=10)
...
frame_controls = ttk.Frame(root)
...
btn_start = ttk.Button(frame_controls, text="Start Detection", command=start_detection)
...
btn_exit = ttk.Button(frame_controls, text="Exit", command=root.quit)
...
lbl_info = ttk.Label(root, text="Press 'ESC' to exit the video display.")
lbl_info.pack(pady=5)
```

## Advanced Functionalities 🌟
## Region of Interest (ROI) Configuration 🔍
Allows the user to specify a region of interest for detection.

```sh
def open_settings():
    ...
    lbl_scale_factor = Label(settings_window, text="ROI x1")
    ...
    def save_settings():
        global roi
        x1 = int(scale_factor_entry.get())
        y1 = int(min_neighbors_entry.get())
        x2 = int(min_size_entry.get())
        y2 = int(min_size_entry2.get())
        roi = (x1, y1, x2, y2)
        settings_window.destroy()
        speak("Settings saved")
```

### Snapshot Capture 📸
Saves the current video frame as a JPEG image.

```sh
def take_snapshot():
    if not stop_thread:
        ret, frame = kamera.read()
        ...
        cv2.imwrite(filename, frame)
        messagebox.showinfo("Snapshot", "Snapshot saved successfully!")
        speak("Snapshot saved successfully")
```

### Log Viewing 📜
Displays a log of detection events.

```sh
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
```
## Additional Features to Add to the Project 🚀

### Cybersecurity Features 🔒

- **Data Encryption**: Encrypt data using AES encryption with the Cryptography library and store encrypted data.
- **HMAC Verification**: Use HMAC (Hash-based Message Authentication Code) for data integrity verification.

### Photo and Video Processing Features 📷🎥

- **Photo Size Reduction**: Option to reduce the size of captured photos.
- **Video Size Reduction**: Option to reduce the size of recorded videos.

### Other Features 🎙️

- **Logging**: Write detection events to a log file.
- **Voice Command Recognition**: Use the SpeechRecognition library to detect and process voice commands.

### Frequently Asked Questions (FAQ) ❓

**Question:** How can I start the application?  
**Answer:** To start the application, run the command `python app.py` in your terminal.

**Question:** How can I process photos and videos?  
**Answer:** You can process photos and videos by selecting the Photo/Video option to detect them.

**Question:** How can I use voice commands in the application?  
**Answer:** Use your microphone to detect and process commands. For example, start the detection by saying "Start Detection".

**Question:** How can I configure the region of interest (ROI) for detection?  
**Answer:** Open the settings window and enter the desired coordinates for x1, y1, x2, and y2.

**Question:** Can I view the log of detection events?  
**Answer:** Yes, you can view the log of detection events by selecting the View Log option in the menu.

**Question:** How does the application handle encryption and decryption?  
**Answer:** The application uses AES encryption for secure data storage and transmission. You can encrypt and decrypt data using the Encrypt and Decrypt options.

**Question:** What languages does the application support for voice commands?  
**Answer:** The application currently supports English for voice commands. Support for other languages may be added in future updates.

## Collaboration and Contact Information 🤝📧

### Collaborate
- **Contributions**: Contributions are welcome! Feel free to fork the repository and submit pull requests.
- **Issues**: Found a bug or have a feature request? Open an issue on GitHub.

### Contact
- **Email**: You can reach us at piinartp@gmail.com for any inquiries.
- **LinkedIn**: Connect with us on [LinkedIn](https://www.linkedin.com/in/piinartp) for updates and discussions.

# 🌟 Conclusion
This Face Detection Application is a robust and feature-rich tool for real-time face and object detection, enhanced with voice command functionality and data encryption capabilities. Feel free to explore and modify the code to suit your needs. Enjoy using the application! 🎉

For any issues or contributions, please open an issue or submit a pull request on our GitHub repository.