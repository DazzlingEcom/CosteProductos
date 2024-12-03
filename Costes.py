import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Procesador de CSV - Costes por SKU y Fecha de Venta")

# Subida del archivo CSV
uploaded_file = st.file_uploader("Sube un archivo CSV", type="csv")

if uploaded_file is not None:
    try:
        # Detectar y leer el archivo con encoding 'ISO-8859-1' y separador ';'
        df = pd.read_csv(uploaded_file, sep=';', quotechar='"', encoding='ISO-8859-1')
        st.write("Archivo leído correctamente.")
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        st.stop()

    # Mostrar columnas detectadas
    st.write("Columnas detectadas:", list(df.columns))

    # Limpiar los nombres de las columnas
    df.columns = df.columns.str.strip().str.lower()

    # Mostrar columnas procesadas
    st.write("Columnas después de limpiar:", list(df.columns))

    try:
        # Renombrar las columnas para que coincidan con las esperadas
        column_mapping = {
            "cantidad del producto": "cantidad",
            "fecha": "fecha_venta",
            "sku": "sku"
        }
        df.rename(columns=column_mapping, inplace=True)

        # Validar columnas requeridas
        required_columns = ["sku", "cantidad", "fecha_venta"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Faltan las siguientes columnas requeridas: {missing_columns}")
            st.stop()

        # Asegurar que las columnas tienen el tipo correcto
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce", format='%d/%m/%Y')

        # Crear una columna para los costos de productos por SKU
        df["costo_producto"] = 0.0

        # Ordenar por fecha y SKU
        df = df.sort_values(by=["fecha_venta", "sku"])

        # Agrupar por SKU y Fecha, sumando cantidades
        grouped_data = df.groupby(["fecha_venta", "sku"]).agg({
            "cantidad": "sum",
            "costo_producto": "sum"
        }).reset_index()

        grouped_data.columns = ["Fecha de Venta", "SKU", "Cantidad Total", "Costo Producto Total"]

        # Crear un resumen de costos totales por fecha
        resumen_costos = grouped_data.groupby("Fecha de Venta")["Costo Producto Total"].sum().reset_index()
        resumen_costos.columns = ["Fecha de Venta", "Costo Total por Día"]

        # Mostrar tablas interactivas en la aplicación
        st.subheader("Datos Agrupados:")
        st.dataframe(grouped_data)

        st.subheader("Resumen de Costos por Fecha:")
        st.dataframe(resumen_costos)

        # Exportar datos procesados
        csv_resumen = resumen_costos.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar Resumen de Costos por Fecha",
            data=csv_resumen,
            file_name="resumen_costos_por_fecha.csv",
            mime="text/csv"
        )

        csv_data = grouped_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar Datos Completos con Costos",
            data=csv_data,
            file_name="costos_por_sku.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
