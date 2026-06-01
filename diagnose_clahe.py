"""
Diagnostic: Compare embedding distances WITH vs WITHOUT CLAHE preprocessing.
This tests if CLAHE is making different faces too similar.
"""
import numpy as np
import cv2
import face_recognition
from PIL import Image as PILImage, ExifTags
import glob
import os

def fix_exif(image, image_path):
    try:
        pil_image = PILImage.open(image_path)
        exif = pil_image.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == "Orientation":
                    if value == 3: image = np.rot90(image, 2)
                    elif value == 6: image = np.rot90(image, 3)
                    elif value == 8: image = np.rot90(image, 1)
                    break
    except: pass
    return image

def resize_if_large(image, max_dim=1600):
    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return image

def apply_clahe(image):
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

def l2_normalize(emb):
    norm = np.linalg.norm(emb)
    return emb / norm if norm > 0 else emb

def get_embedding(image_path, use_clahe=False):
    image = face_recognition.load_image_file(image_path)
    image = fix_exif(image, image_path)
    image = resize_if_large(image)
    if use_clahe:
        image = apply_clahe(image)
    
    locs = face_recognition.face_locations(image, model="hog", number_of_times_to_upsample=2)
    if not locs:
        return None
    encs = face_recognition.face_encodings(image, [locs[0]], num_jitters=5, model="large")
    if not encs:
        return None
    return l2_normalize(encs[0])

def cosine_dist(a, b):
    return 1.0 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Find all uploaded original images
image_dir = "uploads/originals"
image_files = sorted(glob.glob(os.path.join(image_dir, "*")))

if len(image_files) < 2:
    print(f"Only {len(image_files)} images found. Need at least 2.")
    exit()

print(f"Found {len(image_files)} images.\n")

# Get embeddings with and without CLAHE
for use_clahe in [False, True]:
    label = "WITH CLAHE" if use_clahe else "WITHOUT CLAHE"
    print(f"=== {label} ===")
    
    embeddings = []
    for path in image_files:
        emb = get_embedding(path, use_clahe=use_clahe)
        fname = os.path.basename(path)
        if emb is not None:
            embeddings.append((fname, emb))
            print(f"  Encoded: {fname}")
        else:
            print(f"  SKIPPED (no face): {fname}")
    
    print(f"\n  Pairwise Cosine Distances:")
    for i in range(len(embeddings)):
        for j in range(i+1, len(embeddings)):
            d = cosine_dist(embeddings[i][1], embeddings[j][1])
            a_name = embeddings[i][0][:30]
            b_name = embeddings[j][0][:30]
            print(f"    {a_name} <-> {b_name}: {d:.6f}")
    print()
