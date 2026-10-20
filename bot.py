import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Credenciales seguras que se configurarán en la nube (Render)
TOKEN = os.environ.get("WHATSAPP_TOKEN", "TU_TOKEN_TEMPORAL")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "TU_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "token_secreto_magic")


@app.route("/webhook", methods=["GET"])
def verificar_webhook():
  mode = request.args.get("hub.mode")
  token = request.args.get("hub.verify_token")
  challenge = request.args.get("hub.challenge")

  if mode and token:
    if mode == "subscribe" and token == VERIFY_TOKEN:
      return challenge, 200
    else:
      return "Error de verificación", 403
  return "¡El bot de Comercial Magic está activo y funcionando!", 200


@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
  data = request.get_json()
  try:
    mensaje_entrada = (
        data["entry"][0]["changes"][0]["value"]["messages"][0]["text"][
            "body"
        ]
    )
    numero_remitente = data["entry"][0]["changes"][0]["value"]["messages"][0][
        "from"
    ]

    # Procesar respuesta orientada a Comercial Magic
    respuesta = procesar_comercial_magic(mensaje_entrada)
    enviar_mensaje_whatsapp(numero_remitente, respuesta)
  except Exception as e:
    print(f"Error procesando mensaje: {e}")

  return "EVENT_RECEIVED", 200


def procesar_comercial_magic(texto):
  texto = texto.lower()

  # Menú Principal y Saludos
  if (
      "hola" in texto
      or "buenas" in texto
      or "menu" in texto
      or "menú" in texto
      or "magic" in texto
  ):
    return (
        "✨ ¡Bienvenido a *Comercial Magic*! 🪄\nEs un placer atenderte. ¿En qué"
        " podemos ayudarte hoy?\n\n1️⃣ Catálogo de Productos y Ofertas\n2️⃣"
        " Consultar Estado de mi Pedido\n3️⃣ Horarios y Ubicación de la Tienda\n4️⃣"
        " Hablar con un Asesor Comercial"
    )

  # Opción 1: Catálogo
  elif "1" in texto or "catalogo" in texto or "catálogo" in texto:
    return (
        "🛍️ *Catálogo Comercial Magic:*\n• Contamos con gran variedad de"
        " productos al por mayor y detalle.\n• Escríbenos el nombre del"
        " artículo que buscas para verificar disponibilidad y precios en"
        " tiempo real."
    )

  # Opción 2: Pedidos
  elif "2" in texto or "pedido" in texto:
    return (
        "📦 Para consultar el estado de tu envío o pedido, por favor facilítanos"
        " tu *número de boleta* o *cédula/rut* y te daremos información en un"
        " momento."
    )

  # Opción 3: Horarios y Ubicación
  elif "3" in texto or "horario" in texto or "ubicacion" in texto:
    return (
        "🕒 *Horarios de Atención:* Lunes a Sábado de 9:00 AM a 7:00 PM.\n📍"
        " *Ubicación:* Local principal de Comercial Magic.\n¡Te esperamos!"
    )

  # Opción 4: Asesor Humano
  elif "4" in texto or "asesor" in texto or "humano" in texto:
    return (
        "👨‍💼 Claro que sí. Estamos derivando tu consulta con un asesor de"
        " Comercial Magic. Te responderá en breve por este medio."
    )

  else:
    return (
        "No logramos comprender tu mensaje. 🤔 Escribe *'Hola'* para regresar"
        " al menú principal de Comercial Magic."
    )


def enviar_mensaje_whatsapp(destinatario, texto):
  url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
  headers = {
      "Authorization": f"Bearer {TOKEN}",
      "Content-Type": "application/json",
  }
  payload = {
      "messaging_product": "whatsapp",
      "to": destinatario,
      "type": "text",
      "text": {"body": texto},
  }
  requests.post(url, json=payload, headers=headers)


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)