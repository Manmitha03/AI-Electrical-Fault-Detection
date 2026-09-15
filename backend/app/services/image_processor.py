"""
Image Processing Pipeline for Electrical Fault Detection
==========================================================
Uses OpenCV to analyze uploaded images of electrical components
for visual indicators of faults (burn marks, discoloration,
corrosion, cracks, etc.).

IMPORTANT: Image analysis is an ASSISTIVE diagnostic tool.
It cannot definitively diagnose dangerous electrical faults
from an ordinary photograph. Professional inspection is always
recommended.
"""

import io
import os
import base64
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# Allowed image formats
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_DIMENSION = 4096  # pixels


@dataclass
class ImageAnalysisResult:
    """Structured result from image analysis."""
    valid: bool = True
    error: str = ""
    fault_indicators: List[str] = field(default_factory=list)
    confidence: float = 0.0
    severity: str = "LOW"
    analysis_details: Dict = field(default_factory=dict)
    annotated_image_b64: str = ""
    regions_of_interest: List[Dict] = field(default_factory=list)
    disclaimer: str = (
        "Image analysis is an assistive diagnostic tool and cannot "
        "definitively diagnose electrical faults from photographs. "
        "Professional inspection is recommended."
    )

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "error": self.error,
            "fault_indicators": self.fault_indicators,
            "confidence": round(self.confidence, 4),
            "severity": self.severity,
            "analysis_details": self.analysis_details,
            "annotated_image_b64": self.annotated_image_b64,
            "regions_of_interest": self.regions_of_interest,
            "disclaimer": self.disclaimer,
        }


