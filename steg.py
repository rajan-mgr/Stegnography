import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import wave
from PIL import Image
from pydub import AudioSegment
from moviepy.video.io.VideoFileClip import VideoFileClip
import os

# ========================== Video Steganography ==========================

def convert_video_to_avi(input_path, output_path):
    """Convert any video format to AVI using moviepy."""
    try:
        video = VideoFileClip(input_path)
        video.write_videofile(output_path, codec='libxvid')  # Use XVID codec for AVI
        video.close()
        return True
    except Exception as e:
        print(f"Error converting video: {e}")
        return False

def encode_message_in_video(video_path, message, output_path):
    if not video_path.lower().endswith('.avi'):
        temp_avi_path = "temp_video.avi"
        if not convert_video_to_avi(video_path, temp_avi_path):
            raise ValueError("Failed to convert video to AVI format.")
        video_path = temp_avi_path

    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError("Error opening video file")

    message_binary = ''.join([format(ord(char), '08b') for char in message])
    message_binary += '1111111111111110'
    print(f"Binary Message to Encode: {message_binary}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    max_message_size = width * height * 3 * frame_count
    if len(message_binary) > max_message_size:
        raise ValueError(f"Message too large for video. Max size: {max_message_size} bits")

    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    message_idx = 0
    message_len = len(message_binary)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if message_idx < message_len:
            for row in frame:
                for pixel in row:
                    for i in range(3):
                        if message_idx < message_len:
                            pixel[i] = (pixel[i] & 0xFE) | int(message_binary[message_idx])
                            message_idx += 1
                        else:
                            break

        out.write(frame)

    cap.release()
    out.release()
    print("Encoding complete. Message embedded in video.")

    if os.path.exists("temp_video.avi"):
        os.remove("temp_video.avi")

def decode_message_from_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Error opening video file")

    binary_message = ''
    delimiter = '1111111111111110'

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        for row in frame:
            for pixel in row:
                for i in range(3):
                    binary_message += str(pixel[i] & 1)
                    if binary_message[-16:] == delimiter:
                        cap.release()
                        decoded_message = ''.join([chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message) - 16, 8)])
                        print(f"Binary Message Found: {binary_message}")
                        print("Decoding complete. Message found:", decoded_message)
                        return decoded_message

    cap.release()
    raise ValueError("No hidden message found or decoding failed.")

# ========================== Image Steganography ==========================

def encode_message_in_image(image_path, message, output_path):
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    message_binary = ''.join([format(ord(char), '08b') for char in message])
    message_binary += '1111111111111110'
    print(f"Binary Message to Encode: {message_binary}")

    image_array = np.array(image)
    message_idx = 0
    message_len = len(message_binary)

    for row in image_array:
        for pixel in row:
            for i in range(3):
                if message_idx < message_len:
                    pixel[i] = (pixel[i] & 0xFE) | int(message_binary[message_idx])
                    message_idx += 1
                else:
                    break

    encoded_image = Image.fromarray(image_array)
    encoded_image.save(output_path)
    print("Encoding complete. Message embedded in image.")

def decode_message_from_image(image_path):
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    image_array = np.array(image)
    binary_message = ''
    delimiter = '1111111111111110'

    for row in image_array:
        for pixel in row:
            for i in range(3):
                binary_message += str(pixel[i] & 1)
                if binary_message[-16:] == delimiter:
                    decoded_message = ''.join([chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message) - 16, 8)])
                    print(f"Binary Message Found: {binary_message}")
                    print("Decoding complete. Message found:", decoded_message)
                    return decoded_message

    raise ValueError("No hidden message found or decoding failed.")

# ========================== Audio Steganography ==========================

