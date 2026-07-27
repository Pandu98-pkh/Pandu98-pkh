import os
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

# Color Palette Definitions
DARK_BG = "#0A101F"
LIGHT_BG = "#F8FAFC"

DARK_CONTAINER = "#0F172A"
LIGHT_CONTAINER = "#FFFFFF"

DARK_BORDER = "#1E293B"
LIGHT_BORDER = "#E2E8F0"

UI_CYAN = "#22D3EE"
UI_LIGHT_CYAN = "#0891B2"
ACCENT_EMERALD = "#10B981"
PORTRAIT_PURPLE = "#A78BFA"
PORTRAIT_DARK_PURPLE = "#7C3AED"
TEXT_MUTED_DARK = "#94A3B8"
TEXT_MUTED_LIGHT = "#64748B"
TEXT_MAIN_DARK = "#F8FAFC"
TEXT_MAIN_LIGHT = "#0F172A"

def apply_floyd_steinberg_dither(img_gray):
    """Applies Floyd-Steinberg dithering to a grayscale PIL image."""
    arr = np.array(img_gray, dtype=float)
    h, w = arr.shape
    for y in range(h):
        for x in range(w):
            old_val = arr[y, x]
            new_val = 255 if old_val > 127 else 0
            arr[y, x] = new_val
            err = old_val - new_val
            if x + 1 < w:
                arr[y, x + 1] += err * 7 / 16
            if y + 1 < h:
                if x > 0:
                    arr[y + 1, x - 1] += err * 3 / 16
                arr[y + 1, x] += err * 5 / 16
                if x + 1 < w:
                    arr[y + 1, x + 1] += err * 1 / 16
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def generate_fallback_portrait(width=300, height=340):
    """Generates a dithered synthetic tech avatar if input.jpg is missing."""
    img = Image.new('L', (width, height), color=20)
    draw = ImageDraw.Draw(img)
    
    # Outer head silhouette outline
    draw.ellipse([80, 50, 220, 190], fill=180)
    # Shoulders
    draw.ellipse([30, 180, 270, 360], fill=160)
    # Cybernetic accents / matrix grid patterns
    for y in range(0, height, 10):
        draw.line([(0, y), (width, y)], fill=int(80 + 50 * np.sin(y / 15.0)))
    for x in range(0, width, 12):
        draw.line([(x, 0), (x, height)], fill=int(70 + 40 * np.cos(x / 10.0)))
        
    draw.text((100, 140), "Pandu98", fill=255)
    return apply_floyd_steinberg_dither(img)

def process_portrait(image_path="input.jpg", target_size=(240, 280)):
    if os.path.exists(image_path):
        img = Image.open(image_path).convert('L')
        img = ImageEnhance.Contrast(img).enhance(1.3)
        img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        dithered = apply_floyd_steinberg_dither(img)
    else:
        print(f"[{image_path}] not found. Using synthesized tech avatar for dithering.")
        dithered = generate_fallback_portrait(target_size[0], target_size[1])
    return dithered

def dither_to_svg_dots(dithered_img, start_x=870, start_y=160, dot_color="#A78BFA", sample_step=3):
    arr = np.array(dithered_img)
    h, w = arr.shape
    svg_elements = []
    
    for y in range(0, h, sample_step):
        for x in range(0, w, sample_step):
            val = arr[y, x]
            if val > 127: # Lit dot
                cx = start_x + x
                cy = start_y + y
                svg_elements.append(f'<circle cx="{cx}" cy="{cy}" r="1.2" fill="{dot_color}" opacity="0.95"/>')
    return "\n".join(svg_elements)

