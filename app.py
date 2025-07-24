
import streamlit as st
import pandas as pd

# Cargar el archivo Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("BASE_DE_DATOS_DE_HORAS.xlsx", sheet_name="Detalle")
    df["NombreCompleto"] = df["Nombre"].str.strip() + " " + df["Apellido"].str.strip()
    return df

df = cargar_datos()

# Diccionario de meses
meses = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

def responder_pregunta(pregunta):
    pregunta_lower = pregunta.lower()

    if "cliente" in pregunta_lower and "horas" in pregunta_lower:
        for cliente in df["Cliente"].dropna().unique():
            if cliente.lower() in pregunta_lower:
                total = df[df["Cliente"].str.lower() == cliente.lower()]["HorasImputadas"].sum()
                return f"Se imputaron {total:.2f} horas al cliente '{cliente}'."

    if "horas" in pregunta_lower and any(mes in pregunta_lower for mes in meses):
        for nombre in df["NombreCompleto"].dropna().unique():
            if nombre.lower() in pregunta_lower:
                for mes_nombre, mes_num in meses.items():
                    if mes_nombre in pregunta_lower:
                        total = df[(df["NombreCompleto"].str.lower() == nombre.lower()) & (df["Mes"] == mes_num)]["HorasImputadas"].sum()
                        return f"{nombre} imputó {total:.2f} horas en {mes_nombre.capitalize()}."

    if "tarea" in pregunta_lower and "periodo" in pregunta_lower:
        resumen = df.groupby("Tarea")["HorasImputadas"].sum().reset_index()
        resumen = resumen.sort_values(by="HorasImputadas", ascending=False)
        return "Resumen de horas imputadas por tarea:\n\n" + resumen.head(10).to_string(index=False)

    return "Lo siento, esta pregunta aún no está cubierta por el prototipo del agente."

# Interfaz
st.title("🧠 Agente de Consulta de Horas Imputadas")
st.write("Hacé una pregunta en lenguaje natural sobre horas imputadas:")

pregunta = st.text_input("Tu pregunta aquí")

if pregunta:
    respuesta = responder_pregunta(pregunta)
    st.success(respuesta)
