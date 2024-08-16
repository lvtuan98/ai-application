import os
import cv2
import PIL
import numpy as np
from tqdm import tqdm
from PIL import Image, ImageFont, ImageDraw
from typing import Optional, Union, List


import albumentations as alb
from albumentations.pytorch import ToTensorV2

import torch
import accelerate
from accelerate import Accelerator
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from diffusers.utils.torch_utils import randn_tensor
from diffusers import (
    AutoencoderKL, 
    DDPMScheduler,
    # KarrasDiffusionSchedulers,
    StableDiffusionPipeline, 
    UNet2DConditionModel, 
    DiffusionPipeline
)

# dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(dir_path)

from .utils import(
    draw_text, 
    generate_mask, 
    process_location, 
    prepare_mask_and_masked_image)


class DocGenProcessor:
    def __init__(
            self, 
            size=(512, 512),
            crop_scale=256
            ):
        self.size = size
        self.crop_scale = crop_scale

        self.transform_resize_crop = alb.Compose([   
                alb.Resize(size[0], size[1]),
                alb.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
            ])

        self.mask_transform = alb.Compose([   
                alb.Resize(size[0], size[1]),
            ])

        self.transform_to_tensor = alb.Compose([
                ToTensorV2(),
            ])
        
    def __call__(self, img_path, location, text):
        instance_image = cv2.imread(img_path)
        image_size = instance_image.shape
        h, w, c = image_size

        location = process_location(location, image_size)
        location = np.int32(location)

        # masked image
        mask = generate_mask((w, h), location)
        masked_image = prepare_mask_and_masked_image(instance_image, mask)

        # Resize if original image size is less than 256
        short_side = min(h, w)
        if short_side < self.crop_scale:
            scale_factor = int(self.crop_scale*2/short_side)
            new_h, new_w = h * scale_factor, w * scale_factor
            instance_image = cv2.resize(instance_image, (new_w, new_h))
            mask = cv2.resize(mask, (new_w, new_h))
            masked_image = cv2.resize(masked_image, (new_w, new_h))

        # Crop text based on location
        x1,y1,x2,y2 = location
        if x2-x1 < self.crop_scale:
            try:
                x_s = np.random.randint(max(0, x2-self.crop_scale), x1)
            except:
                x_s = 0
            text = text
        else:
            x_s = x1
            text = text[:int(len(text)*(self.crop_scale)/(x2-x1))]

        if y2-y1 < self.crop_scale:
            try:
                y_s = np.random.randint(max(0, y2-self.crop_scale), y1)
            except:
                y_s = 0
            text = text
        else:
            y_s = y1
            text = text[:int(len(text)*(self.crop_scale)/(y2-y1))]


        draw_ttf = draw_text(instance_image.shape[:2][::-1], text)
        instance_image_1 = instance_image[y_s:y_s+self.crop_scale, x_s:x_s+self.crop_scale,:]
        mask_crop = mask[y_s:y_s+self.crop_scale, x_s:x_s+self.crop_scale]
        masked_image_crop = masked_image[y_s:y_s+self.crop_scale, x_s:x_s+self.crop_scale,:]

        # print('[INFO] Valid text:', text)
        # cv2.imwrite('mask.jpg', mask*255)
        # cv2.imwrite('mask_img.jpg', masked_image)
        # cv2.imwrite('ttf.jpg', draw_ttf)
        # cv2.imwrite('instance_image_1.jpg', instance_image_1)
        # cv2.imwrite('mask_crop.jpg', mask_crop*255)
        # cv2.imwrite('masked_image_crop.jpg', masked_image_crop)

        original_imgs = [instance_image, mask, masked_image]
        cropped_imgs = [instance_image_1, mask_crop, masked_image_crop, draw_ttf]

        augmented = self.transform_resize_crop(image=instance_image_1)
        instance_image_1 = augmented["image"]
        augmented = self.transform_to_tensor(image=instance_image_1)
        instance_image_1 = augmented["image"]

        augmented = self.transform_resize_crop(image=masked_image_crop)
        masked_image_crop = augmented["image"]
        augmented = self.transform_to_tensor(image=masked_image_crop)
        masked_image_crop = augmented["image"]

        augmented = self.mask_transform(image=mask_crop)
        mask_crop = augmented["image"]
        augmented = self.transform_to_tensor(image=mask_crop)
        mask_crop = augmented["image"]

        augmented = self.transform_to_tensor(image=draw_ttf)
        draw_ttf = augmented["image"]

        # print('ttf shape:', draw_ttf.shape)
        # print('instance_image_1 shape:', instance_image_1.shape)
        # print('mask_crop shape:', mask_crop.shape)
        # print('masked_image_crop shape:', masked_image_crop.shape)

        instance_image_1 = instance_image_1.to(memory_format=torch.contiguous_format).float()
        
        example = {}
        example["image"] = instance_image_1.unsqueeze(0)
        example['mask'] = mask_crop.unsqueeze(0)
        example['masked_image'] = masked_image_crop.unsqueeze(0)
        example['ttf_image'] = draw_ttf.unsqueeze(0)
        example['originals'] = original_imgs
        example['cropped'] = cropped_imgs

        return example


