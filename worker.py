from PySide6.QtCore import QThread, Signal
import isg_core
import os


class ConvertWorker(QThread):
    finished = Signal(str)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, file_path, output_dir):
        super().__init__()
        self.file_path = file_path
        self.output_dir = output_dir

    def run(self):
        try:
            def progress_callback(p):
                self.progress.emit(p)

            data, original_name = isg_core.file_to_binary(self.file_path)
            self.progress.emit(15)

            base_name = os.path.splitext(original_name)[0]
            output_video = os.path.join(self.output_dir, f"{base_name}.mp4")

            output = isg_core.binary_to_video(
                data, 
                output=output_video,
                progress_callback=progress_callback
            )
            self.finished.emit(output)
        except Exception as e:
            self.error.emit(str(e))


class RecoverWorker(QThread):
    finished = Signal(str)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, file_path, output_dir):
        super().__init__()
        self.file_path = file_path
        self.output_dir = output_dir

    def run(self):
        try:
            def progress_callback(p):
                self.progress.emit(p)

            frames = isg_core.video_to_frames(self.file_path, progress_callback=progress_callback)
            self.progress.emit(60)

            bits = isg_core.process_images(frames, progress_callback=progress_callback)
            self.progress.emit(85)

            # Recuperar con nombre original en la carpeta elegida
            output = isg_core.binaryToFile(bits, self.output_dir)
            self.progress.emit(100)
            self.finished.emit(output)
        except Exception as e:
            self.error.emit(str(e))