import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Procesador de CSV - Cantidad de Productos por SKU y Fecha de Venta")

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

        # Crear un rango de fechas completo
        min_date = df["fecha_venta"].min()
        max_date = df["fecha_venta"].max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')

        # Agrupar por SKU y Fecha, sumando cantidades
        grouped_data = df.groupby(["fecha_venta", "sku"]).agg({
            "cantidad": "sum"
        }).reset_index()

        # Crear un DataFrame con todas las combinaciones de fechas y SKUs
        all_skus = df["sku"].unique()
        all_combinations = pd.MultiIndex.from_product([all_dates, all_skus], names=["fecha_venta", "sku"])
        all_combinations_df = pd.DataFrame(index=all_combinations).reset_index()

        # Unir los datos agrupados con el rango completo
        merged_data = pd.merge(all_combinations_df, grouped_data, on=["fecha_venta", "sku"], how="left").fillna(0)

        # Renombrar las columnas finales
        merged_data.columns = ["Fecha de Venta", "SKU", "Cantidad Total"]

        # Mostrar tablas interactivas en la aplicación
        st.subheader("Cantidad de Productos por SKU y Fecha (Con Fechas Completas):")
        st.dataframe(merged_data)

        # Exportar datos procesados
        csv_data = merged_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar Cantidades por SKU y Fecha",
            data=csv_data,
            file_name="cantidad_por_sku_y_fecha_completo.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
