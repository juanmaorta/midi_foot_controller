import time
import board
import busio
import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from pmk import PMK
from pmk.platform.rgbkeypadbase import RGBKeypadBase

# Configurar la interfaz MIDI USB
midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], midi_out=usb_midi.ports[1], in_channel=0, out_channel=0)

# Inicializar el teclado Pico RGB Keypad
hardware = RGBKeypadBase()
keypad = PMK(hardware)

# Mapeo de teclas a valores de Control Change (CC) comenzando desde 36
cc_values = list(range(36, 52))  # CC 36 a 51 (ajustar según necesidad)

# Definir colores con brillo ajustado
BRIGHTNESS_LOW = 0.015  # Brillo tenue
BRIGHTNESS_HIGH = 0.5  # Brillo alto al presionar
COLOR_COL1 = (int(255 * BRIGHTNESS_LOW), 0, 0)  # Rojo tenue
COLOR_COL2 = (0, int(255 * BRIGHTNESS_LOW), 0)  # Verde tenue
COLOR_COL3 = (0, 0, int(255 * BRIGHTNESS_LOW))  # Azul tenue
COLOR_COL4 = (int(255 * BRIGHTNESS_LOW), int(255 * BRIGHTNESS_LOW), int(255 * BRIGHTNESS_LOW))  # Blanco tenue

# Estado previo de las teclas
teclas_estado = [False] * 16

# Encender los LEDs con brillo tenue inicialmente
for i in range(16):
    if i % 4 == 0:
        keypad.keys[i].set_led(*COLOR_COL1)
    elif i % 4 == 1:
        keypad.keys[i].set_led(*COLOR_COL2)
    elif i % 4 == 2:
        keypad.keys[i].set_led(*COLOR_COL3)
    elif i % 4 == 3:
        keypad.keys[i].set_led(*COLOR_COL4)
keypad.update()

while True:
    # Leer mensajes MIDI entrantes
    msg = midi.receive()
    if msg and isinstance(msg, ControlChange):
        index = msg.control - 36  # Ajustar al índice de las teclas
        if 0 <= index < 16:
            print(f"ControlChange {msg.control}: {msg.value}")
    
    # Procesar teclas
    for i, key in enumerate(keypad.keys):
        if key.pressed and not teclas_estado[i]:  # Si la tecla se presiona
            midi.send(ControlChange(cc_values[i], 127))  # Enviar CC con valor 127
            print(f"Enviado Control Change {cc_values[i]}: 127")
            teclas_estado[i] = True
            if i % 4 == 0:  # 1a columna
                key.set_led(int(255 * BRIGHTNESS_HIGH), 0, 0)
            elif i % 4 == 1:  # 2a columna
                key.set_led(0, int(255 * BRIGHTNESS_HIGH), 0)
            elif i % 4 == 2:  # 3a columna
                key.set_led(0, 0, int(255 * BRIGHTNESS_HIGH))
            elif i % 4 == 3:  # 4a columna
                key.set_led(int(255 * BRIGHTNESS_HIGH), int(255 * BRIGHTNESS_HIGH), int(255 * BRIGHTNESS_HIGH))
        elif not key.pressed and teclas_estado[i]:  # Si la tecla se suelta
            midi.send(ControlChange(cc_values[i], 0))  # Enviar CC con valor 0
            print(f"Enviado Control Change {cc_values[i]}: 0")
            teclas_estado[i] = False
            if i % 4 == 0:
                key.set_led(*COLOR_COL1)
            elif i % 4 == 1:
                key.set_led(*COLOR_COL2)
            elif i % 4 == 2:
                key.set_led(*COLOR_COL3)
            elif i % 4 == 3:
                key.set_led(*COLOR_COL4)
    keypad.update()  # Actualizar los LEDs
    time.sleep(0.01)  # Pequeño retardo para evitar rebotes
