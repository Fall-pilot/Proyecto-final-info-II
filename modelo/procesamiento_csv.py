import os
import pandas as pd
import numpy as np


class ModeloTabular:
    def __init__(self):
        self.df = None
        self.nombre_archivo = ""
        self.info_df = None
        self.describe_df = None

    def cargar_archivo(self, ruta):
        try:
            self.nombre_archivo = os.path.basename(ruta)
            extension = os.path.splitext(ruta)[1].lower()

            if extension == '.csv':
                self.df = pd.read_csv(ruta)
            elif extension in ['.xlsx', '.xls']:
                self.df = pd.read_excel(ruta)
            else:
                raise ValueError(f"Formato no soportado: {extension}")

            self._generar_info_describe()
            print(f"Archivo cargado: {self.nombre_archivo}, {self.df.shape[0]} filas, {self.df.shape[1]} columnas")
            return self.df

        except Exception as e:
            raise Exception(f"Error cargando archivo: {str(e)}")

    def _generar_info_describe(self):
        if self.df is None:
            return

        info_data = []
        for col in self.df.columns:
            info_data.append({
                'Columna': col,
                'Tipo': str(self.df[col].dtype),
                'No Nulos': self.df[col].count(),
                'Nulos': self.df[col].isnull().sum(),
                '% Nulos': f"{(self.df[col].isnull().sum() / len(self.df)) * 100:.1f}%"
            })
        self.info_df = pd.DataFrame(info_data)

        columnas_numericas = self.df.select_dtypes(include=[np.number]).columns
        if len(columnas_numericas) > 0:
            self.describe_df = self.df[columnas_numericas].describe()
        else:
            self.describe_df = pd.DataFrame({"Mensaje": ["No hay columnas numericas para describir"]})

    def obtener_columnas(self):
        if self.df is None:
            return []
        return self.df.columns.tolist()

    def obtener_datos_columna(self, nombre_columna):
        if self.df is not None and nombre_columna in self.df.columns:
            return self.df[nombre_columna].dropna()
        return None

    def obtener_datos_columnas_multiples(self, nombres_columnas):
        resultados = {}
        for col in nombres_columnas:
            datos = self.obtener_datos_columna(col)
            if datos is not None:
                resultados[col] = datos
        return resultados

    def obtener_datos_scatter(self, columna_x, columna_y):
        if self.df is None:
            return None, None

        if columna_x in self.df.columns and columna_y in self.df.columns:
            datos_validos = self.df[[columna_x, columna_y]].dropna()
            return datos_validos[columna_x], datos_validos[columna_y]
        return None, None

    def obtener_info(self):
        return self.info_df

    def obtener_describe(self):
        return self.describe_df

    def obtener_nombres_columnas_numericas(self):
        if self.df is None:
            return []
        return self.df.select_dtypes(include=[np.number]).columns.tolist()

    def obtener_nombres_columnas_categoricas(self):
        if self.df is None:
            return []
        return self.df.select_dtypes(exclude=[np.number]).columns.tolist()

    def obtener_resumen(self):
        if self.df is None:
            return None
        return {
            'filas': self.df.shape[0],
            'columnas': self.df.shape[1],
            'columnas_numericas': len(self.obtener_nombres_columnas_numericas()),
            'columnas_categoricas': len(self.obtener_nombres_columnas_categoricas()),
            'valores_nulos_totales': self.df.isnull().sum().sum()
        }