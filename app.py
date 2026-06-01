import streamlit as st
import google.generativeai as genai
import json
import re

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="PalletAI",
    page_icon="🎨",
    layout="centered"
)

# ── Estilos ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f7fafa; }
    .title { font-size: 2.5rem; font-weight: 700; color: #01606A; }
    .subtitle { color: #64748B; font-size: 1rem; margin-bottom: 1.5rem; }
    .swatch-container { display: flex; gap: 12px; flex-wrap: wrap; margin: 1rem 0; }
    .swatch {
        border-radius: 10px;
        width: 80px; height: 80px;
        display: flex; align-items: flex-end;
        justify-content: center;
        padding-bottom: 6px;
        font-size: 10px;
        font-weight: 600;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .color-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        border-left: 5px solid;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .hex-badge {
        font-family: monospace;
        background: #f1f5f9;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #374151;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<p class="title">🎨 PalletAI</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Generador inteligente de paletas de color con narrativa artística</p>', unsafe_allow_html=True)
st.divider()

# ── API Key input ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("Google AI API Key", type="password", placeholder="AIza...")
    st.caption("Tu API key no se almacena. Solo se usa durante esta sesión.")
    st.divider()
    st.markdown("**¿Cómo funciona?**")
    st.markdown("1. Ingresás una descripción\n2. La IA interpreta el concepto\n3. Recibís una paleta de 5 colores con narrativa")

# ── Input del usuario ─────────────────────────────────────────────────────────
st.subheader("✍️ Describí tu concepto")
descripcion = st.text_area(
    label="Descripción",
    placeholder="Ej: atardecer melancólico en el mar, energía de los años 80, bosque en invierno...",
    height=100,
    label_visibility="collapsed"
)

col1, col2 = st.columns([3, 1])
with col2:
    generar = st.button("Generar paleta 🎨", use_container_width=True, type="primary")

# ── Generación de paleta ──────────────────────────────────────────────────────
if generar:
    if not api_key:
        st.error("⚠️ Ingresá tu API Key de Google AI en el panel izquierdo.")
    elif not descripcion.strip():
        st.warning("⚠️ Escribí una descripción para generar la paleta.")
    else:
        with st.spinner("Generando tu paleta..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash-lite")

                prompt = f"""Eres un diseñador visual y teórico del color con amplio conocimiento en psicología del color, arte y diseño gráfico.

El usuario te dará una descripción en lenguaje natural: puede ser una emoción, una escena, una época, un ambiente o cualquier concepto visual.

Tu tarea:
1. Generar una paleta de exactamente 5 colores que represente fielmente ese concepto.
2. Para cada color proporcionar: el código HEX válido, el nombre artístico del tono, y una justificación de 1 a 2 oraciones que explique por qué ese color pertenece a esta paleta (desde una perspectiva emocional, cultural o estética).
3. Responder ÚNICAMENTE con un JSON válido con esta estructura exacta, sin texto adicional ni backticks:
[{{"hex": "#RRGGBB", "nombre": "nombre artístico", "justificacion": "explicación"}}]

Descripción del usuario: {descripcion}"""

                response = model.generate_content(prompt)
                raw = response.text.strip()

                # Limpiar posibles markdown fences
                raw = re.sub(r"```json|```", "", raw).strip()
                colores = json.loads(raw)

                # ── Mostrar paleta ──────────────────────────────────────────
                st.divider()
                st.subheader(f"🖌️ Paleta para: *{descripcion[:60]}{'...' if len(descripcion) > 60 else ''}*")

                # Swatches visuales
                swatches_html = '<div class="swatch-container">'
                for c in colores:
                    hex_val = c.get("hex", "#cccccc")
                    swatches_html += f'<div class="swatch" style="background-color:{hex_val};">{hex_val}</div>'
                swatches_html += '</div>'
                st.markdown(swatches_html, unsafe_allow_html=True)

                # Detalle de cada color
                st.markdown("### Narrativa de colores")
                for c in colores:
                    hex_val = c.get("hex", "#cccccc")
                    nombre = c.get("nombre", "Sin nombre")
                    justificacion = c.get("justificacion", "")
                    st.markdown(f"""
                    <div class="color-card" style="border-left-color:{hex_val};">
                        <strong>{nombre}</strong> &nbsp; <span class="hex-badge">{hex_val}</span>
                        <p style="margin-top:8px; color:#374151; font-size:0.9rem;">{justificacion}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Exportar colores
                st.divider()
                export_text = "\n".join([f"{c['nombre']} — {c['hex']}\n{c['justificacion']}" for c in colores])
                st.download_button(
                    label="📥 Descargar paleta como .txt",
                    data=export_text,
                    file_name="paleta.txt",
                    mime="text/plain"
                )

            except json.JSONDecodeError:
                st.error("Error al procesar la respuesta de la IA. Intentá de nuevo.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("PalletAI — Desarrollado con Streamlit y Google Gemini")