import torch
import torch.nn.functional as F

class OODDetector:
    """
    Simple OOD check using:
    - Softmax confidence threshold
    - Prediction entropy
    """

    def __init__(self, conf_threshold=0.40, entropy_threshold=1.50):
        self.conf_threshold = conf_threshold
        self.entropy_threshold = entropy_threshold

    def is_ood(self, logits):
        probs = F.softmax(logits, dim=1)
        conf, _ = probs.max(dim=1)

        # entropy = -sum(p log p)
        entropy = -(probs * torch.log(probs + 1e-12)).sum(dim=1)

        return {
            "confidence": conf.item(),
            "entropy": entropy.item(),
            "is_ood": conf.item() < self.conf_threshold or entropy.item() > self.entropy_threshold
        }
