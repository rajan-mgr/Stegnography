🕵️ Steganography Tool

A Python-based steganography tool that allows users to hide and retrieve secret messages in video, image, and audio files. The tool supports a GUI built with Tkinter for ease of use.

🚀 Features

🔹 Video Steganography

Embed secret messages into AVI video files using Least Significant Bit (LSB) manipulation.

Automatically converts unsupported video formats to AVI.

Extract hidden messages from modified video files.

🔹 Image Steganography

Hide messages inside image pixels using LSB encoding.

Works with PNG, JPG, and BMP formats.

Extract messages from encoded images.

🔹 Audio Steganography

Hide messages inside WAV files.

Uses LSB to encode secret messages into audio samples.

Extracts messages from modified audio files.

🔹 Graphical User Interface (GUI)

Built with Tkinter for easy interaction.

Supports file selection, encoding, and decoding operations.

🛠️ Installation

1️⃣ Prerequisites

Make sure you have Python 3.8+ installed.

2️⃣ Install Dependencies

pip install opencv-python numpy pillow pydub moviepy tkinter

For Windows users, install ffmpeg for video processing:

choco install ffmpeg

For Linux/macOS users:

sudo apt install ffmpeg

4️⃣ Run the Application

python main.py

📌 Usage

Open the Steganography Tool.

Select a Video, Image, or Audio file.

Choose to Encode or Decode a message.

Save and retrieve hidden messages securely.

📸 Screenshots

Encoding Message in an Image:



Decoding Message from a Video:



🔐 Security Considerations

This tool does not encrypt the hidden messages. For added security, encrypt your messages before encoding.

Large messages may impact file quality. Use small messages for best results.

🤝 Contributing

Feel free to submit issues or pull requests to improve the tool! 🎯