def encode_message_in_audio(audio_path, message, output_path):
    try:
        audio = AudioSegment.from_file(audio_path)
    except Exception as e:
        raise ValueError(f"Error loading audio file: {e}")

    wav_path = "temp.wav"
    audio.export(wav_path, format="wav")

    try:
        with wave.open(wav_path, mode='rb') as audio:
            frames = bytearray(list(audio.readframes(audio.getnframes())))
    except Exception as e:
        raise ValueError(f"Error reading WAV file: {e}")

    message_binary = ''.join([format(ord(char), '08b') for char in message])
    message_binary += '1111111111111110'
    print(f"Binary Message to Encode: {message_binary}")

    for i in range(len(message_binary)):
        frames[i] = (frames[i] & 0xFE) | int(message_binary[i])

    with wave.open(output_path, 'wb') as output_audio:
        output_audio.setparams(audio.getparams())
        output_audio.writeframes(frames)

    print("Encoding complete. Message embedded in audio.")

    if os.path.exists("temp.wav"):
        os.remove("temp.wav")

def decode_message_from_audio(audio_path):
    audio = wave.open(audio_path, mode='rb')
    frames = bytearray(list(audio.readframes(audio.getnframes())))

    binary_message = ''
    delimiter = '1111111111111110'

    for frame in frames:
        binary_message += str(frame & 1)
        if binary_message[-16:] == delimiter:
            decoded_message = ''.join([chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message) - 16, 8)])
            print(f"Binary Message Found: {binary_message}")
            print("Decoding complete. Message found:", decoded_message)
            return decoded_message

    raise ValueError("No hidden message found or decoding failed.")

# ========================== Enhanced GUI ==========================

def main_gui():
    root = tk.Tk()
    root.title("Steganography Tool")
    root.geometry("600x650")
    root.configure(bg="#2E2E2E")

    style = {
        "bg": "#2E2E2E",
        "fg": "white",
        "font_title": ("Helvetica", 18, "bold"),
        "font_section": ("Helvetica", 14, "bold"),
        "font_button": ("Helvetica", 12),
        "button_bg": "#4CAF50",
        "button_active": "#45a049",
        "section_bg": "#3E3E3E",
        "text_bg": "#505050",
        "text_fg": "white"
    }

    header_frame = tk.Frame(root, bg=style['bg'])
    header_frame.pack(pady=20)
    tk.Label(header_frame, 
             text="🕵️ Steganography Tool", 
             font=style['font_title'],
             bg=style['bg'],
             fg=style['fg']).pack()

    def create_section(parent, title):
        frame = tk.LabelFrame(parent, text=title, 
                            font=style['font_section'],
                            bg=style['section_bg'],
                            fg=style['fg'],
                            padx=10,
                            pady=10)
        frame.pack(pady=15, padx=20, fill="x")
        return frame

    video_frame = create_section(root, "🎥 Video Steganography")
    tk.Button(video_frame, text="Encode Message", 
             command=lambda: open_encode_gui("video"),
             font=style['font_button'],
             bg=style['button_bg'],
             activebackground=style['button_active'],
             fg="white",
             padx=15,
             pady=5).pack(side=tk.LEFT, expand=True)
    tk.Button(video_frame, text="Decode Message", 
             command=lambda: open_decode_gui("video"),
             font=style['font_button'],
             bg="#2196F3",
             activebackground="#1976D2",
             fg="white",
             padx=15,
             pady=5).pack(side=tk.RIGHT, expand=True)

    image_frame = create_section(root, "🖼️ Image Steganography")
    tk.Button(image_frame, text="Encode Message", 
             command=lambda: open_encode_gui("image"),
             font=style['font_button'],
             bg=style['button_bg'],
             activebackground=style['button_active'],
             fg="white",
             padx=15,
             pady=5).pack(side=tk.LEFT, expand=True)
    tk.Button(image_frame, text="Decode Message", 
             command=lambda: open_decode_gui("image"),
             font=style['font_button'],
             bg="#2196F3",
             activebackground="#1976D2",
             fg="white",
             padx=15,
             pady=5).pack(side=tk.RIGHT, expand=True)

    audio_frame = create_section(root, "🎵 Audio Steganography")
    tk.Button(audio_frame, text="Encode Message", 
             command=lambda: open_encode_gui("audio"),
             font=style['font_button'],
             bg=style['button_bg'],
             activebackground=style['button_active'],
             fg="white",
             padx=15,
             pady=5).pack(side=tk.LEFT, expand=True)
    tk.Button(audio_frame, text="Decode Message", 
             command=lambda: open_decode_gui("audio"),
             font=style['font_button'],
             bg="#2196F3",
             activebackground="#1976D2",
             fg="white",
             padx=15,
             pady=5).pack(side=tk.RIGHT, expand=True)

    tk.Label(root, text="Developed by [Rajan Magar]", 
            bg=style['bg'],
            fg="gray",
            font=("Helvetica", 10)).pack(side=tk.BOTTOM, pady=10)

    root.mainloop()