def build_svg(is_dark=True):
    bg_color = DARK_BG if is_dark else LIGHT_BG
    card_bg = DARK_CONTAINER if is_dark else LIGHT_CONTAINER
    border_color = DARK_BORDER if is_dark else LIGHT_BORDER
    cyan_accent = UI_CYAN if is_dark else UI_LIGHT_CYAN
    text_main = TEXT_MAIN_DARK if is_dark else TEXT_MAIN_LIGHT
    text_muted = TEXT_MUTED_DARK if is_dark else TEXT_MUTED_LIGHT
    portrait_color = PORTRAIT_PURPLE if is_dark else PORTRAIT_DARK_PURPLE

    dithered = process_portrait("S101-2606-08313-S101-2606-08313_DM 4x6 crop 1mb2.jpg", target_size=(250, 290))
    portrait_dots = dither_to_svg_dots(dithered, start_x=860, start_y=180, dot_color=portrait_color, sample_step=3)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&amp;family=Inter:wght@400;600;700&amp;display=swap');
      .bg {{ fill: {bg_color}; }}
      .card {{ fill: {card_bg}; stroke: {border_color}; stroke-width: 1.5px; rx: 12px; }}
      .terminal-header {{ fill: {"#1E293B" if is_dark else "#F1F5F9"}; }}
      .title {{ font-family: 'Fira Code', monospace; font-size: 13px; fill: {text_muted}; font-weight: 600; }}
      .prompt {{ font-family: 'Fira Code', monospace; font-size: 15px; fill: {cyan_accent}; font-weight: 700; }}
      .command {{ font-family: 'Fira Code', monospace; font-size: 15px; fill: {text_main}; font-weight: 600; }}
      .label {{ font-family: 'Fira Code', monospace; font-size: 13.5px; fill: {cyan_accent}; font-weight: 600; }}
      .val {{ font-family: 'Inter', sans-serif; font-size: 14px; fill: {text_main}; font-weight: 400; }}
      .badge-bg {{ fill: {"#1E293B" if is_dark else "#E2E8F0"}; rx: 4px; }}
      .badge-text {{ font-family: 'Fira Code', monospace; font-size: 12px; fill: {ACCENT_EMERALD}; font-weight: 600; }}
      .subtext {{ font-family: 'Inter', sans-serif; font-size: 13px; fill: {text_muted}; }}
      .portrait-frame {{ fill: none; stroke: {cyan_accent}; stroke-width: 1px; stroke-dasharray: 4 4; rx: 8px; }}
    </style>
    <linearGradient id="cyanGlow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{cyan_accent}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{ACCENT_EMERALD}" stop-opacity="0.8"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="1180" height="610" class="bg"/>

  <!-- Main Terminal Window Card -->
  <rect x="25" y="25" width="1130" height="560" class="card"/>

  <!-- Terminal Header Bar -->
  <path d="M 25 37 Q 25 25 37 25 L 1143 25 Q 1155 25 1155 37 L 1155 70 L 25 70 Z" class="terminal-header"/>
  <line x1="25" y1="70" x2="1155" y2="70" stroke="{border_color}" stroke-width="1.5"/>

  <!-- Window Controls -->
  <circle cx="55" cy="47.5" r="6" fill="#FF5F56"/>
  <circle cx="75" cy="47.5" r="6" fill="#FFBD2E"/>
  <circle cx="95" cy="47.5" r="6" fill="#27C93F"/>

  <!-- Window Title -->
  <text x="590" y="52" text-anchor="middle" class="title">profile.sh — live</text>

  <!-- Terminal Body Content -->
  <!-- Command Prompt line -->
  <text x="65" y="115" class="prompt">pandu@secular-dev:~$ <tspan class="command">./profile.sh --user=Pandu98-pkh</tspan></text>

  <!-- Output Details Section -->
  <!-- Name -->
  <text x="65" y="165" class="label">USER_NAME   :</text>
  <text x="210" y="165" class="val" font-weight="700">Pandu Kaya Hakiki</text>

  <!-- Role -->
  <text x="65" y="205" class="label">ROLE        :</text>
  <text x="210" y="205" class="val">Full-Stack Developer &amp; Security Researcher</text>

  <!-- Location -->
  <text x="65" y="245" class="label">LOCATION    :</text>
  <text x="210" y="245" class="val">Bandung / Pasuruan, Indonesia 🇮🇩</text>

  <!-- Education -->
  <text x="65" y="285" class="label">EDUCATION   :</text>
  <text x="210" y="285" class="val">S1 Computer Engineering @ Telkom University</text>

  <!-- Status / Affiliation -->
  <text x="65" y="325" class="label">AFFILIATION :</text>
  <rect x="210" y="308" width="145" height="24" class="badge-bg"/>
  <text x="217" y="324" class="badge-text">Lab Assistant @ SECULAB</text>

  <rect x="365" y="308" width="165" height="24" class="badge-bg"/>
  <text x="372" y="324" class="badge-text">Secretary @ Digistar Club</text>

  <!-- Security Focus -->
  <text x="65" y="365" class="label">SEC_FOCUS   :</text>
  <text x="210" y="365" class="val">Web Application Security &amp; Digital Forensics (CTF)</text>

  <!-- Core Stack -->
  <text x="65" y="405" class="label">CORE_STACK  :</text>
  <text x="210" y="405" class="val" font-family="'Fira Code', monospace" fill="{ACCENT_EMERALD}">React • Python • JavaScript • Tailwind CSS • Node.js • MySQL</text>

  <!-- Divider Line -->
  <line x1="65" y1="440" x2="810" y2="440" stroke="{border_color}" stroke-width="1" stroke-dasharray="6 6"/>

  <!-- Status Bar Line at bottom of terminal -->
  <text x="65" y="480" class="prompt">STATUS      : <tspan fill="{ACCENT_EMERALD}">● ONLINE</tspan> <tspan class="subtext">| Ready for research &amp; collaboration</tspan></text>

  <!-- Terminal Cursor Animation Effect -->
  <rect x="520" y="468" width="8" height="15" fill="{cyan_accent}">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
  </rect>

  <!-- Right Side: Floyd-Steinberg Dithered Portrait Box -->
  <rect x="840" y="110" width="280" height="430" class="card" fill="{"#0B1329" if is_dark else "#F8FAFC"}"/>
  <rect x="850" y="120" width="260" height="410" class="portrait-frame"/>
  <text x="980" y="150" text-anchor="middle" class="label" font-size="12px">[ DITHERED_AVATAR ]</text>

  <!-- Dithered Dots Render -->
  <g>
    {portrait_dots}
  </g>

  <!-- Footer Tag inside Portrait Container -->
  <text x="980" y="505" text-anchor="middle" class="title" font-size="11px">FLOYD-STEINBERG DITHER</text>
  <text x="980" y="520" text-anchor="middle" class="subtext" font-size="10px">1180x610 LIVE TERMINAL UI</text>
</svg>'''

    filename = "dark.svg" if is_dark else "light.svg"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {filename} successfully.")

if __name__ == "__main__":
    build_svg(is_dark=True)
    build_svg(is_dark=False)
