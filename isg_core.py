import os
import cv2
import numpy as np
import math

def file_to_binary(file_name):
    with open(file_name, "rb") as f:
        data = f.read()

    # Guardamos nombre y extensión en el header (simple)
    original_name = os.path.basename(file_name).encode('utf-8')
    name_length = len(original_name).to_bytes(4, "big")
    
    size_header = len(data).to_bytes(8, "big")
    
    # Header: tamaño_nombre + nombre + tamaño_datos
    header = name_length + original_name + size_header
    full_data = header + data

    binary_string = "".join(f"{byte:08b}" for byte in full_data)
    return binary_string, os.path.basename(file_name)


def binary_to_video(bin_string, output="video.mp4", width=1920, height=1080, pixel_size=4, fps=24, progress_callback=None):
    num_pixels = len(bin_string)
    pixels_per_image = (width // pixel_size) * (height // pixel_size)
    num_images = math.ceil(num_pixels / pixels_per_image)

    frames = []

    for i in range(num_images):
        if progress_callback:
            progress = int((i / num_images) * 80)
            progress_callback(progress)

        start_index = i * pixels_per_image
        binary_digits = bin_string[start_index:start_index + pixels_per_image]

        img = np.full((height, width, 3), 255, dtype=np.uint8)

        index = 0
        for y in range(0, height, pixel_size):
            for x in range(0, width, pixel_size):
                if index < len(binary_digits):
                    color = 0 if binary_digits[index] == "1" else 255
                    cv2.rectangle(img, (x, y), (x + pixel_size, y + pixel_size), (color, color, color), -1)
                index += 1

        frames.append(img)

    if progress_callback:
        progress_callback(90)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output, fourcc, fps, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()

    if progress_callback:
        progress_callback(100)

    return os.path.abspath(output)


def video_to_frames(video_path, progress_callback=None):
    cap = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        count += 1
        if progress_callback and total_frames > 0:
            progress = int((count / total_frames) * 50)
            progress_callback(progress)
    cap.release()
    return frames


def process_images(frames, progress_callback=None):
    threshold = 128
    binary_digits = ''
    total = len(frames)
    
    for i, frame in enumerate(frames):
        gray_frame = np.mean(frame, axis=2).astype(np.uint8)
        pixel_size = 4

        for y in range(0, gray_frame.shape[0], pixel_size):
            for x in range(0, gray_frame.shape[1], pixel_size):
                pixel = gray_frame[y:y+pixel_size, x:x+pixel_size]
                binary_digits += '1' if pixel.mean() < threshold else '0'

        if progress_callback:
            progress = 50 + int((i + 1) / total * 40)
            progress_callback(progress)

    return binary_digits


def binaryToFile(binary_string, output_dir="."):
    binary_data = bytes(
        int(binary_string[i:i+8], 2)
        for i in range(0, len(binary_string) - 7, 8)
    )

    # Leer header
    name_len = int.from_bytes(binary_data[:4], "big")
    original_name = binary_data[4:4 + name_len].decode('utf-8')
    data_start = 4 + name_len + 8  # después de nombre + size
    file_size = int.from_bytes(binary_data[4 + name_len:4 + name_len + 8], "big")
    
    file_data = binary_data[data_start:data_start + file_size]

    output_path = os.path.join(output_dir, original_name)
    
    with open(output_path, "wb") as f:
        f.write(file_data)

    return os.path.abspath(output_path)