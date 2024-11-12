
# Image Requirements and Analysis Criteria

This project analyzes images based on the following specifications and thresholds to ensure quality and usability:

### **Supported Formats**
- The system supports the following image file extensions:
  - `png`
  - `jpg`
  - `jpeg`

---

### **Minimum Requirements**

#### **Resolution**
- The image must meet a **minimum resolution** of:
  - **Width:** `300 pixels`
  - **Height:** `300 pixels`

#### **Blur Threshold**
- The image is considered acceptable if the **Laplace variance** is:
  - `>= 100`
  - Higher values indicate sharper images.

#### **Brightness Range**
- The **mean brightness** of the image (grayscale values) must fall within:
  - `[50, 200]`
  - Values outside this range indicate the image is either too dark or too bright.

#### **Contrast Range**
- The **contrast** (difference between maximum and minimum pixel values) must fall within:
  - `[30, 150]`
  - Low contrast indicates a "flat" image, while high contrast might indicate over-processing.

---

### **Edge Detection**
- Edge detection is performed using the **Canny Edge Detection Algorithm**.
- The `sigma` parameter controls the sensitivity of the edge detection:
  - `0.5:` Detects many small edges, including noise.
  - `1.0:` Detects clear edges while minimizing noise.
  - `2.0:` Focuses on prominent edges, smoothing finer details.

---

### **Noise Detection**
- The system estimates **image noise** by comparing the original image to a Gaussian-blurred version:
  - **Acceptable Threshold:** Noise level should be `<= 0.05` (lower is better).

---

### **Sharpness Analysis**
- Sharpness is evaluated using the **Sobel filter**, which measures the gradient variation in the image.
- **Sharpness Threshold:** 
  - Acceptable if the Sobel variance is `>= 0.5` (higher values indicate sharper images).

---

### **Overexposure Analysis**
- Checks for regions that are too dark or too bright in the image:
  - **Dark Pixels Threshold:** Less than `10%` of the pixels should be excessively dark.
  - **Bright Pixels Threshold:** Less than `10%` of the pixels should be excessively bright.

---

### **Comprehensive Image Quality Evaluation**
The system provides an overall quality assessment based on:
- Resolution
- Brightness
- Contrast
- Blur (sharpness)
- Noise level
- Overexposure

The image is marked as "acceptable" if all the criteria are met.

---

### Example Usage
You can refer to the function `evaluate_image_quality` for a comprehensive quality assessment. The function evaluates all the above criteria and returns a detailed report of the image quality.
