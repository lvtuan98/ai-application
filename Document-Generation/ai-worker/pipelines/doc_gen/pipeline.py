from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from diffusers import (
    AutoencoderKL, 
    DDPMScheduler,
    # KarrasDiffusionSchedulers,
    StableDiffusionPipeline, 
    UNet2DConditionModel, 
    DiffusionPipeline
)


from configs.doc_gen.config import VAE_MODEL_PATH, SD_MODEL_PATH, OCR_MODEL_PATH
from .diffutes import DocGenPipeline, DocGenProcessor

def load_models(
    diffute_model_name_or_path: str,
    ocr_pretrained_model_or_path: str,
    vae_pretrained_model_or_path: str
):
    noise_scheduler = DDPMScheduler.from_pretrained(diffute_model_name_or_path, subfolder="scheduler")
    processor = TrOCRProcessor.from_pretrained(ocr_pretrained_model_or_path)
    trocr_model = VisionEncoderDecoderModel.from_pretrained(ocr_pretrained_model_or_path).encoder
    vae = AutoencoderKL.from_pretrained(vae_pretrained_model_or_path, subfolder="vae")
    unet = UNet2DConditionModel.from_pretrained(
        diffute_model_name_or_path, subfolder="unet"
    )

    return {
        "vae": vae,
        "text_encoder": trocr_model,
        "tokenizer": processor,
        "unet": unet,
        "scheduler": noise_scheduler
    }

def get_pipeline():
    models = load_models(
        diffute_model_name_or_path=SD_MODEL_PATH,
        ocr_pretrained_model_or_path=OCR_MODEL_PATH,
        vae_pretrained_model_or_path=VAE_MODEL_PATH
    )

    processor = DocGenProcessor()
    pipe = DocGenPipeline(**models)
    return processor, pipe