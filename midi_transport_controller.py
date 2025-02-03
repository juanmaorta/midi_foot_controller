import time
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
BRIGHTNESS = 0.5
COLOR_COL1 = (int(255 * BRIGHTNESS), 0, 0)  # Rojo
COLOR_COL2 = (0, int(255 * BRIGHTNESS), 0)  # Verde
COLOR_COL3 = (0, 0, int(255 * BRIGHTNESS))  # Azul
COLOR_COL4 = (int(255 * BRIGHTNESS), int(255 * BRIGHTNESS), int(255 * BRIGHTNESS))  # Blanco

# Estado previo de las teclas
teclas_estado = [False] * 16

while True:
    # Leer mensajes MIDI entrantes
    msg = midi.receive()
    if msg and isinstance(msg, ControlChange):
        index = msg.control - 36  # Ajustar al índice de las teclas
        if 0 <= index < 16:
            brightness = msg.value / 127  # Escalar valor CC a brillo
            if index % 4 == 0:
                keypad.keys[index].set_led(int(255 * brightness), 0, 0)  # Rojo
            elif index % 4 == 1:
                keypad.keys[index].set_led(0, int(255 * brightness), 0)  # Verde
            elif index % 4 == 2:
                keypad.keys[index].set_led(0, 0, int(255 * brightness))  # Azul
            elif index % 4 == 3:
                keypad.keys[index].set_led(int(255 * brightness), int(255 * brightness), int(255 * brightness))  # Blanco
            keypad.update()
            print(f"Recibido Control Change {msg.control}: {msg.value}")
    
    # Procesar teclas
    for i, key in enumerate(keypad.keys):
        if key.pressed and not teclas_estado[i]:  # Si la tecla se presiona
            midi.send(ControlChange(cc_values[i], 127))  # Enviar CC con valor 127
            print(f"Enviado Control Change {cc_values[i]}: 127")
            teclas_estado[i] = True
            if i % 4 == 0:  # 1a columna
                key.set_led(*COLOR_COL1)
            elif i % 4 == 1:  # 2a columna
                key.set_led(*COLOR_COL2)
            elif i % 4 == 2:  # 3a columna
                key.set_led(*COLOR_COL3)
            elif i % 4 == 3:  # 4a columna
                key.set_led(*COLOR_COL4)
        elif not key.pressed and teclas_estado[i]:  # Si la tecla se suelta
            midi.send(ControlChange(cc_values[i], 0))  # Enviar CC con valor 0
            print(f"Enviado Control Change {cc_values[i]}: 0")
            teclas_estado[i] = False
            key.set_led(0, 0, 0)  # Apagar LED
    keypad.update()  # Actualizar los LEDs
    time.sleep(0.01)  # Pequeño retardo para evitar rebotes
