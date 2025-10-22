import streamlit as st
import pandas as pd
from datetime import date
import os
import base64
import gspread
import json
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account




# CONFIGURACIÓN GENERAL
st.set_page_config(page_title="Registro de Asistencia", page_icon="📝")

# ---------------------------------------------------------------------------------
# ESTILOS PERSONALIZADOS
st.markdown("""
<style>
  /* Fondo principal */
  .main { background-color: #F6F6F6; }

  /* Encabezado con logos */
  .brand-header {
      background: #141414;
      border-radius: 10px;
      padding: 10px 20px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
  }
  .brand-header img { height: 60px; }

  /* Título principal */
  h1 {
      color: #1F1F1F;
      text-align: center;
      font-weight: 800;
      margin: 18px 0 12px;
  }

  /* Fecha automática */
  .date-badge {
      display: inline-block;
      background: #E0E2E0;
      border-left: 4px solid #374C3C;
      color: #1F1F1F;
      padding: 10px 14px;
      border-radius: 6px;
      font-weight: 600;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
      margin-bottom: 20px;
  }

  /* Botones generales */
  .stButton>button {
      background-color: #374C3C;
      color: white;
      font-weight: bold;
      border-radius: 6px;
      height: 2.8em;
      width: 100%;
      border: none;
      transition: 0.3s;
  }
  .stButton>button:hover {
      background-color: #4D6650;
      transform: scale(1.02);
  }

  /* Campos de entrada */
  .stTextInput>div>div>input,
  .stSelectbox>div>div>select,
  .stNumberInput>div>div>input {
      border: 1.5px solid #C7C7C7 !important;
      border-radius: 6px !important;
      color: #1F1F1F;
  }

  /* Cuadro de éxito */
  .success-box {
      background-color: #E8F2EB;
      border-left: 6px solid #4D6650;
      border-radius: 6px;
      padding: 16px 20px;
      display: flex;
      align-items: flex-start;
      gap: 14px;
      margin-top: 30px;
      margin-bottom: 20px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  }
}
</style>           
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Forzar modo claro en toda la app */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #F6F6F6 !important;
    color: #1F1F1F !important;
}

/* Asegurar que los inputs tengan texto visible */
input, select, textarea {
    background-color: white !important;
    color: #1F1F1F !important;
}

/* Evitar que el navegador cambie los colores en modo oscuro */
@media (prefers-color-scheme: dark) {
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #F6F6F6 !important;
        color: #1F1F1F !important;
    }
    input, select, textarea {
        background-color: white !important;
        color: #1F1F1F !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# LOGOS MOMA Y MANTRA
def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

moma_b64   = img_b64("data/logo_moma_blanco.png")
mantra_b64 = img_b64("data/logo_mantra_blanco.png")

st.markdown(f"""
    <div class="brand-header">
        <img src="data:image/png;base64,{moma_b64}" alt="MOMA"/>
        <img src="data:image/png;base64,{mantra_b64}" alt="MANTRA"/>
    </div>
""", unsafe_allow_html=True)

st.title("Registro de Asistencia Comercial MOMA Y MANTRA")

# ---------------------------------------------------------------------------------
# CARGA DE BASE DE CÓDIGOS
@st.cache_data
def cargar_base():
    ruta = "data/Base_codigos.xlsx"
    df = pd.read_excel(ruta, sheet_name="Base_codigos")
    return df

df_codigos = cargar_base()
# st.write(st.secrets.keys())
# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_google_sheets():
    # cred_dict = json.loads(st.secrets["GOOGLE_SHEETS_KEY"])
    # cred = service_account.Credentials.from_service_account_info(
        # cred_dict,
    cred = service_account.Credentials.from_service_account_info(
        st.secrets["GOOGLE_SHEETS_KEY"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    cliente = gspread.authorize(cred)
    hoja = cliente.open_by_key("1mff_oUQpx2SU_sG_bMZ5ZJ0rXZzQ_NMAiR1HtIYoS6A").worksheet("Asistencias")
    return hoja


hoja = conectar_google_sheets()

# ---------------------------------------------------------------------------------
# FECHA
fecha = date.today()
st.markdown(f'<div class="date-badge">Fecha registrada automáticamente: {fecha}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# SELECCIONAR TIENDA
tiendas_unicas = sorted(df_codigos["nombre_tienda"].unique())
tienda = st.selectbox(
    "Selecciona tu tienda", 
    options=tiendas_unicas,
    index=None,
    placeholder="Busca el nombre de tu tienda..."
)

# ---------------------------------------------------------------------------------
# SELECCIONAR CÓDIGO DE VENDEDORA
if tienda:
    df_filtrado = df_codigos[df_codigos["nombre_tienda"] == tienda]
    codigo_opcion = st.selectbox(
        "Selecciona tu código de vendedora", 
        options=df_filtrado["nombre_vendedor"].unique(),
        index=None,
        placeholder="Selecciona el código asignado..."
    )

    if codigo_opcion:
        codigo_num = df_filtrado.loc[
            df_filtrado["nombre_vendedor"] == codigo_opcion, 
            "codigo_vendedor"
        ].values[0]

        zona = df_filtrado.loc[
            df_filtrado["nombre_vendedor"] == codigo_opcion, 
            "Zona"
        ].values[0]

        supervisora = df_filtrado.loc[
            df_filtrado["nombre_vendedor"] == codigo_opcion, 
            "Supervisora"
        ].values[0]

        # Guardar en session_state para no perderlos cuando hayan cambios
        st.session_state.zona = str(zona)
        st.session_state.supervisora = str(supervisora)
        
        st.write(f"Código numérico del sistema: **{codigo_num}**")
        st.write(f"Zona: **{zona}**")
        st.write(f"Supervisora: **{supervisora}**")

    else:
        codigo_num = None
else:
    codigo_opcion = None
    codigo_num = None

# ---------------------------------------------------------------------------------
# NOMBRE REAL
nombre_real = st.text_input("Escribe tu nombre completo")

# ---------------------------------------------------------------------------------
# VENTA TOTAL DEL DÍA
venta = st.number_input("Escribe tu venta total del día", min_value=0.0, step=100000.0, format="%.0f")

# ---------------------------------------------------------------------------------
# ESTADOS DE SESIÓN
if "guardado" not in st.session_state:
    st.session_state.guardado = False
if "confirmar_cero" not in st.session_state:
    st.session_state.confirmar_cero = False
if "zona" not in st.session_state:
    st.session_state.zona = ""
if "supervisora" not in st.session_state:
    st.session_state.supervisora = ""


# ---------------------------------------------------------------------------------
# GUARDAR DATOS
if st.session_state.guardado is False:
    if st.button("Guardar Asistencia"):
        if not tienda or not codigo_opcion:
            st.warning("Por favor selecciona la tienda y tu código antes de guardar.")
        elif not nombre_real.strip():
            st.warning("Por favor escribe tu nombre completo antes de guardar.")
        elif venta == 0:
            st.session_state.confirmar_cero = True
            st.markdown("""
            <div style="background-color:#FFF4E0;
                        border-left:6px solid #E6A700;
                        border-radius:8px;
                        padding:12px 16px;
                        margin-top:12px;
                        margin-bottom:6px;
                        color:#5C4400;
                        font-weight:500;">
                ⚠️ Has ingresado una venta igual a $0.<br>
                Si la tienda <strong>NO tuvo venta hoy</strong>, por favor confírmalo a continuación.
            </div>
            """, unsafe_allow_html=True)
        else:
            nuevo_registro = pd.DataFrame({
                "Fecha": [fecha],
                "Tienda": [tienda],
                "Codigo_Num": [codigo_num],
                "Nombre_Codigo": [codigo_opcion],
                "Nombre_Real": [nombre_real.strip()],
                "Venta": [venta],
                "Zona":[zona],
                "Supervisora": [supervisora]

            })

            duplicado = False
            try:
                registros_existentes = hoja.get_all_records()
                for fila in registros_existentes:
                    if fila["Codigo_Num"] == codigo_num and fila["Fecha"] == str(fecha):
                        duplicado = True
                        break
            except Exception as e:
                st.warning("⚠️ No se pudo verificar duplicados correctamente. Guardando de todos modos...")
            
            if duplicado:
                st.error("❌ Ya existe un registro para este código en el día de hoy.")
            else:
                hoja.append_row([
                    str(fecha),
                    str(tienda),
                    str(codigo_num),
                    str(codigo_opcion),
                    str(nombre_real.strip()),
                    str(int(venta)),
                    str(st.session_state.zona),
                    str(st.session_state.supervisora)
                ])
                st.session_state.guardado = True
                st.session_state.confirmar_cero = False

# ---------------------------------------------------------------------------------
# CONFIRMACIÓN DE VENTA 0
if st.session_state.get("confirmar_cero", False) and venta == 0:
    st.markdown("""
    <div style="background-color:#FFF4E0;
                border-left:6px solid #E6A700;
                border-radius:8px;
                padding:14px 18px;
                margin-top:12px;
                margin-bottom:14px;
                color:#5C4400;">
        <strong>Confirmación requerida:</strong><br>
        ¿Deseas registrar tu asistencia con venta igual a <strong>$0</strong>?<br>
    </div>
    """, unsafe_allow_html=True)

    # Botón centrado y estilizado
    st.markdown("""
    <style>
        div[data-testid="stHorizontalBlock"] div:has(> .stButton) {
            display: flex;
            justify-content: center;
        }
        .confirmar-btn>button {
            background-color: #374C3C !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 0.6em 1.6em !important;
            transition: 0.2s ease-in-out;
            margin-top: 10px !important;
        }
        .confirmar-btn>button:hover {
            background-color: #4D6650 !important;
            transform: scale(1.02);
        }
    </style>
    """, unsafe_allow_html=True)

    # Botón de confirmación sin ícono adicional
    with st.container():
        if st.button("Sí, confirmar venta $0 y guardar", key="confirmar_0"):
            nuevo_registro = pd.DataFrame({
                "Fecha": [fecha],
                "Tienda": [tienda],
                "Codigo_Num": [codigo_num],
                "Nombre_Codigo": [codigo_opcion],
                "Nombre_Real": [nombre_real.strip()],
                "Venta": [venta],
                "Zona": [zona],
                "Supervisora": [supervisora]
            })

            duplicado = False
            try:
                registros_existentes = hoja.get_all_records()
                for fila in registros_existentes:
                    if fila["Codigo_Num"] == codigo_num and fila["Fecha"] == str(fecha):
                        duplicado = True
                        break
            except Exception as e:
                st.warning("⚠️ No se pudo verificar duplicados correctamente. Guardando de todos modos...")
            if duplicado:
                st.error("❌ Ya existe un registro para este código en el día de hoy.")
            else:
                hoja.append_row([
                    str(fecha),
                    str(tienda),
                    str(codigo_num),
                    str(codigo_opcion),
                    str(nombre_real.strip()),
                    str(int(venta)),
                    str(st.session_state.zona),
                    str(st.session_state.supervisora)
                ])
                st.session_state.guardado = True
                st.session_state.confirmar_cero = False


# ---------------------------------------------------------------------------------
# PANTALLA DE CONFIRMACIÓN FINAL
if st.session_state.guardado:
    st.markdown("""
        <div style="background-color:#EAF6EC;
                    border-left:6px solid #2E7D32;
                    border-radius:8px;
                    padding:16px 22px;
                    display:flex;
                    align-items:center;
                    gap:14px;
                    margin-top:30px;
                    margin-bottom:18px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.05);">
            <div style="flex-shrink:0;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" 
                     fill="#2E7D32" width="38px" height="38px">
                     <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10
                              10-4.48 10-10S17.52 2 12 2zm-1 15l-4-4 
                              1.41-1.41L11 14.17l5.59-5.59L18 
                              10l-7 7z"/>
                </svg>
            </div>
            <div style="flex:1;">
                <p style="margin:0; font-size:17px; color:#1F1F1F; font-weight:700;">
                    Registro guardado correctamente
                </p>
                <p style="margin:2px 0 0; font-size:14px; color:#333;">
                    Tu asistencia ha sido registrada con éxito.<br>
                    ¡Gracias por tu compromiso!
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.toast("✅ Registro exitoso 🎯")

    st.markdown("<hr style='margin:25px 0;'>", unsafe_allow_html=True)
    if st.button("➕ Hacer nuevo registro"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


