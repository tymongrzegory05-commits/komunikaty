#!/usr/bin/env python3
"""
Tworzy ikonę dla aplikacji Komunikaty.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Rozmiary ikony Windows
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

images = []

for size in sizes:
    # Stwórz przezroczyste tło
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rysuj tło (okrąg)
    margin = 2
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                 fill=(70, 130, 180), outline=(50, 100, 150), width=2)
    
    # Rysuj symbol głośnika
    center_x = size[0] // 2
    center_y = size[1] // 2
    
    # Prostokąt głośnika
    speaker_width = size[0] // 5
    speaker_height = size[1] // 4
    speaker_x = center_x - speaker_width - 5
    speaker_y = center_y - speaker_height // 2
    draw.rectangle([speaker_x, speaker_y, speaker_x + speaker_width, speaker_y + speaker_height],
                   fill=(255, 255, 255))
    
    # Trójkąt (stożek dźwięku)
    cone_points = [
        (speaker_x + speaker_width, speaker_y + 2),
        (speaker_x + speaker_width + speaker_width, center_y - speaker_height),
        (speaker_x + speaker_width + speaker_width, center_y + speaker_height)
    ]
    draw.polygon(cone_points, fill=(255, 255, 255))
    
    # Fale dźwiękowe
    if size[0] >= 32:
        wave_x = speaker_x + speaker_width + speaker_width + 5
        # Pierwsza fala
        draw.arc([wave_x, center_y - speaker_height - 2, wave_x + 8, center_y + speaker_height + 2],
                 start=-45, end=45, fill=(255, 255, 255), width=2)
    
    if size[0] >= 48:
        wave_x2 = wave_x + 10
        # Druga fala
        draw.arc([wave_x2, center_y - speaker_height - 4, wave_x2 + 12, center_y + speaker_height + 4],
                 start=-45, end=45, fill=(255, 255, 255), width=2)
    
    images.append(img)

# Zapisz jako .ico
images[0].save('icon.ico', format='ICO', sizes=[(img.width, img.height) for img in images])
print("Utworzono ikonę: icon.ico")