class ImageProcessor:
    """
    OpenCV-based image processing pipeline for electrical fault detection.

    Pipeline:
    1. Validation → 2. Resize → 3. Noise Reduction → 4. Contrast Enhancement →
    5. Edge Detection → 6. Color Analysis → 7. Region Detection → 8. Anomaly Detection
    """

    def __init__(self):
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV is required. Install with: pip install opencv-python")

    def validate_image(self, file_data: bytes, filename: str) -> Tuple[bool, str]:
        """Validate image file type, size, and basic integrity."""
        # Check file size
        if len(file_data) > MAX_FILE_SIZE:
            return False, f"File too large ({len(file_data) / 1024 / 1024:.1f}MB). Max: {MAX_FILE_SIZE / 1024 / 1024}MB"

        # Check extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Unsupported format '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

        # Try to decode image
        try:
            nparr = np.frombuffer(file_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return False, "File is not a valid image or is corrupted."
            h, w = img.shape[:2]
            if h < 10 or w < 10:
                return False, "Image too small for analysis."
            if h > MAX_DIMENSION or w > MAX_DIMENSION:
                return False, f"Image too large ({w}x{h}). Max dimension: {MAX_DIMENSION}px"
        except Exception as e:
            return False, f"Image validation failed: {str(e)}"

        return True, "Valid"

    def analyze(self, file_data: bytes, filename: str = "image.jpg") -> ImageAnalysisResult:
        """
        Run the complete image analysis pipeline.

        Args:
            file_data: Raw image bytes.
            filename: Original filename for validation.

        Returns:
            ImageAnalysisResult with fault indicators and analysis details.
        """
        result = ImageAnalysisResult()

        # Step 1: Validate
        is_valid, msg = self.validate_image(file_data, filename)
        if not is_valid:
            result.valid = False
            result.error = msg
            return result

        # Decode image
        nparr = np.frombuffer(file_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Step 2: Resize
        img = self._resize(img)
        h, w = img.shape[:2]

        # Step 3: Noise reduction
        denoised = self._denoise(img)

        # Step 4: Contrast enhancement
        enhanced = self._enhance_contrast(denoised)

        # Step 5: Edge detection
        edges, edge_density = self._detect_edges(enhanced)

        # Step 6: Color analysis
        color_analysis = self._analyze_colors(enhanced)

        # Step 7: Region detection
        regions = self._detect_regions(enhanced, edges)

        # Step 8: Thermal analysis (if thermal image detected)
        thermal = self._analyze_thermal(enhanced)

        # Step 9: Anomaly detection - combine all signals
        anomalies = self._detect_anomalies(
            color_analysis, edge_density, regions, thermal
        )

        # Build fault indicators
        fault_indicators = []
        overall_confidence = 0.0
        severity_score = 0

        # Color-based indicators
        if color_analysis.get("burn_ratio", 0) > 0.02:
            indicator = "Possible burn marks or heat discoloration detected"
            fault_indicators.append(indicator)
            overall_confidence += 0.2
            severity_score += 25

        if color_analysis.get("dark_ratio", 0) > 0.15:
            indicator = "Darkened/charred regions identified"
            fault_indicators.append(indicator)
            overall_confidence += 0.15
            severity_score += 20

        if color_analysis.get("corrosion_ratio", 0) > 0.03:
            indicator = "Possible corrosion (green/white oxidation) detected"
            fault_indicators.append(indicator)
            overall_confidence += 0.15
            severity_score += 15

        if color_analysis.get("discoloration_ratio", 0) > 0.05:
            indicator = "Abnormal discoloration in component surface"
            fault_indicators.append(indicator)
            overall_confidence += 0.1
            severity_score += 15

        # Edge-based indicators
        if edge_density > 0.15:
            indicator = "High edge density suggesting surface damage or cracking"
            fault_indicators.append(indicator)
            overall_confidence += 0.1
            severity_score += 10

        # Region-based indicators
        if len(regions) > 0:
            for region in regions[:3]:  # top 3 anomalous regions
                fault_indicators.append(f"Anomalous region at ({region['x']}, {region['y']}): {region['description']}")
                overall_confidence += 0.05
                severity_score += 5

        # Thermal indicators
        if thermal.get("is_thermal", False):
            if thermal.get("hotspot_detected", False):
                fault_indicators.append("Thermal hotspot detected in infrared image")
                overall_confidence += 0.25
                severity_score += 30

        # No clear anomalies
        if not fault_indicators:
            fault_indicators.append("No obvious visual anomalies detected")
            overall_confidence = 0.1

        # Calculate final confidence and severity
        overall_confidence = min(0.95, overall_confidence)

        if severity_score >= 60:
            severity = "CRITICAL"
        elif severity_score >= 40:
            severity = "HIGH"
        elif severity_score >= 20:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Generate annotated image
        annotated = self._annotate_image(img, regions, color_analysis)
        annotated_b64 = self._image_to_base64(annotated)

        result.fault_indicators = fault_indicators
        result.confidence = overall_confidence
        result.severity = severity
        result.annotated_image_b64 = annotated_b64
        result.regions_of_interest = regions[:5]
        result.analysis_details = {
            "image_size": f"{w}x{h}",
            "color_analysis": {k: round(v, 4) if isinstance(v, float) else v
                             for k, v in color_analysis.items()},
            "edge_density": round(edge_density, 4),
            "anomalous_regions": len(regions),
            "thermal_detected": thermal.get("is_thermal", False),
        }

        return result

    def _resize(self, img: np.ndarray, max_dim: int = 800) -> np.ndarray:
        """Resize image while maintaining aspect ratio."""
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return img

    def _denoise(self, img: np.ndarray) -> np.ndarray:
        """Apply noise reduction."""
        return cv2.fastNlMeansDenoisingColored(img, None, 6, 6, 7, 21)

    def _enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        """Enhance contrast using CLAHE."""
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    def _detect_edges(self, img: np.ndarray) -> Tuple[np.ndarray, float]:
        """Detect edges and calculate edge density."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        return edges, edge_density

    def _analyze_colors(self, img: np.ndarray) -> dict:
        """Analyze color distribution for fault indicators."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        total_pixels = img.shape[0] * img.shape[1]

        # Burn marks: dark brown/black regions
        # HSV: low saturation, low value
        burn_mask = cv2.inRange(hsv, (0, 20, 10), (30, 200, 80))
        burn_ratio = np.sum(burn_mask > 0) / total_pixels

        # Dark/charred regions: very low brightness
        dark_mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 40))
        dark_ratio = np.sum(dark_mask > 0) / total_pixels

        # Corrosion: green (copper oxide) or white (aluminum oxide)
        # Green: H=35-85, S>40
        green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
        # White/gray oxidation
        white_mask = cv2.inRange(hsv, (0, 0, 180), (180, 30, 255))
        corrosion_ratio = (np.sum(green_mask > 0) + np.sum(white_mask > 0) * 0.3) / total_pixels

        # Discoloration: abnormal yellow/orange tint
        yellow_mask = cv2.inRange(hsv, (15, 100, 100), (35, 255, 255))
        discoloration_ratio = np.sum(yellow_mask > 0) / total_pixels

        # Red/warm indicators (heat damage)
        red_mask1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
        red_mask2 = cv2.inRange(hsv, (160, 100, 100), (180, 255, 255))
        red_ratio = (np.sum(red_mask1 > 0) + np.sum(red_mask2 > 0)) / total_pixels

        # Average color statistics
        mean_l = float(np.mean(lab[:, :, 0]))
        mean_a = float(np.mean(lab[:, :, 1]))
        mean_b = float(np.mean(lab[:, :, 2]))

        return {
            "burn_ratio": float(burn_ratio),
            "dark_ratio": float(dark_ratio),
            "corrosion_ratio": float(corrosion_ratio),
            "discoloration_ratio": float(discoloration_ratio),
            "red_ratio": float(red_ratio),
            "mean_lightness": mean_l,
            "mean_a_channel": mean_a,
            "mean_b_channel": mean_b,
        }

    def _detect_regions(self, img: np.ndarray, edges: np.ndarray) -> List[Dict]:
        """Detect anomalous regions using contour analysis."""
        regions = []

        # Convert to grayscale for adaptive thresholding
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Adaptive threshold to find unusual regions
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 21, 10
        )

        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        img_area = img.shape[0] * img.shape[1]

        for contour in contours:
            area = cv2.contourArea(contour)
            # Filter by size: not too small, not the entire image
            if area < img_area * 0.005 or area > img_area * 0.5:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / max(h, 1)

            # Analyze the region color
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            mean_val = cv2.mean(img, mask=mask)

            # Determine region description
            description = self._classify_region(mean_val, area, img_area)

            regions.append({
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "area": int(area),
                "area_ratio": round(area / img_area, 4),
                "description": description,
                "mean_color_bgr": [int(mean_val[0]), int(mean_val[1]), int(mean_val[2])],
            })

        # Sort by area (largest anomalies first)
        regions.sort(key=lambda r: r["area"], reverse=True)
        return regions[:10]

    def _classify_region(self, mean_color: tuple, area: int, img_area: int) -> str:
        """Classify a detected region based on color and size."""
        b, g, r = mean_color[0], mean_color[1], mean_color[2]

        # Very dark: possible burn
        if b < 50 and g < 50 and r < 50:
            return "Dark region - possible burn/char damage"

        # Brown/orange: heat discoloration
        if r > 100 and g < 80 and b < 60:
            return "Brownish region - possible heat discoloration"

        # Green: possible corrosion
        if g > 100 and g > r and g > b:
            return "Green region - possible copper corrosion"

        # Yellow: possible discoloration
        if r > 150 and g > 120 and b < 80:
            return "Yellow/brown region - possible discoloration"

        # Large irregular region
        if area > img_area * 0.1:
            return "Large anomalous region detected"

        return "Region of interest"

    def _analyze_thermal(self, img: np.ndarray) -> dict:
        """
        Check if the image appears to be from a thermal/infrared camera
        and identify hotspots.
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        total_pixels = img.shape[0] * img.shape[1]

        # Thermal images tend to have a specific color palette
        # Check for dominant warm colors (red/yellow/white gradients)
        warm_mask = cv2.inRange(hsv, (0, 100, 100), (30, 255, 255))
        warm_ratio = np.sum(warm_mask > 0) / total_pixels

        # Check for the purple/blue cold regions typical in thermal
        cool_mask = cv2.inRange(hsv, (100, 50, 50), (140, 255, 255))
        cool_ratio = np.sum(cool_mask > 0) / total_pixels

        # Heuristic: if image has significant warm and cool regions, it might be thermal
        is_thermal = (warm_ratio > 0.1 and cool_ratio > 0.1) or warm_ratio > 0.4

        hotspot_detected = False
        if is_thermal:
            # Look for intense hotspots (very bright white/red areas)
            hotspot_mask = cv2.inRange(hsv, (0, 0, 230), (180, 60, 255))
            hotspot_ratio = np.sum(hotspot_mask > 0) / total_pixels
            hotspot_detected = hotspot_ratio > 0.01

        return {
            "is_thermal": is_thermal,
            "warm_ratio": float(warm_ratio),
            "cool_ratio": float(cool_ratio),
            "hotspot_detected": hotspot_detected,
        }

    def _detect_anomalies(self, color_analysis: dict, edge_density: float,
                          regions: list, thermal: dict) -> list:
        """Combine signals to detect anomalies."""
        anomalies = []

        if color_analysis["burn_ratio"] > 0.02:
            anomalies.append({"type": "burn_marks", "score": color_analysis["burn_ratio"]})
        if color_analysis["corrosion_ratio"] > 0.03:
            anomalies.append({"type": "corrosion", "score": color_analysis["corrosion_ratio"]})
        if color_analysis["dark_ratio"] > 0.15:
            anomalies.append({"type": "charred_area", "score": color_analysis["dark_ratio"]})
        if edge_density > 0.15:
            anomalies.append({"type": "surface_damage", "score": edge_density})
        if thermal.get("hotspot_detected"):
            anomalies.append({"type": "thermal_hotspot", "score": 0.8})

        return anomalies

    def _annotate_image(self, img: np.ndarray, regions: List[Dict],
                        color_analysis: dict) -> np.ndarray:
        """Draw annotations on the image for visualization."""
        annotated = img.copy()

        # Draw region bounding boxes
        for i, region in enumerate(regions[:5]):
            x, y, w, h = region["x"], region["y"], region["width"], region["height"]
            # Color based on description
            if "burn" in region["description"].lower() or "char" in region["description"].lower():
                color = (0, 0, 255)  # Red
            elif "corrosion" in region["description"].lower():
                color = (0, 255, 255)  # Yellow
            elif "discoloration" in region["description"].lower():
                color = (0, 165, 255)  # Orange
            else:
                color = (255, 255, 0)  # Cyan

            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            label = f"R{i+1}: {region['description'][:30]}"
            cv2.putText(annotated, label, (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # Add analysis header
        cv2.putText(annotated, "AI Fault Detection Analysis",
                   (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return annotated

    def _image_to_base64(self, img: np.ndarray) -> str:
        """Convert image to base64 string for API response."""
        _, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer).decode("utf-8")
