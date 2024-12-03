import streamlit as st
import pandas as pd
from io import BytesIO

# Título de la aplicación
st.title("Procesador de Archivo .xlsx - Cantidad de Productos por SKU y Fecha")

# Subida del archivo .xlsx
uploaded_file = st.file_uploader("Sube un archivo .xlsx", type="xlsx")

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file)
        st.write("Archivo cargado correctamente.")
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        st.stop()

    # Mostrar las columnas detectadas
    st.write("Columnas detectadas:", list(df.columns))

    try:
        # Renombrar las columnas para que coincidan con las esperadas
        column_mapping = {
            "cantidad del producto": "cantidad",
            "fecha": "fecha_venta",
            "sku": "sku"
        }
        df.rename(columns=column_mapping, inplace=True)

        # Validar columnas requeridas
        required_columns = ["fecha_venta", "sku", "cantidad"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Faltan las siguientes columnas requeridas: {missing_columns}")
            st.stop()

        # Convertir las columnas a los tipos adecuados
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce", format='%Y-%m-%d')

        # Crear un rango completo de fechas
        min_date = df["fecha_venta"].min()
        max_date = df["fecha_venta"].max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')

        # Obtener todos los SKUs únicos
        all_skus = df["sku"].unique()

        # Generar todas las combinaciones de fechas y SKUs
        all_combinations = pd.MultiIndex.from_product([all_dates, all_skus], names=["fecha_venta", "sku"])
        all_combinations_df = pd.DataFrame(index=all_combinations).reset_index()

        # Agrupar por SKU y Fecha, sumando cantidades
        grouped_data = df.groupby(["fecha_venta", "sku"]).agg({
            "cantidad": "sum"
        }).reset_index()

        # Unir los datos agrupados con el rango completo
        merged_data = pd.merge(all_combinations_df, grouped_data, on=["fecha_venta", "sku"], how="left").fillna(0)

        # Crear un rango completo de fechas
        full_date_range = pd.DataFrame({'fecha_venta': all_dates})
        aggregated_data = merged_data.groupby(["fecha_venta"]).agg({"cantidad": "sum"}).reset_index()

        # Unir con el rango completo para garantizar que todas las fechas aparezcan
        final_data = pd.merge(full_date_range, aggregated_data, on="fecha_venta", how="left").fillna(0)

        # Filtrar filas con cantidad igual a 0
        final_data = final_data[final_data["cantidad"] > 0]

        # Renombrar columnas para claridad
        final_data.columns = ["Fecha de Venta", "Cantidad Total"]

        # Mostrar los datos procesados
        st.subheader("Cantidad de Productos por SKU y Fecha (sin valores 0):")
        st.dataframe(final_data)

        # Exportar los datos procesados a un archivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            final_data.to_excel(writer, index=False, sheet_name="Datos Procesados")
        processed_data = output.getvalue()

        # Botón de descarga
        st.download_button(
            label="Descargar Archivo Excel",
            data=processed_data,
            file_name="cantidad_por_fecha.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo .xlsx para comenzar.")
