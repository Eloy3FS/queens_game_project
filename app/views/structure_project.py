import os

def create_project_structure():
    # Ruta base de 'views', asumiendo que ya existe dentro de 'app'
    base_dir = os.path.join('app', 'views')

    # Definir las rutas de los directorios a crear
    directories = [
        os.path.join(base_dir, 'templates'),
        os.path.join(base_dir, 'static'),
        os.path.join(base_dir, 'static', 'css'),
        os.path.join(base_dir, 'static', 'js'),
        os.path.join(base_dir, 'static', 'assets'),
    ]

    # Crear directorios (si no existen)
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Directorio creado o ya existente: {directory}")

    # Crear archivos con contenido en la carpeta 'templates'
    templates_files = {
        os.path.join(base_dir, 'templates', 'base.html'): (
            "<!-- Template base con la estructura general -->\n"
            "<!DOCTYPE html>\n"
            "<html lang='es'>\n"
            "<head>\n"
            "    <meta charset='UTF-8'>\n"
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
            "    <title>Mi Proyecto</title>\n"
            "</head>\n"
            "<body>\n"
            "    <header>\n"
            "        <!-- Header -->\n"
            "    </header>\n"
            "    <main>\n"
            "        {% block content %}{% endblock %}\n"
            "    </main>\n"
            "    <footer>\n"
            "        <!-- Footer -->\n"
            "    </footer>\n"
            "</body>\n"
            "</html>\n"
        ),
        os.path.join(base_dir, 'templates', 'index.html'): (
            "<!-- Página principal: se extiende de base.html -->\n"
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "    <h1>Bienvenido al tablero</h1>\n"
            "    <!-- Agregar más contenido aquí -->\n"
            "{% endblock %}\n"
        )
    }

    for file_path, content in templates_files.items():
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Archivo creado: {file_path}")

    # Crear archivos con contenido en la carpeta 'static'
    static_files = {
        os.path.join(base_dir, 'static', 'css', 'styles.css'): (
            "/* Hoja de estilos custom */\n"
            "body {\n"
            "    font-family: Arial, sans-serif;\n"
            "    margin: 0;\n"
            "    padding: 0;\n"
            "}\n"
        ),
        os.path.join(base_dir, 'static', 'js', 'main.js'): (
            "// Archivo principal de JavaScript\n"
            "document.addEventListener('DOMContentLoaded', function() {\n"
            "    console.log('JavaScript cargado correctamente');\n"
            "});\n"
        )
    }

    for file_path, content in static_files.items():
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Archivo creado: {file_path}")

    # Crear archivos vacíos en el directorio 'static/assets'
    # Ejemplo de archivos vacíos: queen.png, cross.png y error.png
    empty_files_assets = [
        os.path.join(base_dir, 'static', 'assets', 'queen.png'),
        os.path.join(base_dir, 'static', 'assets', 'cross.png'),
        os.path.join(base_dir, 'static', 'assets', 'error.png'),
    ]

    for file_path in empty_files_assets:
        # Se crea el archivo vacío
        open(file_path, "w").close()
        print(f"Archivo vacío creado: {file_path}")

if __name__ == "__main__":
    create_project_structure()
