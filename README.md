# Scraper de Canales y Contenido en Pluto TV#
Este proyecto en Python es una herramienta para extraer información de canales y contenido (películas y series) desde el sitio web Pluto TV en la región de Latinoamérica. Utiliza Selenium para automatizar la navegación en el sitio y recopilar datos relevantes.

## Descripción
El script realiza las siguientes tareas:

## Scraping de Canales:

Accede a la página de Pluto TV que lista los canales en vivo.
Expande la lista de categorías de canales.
Extrae y guarda los nombres de los canales en un archivo CSV.
Scraping de Contenido (Películas y Series):

Navega a la sección de contenido bajo demanda.
Extrae detalles de películas y series de varias secciones específicas.
Guarda la información en un archivo CSV, incluyendo título, descripción, duración y enlace.
## Requisitos:
Para ejecutar este script, necesitas los siguientes paquetes de Python:
selenium
webdriver_manager
csv (incluido en la biblioteca estándar de Python)
También necesitarás el navegador Google Chrome y el chromedriver correspondiente para Selenium. El script utiliza webdriver_manager para gestionar automáticamente la instalación del chromedriver.

### Instalación de Dependencias
Instala las dependencias necesarias usando pip:
pip install selenium webdriver_manager

## Clona este repositorio:
git clone https://github.com/tu_usuario/tu_repositorio.git

cd tu_repositorio

Ejecuta el script:


python nombre_del_script.py

Asegúrate de reemplazar nombre_del_script.py con el nombre real del archivo del script.

## Estructura del Código
scrapearCanales(): Realiza el scraping de los nombres de los canales y los guarda en canales_pluto_tv.csv.

configurar_driver(): Configura el navegador Chrome para la sesión de scraping.

click_element(driver, by, value): Función auxiliar para hacer clic en elementos específicos en la página.

cerrar_overlay(driver, wait): Intenta cerrar el overlay que aparece en la interfaz de usuario.

regresar_a_seccion_peliculas(driver, wait): Regresa a la sección de películas después de un scraping.

scrape_movies_from_section(driver, section_xpath, writer, seen_movies): Extrae información sobre películas de una sección específica.

scrape_series_from_section(driver, section_xpath_series, writer, seen_movies): Extrae información sobre series de una sección específica.

main(): Función principal que coordina el flujo de scraping para canales, películas y series.


### Notas
Tiempo de Ejecución: El tiempo total de ejecución puede variar dependiendo de la velocidad de la conexión a internet y la respuesta del sitio web.

Manejo de Errores: Se han implementado manejos básicos de errores para situaciones comunes, como elementos no encontrados o tiempos de espera excedidos.