def open_encode_gui(media_type):
    def encode_message():
        file_path = filedialog.askopenfilename(title=f"Select {media_type.capitalize()} File")
        if not file_path:
            return

        output_path = filedialog.asksaveasfilename(defaultextension=f".{media_type}", filetypes=[(f"{media_type.upper()} files", f"*.{media_type}")])
        if not output_path:
            return

        message = message_entry.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Message cannot be empty!")
            return

        try:
            if media_type == "video":
                encode_message_in_video(file_path, message, output_path)
            elif media_type == "image":
                encode_message_in_image(file_path, message, output_path)
            elif media_type == "audio":
                encode_message_in_audio(file_path, message, output_path)
            messagebox.showinfo("Success", f"Message encoded successfully and saved to {output_path}")
            encode_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    style = {
        "bg": "#3E3E3E",
        "fg": "white",
        "font": ("Helvetica", 12),
        "entry_bg": "#505050",
        "button_bg": "#4CAF50",
        "button_active": "#45a049"
    }

    encode_window = tk.Toplevel()
    encode_window.title(f"Encode Message in {media_type.capitalize()}")
    encode_window.configure(bg=style['bg'])
    encode_window.geometry("500x300")

    tk.Label(encode_window, 
            text=f"Enter Message to Encode in {media_type.capitalize()}:",
            font=style['font'],
            bg=style['bg'],
            fg=style['fg']).pack(pady=10)

    message_entry = tk.Text(encode_window, 
                           height=8,
                           width=50,
                           bg=style['entry_bg'],
                           fg=style['fg'],
                           insertbackground="white")
    message_entry.pack(pady=5, padx=20)

    button_frame = tk.Frame(encode_window, bg=style['bg'])
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Encode", 
             command=encode_message,
             font=style['font'],
             bg=style['button_bg'],
             activebackground=style['button_active'],
             fg="white",
             padx=15).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="Cancel", 
             command=encode_window.destroy,
             font=style['font'],
             bg="#F44336",
             activebackground="#d32f2f",
             fg="white",
             padx=15).pack(side=tk.RIGHT, padx=10)

def open_decode_gui(media_type):
    def decode_message():
        file_path = filedialog.askopenfilename(title=f"Select Encoded {media_type.capitalize()} File")
        if not file_path:
            return

        try:
            if media_type == "video":
                message = decode_message_from_video(file_path)
            elif media_type == "image":
                message = decode_message_from_image(file_path)
            elif media_type == "audio":
                message = decode_message_from_audio(file_path)
            
            if message:
                result_text.set(f"Decoded Message:\n{message}")
            else:
                result_text.set("No hidden message found or decoding failed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    style = {
        "bg": "#3E3E3E",
        "fg": "white",
        "font": ("Helvetica", 12),
        "button_bg": "#2196F3",
        "button_active": "#1976D2"
    }

    decode_window = tk.Toplevel()
    decode_window.title(f"Decode Message from {media_type.capitalize()}")
    decode_window.configure(bg=style['bg'])
    decode_window.geometry("500x200")

    result_text = tk.StringVar()
    result_label = tk.Label(decode_window, 
                           textvariable=result_text,
                           wraplength=450,
                           justify="left",
                           bg=style['bg'],
                           fg=style['fg'],
                           font=style['font'])
    result_label.pack(pady=20, padx=20)

    tk.Button(decode_window, 
             text=f"Select {media_type.capitalize()} to Decode",
             command=decode_message,
             font=style['font'],
             bg=style['button_bg'],
             activebackground=style['button_active'],
             fg="white").pack(pady=10)

if __name__ == "__main__":
    main_gui()
