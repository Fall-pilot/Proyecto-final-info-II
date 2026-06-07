import os
import numpy as np
from scipy.io import loadmat


class ModeloSenales:
    def __init__(self):
        self.senal_3d = None
        self.senal_2d = None
        self.fs = 250
        self.nombre_archivo = ""
        self.nombres_canales = []

    def cargar_senal(self, ruta):
        try:
            self.nombre_archivo = os.path.basename(ruta)

            data = loadmat(ruta) 
            keys = [k for k in data.keys() if not k.startswith('__')]
            if not keys:
                raise ValueError("No se encontraron variables en el archivo .mat")

            raw_senal = data[keys[0]]
            print(f"Variable cargada: '{keys[0]}', forma original: {raw_senal.shape}")

            self.senal_3d = np.squeeze(raw_senal)

            if self.senal_3d.ndim == 1:
                self.senal_2d = self.senal_3d.reshape(1, -1)
                self.nombres_canales = ['Canal 1']

            elif self.senal_3d.ndim == 2:
                if self.senal_3d.shape[0] > self.senal_3d.shape[1]:
                    self.senal_2d = self.senal_3d.T
                else:
                    self.senal_2d = self.senal_3d
                self.nombres_canales = [f'Canal {i+1}' for i in range(self.senal_2d.shape[0])]

            elif self.senal_3d.ndim == 3:
                self.senal_2d = np.mean(self.senal_3d, axis=2)
                self.nombres_canales = [f'Canal {i+1}' for i in range(self.senal_3d.shape[0])]

            print(f"Senal procesada - 2D: {self.senal_2d.shape}")
            return self.senal_2d

        except Exception as e:
            raise Exception(f"Error cargando senal: {str(e)}")

    def seleccionar_segmento(self, canal_idx, punto_inicio, punto_final):
        if self.senal_2d is None:
            raise ValueError("No hay senal cargada")

        if canal_idx >= self.senal_2d.shape[0]:
            raise ValueError(f"Canal {canal_idx} no existe. Maximo: {self.senal_2d.shape[0]-1}")

        datos_canal = self.senal_2d[canal_idx, :]
        punto_inicio = max(0, min(punto_inicio, len(datos_canal)-1))
        punto_final = max(punto_inicio+1, min(punto_final, len(datos_canal)))

        segmento = datos_canal[punto_inicio:punto_final]
        tiempo = np.arange(len(segmento)) / self.fs

        return segmento, tiempo

    def anadir_ruido(self, canal_idx, tipo_ruido='gaussiano', intensidad=0.1):
        if self.senal_2d is None:
            raise ValueError("No hay senal cargada")

        senal_original = self.senal_2d[canal_idx, :].copy()
        senal_ruidosa = senal_original.copy()

        if tipo_ruido == 'gaussiano':
            ruido = np.random.normal(0, intensidad * np.std(senal_original), len(senal_original))
            senal_ruidosa = senal_original + ruido
        elif tipo_ruido == 'impulsivo':
            num_impulsos = int(len(senal_original) * intensidad)
            indices = np.random.choice(len(senal_original), num_impulsos, replace=False)
            senal_ruidosa[indices] = senal_ruidosa[indices] * 2

        return senal_original, senal_ruidosa

    def calcular_promedio_std(self, eje='canales'):
        if self.senal_2d is None:
            raise ValueError("No hay senal cargada")

        if eje == 'canales':
            promedios = np.mean(self.senal_2d, axis=1)
            desviaciones = np.std(self.senal_2d, axis=1)
            etiquetas = self.nombres_canales
        else:
            promedios = np.mean(self.senal_2d, axis=0)
            desviaciones = np.std(self.senal_2d, axis=0)
            etiquetas = np.arange(len(promedios))

        return promedios, desviaciones, etiquetas

    def obtener_num_canales(self):
        return self.senal_2d.shape[0] if self.senal_2d is not None else 0

    def obtener_longitud_tiempo(self):
        return self.senal_2d.shape[1] if self.senal_2d is not None else 0

    def obtener_datos_canal(self, canal_idx):
        if self.senal_2d is not None and 0 <= canal_idx < self.senal_2d.shape[0]:
            return self.senal_2d[canal_idx, :]
        return None

    def obtener_todos_canales(self):
        return self.senal_2d

    def calcular_fft_canal(self, canal_idx):
        if self.senal_2d is None:
            return None, None

        y = self.senal_2d[canal_idx, :]
        N = len(y)
        freqs = np.fft.rfftfreq(N, d=1/self.fs)
        magnitud = np.abs(np.fft.rfft(y))

        return freqs, magnitud

    def obtener_frecuencia_muestreo(self):
        return self.fs

    def set_frecuencia_muestreo(self, nueva_fs):
        self.fs = nueva_fs