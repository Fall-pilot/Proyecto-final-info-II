import os
import numpy as np
import pandas as pd
import pydicom
import nibabel as nib
import cv2
from datetime import datetime


class ModeloImagenes:
    def __init__(self):
        self.matriz_3d = None
        self.matriz_3d_uint8 = None
        self.metadata = {}
        self.pixel_spacing = (1.0, 1.0)
        self.slice_thickness = 1.0
        self.ruta_archivo = ""
        self.tipo_imagen = None

    def cargar_dicom(self, ruta):
        try:
            if os.path.isdir(ruta):
                archivos = [os.path.join(ruta, f) for f in os.listdir(ruta) if f.endswith('.dcm')]
                archivos.sort()
                slices = [pydicom.dcmread(f) for f in archivos]
                slices.sort(key=lambda x: int(getattr(x, 'InstanceNumber', 0)))
                self.matriz_3d = np.stack([s.pixel_array for s in slices], axis=0)
                ds = slices[0]
            else:
                ds = pydicom.dcmread(ruta)
                self.matriz_3d = np.expand_dims(ds.pixel_array, axis=0)

            self.ruta_archivo = ruta
            self.tipo_imagen = 'dicom'
            self.metadata = {
                "Study Date": str(getattr(ds, 'StudyDate', 'No disponible')),
                "Study Time": str(getattr(ds, 'StudyTime', 'No disponible')),
                "Series Time": str(getattr(ds, 'SeriesTime', 'No disponible')),
                "Study Modality": str(getattr(ds, 'Modality', 'No disponible')),
                "Study Description": str(getattr(ds, 'StudyDescription', 'No disponible')),
                "Manufacturer": str(getattr(ds, 'Manufacturer', 'No disponible')),
                "Patient ID": str(getattr(ds, 'PatientID', 'No disponible')),
                "Patient Name": str(getattr(ds, 'PatientName', 'No disponible'))
            }

            try:
                study_time_str = self.metadata["Study Time"].split('.')[0]
                series_time_str = self.metadata["Series Time"].split('.')[0]
                study_time = datetime.strptime(study_time_str, '%H%M%S')
                series_time = datetime.strptime(series_time_str, '%H%M%S')
                duracion = series_time - study_time
                self.metadata["Study Duration (s)"] = str(duracion.total_seconds())
            except:
                self.metadata["Study Duration (s)"] = "No calculable"

            if hasattr(ds, 'PixelSpacing'):
                self.pixel_spacing = (float(ds.PixelSpacing[0]), float(ds.PixelSpacing[1]))
            if hasattr(ds, 'SliceThickness'):
                self.slice_thickness = float(ds.SliceThickness)

            self._convertir_a_hounsfield(ds)

            self._normalizar_a_uint8()

            return self.matriz_3d, self.metadata

        except Exception as e:
            raise Exception(f"Error cargando DICOM: {str(e)}")

    def _convertir_a_hounsfield(self, ds):
        slope = getattr(ds, 'RescaleSlope', 1)
        intercept = getattr(ds, 'RescaleIntercept', 0)
        self.matriz_3d = self.matriz_3d.astype(np.float32) * slope + intercept

    def _normalizar_a_uint8(self):
        if self.matriz_3d is None:
            return
        min_val = np.min(self.matriz_3d)
        max_val = np.max(self.matriz_3d)
        if max_val - min_val > 0:
            norm = (self.matriz_3d - min_val) / (max_val - min_val) * 255
            self.matriz_3d_uint8 = norm.astype(np.uint8)
        else:
            self.matriz_3d_uint8 = np.zeros_like(self.matriz_3d, dtype=np.uint8)

    def convertir_dicom_a_nifti(self, ruta_salida=None):
        if self.matriz_3d is None:
            raise ValueError("No hay imagen DICOM cargada")

        if ruta_salida is None:
            base = os.path.splitext(self.ruta_archivo)[0]
            ruta_salida = base + "_convertido.nii"

        nifti_img = nib.Nifti1Image(self.matriz_3d, affine=np.eye(4))
        nib.save(nifti_img, ruta_salida)
        return ruta_salida

    def obtener_dimensiones(self):
        if self.matriz_3d_uint8 is None:
            return (0, 0, 0)
        return self.matriz_3d_uint8.shape

    def obtener_corte_axial(self, indice):
        if self.matriz_3d_uint8 is None:
            return None
        indice = max(0, min(indice, self.matriz_3d_uint8.shape[0] - 1))
        return self.matriz_3d_uint8[indice, :, :]

    def obtener_corte_coronal(self, indice):
        if self.matriz_3d_uint8 is None:
            return None
        indice = max(0, min(indice, self.matriz_3d_uint8.shape[1] - 1))
        return self.matriz_3d_uint8[:, indice, :]

    def obtener_corte_sagital(self, indice):
        if self.matriz_3d_uint8 is None:
            return None
        indice = max(0, min(indice, self.matriz_3d_uint8.shape[2] - 1))
        return self.matriz_3d_uint8[:, :, indice]

    def aplicar_zoom(self, imagen_2d, x1, y1, x2, y2, factor_redimension=2):
        if len(imagen_2d.shape) == 2:
            img_color = cv2.cvtColor(imagen_2d, cv2.COLOR_GRAY2BGR)
        else:
            img_color = imagen_2d.copy()

        cv2.rectangle(img_color, (x1, y1), (x2, y2), (0, 255, 0), 2)

        recorte = imagen_2d[y1:y2, x1:x2]

        nuevo_alto = recorte.shape[0] * factor_redimension
        nuevo_ancho = recorte.shape[1] * factor_redimension
        recorte_redimensionado = cv2.resize(recorte, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LINEAR)

        ancho_mm = (x2 - x1) * self.pixel_spacing[0]
        alto_mm = (y2 - y1) * self.pixel_spacing[1]
        texto_dimensiones = f"{ancho_mm:.1f} mm x {alto_mm:.1f} mm"

        return img_color, recorte_redimensionado, texto_dimensiones

    def segmentar(self, imagen, tipo_umbral, valor_umbral=128):
        if len(imagen.shape) == 3:
            imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

        tipos = {
            'binario': cv2.THRESH_BINARY,
            'binario_inv': cv2.THRESH_BINARY_INV,
            'truncado': cv2.THRESH_TRUNC,
            'tozero': cv2.THRESH_TOZERO,
            'tozero_inv': cv2.THRESH_TOZERO_INV
        }

        tipo = tipos.get(tipo_umbral, cv2.THRESH_BINARY)
        _, img_umbralizada = cv2.threshold(imagen, valor_umbral, 255, tipo)
        return img_umbralizada

    def aplicar_morfologia(self, imagen, tipo_operacion, kernel_size=3):
        if len(imagen.shape) == 3:
            imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        operaciones = {
            'apertura': cv2.morphologyEx(imagen, cv2.MORPH_OPEN, kernel),
            'cierre': cv2.morphologyEx(imagen, cv2.MORPH_CLOSE, kernel),
            'gradiente': cv2.morphologyEx(imagen, cv2.MORPH_GRADIENT, kernel),
            'erosion': cv2.erode(imagen, kernel, iterations=1),
            'dilatacion': cv2.dilate(imagen, kernel, iterations=1)
        }

        return operaciones.get(tipo_operacion, imagen)

    def guardar_metadata_csv(self, ruta_csv):
        os.makedirs(os.path.dirname(ruta_csv) if os.path.dirname(ruta_csv) else '.', exist_ok=True)
        df = pd.DataFrame(list(self.metadata.items()), columns=['Campo', 'Valor'])
        df.to_csv(ruta_csv, index=False, encoding='utf-8')
        return ruta_csv

    def cargar_convencional(self, ruta):
        img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("No se pudo cargar la imagen")

        self.matriz_3d = np.expand_dims(img.astype(np.float32), axis=0)
        self.matriz_3d_uint8 = np.expand_dims(img, axis=0)
        self.tipo_imagen = 'convencional'
        self.metadata = {"tipo": "Imagen convencional", "ruta": ruta}

        return self.matriz_3d_uint8, self.metadata