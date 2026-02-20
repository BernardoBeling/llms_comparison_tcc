def ui_theme(request):
    """
    Retorna o tema atual para templates.
    Ordem:
      1) session
      2) cookie
      3) default light
    """
    theme = request.session.get("ui_theme")
    if not theme:
        theme = request.COOKIES.get("ui_theme")
    if theme not in ["light", "dark"]:
        theme = "light"
    return {"ui_theme": theme}
