import cv2
import numpy as np

# Mappatura dei 7 segmenti
DIGITS_LOOKUP = {
    (1,1,1,0,1,1,1): '0',
    (0,0,1,0,0,1,0): '1',
    (1,0,1,1,1,0,1): '2',
    (1,0,1,1,0,1,1): '3',
    (0,1,1,1,0,1,0): '4',
    (1,1,0,1,0,1,1): '5',
    (1,1,0,1,1,1,1): '6',
    (1,0,1,0,0,1,0): '7',
    (1,1,1,1,1,1,1): '8',
    (1,1,1,1,0,1,1): '9'
}

def recognize_display(image_path):
    # 1. Carica immagine
    image = cv2.imread(image_path)
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur  = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    h, w = thresh.shape
    digit_w = w // 4  # larghezza di ciascuna cifra

    result = []
    for i in range(4):
        # ROI per la i-esima cifra
        x_start = i * digit_w
        x_end   = (i+1) * digit_w
        roi = thresh[0:h, x_start:x_end]

        # definizione delle 7 aree segmenti RELATIVE
        seg_coords = [
            ((int(0.30*digit_w), int(0.05*h)),
             (int(0.70*digit_w), int(0.15*h))),  # top
            ((int(0.75*digit_w), int(0.15*h)),
             (int(0.85*digit_w), int(0.45*h))),  # top-right
            ((int(0.75*digit_w), int(0.55*h)),
             (int(0.85*digit_w), int(0.85*h))),  # bottom-right
            ((int(0.30*digit_w), int(0.85*h)),
             (int(0.70*digit_w), int(0.95*h))),  # bottom
            ((int(0.15*digit_w), int(0.55*h)),
             (int(0.25*digit_w), int(0.85*h))),  # bottom-left
            ((int(0.15*digit_w), int(0.15*h)),
             (int(0.25*digit_w), int(0.45*h))),  # top-left
            ((int(0.30*digit_w), int(0.45*h)),
             (int(0.70*digit_w), int(0.55*h)))   # middle
        ]

        on = []
        for (p1, p2) in seg_coords:
            x1, y1 = p1; x2, y2 = p2
            seg_roi = roi[y1:y2, x1:x2]
            # percentuale di pixel bianchi
            frac = cv2.countNonZero(seg_roi) / float((x2-x1)*(y2-y1))
            on.append(1 if frac > 0.5 else 0)

        # Decodifica cifra
        digit = DIGITS_LOOKUP.get(tuple(on), '?')

        # Verifica punto decimale (in basso a destra)
        dp_x1 = int(0.85*digit_w); dp_y1 = int(0.90*h)
        dp = roi[dp_y1:h, dp_x1:digit_w]
        dp_frac = cv2.countNonZero(dp) / float(dp.size)
        has_dot = dp_frac > 0.5

        result.append((digit, has_dot))

    # Ricostruisci stringa con il punto
    output = ""
    for idx, (d, dot) in enumerate(result):
        output += d
        if dot:
            output += "."
    # rimuove eventuale "." finale
    output = output.rstrip(".")

    return output

if __name__ == "__main__":
    path = "display.jpg"
    value = recognize_display(path)
    print("Valore letto:", value)
