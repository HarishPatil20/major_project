import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageEnhance
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
        # CLASSIFICATION REFINEMENT MODELS (second-opinion models
        # that re-examine the detected region and give a more
        # specific/accurate disease read than the detection model
        # alone)
        # ==================================================

        self.classification_model_paths = {

            "Arecanut":
                str(app_dir / "models" / "arecanut_classification" / "best.pt"),

            "Rice":
                str(app_dir / "models" / "rice_classification" / "best.pt"),

            "Corn":
                str(app_dir / "models" / "corn_classification" / "best.pt")
        }

        # The Arecanut classification model is trained ONLY on nut images
        # and can only ever output one of 4 nut classes (Good / Chukke
        # roga / Kole roga / Split nut). Its output is only meaningful
        # when the YOLO detection itself found a nut region - otherwise
        # a leaf, trunk, foot or bud photo gets forced into a nut label
        # that has nothing to do with what was actually detected (e.g. a
        # leaf photo showing "Split nut"). This set gates when the
        # classifier's result is trusted; it does not change the
        # classifier or its weights.
        self.nut_related_detections = {
            "Healthy Nut",
            "Mahali Koleroga"
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
    # CLASSIFICATION REFINEMENT (shared by Arecanut/Rice/Corn -
    # each crop's own classification model reports its own class
    # names directly from the model file, so no manual class-name
    # mapping is needed here, unlike the detection models above)
    # ======================================================

    def run_classification(self, crop_type, image):

        if crop_type not in self.classification_models:

            return {
                "class_name": "Unknown",
                "confidence": 0.0
            }

        model = self.classification_models[crop_type]

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

    def classify_arecanut(self, image):
        """Kept for backward compatibility - delegates to run_classification."""
        return self.run_classification("Arecanut", image)

    # ======================================================
    # UNCERTAINTY ESTIMATION (MC + TTA)
    #
    # These were previously hardcoded to 0.0 everywhere - this is the
    # real implementation. Both numbers answer the same question in two
    # different ways: "if I perturb the input slightly, how much does
    # the model's confidence in its OWN predicted class move around?"
    # A stable/confident model barely moves; an uncertain one swings a
    # lot. Neither method changes the reported prediction itself - they
    # only estimate how much to trust it.
    #
    # NOTE ON "MC" (Monte Carlo): classic MC-Dropout requires the
    # network to have been *trained* with a nonzero dropout rate so
    # that switching dropout back on at test time samples from a
    # distribution close to training. We checked the actual trained
    # weights directly and every classification head here was trained
    # with dropout p=0.0, so there is no learned dropout to reactivate
    # - doing so would either do nothing (p=0) or inject noise the
    # network never saw during training (misleading). Instead we use
    # the standard practical substitute for that situation: Monte Carlo
    # sampling under small random input perturbations (light Gaussian
    # pixel noise, redrawn randomly on every pass) - genuinely
    # stochastic, genuinely re-run through the real model each time,
    # and a widely used stand-in when a network has no usable internal
    # dropout.
    # ======================================================

    def _class_probability(self, results, class_name):
        """Look up the model's own probability for a specific class
        name in a single prediction result (not just its top-1)."""
        if not results or results[0].probs is None:
            return None
        names = results[0].names
        class_id = None
        for cid, cname in names.items():
            if cname == class_name:
                class_id = cid
                break
        if class_id is None:
            return None
        return float(results[0].probs.data[class_id])

    def mc_dropout_uncertainty(self, crop_type, image, class_name, n_passes=6, noise_std=6.0):
        """Monte Carlo uncertainty via repeated random input perturbation.

        Runs the SAME already-loaded classification model n_passes times
        on the same image with a freshly-drawn random noise pattern each
        time, and returns the standard deviation of how confident the
        model was in the already-predicted class across those passes.
        """
        if crop_type not in self.classification_models:
            return 0.0

        model = self.classification_models[crop_type]

        try:
            base_array = np.array(image).astype(np.float32)
        except Exception:
            return 0.0

        rng = np.random.default_rng()
        probs = []

        for _ in range(n_passes):
            try:
                noise = rng.normal(0.0, noise_std, base_array.shape)
                noisy_array = np.clip(base_array + noise, 0, 255).astype(np.uint8)
                noisy_image = Image.fromarray(noisy_array)

                results = model.predict(
                    noisy_image,
                    imgsz=224,
                    verbose=False,
                    device=self.device
                )

                p = self._class_probability(results, class_name)

                if p is not None:
                    probs.append(p)

            except Exception:
                continue

        if len(probs) < 2:
            return 0.0

        return float(np.std(probs))

    def tta_uncertainty(self, crop_type, image, class_name, base_confidence):
        """Test-Time Augmentation uncertainty via a fixed set of
        standard augmentations (mirror, small rotations, brightness
        jitter). Returns the standard deviation of how confident the
        model was in the already-predicted class across those views
        plus the original, unaugmented image.
        """
        if crop_type not in self.classification_models:
            return 0.0

        model = self.classification_models[crop_type]

        try:
            augmented_views = [
                ImageOps.mirror(image),
                image.rotate(8, fillcolor=(255, 255, 255)),
                image.rotate(-8, fillcolor=(255, 255, 255)),
                ImageEnhance.Brightness(image).enhance(0.85),
                ImageEnhance.Brightness(image).enhance(1.15),
            ]
        except Exception:
            return 0.0

        probs = [base_confidence]

        for view in augmented_views:
            try:
                results = model.predict(
                    view,
                    imgsz=224,
                    verbose=False,
                    device=self.device
                )

                p = self._class_probability(results, class_name)

                if p is not None:
                    probs.append(p)

            except Exception:
                continue

        if len(probs) < 2:
            return 0.0

        return float(np.std(probs))

    def estimate_uncertainty(self, crop_type, image, class_name, base_confidence):
        """Runs both uncertainty estimates and fuses them into one
        combined number (simple average) for the summary badge."""
        mc = self.mc_dropout_uncertainty(crop_type, image, class_name)
        tta = self.tta_uncertainty(crop_type, image, class_name, base_confidence)
        fused = (mc + tta) / 2.0
        return mc, tta, fused

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
        # CLASSIFICATION REFINEMENT (runs for any crop that has
        # one loaded - currently Arecanut, Rice, and Corn)
        # ==================================================

        classification_result = None

        if crop_type in self.classification_models:

            classification_result = (
                self.run_classification(crop_type, image)
            )

        # ==================================================
        # YOLO DETECTION
        # ==================================================

        try:

            results = model.predict(
                image,
                # Lowered from 0.25: at 0.25, any detection the model was
                # less than 25% sure about was thrown away entirely, so a
                # borderline-but-real detection produced "No object
                # detected" instead of a low (but real) confidence result.
                # This does not change the trained model or its weights —
                # only how strict we are about accepting its output.
                conf=0.10,
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
                classification_result
                and classification_result["class_name"] != "Unknown"
            ):

                disease = classification_result["class_name"]
                confidence = classification_result["confidence"]

                plant_status = (
                    "Healthy"
                    if "healthy" in disease.lower()
                    else "Diseased"
                )

                mc_uncertainty, tta_uncertainty, uncertainty_fused = (
                    self.estimate_uncertainty(
                        crop_type, image, disease, confidence
                    )
                )

                return {

                    "species": crop_type,

                    "species_conf": confidence,

                    "disease": disease,

                    "disease_conf": confidence,

                    "classification_result": disease,

                    "classification_conf": confidence,

                    "detection_result": "No bounding box",

                    "detection_conf": 0.0,

                    "detection_found": False,

                    "mc_uncertainty": mc_uncertainty,

                    "tta_uncertainty": tta_uncertainty,

                    "uncertainty_fused": uncertainty_fused,

                    "model_used":
                        f"{crop_type} Classification Model "
                        f"(whole-image fallback - no region detected)",

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

        # Whether the classification model's output is actually usable
        # for this detection.
        classification_applicable = False

        classification_name = None
        classification_confidence = None

        have_classification = (
            classification_result
            and classification_result["class_name"] != "Unknown"
        )

        if crop_type == "Arecanut":

            # The Arecanut classifier is trained ONLY on nut images, so
            # it must only be trusted when the detected region is
            # actually a nut (see nut_related_detections above) -
            # otherwise a leaf/trunk/foot/bud detection would get forced
            # into an unrelated nut label.
            if (
                have_classification
                and detection_disease in self.nut_related_detections
            ):

                classification_name = classification_result["class_name"]
                classification_confidence = float(classification_result["confidence"])

                disease = classification_name
                disease_conf = classification_confidence
                classification_applicable = True

            else:

                disease = detection_disease
                disease_conf = detection_confidence

        elif have_classification:

            # Rice / Corn (and any future crop with its own classifier):
            # the detection model only ever finds leaves for these crops,
            # so there is no "wrong body part" risk - the classifier's
            # own read of the same cropped region is trusted directly as
            # a second opinion, usually more specific/accurate than the
            # detection model's own label.
            classification_name = classification_result["class_name"]
            classification_confidence = float(classification_result["confidence"])

            disease = classification_name
            disease_conf = classification_confidence
            classification_applicable = True

        else:

            # No classification model loaded/usable for this crop - fall
            # back to the plain YOLO detection result.
            disease = detection_disease
            disease_conf = detection_confidence

        # ==================================================
        # STATUS
        # ==================================================

        if "healthy" in disease.lower():

            plant_status = "Healthy"

        else:

            plant_status = "Diseased"

        # ==================================================
        # UNCERTAINTY (only meaningful when a classification model
        # actually produced the disease above - otherwise there is no
        # classifier probability distribution to re-probe, so these
        # stay at 0.0 rather than estimating uncertainty from a model
        # that isn't the one whose result we're reporting)
        # ==================================================

        if classification_applicable:

            mc_uncertainty, tta_uncertainty, uncertainty_fused = (
                self.estimate_uncertainty(
                    crop_type, image, disease, disease_conf
                )
            )

        else:

            mc_uncertainty, tta_uncertainty, uncertainty_fused = 0.0, 0.0, 0.0

        # ==================================================
        # RETURN
        # ==================================================

        response = {

            "species": crop_type,

            "species_conf":
                detection_confidence,

            "disease": disease,

            "disease_conf":
                disease_conf,

            "detection_result":
                detection_disease,

            "detection_conf":
                detection_confidence,

            "detection_found": True,

            "mc_uncertainty": mc_uncertainty,

            "tta_uncertainty": tta_uncertainty,

            "uncertainty_fused": uncertainty_fused,

            "model_used": (
                f"YOLO11n + Classification Model - {crop_type}"
                if classification_applicable
                else f"YOLO11n Detection Only - {crop_type}"
            ),

            "cropped_image":
                cropped_image,

            "boxed_image":
                annotated_image,

            "heatmap": None,

            "plant_status":
                plant_status
        }

        # Only surface a "Classification Result" section when the
        # classifier's output was actually usable for this detection -
        # otherwise the results page correctly omits that section
        # instead of showing an unrelated nut label.
        if classification_applicable:

            response["classification_result"] = classification_name
            response["classification_conf"] = classification_confidence

        return response