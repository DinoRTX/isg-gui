DARK = {
    "background": "#1e1e1e",
    "surface": "#2b2b2b",

    "text": "#ffffff",
    "text_secondary": "#bdbdbd",

    "accent": "#00aaff",
    "accent_hover": "#0095dd",

    "button_bg": "#3a3a3a",
    "button_hover": "#4a4a4a",
    "button_pressed": "#2a2a2a",

    "drop_background": "#2b2b2b",
    "drop_border": "#666666",
    "drop_border_active": "#00aaff",

    "success": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c"
}

LIGHT = {
    "background": "#f2f2f2",
    "surface": "#ffffff",

    "text": "#202020",
    "text_secondary": "#555555",

    "accent": "#0078d4",
    "accent_hover": "#0060aa",

    "button_bg": "#dddddd",
    "button_hover": "#cccccc",
    "button_pressed": "#bbbbbb",

    "drop_background": "#ffffff",
    "drop_border": "#999999",
    "drop_border_active": "#0078d4",

    "success": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c"
}

GLITCH = {
    **DARK,
    "accent": "#ff00ff",
    "drop_border_active": "#00ff00",
    "button_hover": "#6a006a"
}

THEMES = {
    "Dark": DARK,
    "Light": LIGHT,
    "Glitch": GLITCH
}

THEME = THEMES["Dark"]

def get_style_sheet(theme_dict=None):
    if theme_dict is None:
        theme_dict = THEME
    return f"""
    QWidget {{
        background-color: {theme_dict["background"]};
        color: {theme_dict["text"]};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    QPushButton {{
        background-color: {theme_dict["button_bg"]};
        color: {theme_dict["text"]};
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background-color: {theme_dict["button_hover"]};
    }}
    QPushButton:pressed {{
        background-color: {theme_dict["button_pressed"]};
    }}
    QLabel#dropLabel {{
        border: 2px dashed {theme_dict.get("drop_border", "#666666")};
        border-radius: 12px;
        background-color: {theme_dict.get("drop_background", "#2b2b2b")};
        padding: 20px;
        font-size: 15px;
    }}
    QProgressBar {{
        border: 1px solid #555555;
        border-radius: 4px;
        text-align: center;
        height: 20px;
    }}
    QProgressBar::chunk {{
        background-color: {theme_dict.get("accent", "#00aaff")};
    }}
    """