from PIL import Image
import cv2
import os

class ImageCheck():
    def __init__(self,path):
        self._path=path
        if not os.path.isfile(path):
            raise FileNotFoundError(f'Plik {path} nie istnieje.')

        allowed_extensions = os.environ.get('ALLOWED_EXTENSIONS',[".jpg", ".jpeg", ".png"])
        if os.path.splitext(path)[1].lower() not in allowed_extensions:
            raise TypeError(f'Ten rodzaj pliku nie jest obsługiwany.')

        self._cv_image=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
        if self._cv_image is None:
            raise ValueError(f"Nie można wczytać pliku {path} jako obrazu.")


    def check_resolution(self,min_width=300, min_height=300):
        with Image.open(self._path) as img:
            width, height = img.size
            return {
                "width": width,
                "height": height,
                "min_width": min_width,
                "min_height": min_height,
                "is_acceptable":width>=min_width and height>=min_height
            }

    def checK_blur(self,threshold=100):
        return {
            "threshold": threshold,
            "is_acceptable":cv2.Laplacian(self._cv_image,cv2.CV_64F).var()>=threshold
        }

    def check_brightness_contrast(self, brightness_range=(50, 200), contrast_range=(30, 150)):
        mean_brightness = self._cv_image.mean()
        contrast = self._cv_image.max() - self._cv_image.min()

        # Sprawdzanie progów
        brightness_ok = brightness_range[0] <= mean_brightness <= brightness_range[1]
        contrast_ok = contrast_range[0] <= contrast <= contrast_range[1]

        return {
            "mean_brightness": mean_brightness,
            "contrast": contrast,
            "brightness_ok": brightness_ok,
            "contrast_ok": contrast_ok,
            "is_acceptable": brightness_ok and contrast_ok
        }

    def generate_report(self, min_width=300, min_height=300, brightness_range=(50, 200), contrast_range=(30, 150), blur_threshold=100):
        resolution_result = self.check_resolution(min_width, min_height)
        blur_result = self.checK_blur(blur_threshold)
        brightness_contrast_result = self.check_brightness_contrast(brightness_range, contrast_range)

        return {
            "resolution": resolution_result,
            "blur": blur_result,
            "brightness_contrast": brightness_contrast_result,
            "overall_acceptable": (
                resolution_result["is_acceptable"] and
                blur_result["is_acceptable"] and
                brightness_contrast_result["is_acceptable"]
            )
        }
