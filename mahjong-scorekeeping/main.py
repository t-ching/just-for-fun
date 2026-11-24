import os
import flet as ft
from mahj import main

if __name__ == "__main__":
    # Render provides a dynamic port via environment variables.
    # If it doesn't exist, we fall back to port 8000.
    port = int(os.getenv("PORT", 8000))

    # Run the app as a web service accessible to the internet
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
