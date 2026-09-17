import streamlit as st
import pandas as pd

# 1. Configuración inicial de la página
st.set_page_config(
    page_title="Tracker de Carrera | UAI",
    page_icon="🎓",
    layout="wide"
)

# 2. Cargar datos desde el CSV
@st.cache_data
def load_data():
    return pd.read_csv("materias.csv")

df = load_data()

# 3. Encabezado principal
st.title("🎓 Plan de Estudio - Ingeniería en Sistemas")
st.caption("Universidad Abierta Interamericana (UAI)")

# 4. Cálculo de Métricas y Progreso
total = len(df)
aprobadas_df = df[df['estado'] == 'Aprobada']
aprobadas = len(aprobadas_df)
en_curso = len(df[df['estado'] == 'En Curso'])
promedio = aprobadas_df['nota'].mean() if aprobadas > 0 else 0.0
porcentaje = (aprobadas / total) if total > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Materias", total)
col2.metric("Materias Aprobadas", f"{aprobadas} / {total}", f"{porcentaje*100:.1f}%")
col3.metric("En Curso", en_curso)
col4.metric("Promedio General", f"{promedio:.2f}")

st.progress(porcentaje)
st.divider()

# 5. Buscador de materias
search_query = st.text_input("🔍 Buscar materia por nombre...", placeholder="Ej: Algoritmos, Física, Bases de Datos...").strip()


# 6. Función para dibujar cada tarjeta de materia (100% Python nativo, sin HTML)
def render_materia_card(row):
    m_id = int(row['id'])
    nombre = row['nombre']
    estado = row['estado']
    nota = int(row['nota'])

    with st.container(border=True):
        st.caption(f"Código: {m_id:02d}")
        st.subheader(nombre)

        if estado == "Aprobada":
            st.success(f"✓ Aprobada — Nota: {nota}")
        elif estado == "En Curso":
            st.warning("⏳ En Curso")
        else:
            st.error("○ Pendiente")

        with st.expander("✏️ Editar estado / nota"):
            c_est, c_not, c_btn = st.columns([2, 1, 1])

            with c_est:
                nuevo_estado = st.selectbox(
                    "Estado",
                    ["Pendiente", "En Curso", "Aprobada"],
                    index=["Pendiente", "En Curso", "Aprobada"].index(estado),
                    key=f"est_{m_id}"
                )

            with c_not:
                nueva_nota = st.number_input(
                    "Nota",
                    min_value=0,
                    max_value=10,
                    value=nota,
                    key=f"not_{m_id}",
                    disabled=(nuevo_estado != "Aprobada")
                )

            with c_btn:
                st.write("")
                st.write("")
                if st.button("Guardar", key=f"btn_{m_id}", use_container_width=True):
                    df.loc[df['id'] == m_id, 'estado'] = nuevo_estado
                    df.loc[df['id'] == m_id, 'nota'] = nueva_nota if nuevo_estado == "Aprobada" else 0
                    df.to_csv("materias.csv", index=False)
                    st.cache_data.clear()
                    st.rerun()


# 7. Despliegue de Materias (Búsqueda o Pestañas por Año)
if search_query:
    st.subheader(f"Resultados de la búsqueda: '{search_query}'")
    resultados = df[df['nombre'].str.contains(search_query, case=False, na=False)]

    if len(resultados) == 0:
        st.info("No se encontraron materias con ese nombre.")
    else:
        cols = st.columns(2)
        for idx, (_, row) in enumerate(resultados.iterrows()):
            with cols[idx % 2]:
                render_materia_card(row)
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["1º Año", "2º Año", "3º Año", "4º Año", "5º Año"])
    tabs_dict = {1: tab1, 2: tab2, 3: tab3, 4: tab4, 5: tab5}

    for anio, tab in tabs_dict.items():
        with tab:
            df_anio = df[df['anio'] == anio]

            st.markdown("### 📘 Primer Cuatrimestre")
            df_c1 = df_anio[df_anio['cuatrimestre'] == 1]
            cols_c1 = st.columns(2)
            for idx, (_, row) in enumerate(df_c1.iterrows()):
                with cols_c1[idx % 2]:
                    render_materia_card(row)

            st.write("")

            st.markdown("### 📙 Segundo Cuatrimestre")
            df_c2 = df_anio[df_anio['cuatrimestre'] == 2]
            cols_c2 = st.columns(2)
            for idx, (_, row) in enumerate(df_c2.iterrows()):
                with cols_c2[idx % 2]:
                    render_materia_card(row)