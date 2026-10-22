import os
import tempfile
from pathlib import Path


INPUT = Path("vid.mp4")
OUTPUT = Path("vid_compressed.mp4")


def compress():
	if not INPUT.is_file():
		raise FileNotFoundError(f"Put vid.mp4 in this folder: {Path.cwd()}")
	try:
		import cv2
	except ImportError as error:
		raise RuntimeError("Install OpenCV with: pip install opencv-python") from error

	target_bytes = INPUT.stat().st_size // 2
	capture = cv2.VideoCapture(str(INPUT))
	if not capture.isOpened():
		capture.release()
		raise RuntimeError("OpenCV could not open the input video.")

	width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
	fps = capture.get(cv2.CAP_PROP_FPS)
	if width <= 0 or height <= 0 or fps <= 0:
		capture.release()
		raise RuntimeError("Unable to read the video's dimensions or frame rate.")

	with tempfile.TemporaryDirectory() as temp:
		temp = Path(temp)
		trial = temp / "compressed.mp4"
		scale = 1.0

		for _ in range(10):
			out_width = max(2, int(width * scale) // 2 * 2)
			out_height = max(2, int(height * scale) // 2 * 2)
			writer = cv2.VideoWriter(
				str(trial), cv2.VideoWriter_fourcc(*"mp4v"), fps,
				(out_width, out_height),
			)
			if not writer.isOpened():
				capture.release()
				writer.release()
				raise RuntimeError("OpenCV could not create an MP4 video writer.")

			capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
			try:
				while True:
					ok, frame = capture.read()
					if not ok:
						break
					if (out_width, out_height) != (width, height):
						frame = cv2.resize(frame, (out_width, out_height), interpolation=cv2.INTER_AREA)
					writer.write(frame)
			finally:
				writer.release()

			size = trial.stat().st_size
			if size <= target_bytes:
				capture.release()
				os.replace(trial, OUTPUT)
				print(f"Created {OUTPUT}: {size:,} bytes (original: {INPUT.stat().st_size:,}). Audio is not preserved.")
				return

			if out_width <= 2 and out_height <= 2:
				break
			scale *= min(0.9, max(0.5, (target_bytes / size) ** 0.5 * 0.9))

		capture.release()
	raise RuntimeError("Could not reach half the original size by reducing video resolution.")


if __name__ == "__main__":
	try:
		compress()
	except (OSError, ValueError, RuntimeError) as error:
		raise SystemExit(f"Compression failed: {error}")
