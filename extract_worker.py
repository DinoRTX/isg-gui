from PySide6.QtCore import QThread, Signal
import isg_core


class ExtractWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, video):
        super().__init__()
        self.video = video

    def run(self):
        try:
            frames = isg_core.video_to_frames(self.video)
            output = isg_core.binary_to_file(frames)
            self.finished.emit(output)

        except Exception as e:
            self.error.emit(str(e))