from ultralytics import YOLO
from PIL import Image, ImageDraw
import numpy as np

class LeafDetector:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def detect_leaf(self, pil_image: Image.Image):
        """
        Returns:
            cropped_leaf (PIL.Image or None)
            annotated_image (PIL.Image) — original image with YOLO bounding boxes drawn
        """
        results = self.model.predict(pil_image, conf=0.10)

        if len(results) == 0 or len(results[0].boxes) == 0:
            # Return original image and no crop
            return None, pil_image

        # Convert to editable copy
        annotated = pil_image.copy()
        draw = ImageDraw.Draw(annotated)

        # Take the strongest detection
        box = results[0].boxes.xyxy[0].tolist()  # [x1, y1, x2, y2]
        x1, y1, x2, y2 = map(int, box)

        # Draw box
        draw.rectangle([x1, y1, x2, y2], outline="red", width=6)

        # Crop region
        cropped_leaf = pil_image.crop((x1, y1, x2, y2))

        return cropped_leaf, annotated
