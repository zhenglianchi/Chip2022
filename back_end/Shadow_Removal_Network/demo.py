#!/usr/bin/env python
# coding: utf-8

import numpy as np
import torch
import cv2

from .libs.models import get_model
from albumentations import (Compose, Normalize, Resize)
from albumentations.pytorch import ToTensorV2

import torch.nn.functional as F




def reverse_normalize(x,
                      mean=[0.485, 0.456, 0.406],
                      std=[0.229, 0.224, 0.225]):
    x[:, 0, :, :] = x[:, 0, :, :] * std[0] + mean[0]
    x[:, 1, :, :] = x[:, 1, :, :] * std[1] + mean[1]
    x[:, 2, :, :] = x[:, 2, :, :] * std[2] + mean[2]
    return x


def visualize(img, cam):
    _, _, H, W = img.shape
    cam = F.interpolate(cam, size=(H, W), mode='bilinear', align_corners=False)
    cam = 255 * cam.squeeze()
    heatmap = cv2.applyColorMap(np.uint8(cam), cv2.COLORMAP_JET)
    heatmap = torch.from_numpy(heatmap.transpose(2, 0, 1))
    heatmap = heatmap.float() / 255
    b, g, r = heatmap.split(1)
    heatmap = torch.cat([r, g, b])

    result = heatmap + img.cpu()
    result = result.div(result.max())

    return result


def convert_show_image(tensor, idx=None):
    if tensor.shape[1] == 3:
        img = reverse_normalize(tensor,
                                mean=[0.5, 0.5, 0.5],
                                std=[0.5, 0.5, 0.5])
    elif tensor.shape[1] == 1:
        img = tensor * 0.5 + 0.5

    if idx is not None:
        img = (img[idx].transpose(1, 2, 0) * 255).astype(np.uint8)
    else:
        img = (img.squeeze(axis=0).transpose(1, 2, 0) * 255).astype(np.uint8)

    return img


def get_unshadow(imgae_data):
    test_transform = Compose([
        Resize(1024, 768),
        Normalize(mean=(0.5, ), std=(0.5, )),
        ToTensorV2()
    ])

    device = "cpu"
    benet = get_model('cam_benet', in_channels=3, pretrained=True)
    benet.model = benet.model.to(device)
    srnet = get_model('srnet', pretrained=True)
    generator, discriminator = srnet[0].to(torch.device('cpu')), srnet[1].to(
        torch.device('cpu'))
    generator.eval()
    discriminator.eval()
    generator.to(device)
    discriminator.to(device)

    image=imgae_data
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, c = image.shape

    tensor = test_transform(image=image)
    tensor = tensor['image'].unsqueeze(0).to(device)

    with torch.no_grad():

        with torch.set_grad_enabled(True):
            color, attmap, _ = benet(tensor)
            attmap = (attmap - 0.5) / 0.5
            back_color = torch.repeat_interleave(color.detach(),
                                                 1024 * 768,
                                                 dim=0)
            back_ground = back_color.reshape(1, c, 1024, 768).to(device)

        input = torch.cat([tensor, attmap, back_ground], dim=1)

        tensor = tensor.detach().cpu()
        attmap = attmap.detach().cpu()
        back_ground = back_ground.detach().cpu()
        shadow_removal_image = generator(input).detach().cpu()

    removal = convert_show_image(
        shadow_removal_image.clone().detach().cpu().numpy())

    return cv2.cvtColor(removal, cv2.COLOR_RGB2BGR)
