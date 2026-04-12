"""
Feature extraction pipeline for scanner identification.
Uses CPU-friendly hand-crafted features: PRNU, FFT, LBP, Wavelet, GLCM.
No GPU required.

Feature vector breakdown (total: 502 dims):
  PRNU stats       :  18  (6 stats x 3 sigma levels)
  PRNU patch stats :  24  (6 stats x 4 patches)
  FFT radial       :  64
  FFT quadrant     :  16  (4 quadrants x 4 stats)
  LBP histogram    : 256
  Wavelet energy   :  12  (3 levels x 4 subbands)
  GLCM texture     :  16  (4 props x 4 distances)
  Gradient stats   :   6
  Laplacian stats  :   6
  Co-occurrence    :  84  (extra discriminative for similar scanners)
  ───────────────────────
  Total            : 502
"""

import numpy as np
import cv2
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops
from scipy.fft import fft2, fftshift
import logging

logger = logging.getLogger(__name__)

IMAGE_SIZE = (256, 256)
LBP_RADIUS  = 3
LBP_POINTS  = 8 * LBP_RADIUS
LBP_BINS    = 256
FFT_BINS    = 64
PRNU_SIGMAS = [1.5, 3.0, 5.0]   # multi-scale PRNU


# ─── Preprocessing ────────────────────────────────────────────

