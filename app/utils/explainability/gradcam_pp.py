import torch
import numpy as np
import cv2
from PIL import Image

class GradCAMPP:
    def __init__(self, model):
        self.model = model
        self.model.eval()

        # Automatically find the last conv layer
        self.target_layer = self._get_last_conv_layer()

        self.gradients = None
        self.activations = None

        # Attach hooks
        self.target_layer.register_forward_hook(self._save_activation)
        self.target_layer.register_backward_hook(self._save_gradient)

    def _get_last_conv_layer(self):
        # Search model layers for the LAST Conv2d
        for layer in reversed(list(self.model.modules())):
            if isinstance(layer, torch.nn.Conv2d):
                return layer
        raise ValueError("❌ No Conv2D layer found — cannot apply GradCAM++")

    def _save_activation(self, module, input, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def __call__(self, img_tensor, class_idx):
        # Forward pass
        output = self.model(img_tensor)
        score = output[0, class_idx]

        # Backward
        self.model.zero_grad()
        score.backward(retain_graph=True)

        # GradCAM++ weights
        grads = self.gradients
        acts = self.activations

        alpha_num = grads.pow(2)
        alpha_den = 2 * grads.pow(2) + acts * grads.pow(3).sum((2, 3), keepdim=True)
        alpha_den = torch.where(alpha_den != 0, alpha_den, torch.ones_like(alpha_den))

        alphas = alpha_num / alpha_den
        weights = (alphas * grads.relu()).sum((2, 3), keepdim=True)

        # Weighted combination
        cam = (weights * acts).sum(1).squeeze().cpu().numpy()
        cam = np.maximum(cam, 0)

        # Normalize
        cam -= cam.min()
        cam /= cam.max() + 1e-8

        return cam

    @staticmethod
    def overlay(image, mask):
        heat = cv2.applyColorMap(np.uint8(mask * 255), cv2.COLORMAP_JET)
        heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)

        img = np.array(image.resize((heat.shape[1], heat.shape[0])))
        overlay = np.uint8(0.4 * img + 0.6 * heat)

        return Image.fromarray(overlay)
