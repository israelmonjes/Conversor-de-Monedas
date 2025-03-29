import requests
import flet as ft
import json
import os
import matplotlib.pyplot as plt
import matplotlib
import base64
from io import BytesIO

# Usar el backend sin GUI de Matplotlib
matplotlib.use("Agg")

def obtener_tasa(codigo_origen, codigo_destino):
    url = f"https://api.exchangerate-api.com/v4/latest/{codigo_origen}"
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        return datos['rates'].get(codigo_destino, None)
    except Exception:
        return None

def guardar_historial():
    with open("historial.json", "w") as f:
        json.dump(historial, f)

def cargar_historial():
    global historial
    if os.path.exists("historial.json"):
        with open("historial.json", "r") as f:
            historial = json.load(f)
            for item in historial:
                lista_historial.controls.append(ft.Text(item))

def convertir_moneda(evento, page):
    try:
        cantidad = float(entrada_cantidad.value)
        moneda_origen = dropdown_origen.value
        moneda_destino = dropdown_destino.value
        
        tasa = obtener_tasa(moneda_origen, moneda_destino)
        if tasa:
            resultado = cantidad * tasa
            etiqueta_resultado.value = f"{cantidad} {moneda_origen} = {resultado:.2f} {moneda_destino}"
            nueva_conversion = f"{cantidad} {moneda_origen} → {resultado:.2f} {moneda_destino}"
            historial.append(nueva_conversion)
            lista_historial.controls.append(ft.Text(nueva_conversion))
            guardar_historial()
        else:
            etiqueta_resultado.value = "No se pudo obtener la tasa de cambio."
        page.update()
    except ValueError:
        etiqueta_resultado.value = "Ingrese un número válido."
        page.update()

def graficar_tendencia(evento, page):
    moneda_origen = dropdown_origen.value
    moneda_destino = dropdown_destino.value
    fig, ax = plt.subplots()
    
    tasas = [obtener_tasa(moneda_origen, moneda_destino) for _ in range(10)]
    tasas = [t if t else tasas[0] for t in tasas]  # Evitar valores None
    
    if None in tasas or len(set(tasas)) == 1:
        etiqueta_resultado.value = "No se pudo obtener la información de la tasa."
        page.update()
        return
    
    ax.plot(range(1, 11), tasas, marker='o', linestyle='-', color='blue')
    ax.set_title(f"Tendencia de {moneda_origen} a {moneda_destino}")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Valor")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    dialog = ft.AlertDialog(
        title=ft.Text(f"Tendencia de {moneda_origen} a {moneda_destino}"),
        content=ft.Image(src_base64=img_base64, width=500, height=400),
        actions=[ft.TextButton("Cerrar", on_click=lambda e: page.dialog.hide())]
    )
    page.dialog = dialog
    page.dialog.show()
    page.update()

def main(page: ft.Page):
    global entrada_cantidad, dropdown_origen, dropdown_destino, etiqueta_resultado, lista_historial, historial
    page.title = "Conversor de Monedas"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 500
    page.window_height = 700
    
    entrada_cantidad = ft.TextField(label="Cantidad", width=250, text_align=ft.TextAlign.CENTER)
    dropdown_origen = ft.Dropdown(
        label="Moneda origen", 
        options=[ft.dropdown.Option("USD"), ft.dropdown.Option("EUR"), ft.dropdown.Option("GTQ"), ft.dropdown.Option("MXN"), ft.dropdown.Option("JPY")],
        width=120
    )
    dropdown_destino = ft.Dropdown(
        label="Moneda destino", 
        options=[ft.dropdown.Option("USD"), ft.dropdown.Option("EUR"), ft.dropdown.Option("GTQ"), ft.dropdown.Option("MXN"), ft.dropdown.Option("JPY")],
        width=120
    )
    
    boton_convertir = ft.ElevatedButton("Convertir", on_click=lambda e: convertir_moneda(e, page), bgcolor="blue", color="white")
    boton_graficar = ft.ElevatedButton("Ver Tendencia", on_click=lambda e: graficar_tendencia(e, page), bgcolor="green", color="white")
    etiqueta_resultado = ft.Text("Resultado aparecerá aquí", size=20, weight=ft.FontWeight.BOLD, color="yellow")
    lista_historial = ft.Column(scroll=ft.ScrollMode.ALWAYS, spacing=5)
    historial = []
    cargar_historial()
    
    page.add(
        ft.Container(
            ft.Column([
                ft.Text("💰 Conversor de Monedas 💱", size=24, weight=ft.FontWeight.BOLD, color="cyan"),
                entrada_cantidad,
                ft.Row([dropdown_origen, dropdown_destino], alignment=ft.MainAxisAlignment.CENTER),
                boton_convertir,
                boton_graficar,
                etiqueta_resultado,
                ft.Text("📜 Historial de conversiones", size=18, weight=ft.FontWeight.BOLD, color="lightgreen"),
                lista_historial
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            padding=20,
            alignment=ft.alignment.center,
            border_radius=10,
            bgcolor="#222"
        )
    )

ft.app(target=main)