def load_and_preprocess(image_bytes: bytes) -> np.ndarray:
    """
    Decode image bytes → resized grayscale float32 [0,1].
    Handles large 300 DPI TIF files via Pillow fallback when OpenCV fails.
    """
    # Try OpenCV first (fast path)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Fallback: Pillow handles multi-page TIFs, 16-bit TIFs, large files better
    if img is None:
        try:
            from PIL import Image as PILImage
            import io as _io
            pil_img = PILImage.open(_io.BytesIO(image_bytes))
            pil_img.load()  # force decode

            # Handle multi-page TIF — use first page
            try:
                pil_img.seek(0)
            except Exception:
                pass

            # Convert to RGB (handles 16-bit, CMYK, palette modes)
            if pil_img.mode not in ("RGB", "RGBA", "L"):
                pil_img = pil_img.convert("RGB")
            elif pil_img.mode == "RGBA":
                pil_img = pil_img.convert("RGB")

            img = np.array(pil_img)
            if img.ndim == 2:
                # Already grayscale
                gray = img
            else:
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

            # Normalize to uint8 if 16-bit
            if gray.dtype != np.uint8:
                gray = (gray / gray.max() * 255).astype(np.uint8) if gray.max() > 0 else gray.astype(np.uint8)

            resized = cv2.resize(gray, IMAGE_SIZE, interpolation=cv2.INTER_AREA)
            return resized.astype(np.float32) / 255.0

        except Exception as e:
            raise ValueError(f"Could not decode image (tried OpenCV + Pillow): {e}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, IMAGE_SIZE, interpolation=cv2.INTER_AREA)
    return resized.astype(np.float32) / 255.0


def _stats6(arr: np.ndarray) -> np.ndarray:
    """Return 6 statistics of a flat array: mean, std, skew, kurtosis, energy, entropy."""
    flat = arr.flatten().astype(np.float64)
    mean = float(np.mean(flat))
    std  = float(np.std(flat)) + 1e-10
    skew = float(np.mean(((flat - mean) / std) ** 3))
    kurt = float(np.mean(((flat - mean) / std) ** 4))
    energy = float(np.sum(flat ** 2))
    hist, _ = np.histogram(flat, bins=128)
    prob = hist.astype(np.float32) + 1e-10
    prob /= prob.sum()
    entropy = float(-np.sum(prob * np.log2(prob)))
    return np.array([mean, std, skew, kurt, energy, entropy], dtype=np.float32)


# ─── PRNU (multi-scale + patch) ───────────────────────────────

def extract_prnu(gray: np.ndarray) -> np.ndarray:
    """
    Multi-scale PRNU: 3 Gaussian sigma levels → 18 features.
    Patch PRNU: 4 non-overlapping quadrant patches → 24 features.
    Total: 42 features.
    """
    feats = []

    # Multi-scale global PRNU
    for sigma in PRNU_SIGMAS:
        blurred = cv2.GaussianBlur(gray, (0, 0), sigma)
        noise = gray - blurred
        feats.append(_stats6(noise))

    # Patch-based PRNU (4 quadrants) at sigma=3
    h, w = gray.shape
    blurred3 = cv2.GaussianBlur(gray, (0, 0), 3.0)
    noise3 = gray - blurred3
    patches = [
        noise3[:h//2, :w//2],
        noise3[:h//2, w//2:],
        noise3[h//2:, :w//2],
        noise3[h//2:, w//2:],
    ]
    for patch in patches:
        feats.append(_stats6(patch))

    return np.concatenate(feats).astype(np.float32)   # 42 dims


# ─── FFT (radial + quadrant) ──────────────────────────────────

def extract_fft(gray: np.ndarray) -> np.ndarray:
    """
    Radially averaged power spectrum (64 bins) +
    Quadrant energy statistics (16 features).
    Total: 80 features.
    """
    f = fft2(gray)
    fshift = fftshift(f)
    magnitude = np.log1p(np.abs(fshift) ** 2).astype(np.float32)

    # Radial bins
    cy, cx = np.array(magnitude.shape) // 2
    y, x = np.ogrid[:magnitude.shape[0], :magnitude.shape[1]]
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2).astype(int)
    r_max = min(cy, cx)

    radial = np.zeros(FFT_BINS, dtype=np.float32)
    for i in range(FFT_BINS):
        lo = int(i * r_max / FFT_BINS)
        hi = int((i + 1) * r_max / FFT_BINS)
        mask = (r >= lo) & (r < hi)
        if mask.any():
            radial[i] = float(magnitude[mask].mean())
    r_range = radial.max() - radial.min()
    if r_range > 0:
        radial = (radial - radial.min()) / r_range

    # Quadrant statistics (4 quadrants × 4 stats = 16)
    h, w = magnitude.shape
    quadrants = [
        magnitude[:h//2, :w//2],
        magnitude[:h//2, w//2:],
        magnitude[h//2:, :w//2],
        magnitude[h//2:, w//2:],
    ]
    quad_feats = []
    for q in quadrants:
        quad_feats.extend([q.mean(), q.std(), q.max(), float(np.percentile(q, 90))])

    return np.concatenate([radial, np.array(quad_feats, dtype=np.float32)])  # 80 dims


# ─── LBP ─────────────────────────────────────────────────────

def extract_lbp(gray: np.ndarray) -> np.ndarray:
    """Local Binary Patterns histogram — 256 dims."""
    gray_u8 = (gray * 255).astype(np.uint8)
    lbp = local_binary_pattern(gray_u8, LBP_POINTS, LBP_RADIUS, method='uniform')
    hist, _ = np.histogram(lbp, bins=LBP_BINS, range=(0, LBP_BINS))
    hist = hist.astype(np.float32)
    total = hist.sum()
    if total > 0:
        hist /= total
    return hist   # 256 dims


# ─── Wavelet energy ───────────────────────────────────────────

def extract_wavelet(gray: np.ndarray) -> np.ndarray:
    """
    3-level Haar wavelet decomposition energy per subband.
    Returns 12 features (3 levels × 4 subbands: LL, LH, HL, HH).
    No pywavelets needed — implemented with cv2 pyrDown.
    """
    feats = []
    img = gray.copy()
    for _ in range(3):
        h, w = img.shape
        h2, w2 = h // 2, w // 2
        if h2 < 4 or w2 < 4:
            feats.extend([0.0, 0.0, 0.0, 0.0])
            continue

        # Approximate Haar via averaging / differencing
        rows_avg = (img[:2*h2:2, :] + img[1:2*h2:2, :]) / 2
        rows_dif = (img[:2*h2:2, :] - img[1:2*h2:2, :]) / 2

        LL = (rows_avg[:, :2*w2:2] + rows_avg[:, 1:2*w2:2]) / 2
        LH = (rows_avg[:, :2*w2:2] - rows_avg[:, 1:2*w2:2]) / 2
        HL = (rows_dif[:, :2*w2:2] + rows_dif[:, 1:2*w2:2]) / 2
        HH = (rows_dif[:, :2*w2:2] - rows_dif[:, 1:2*w2:2]) / 2

        feats.extend([
            float(np.mean(LL ** 2)),
            float(np.mean(LH ** 2)),
            float(np.mean(HL ** 2)),
            float(np.mean(HH ** 2)),
        ])
        img = LL   # next level uses LL subband

    return np.array(feats, dtype=np.float32)   # 12 dims


# ─── GLCM texture ─────────────────────────────────────────────

def extract_glcm(gray: np.ndarray) -> np.ndarray:
    """
    Gray-Level Co-occurrence Matrix properties at 4 distances.
    Properties: contrast, dissimilarity, homogeneity, energy → 16 dims.
    """
    gray_u8 = (gray * 255).astype(np.uint8)
    # Reduce to 64 levels for speed
    gray_64 = (gray_u8 // 4).astype(np.uint8)
    distances = [1, 2, 4, 8]
    angles = [0]  # horizontal only for speed

    try:
        glcm = graycomatrix(gray_64, distances=distances, angles=angles,
                            levels=64, symmetric=True, normed=True)
        props = ['contrast', 'dissimilarity', 'homogeneity', 'energy']
        feats = []
        for prop in props:
            vals = graycoprops(glcm, prop).flatten()
            feats.extend(vals.tolist())
        return np.array(feats, dtype=np.float32)   # 16 dims
    except Exception:
        return np.zeros(16, dtype=np.float32)


# ─── Gradient + Laplacian ─────────────────────────────────────

def extract_gradient_laplacian(gray: np.ndarray) -> np.ndarray:
    """
    Gradient magnitude stats (6) + Laplacian stats (6) = 12 dims.
    Captures sharpness/blur characteristics of scanner optics.
    """
    gray_u8 = (gray * 255).astype(np.uint8)

    sobelx = cv2.Sobel(gray_u8, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray_u8, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = np.sqrt(sobelx**2 + sobely**2)

    lap = cv2.Laplacian(gray_u8, cv2.CV_64F)

    return np.concatenate([_stats6(grad_mag), _stats6(lap)]).astype(np.float32)  # 12 dims


# ─── Co-occurrence noise features ────────────────────────────

def extract_noise_cooccurrence(gray: np.ndarray) -> np.ndarray:
    """
    PRNU noise co-occurrence: captures spatial correlations in noise
    that are unique per scanner model. Especially helps distinguish
    similar Canon/Epson models. Returns 84 dims.
    """
    blurred = cv2.GaussianBlur(gray, (0, 0), 3.0)
    noise = gray - blurred

    # Quantize noise to 14 levels
    noise_min, noise_max = noise.min(), noise.max()
    if noise_max > noise_min:
        noise_q = ((noise - noise_min) / (noise_max - noise_min) * 13).astype(np.uint8)
    else:
        return np.zeros(84, dtype=np.float32)

    feats = []
    # Horizontal + vertical co-occurrence at 3 distances
    for dist in [1, 2, 3]:
        for direction in ['h', 'v', 'd']:
            if direction == 'h':
                a, b = noise_q[:, :-dist], noise_q[:, dist:]
            elif direction == 'v':
                a, b = noise_q[:-dist, :], noise_q[dist:, :]
            else:
                a, b = noise_q[:-dist, :-dist], noise_q[dist:, dist:]

            # 2-bin histogram of (a, b) pairs
            diff = (a.astype(np.int16) - b.astype(np.int16)).flatten()
            hist, _ = np.histogram(diff, bins=9, range=(-7, 7))
            hist = hist.astype(np.float32)
            if hist.sum() > 0:
                hist /= hist.sum()
            feats.append(hist)

    # 3 dist * 3 directions * 9 bins = 81 dims — pad to 84 for alignment
    result = np.concatenate(feats).astype(np.float32)
    pad = 84 - len(result)
    if pad > 0:
        result = np.concatenate([result, np.zeros(pad, dtype=np.float32)])
    return result[:84]


# ─── Master feature extractor ─────────────────────────────────

def extract_all_features(image_bytes: bytes) -> np.ndarray:
    """
    Full feature pipeline.
    Returns concatenated vector of ~502 dims.
    """
    gray = load_and_preprocess(image_bytes)

    prnu        = extract_prnu(gray)               # 42
    fft_feat    = extract_fft(gray)                # 80
    lbp         = extract_lbp(gray)               # 256
    wavelet     = extract_wavelet(gray)            # 12
    glcm        = extract_glcm(gray)              # 16
    grad_lap    = extract_gradient_laplacian(gray) # 12
    noise_cooc  = extract_noise_cooccurrence(gray) # 81

    features = np.concatenate([prnu, fft_feat, lbp, wavelet, glcm, grad_lap, noise_cooc])
    logger.debug(f"Feature vector: {features.shape[0]} dims")
    return features.astype(np.float32)


# ─── Visualization helpers ────────────────────────────────────

def get_noise_map(image_bytes: bytes) -> np.ndarray:
    """PRNU noise map as colored uint8 image for visualization."""
    gray = load_and_preprocess(image_bytes)
    blurred = cv2.GaussianBlur(gray, (0, 0), 3.0)
    noise = gray - blurred
    n_min, n_max = noise.min(), noise.max()
    if n_max > n_min:
        noise_norm = ((noise - n_min) / (n_max - n_min) * 255).astype(np.uint8)
    else:
        noise_norm = np.zeros_like(noise, dtype=np.uint8)
    return cv2.applyColorMap(noise_norm, cv2.COLORMAP_JET)


def get_fft_map(image_bytes: bytes) -> np.ndarray:
    """FFT magnitude spectrum as colored image for visualization."""
    gray = load_and_preprocess(image_bytes)
    f = fft2(gray)
    fshift = fftshift(f)
    magnitude = np.abs(fshift)
    log_mag = np.log1p(magnitude)
    log_mag_norm = ((log_mag - log_mag.min()) / (log_mag.max() - log_mag.min()) * 255).astype(np.uint8)
    return cv2.applyColorMap(log_mag_norm, cv2.COLORMAP_INFERNO)
