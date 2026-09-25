import os
from pathlib import Path

from PIL import Image
from ultralytics import YOLO


class InferencePipeline:

    def __init__(self, device="cpu"):

        self.device = device

        # ==================================================
        # MODEL PATHS
        # ==================================================

        app_dir = Path(__file__).resolve().parents[2]

        self.model_paths = {

            "Rice":
                str(app_dir / "runs" / "detect" / "runs" / "rice" / "rice_yolo11n_improved" / "weights" / "best.pt"),

            "Corn":
                str(app_dir / "best.pt"),

            # ARECANUT YOLO11 DETECTION
            "Arecanut":
                str(app_dir / "models" / "arecanut_detection" / "best.pt")
        }

        # ==================================================
        # ARECANUT CLASSIFICATION MODEL
        # ==================================================

        self.classification_model_paths = {

            "Arecanut":
                str(app_dir / "models" / "arecanut_classification" / "best.pt")
        }

        # ==================================================
        # CLASS NAMES
        # ==================================================

        self.class_names = {

            "Rice": {
                0: "Bacterial Leaf Blight",
                1: "Brown Spot",
                2: "Healthy Leaf",
                3: "Leaf Blast",
                4: "Leaf Scald",
                5: "Narrow Brown Leaf Spot",
                6: "Neck Blast",
                7: "Rice Hispa"
            },

            "Corn": {
                0: "Brown Spot",
                1: "Corn Rust",
                2: "Corn Smut",
                3: "Downy Mildew",
                4: "Grey Leaf Spot",
                5: "Healthy",
                6: "Leaf Blight"
            },

            "Arecanut": {
                0: "Bud Borer",
                1: "Healthy Foot",
                2: "Healthy Leaf",
                3: "Healthy Nut",
                4: "Healthy Trunk",
                5: "Mahali Koleroga",
                6: "Stem Bleeding",
                7: "Stem Cracking",
                8: "Yellow Leaf Disease"
            }
        }

        # ==================================================
        # LOAD DETECTION MODELS
        # ==================================================

        self.models = {}

        for crop, path in self.model_paths.items():

            print(f"\nChecking {crop} model:")
            print(path)

            if not os.path.isfile(path):

                print(f"❌ FILE NOT FOUND: {path}")
                continue

            try:

                self.models[crop] = YOLO(path)

                print(f"✅ {crop} model loaded")

            except Exception as e:

                print(f"❌ {crop} model loading failed:")
                print(e)

        # ==================================================
        # LOAD CLASSIFICATION MODELS
        # ==================================================

        self.classification_models = {}

        for crop, path in self.classification_model_paths.items():

            print(f"\nChecking {crop} classification model:")
            print(path)

            if not os.path.isfile(path):

                print(f"❌ FILE NOT FOUND: {path}")
                continue

            try:

                self.classification_models[crop] = YOLO(path)

                print(
                    f"✅ {crop} classification model loaded"
                )

            except Exception as e:

                print(
                    f"❌ {crop} classification model failed:"
                )

                print(e)

        # ==================================================
        # FINAL STATUS
        # ==================================================

        print("\n" + "=" * 60)
        print("MODEL STATUS")
        print("=" * 60)

        print(
            "Detection models:",
            list(self.models.keys())
        )

        print(
            "Classification models:",
            list(self.classification_models.keys())
        )

        print("=" * 60)

    # ======================================================
    # ARECANUT CLASSIFICATION
    # ======================================================

    def classify_arecanut(self, image):

        if "Arecanut" not in self.classification_models:

            return {
                "class_name": "Unknown",
                "confidence": 0.0
            }

        model = self.classification_models["Arecanut"]

        try:

            results = model.predict(
                image,
                imgsz=224,
                verbose=False,
                device=self.device
            )

        except Exception as e:

            return {
                "class_name": "Unknown",
                "confidence": 0.0,
                "error": str(e)
            }

        if not results:
            return {
                "class_name": "Unknown",
                "confidence": 0.0
            }

        result = results[0]

        if result.probs is None:

            return {
                "class_name": "Unknown",
                "confidence": 0.0
            }

        class_id = int(result.probs.top1)

        confidence = float(result.probs.top1conf)

        class_name = result.names.get(
            class_id,
            "Unknown"
        )

        return {
            "class_name": class_name,
            "confidence": confidence
        }

    # ======================================================
    # MAIN PREDICTION
    # ======================================================

    def predict(
        self,
        image: Image.Image,
        crop_type="Rice"
    ):

        # ==================================================
        # CHECK MODEL
        # ==================================================

        if crop_type not in self.models:

            return {
                "error":
                    f"{crop_type} detection model is not loaded.\n\n"
                    f"Check the best.pt path in inference.py."
            }

        model = self.models[crop_type]

        # ==================================================
        # ARECANUT CLASSIFICATION
        # ==================================================

        classification_result = None

        if crop_type == "Arecanut":

            classification_result = (
                self.classify_arecanut(image)
            )

        # ==================================================
        # YOLO DETECTION
        # ==================================================

        try:

            results = model.predict(
                image,
                conf=0.25,
                imgsz=640,
                verbose=False,
                device=self.device
            )

        except Exception as e:

            return {
                "error":
                    f"Prediction failed: {str(e)}"
            }

        # ==================================================
        # NO DETECTION
        # ==================================================

        if (
            len(results) == 0
            or results[0].boxes is None
            or len(results[0].boxes) == 0
        ):

            if (
                crop_type == "Arecanut"
                and classification_result
                and classification_result["class_name"] != "Unknown"
            ):

                disease = classification_result["class_name"]
                confidence = classification_result["confidence"]

                plant_status = (
                    "Healthy"
                    if "healthy" in disease.lower()
                    else "Diseased"
                )

                return {

                    "species": "Arecanut",

                    "species_conf": confidence,

                    "disease": disease,

                    "disease_conf": confidence,

                    "classification_result": disease,

                    "classification_conf": confidence,

                    "detection_result": "No bounding box",

                    "detection_conf": 0.0,

                    "mc_uncertainty": 0.0,

                    "tta_uncertainty": 0.0,

                    "uncertainty_fused": 0.0,

                    "model_used":
                        "Arecanut Classification Model",

                    "cropped_image": image,

                    "boxed_image": image,

                    "heatmap": None,

                    "plant_status": plant_status
                }

            return {
                "error":
                    f"No {crop_type} object detected. "
                    f"Please use a clear image."
            }

        # ==================================================
        # BEST DETECTION
        # ==================================================

        result = results[0]

        best_index = int(
            result.boxes.conf.argmax()
        )

        box = result.boxes[best_index]

        detection_class_id = int(
            box.cls.item()
        )

        detection_confidence = float(
            box.conf.item()
        )

        detection_disease = self.class_names[
            crop_type
        ].get(
            detection_class_id,
            "Unknown"
        )

        # ==================================================
        # BOUNDING BOX
        # ==================================================

        x1, y1, x2, y2 = (
            box.xyxy[0]
            .cpu()
            .numpy()
            .astype(int)
        )

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(image.width, x2)
        y2 = min(image.height, y2)

        cropped_image = image.crop(
            (x1, y1, x2, y2)
        )

        # ==================================================
        # ANNOTATED IMAGE
        # ==================================================

        annotated_image = result.plot()

        annotated_image = Image.fromarray(
            annotated_image[..., ::-1]
        )

        # ==================================================
        # FINAL DISEASE
        # ==================================================

        if crop_type == "Arecanut":

            classification_name = (
                classification_result["class_name"]
            )

            classification_confidence = float(
                classification_result["confidence"]
            )

            if classification_name != "Unknown":

                disease = classification_name
                disease_conf = classification_confidence

            else:

                disease = detection_disease
                disease_conf = detection_confidence

        else:

            disease = detection_disease
            disease_conf = detection_confidence

            classification_name = disease
            classification_confidence = (
                detection_confidence
            )

        # ==================================================
        # STATUS
        # ==================================================

        if "healthy" in disease.lower():

            plant_status = "Healthy"

        else:

            plant_status = "Diseased"

        # ==================================================
        # RETURN
        # ==================================================

        return {

            "species": crop_type,

            "species_conf":
                detection_confidence,

            "disease": disease,

            "disease_conf":
                disease_conf,

            "classification_result":
                classification_name,

            "classification_conf":
                classification_confidence,

            "detection_result":
                detection_disease,

            "detection_conf":
                detection_confidence,

            "mc_uncertainty": 0.0,

            "tta_uncertainty": 0.0,

            "uncertainty_fused": 0.0,

            "model_used":
                f"YOLO11n + Classification Model - {crop_type}",

            "cropped_image":
                cropped_image,

            "boxed_image":
                annotated_image,

            "heatmap": None,

            "plant_status":
                plant_status
        }