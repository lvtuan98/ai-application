import os

WEIGHT_DIR = os.getenv("WEIGHT_DIR", "/models/weights/")
DOC_GEN_WEIGHT_PATH = os.path.join(WEIGHT_DIR, "doc_gen")

VAE_MODEL_PATH = os.path.join(DOC_GEN_WEIGHT_PATH, "finetuned_vae")
OCR_MODEL_PATH = os.path.join(DOC_GEN_WEIGHT_PATH, "TrOCR")
SD_MODEL_PATH = os.path.join(DOC_GEN_WEIGHT_PATH, "finetuned_diffute")
