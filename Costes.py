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

    # Mostrar columnas detectadas y vista previa
    st.write("Columnas detectadas:", list(df.columns))
    st.write("Vista previa del archivo:")
    st.dataframe(df.head())

    try:
        # Validar columnas requeridas
        required_columns = ["SKU", "cantidad", "fecha_venta"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Faltan las siguientes columnas requeridas: {missing_columns}")
            st.stop()

        # Asegurar que las columnas tienen el tipo correcto
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce", format='%d/%m/%Y')

        # Crear una columna editable para los costos de productos por SKU
        df["costo_producto"] = 0.0

        # Ordenar por fecha y SKU
        df = df.sort_values(by=["fecha_venta", "SKU"])

        # Agrupar por fecha y SKU, sumando cantidades
        grouped_data = df.groupby(["fecha_venta", "SKU"]).agg({
            "cantidad": "sum",
            "costo_producto": "sum"
        }).reset_index()

        grouped_data.columns = ["Fecha de Venta", "SKU", "Cantidad Total", "Costo Producto Total"]

        # Crear un resumen de costos totales por fecha
        resumen_costos = grouped_data.groupby("Fecha de Venta")["Costo Producto Total"].sum().reset_index()
        resumen_costos.columns = ["Fecha de Venta", "Costo Total por Día"]

        # Mostrar tablas interactivas en la aplicación
        st.subheader("Completa los Costos por SKU:")
        edited_data = st.experimental_data_editor(grouped_data, num_rows="dynamic", key="editor")

        st.subheader("Resumen de Costos por Fecha:")
        resumen_costos = edited_data.groupby("Fecha de Venta")["Costo Producto Total"].sum().reset_index()
        resumen_costos.columns = ["Fecha de Venta", "Costo Total por Día"]
        st.dataframe(resumen_costos)

        # Exportar datos procesados
        csv_resumen = resumen_costos.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar Resumen de Costos por Fecha",
            data=csv_resumen,
            file_name="resumen_costos_por_fecha.csv",
            mime="text/csv"
        )

        csv_data = edited_data.to_csv(index=False).encode("utf-8")
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