class DocGenPipeline(DiffusionPipeline):
    def __init__(
        self,
        vae: AutoencoderKL,
        text_encoder: VisionEncoderDecoderModel,
        tokenizer: TrOCRProcessor,
        unet: UNet2DConditionModel,
        scheduler: DDPMScheduler #KarrasDiffusionSchedulers,
    ):
        super().__init__()
        self.register_modules(
            vae=vae,
            text_encoder=text_encoder,
            tokenizer=tokenizer,
            unet=unet,
            scheduler=scheduler,
        )

        self.vae_scale_factor = 2 ** (len(vae.config.block_out_channels) - 1)

    @property
    # Copied from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion.StableDiffusionPipeline._execution_device
    def _execution_device(self):
        r"""
        Returns the device on which the pipeline's models will be executed. After calling
        `pipeline.enable_sequential_cpu_offload()` the execution device can only be inferred from Accelerate's module
        hooks.
        """
        if not hasattr(self.unet, "_hf_hook"):
            return self.device
        for module in self.unet.modules():
            if (
                hasattr(module, "_hf_hook")
                and hasattr(module._hf_hook, "execution_device")
                and module._hf_hook.execution_device is not None
            ):
                return torch.device(module._hf_hook.execution_device)
        return self.device
        
    @torch.no_grad()
    def __call__(
        self,
        prompt: Union[torch.FloatTensor, PIL.Image.Image] = None,
        location: Optional[np.ndarray]= None,
        image: Union[torch.FloatTensor, PIL.Image.Image] = None,
        mask_image: Union[torch.FloatTensor, PIL.Image.Image] = None,
        mask: Union[torch.FloatTensor, PIL.Image.Image] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        num_images_per_prompt: Optional[int] = 1,
        eta: float = 0.0,
        seed: int = 20,
        generator: Optional[Union[torch.Generator, List[torch.Generator]]] = None,
        latents: Optional[torch.FloatTensor] = None,
        prompt_embeds: Optional[torch.FloatTensor] = None,
        output_type: Optional[str] = "pil",
        return_dict: bool = True,
        # callback: Optional[Callable[[int, int, torch.FloatTensor], None]] = None,
        # callback_steps: int = 1,
    ):
        if image is None:
            raise ValueError("`image` input cannot be undefined.")

        if mask_image is None:
            raise ValueError("`mask_image` input cannot be undefined.")

        device = self._execution_device
        # 2. Encode input prompt
        # if type(prompt) == "string":
        #     ttf_imgs = draw_text(image[0].shape[:2][::-1], prompt, location)

        prompt_images = self.tokenizer(images=prompt, return_tensors="pt").pixel_values.to(device)
        ocr_feature = self.text_encoder(prompt_images)
        prompt_embeds = ocr_feature.last_hidden_state.detach()
        
        # 3. Define call parameters
        batch_size = prompt_embeds.shape[0]

        # 4. Preprocess mask and image
        
        # 5. set timesteps
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps

        # 6. Prepare latent variables
        vae = self.vae
        latents = vae.encode(image).latent_dist.sample()
        latents = latents * vae.config.scaling_factor
        noise = torch.randn_like(latents)

        # 7. Prepare mask latent variables
        # Rex: prepare mask && mask latent as input of UNET  
        vae_scale_factor = self.vae_scale_factor     
        width, height, *_ = mask.size()[::-1]         
        mask = torch.nn.functional.interpolate(
            mask, size=[width // vae_scale_factor, height // vae_scale_factor, *_][:-2][::-1]
        )
        
        masked_image_latents = vae.encode(mask_image).latent_dist.sample()
        masked_image_latents = masked_image_latents * vae.config.scaling_factor

        shape = (1, vae.config.latent_channels, height // vae_scale_factor, width // vae_scale_factor)

        latents = randn_tensor(shape, generator=torch.manual_seed(seed), device=device,)
        
        # scale the initial noise by the standard deviation required by the scheduler
        latents = latents * self.scheduler.init_noise_sigma
        
        # 10. Denoising loop
        # num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                # expand the latents if we are doing classifier free guidance
                latent_model_input = latents

                # concat latents, mask, masked_image_latents in the channel dimension
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                latent_model_input = torch.cat([latent_model_input, mask, masked_image_latents], dim=1)

                # predict the noise residual
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds).sample

                # compute the previous noisy sample x_t -> x_t-1
                latents = self.scheduler.step(noise_pred, t, latents).prev_sample

                progress_bar.update()
                
        # 11. Post-processing
        pred_latents = 1 / vae.config.scaling_factor * latents
        image_vae = vae.decode(pred_latents).sample

        # 13. Convert to PIL
        image = (image_vae / 2 + 0.5) * 255.0
        image = image.cpu().permute(0, 2, 3, 1).float().detach().numpy()
        return image, image_vae
    

class DocGenInpaintingPipeline(DocGenPipeline):
    def __init__(
        self,
        vae: AutoencoderKL,
        text_encoder: VisionEncoderDecoderModel,
        tokenizer: TrOCRProcessor,
        unet: UNet2DConditionModel,
        scheduler: DDPMScheduler
    ):
        super().__init__(
            vae=vae,
            text_encoder=text_encoder,
            tokenizer=tokenizer,
            unet=unet,
            scheduler=scheduler
        )
        
    
    @torch.no_grad()
    def __call__(
        self,
        prompt: Union[torch.FloatTensor, PIL.Image.Image] = None,
        location: Optional[np.ndarray]= None,
        image: Union[torch.FloatTensor, PIL.Image.Image] = None,
        mask_image: Union[torch.FloatTensor, PIL.Image.Image] = None,
        mask: Union[torch.FloatTensor, PIL.Image.Image] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        num_images_per_prompt: Optional[int] = 1,
        eta: float = 0.0,
        seed: int = 20,
        generator: Optional[Union[torch.Generator, List[torch.Generator]]] = None,
        latents: Optional[torch.FloatTensor] = None,
        prompt_embeds: Optional[torch.FloatTensor] = None,
        output_type: Optional[str] = "pil",
        return_dict: bool = True,
        # callback: Optional[Callable[[int, int, torch.FloatTensor], None]] = None,
        # callback_steps: int = 1,
    ):


        if image is None:
            raise ValueError("`image` input cannot be undefined.")

        if mask_image is None:
            raise ValueError("`mask_image` input cannot be undefined.")

        device = self._execution_device

        # 2. Encode input prompt
        prompt_images = self.tokenizer(images=prompt, return_tensors="pt").pixel_values.to(device)
        ocr_feature = self.text_encoder(prompt_images)
        prompt_embeds = ocr_feature.last_hidden_state.detach()

        # 3. Define call parameters
        batch_size = prompt_embeds.shape[0]

        # 5. set timesteps
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps

        # 6. Prepare latent variables
        vae = self.vae
        latents = vae.encode(image).latent_dist.sample()
        latents = latents * vae.config.scaling_factor
        noise = torch.randn_like(latents)

        # 7. Prepare mask latent variables
        # Rex: prepare mask && mask latent as input of UNET  
        vae_scale_factor = self.vae_scale_factor     
        width, height, *_ = mask.size()[::-1]         
        mask = torch.nn.functional.interpolate(
            mask, size=[width // vae_scale_factor, height // vae_scale_factor, *_][:-2][::-1]
        )
        
        masked_image_latents = vae.encode(mask_image).latent_dist.sample()
        masked_image_latents = masked_image_latents * vae.config.scaling_factor

        shape = (1, vae.config.latent_channels, height // vae_scale_factor, width // vae_scale_factor)

        latents = randn_tensor(shape, generator=torch.manual_seed(seed), device=device,)
        
        # scale the initial noise by the standard deviation required by the scheduler
        latents = latents * self.scheduler.init_noise_sigma
        init_latents_orig = latents.clone()

        # 10. Denoising loop
        # num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                # expand the latents if we are doing classifier free guidance
                latent_model_input = latents

                # concat latents, mask, masked_image_latents in the channel dimension
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                latent_model_input = torch.cat([latent_model_input, mask, masked_image_latents], dim=1)

                # predict the noise residual
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds).sample

                # compute the previous noisy sample x_t -> x_t-1
                latents = self.scheduler.step(noise_pred, t, latents).prev_sample

                # masking
                init_latents_proper = self.scheduler.add_noise(init_latents_orig, noise, t)
                latents = (init_latents_proper * mask) + (latents * (1 - mask))

                progress_bar.update()

        # 11. Post-processing
        pred_latents = 1 / vae.config.scaling_factor * latents
        image_vae = vae.decode(pred_latents).sample

        # 13. Convert to PIL
        image = (image_vae / 2 + 0.5) * 255.0
        image = image.cpu().permute(0, 2, 3, 1).float().detach().numpy()
        return image, image_vae