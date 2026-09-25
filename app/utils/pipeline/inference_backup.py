import numpy as np
import torch
from PIL import Image
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF

from utils.detection.leaf_detector import LeafDetector
from utils.explainability.gradcam_pp import GradCAMPP
from utils.model_utils import clean_label
from utils.species_mapping import (
    DISEASE_MODEL_PATHS,
    DISEASE_LABELS,
)
from utils.load_model.loaders import load_disease_model


class InferencePipeline:

    def __init__(self, device="cpu"):

        self.device = device

        # --------------------------------------------------
        # YOLO LEAF DETECTOR
        # --------------------------------------------------

        YOLO_MODEL_PATH = (
            r"C:\CropProject\app\runs\detect\runs\rice"
            r"\rice_yolo11n_improved\weights\best.pt"
        )

        self.detector = LeafDetector(
            YOLO_MODEL_PATH
        )

        # --------------------------------------------------
        # DISEASE MODEL
        # --------------------------------------------------

        self.disease_models = {}

        # PlantVillage model
        plant_model_path = DISEASE_MODEL_PATHS.get(
            "PlantVillage"
        )

        if plant_model_path:
            self.disease_models["PlantVillage"] = (
                load_disease_model(
                    plant_model_path,
                    device=self.device
                )
            )

        # Rice model
        rice_model_path = DISEASE_MODEL_PATHS.get(
            "Rice"
        )

        if rice_model_path:

            try:

                self.disease_models["Rice"] = (
                    load_disease_model(
                        rice_model_path,
                        device=self.device
                    )
                )

            except Exception:
                pass

        # --------------------------------------------------
        # IMAGE TRANSFORM
        # --------------------------------------------------

        self.tfms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])


    # ======================================================
    # TTA
    # ======================================================

    def tta_transforms(self, img: Image.Image):

        return [
            img,
            TF.hflip(img),
            TF.rotate(img, 10),
            TF.rotate(img, -10),
            TF.adjust_brightness(img, 1.2),
            TF.adjust_contrast(img, 1.2),
        ]


    def preprocess(self, img: Image.Image):

        return (
            self.tfms(img)
            .unsqueeze(0)
            .to(self.device)
        )


    # ======================================================
    # TTA PREDICTION
    # ======================================================

    def tta_predict(self, model, img: Image.Image):

        model.eval()

        preds = []

        for aug in self.tta_transforms(img):

            tensor = self.preprocess(aug)

            with torch.no_grad():

                logits = model(tensor)

                probs = torch.softmax(
                    logits,
                    dim=1
                )

            preds.append(
                probs.cpu().numpy()
            )

        preds = np.array(preds)

        return preds.mean(axis=0)[0]


    # ======================================================
    # TTA UNCERTAINTY
    # ======================================================

    def tta_uncertainty(
        self,
        model,
        img: Image.Image
    ):

        model.eval()

        preds = []

        for aug in self.tta_transforms(img):

            tensor = self.preprocess(aug)

            with torch.no_grad():

                logits = model(tensor)

                probs = torch.softmax(
                    logits,
                    dim=1
                )

            preds.append(
                probs.cpu().numpy()
            )

        preds = np.array(preds)[:, 0, :]

        return float(
            preds.std(axis=0).mean()
        )


    # ======================================================
    # MC DROPOUT
    # ======================================================

    def mc_dropout_predict(
        self,
        model,
        img_tensor,
        passes=10
    ):

        model.train()

        preds = []

        with torch.no_grad():

            for _ in range(passes):

                logits = model(img_tensor)

                probs = torch.softmax(
                    logits,
                    dim=1
                )

                preds.append(probs)

        preds = torch.stack(preds)

        mean_pred = preds.mean(dim=0)

        entropy = -(
            mean_pred
            * torch.log(mean_pred + 1e-8)
        ).sum().item()

        model.eval()

        return (
            mean_pred.squeeze(),
            entropy
        )


    # ======================================================
    # MAIN PREDICTION
    # ======================================================

    def predict(
        self,
        image: Image.Image
    ) -> dict:

        # --------------------------------------------------
        # STEP 1: YOLO LEAF DETECTION
        # --------------------------------------------------

        cropped_image, boxed_image = (
            self.detector.detect_leaf(image)
        )

        # No leaf detected
        if cropped_image is None:

            return {
                "error":
                "No rice leaf was detected. "
                "Please upload a clear rice leaf image."
            }

        # --------------------------------------------------
        # STEP 2: PREPROCESS
        # --------------------------------------------------

        img_tensor = self.preprocess(
            cropped_image
        )

        # --------------------------------------------------
        # STEP 3: RICE MODEL
        # --------------------------------------------------

        disease_key = "Rice"

        if disease_key not in self.disease_models:

            return {
                "error":
                "Rice disease model is not available. "
                "Please add the trained Rice model file."
            }

        model = self.disease_models[
            disease_key
        ]

        # --------------------------------------------------
        # STEP 4: MC DROPOUT
        # --------------------------------------------------

        (
            mc_mean_pred,
            mc_uncertainty
        ) = self.mc_dropout_predict(
            model,
            img_tensor
        )

        disease_idx = int(
            mc_mean_pred.argmax()
        )

        disease_conf_mc = float(
            mc_mean_pred[disease_idx]
        )

        # --------------------------------------------------
        # STEP 5: TTA
        # --------------------------------------------------

        tta_mean_pred = self.tta_predict(
            model,
            cropped_image
        )

        tta_uncertainty = (
            self.tta_uncertainty(
                model,
                cropped_image
            )
        )

        disease_conf_tta = float(
            tta_mean_pred[disease_idx]
        )

        # --------------------------------------------------
        # STEP 6: FUSED CONFIDENCE
        # --------------------------------------------------

        fused_conf = (
            disease_conf_mc
            + disease_conf_tta
        ) / 2

        fused_uncertainty = (
            mc_uncertainty
            + tta_uncertainty
        ) / 2

        # --------------------------------------------------
        # STEP 7: DISEASE LABEL
        # --------------------------------------------------

        labels = DISEASE_LABELS.get(
            disease_key,
            []
        )

        if disease_idx >= len(labels):

            return {
                "error":
                "Rice model class labels do not match "
                "the trained model."
            }

        raw_label = labels[
            disease_idx
        ]

        disease_label = clean_label(
            raw_label
        )

        # --------------------------------------------------
        # STEP 8: GRAD-CAM
        # --------------------------------------------------

        try:

            grad = GradCAMPP(model)

            heatmap_mask = grad(
                img_tensor,
                disease_idx
            )

            heatmap_img = (
                GradCAMPP.overlay(
                    cropped_image,
                    heatmap_mask
                )
            )

        except Exception:

            heatmap_img = cropped_image

        # --------------------------------------------------
        # STEP 9: RETURN RESULT
        # --------------------------------------------------

        return {

            "species":
                "Rice",

            "species_conf":
                1.0,

            "disease":
                disease_label,

            "disease_conf":
                fused_conf,

            "mc_uncertainty":
                mc_uncertainty,

            "tta_uncertainty":
                tta_uncertainty,

            "uncertainty_fused":
                fused_uncertainty,

            "model_used":
                "Rice ResNet18",

            "cropped_image":
                cropped_image,

            "boxed_image":
                boxed_image,

            "heatmap":
                heatmap_img
        }