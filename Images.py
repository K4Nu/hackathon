import numpy as np
from PIL import Image
import cv2
import os
from skimage import io,exposure,feature,filters

class ImageCheck():
    def __init__(self, path):
        """
        Inicjalizuje obiekt ImageCheck dla podanego pliku obrazu.

        Sprawdza, czy plik istnieje, ma prawidłowe rozszerzenie oraz czy może być poprawnie wczytany.
        """
        self._path = path
        if not os.path.isfile(path):
            raise FileNotFoundError(f'Plik {path} nie istnieje.')

        # Sprawdzanie rozszerzenia pliku w stosunku do dozwolonych
        allowed_extensions = os.environ.get('ALLOWED_EXTENSIONS', [".jpg", ".jpeg", ".png"])
        if os.path.splitext(path)[1].lower() not in allowed_extensions:
            raise TypeError(f'Ten rodzaj pliku nie jest obsługiwany.')

        # Wczytanie obrazu w skali szarości dla dalszej analizy
        self._cv_image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if self._cv_image is None:
            raise ValueError(f"Nie można wczytać pliku {path} jako obrazu.")

    def check_resolution(self, min_width=300, min_height=300):
        """
        Sprawdza rozdzielczość obrazu.

        :param min_width: Minimalna szerokość obrazu (w pikselach).
        :param min_height: Minimalna wysokość obrazu (w pikselach).
        :return: Słownik zawierający szerokość, wysokość i wynik weryfikacji.
        """
        with Image.open(self._path) as img:
            width, height = img.size
            return {
                "width": width,
                "height": height,
                "min_width": min_width,
                "min_height": min_height,
                "is_acceptable": width >= min_width and height >= min_height
            }

    def checK_blur(self, threshold=100):
        """
        Sprawdza, czy obraz jest rozmyty na podstawie wariancji Laplace'a.

        :param threshold: Minimalna wartość wariancji (im wyższa, tym ostrzejszy obraz).
        :return: Słownik zawierający próg i wynik weryfikacji.
        """
        return {
            "threshold": threshold,
            "is_acceptable": cv2.Laplacian(self._cv_image, cv2.CV_64F).var() >= threshold
        }

    def check_brightness_contrast(self, brightness_range=(50, 200), contrast_range=(30, 150)):
        """
        Sprawdza jasność i kontrast obrazu w skali szarości.

        :param brightness_range: Akceptowalny zakres jasności (średnia wartość pikseli).
        :param contrast_range: Akceptowalny zakres kontrastu (różnica między maks. i min. pikselem).
        :return: Słownik zawierający wartości jasności, kontrastu i wynik weryfikacji.
        """
        mean_brightness = self._cv_image.mean()
        contrast = self._cv_image.max() - self._cv_image.min()

        # Weryfikacja jasności i kontrastu
        brightness_ok = brightness_range[0] <= mean_brightness <= brightness_range[1]
        contrast_ok = contrast_range[0] <= contrast <= contrast_range[1]

        return {
            "mean_brightness": mean_brightness,
            "contrast": contrast,
            "brightness_ok": brightness_ok,
            "contrast_ok": contrast_ok,
            "is_acceptable": brightness_ok and contrast_ok
        }

    def quick_check(self, min_width=300, min_height=300, brightness_range=(50, 200), contrast_range=(30, 150), blur_threshold=100):
        """
        Generuje zbiorczy szybki raport dotyczący jakości obrazu.

        :param min_width: Minimalna szerokość obrazu (w pikselach).
        :param min_height: Minimalna wysokość obrazu (w pikselach).
        :param brightness_range: Akceptowalny zakres jasności.
        :param contrast_range: Akceptowalny zakres kontrastu.
        :param blur_threshold: Minimalna wartość wariancji dla ostrości obrazu.
        :return: Słownik zawierający wyniki poszczególnych testów i ogólną akceptację.
        """
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

    """Pozniej zrobic  z tym dashboard!"""

    def detect_edges(self, sigma=1.0):
        """
        Wykrywa krawędzie na obrazie za pomocą algorytmu wykrywania krawędzi Canny'ego.

        :param sigma: Odchylenie standardowe dla filtru Gaussa. Ustaw, aby dostosować czułość.
        :return: Wykryte krawędzie w obrazie.
        """
        # Bezpośrednie użycie obrazu w skali szarości przechowywanego w self._cv_image
        edges = feature.canny(self._cv_image, sigma=sigma)

        return edges

    def analyze_contrast(self):
        """
        Poprawia kontrast obrazu poprzez rozciągnięcie intensywności pikseli
        pomiędzy 2. a 98. percentylem na pełny zakres intensywności.

        :return: Obraz z poprawionym kontrastem.
        """

        p2, p98 = np.percentile(self._cv_image, (2, 98))
        adjusted = exposure.rescale_intensity(self._cv_image, in_range=(p2, p98))
        return adjusted

    def detect_noise(self):
        """
        Sprawdza poziom szumu na obrazie poprzez porównanie obrazu z jego rozmytą wersją.

        :return: Odchylenie standardowe różnicy między oryginalnym obrazem a rozmytym.
        """
        blurred = filters.gaussian(self._cv_image, sigma=1)
        noise = np.std(self._cv_image - blurred)
        return noise

    def analyze_sharpness(self):
        """
        Analizuje ostrość obrazu za pomocą filtru Sobela.

        :return: Wartość wariancji gradientu (im wyższa, tym ostrzejszy obraz).
        """
        sobel = filters.sobel(self._cv_image)
        sharpness_score = sobel.var()
        return sharpness_score

    def check_overexposure(self, threshold_dark=0.05, threshold_bright=0.95):
        """
        Sprawdza, czy obraz jest przepalony (zbyt jasny) lub zbyt ciemny.

        :param threshold_dark: Minimalna wartość intensywności dla pikseli ciemnych (zakres: 0-1).
        :param threshold_bright: Minimalna wartość intensywności dla pikseli jasnych (zakres: 0-1).
        :return: Słownik z procentem ciemnych i jasnych pikseli.
        """
        dark_pixels = (self._cv_image < threshold_dark).sum()
        bright_pixels = (self._cv_image > threshold_bright).sum()

        total_pixels = self._cv_image.shape[0] * self._cv_image.shape[1]
        percent_dark = (dark_pixels / total_pixels) * 100
        percent_bright = (bright_pixels / total_pixels) * 100

        return {"dark_percent": percent_dark, "bright_percent": percent_bright}

    def evaluate_image_quality(self, min_width=300, min_height=300, brightness_range=(50, 200),
                               contrast_range=(30, 150), blur_threshold=100, noise_threshold=0.05,
                               sharpness_threshold=0.5, overexposure_threshold=10):
        """
        Kompleksowa analiza jakości zdjęcia, która łączy różne aspekty takie jak rozdzielczość,
        kontrast, jasność, ostrość, szum i prześwietlenie.

        :return: Słownik zawierający szczegółowe wyniki analizy i ogólną ocenę jakości zdjęcia.
        """
        resolution = self.check_resolution(min_width, min_height)
        brightness_contrast = self.check_brightness_contrast(brightness_range, contrast_range)
        blur = self.checK_blur(blur_threshold)
        noise = self.detect_noise()
        sharpness = self.analyze_sharpness()
        overexposure = self.check_overexposure()

        # Oceny jakości poszczególnych kryteriów
        quality = {
            "resolution_ok": resolution["is_acceptable"],
            "brightness_contrast_ok": brightness_contrast["is_acceptable"],
            "blur_ok": blur["is_acceptable"],
            "noise_ok": noise <= noise_threshold,
            "sharpness_ok": sharpness >= sharpness_threshold,
            "overexposure_ok": (
                overexposure["dark_percent"] < overexposure_threshold and
                overexposure["bright_percent"] < overexposure_threshold
            ),
        }

        # Ogólna ocena zdjęcia
        quality["overall_quality"] = all(quality.values())

        return {
            "details": {
                "resolution": resolution,
                "brightness_contrast": brightness_contrast,
                "blur": blur,
                "noise": noise,
                "sharpness": sharpness,
                "overexposure": overexposure,
            },
            "quality": quality
        }

