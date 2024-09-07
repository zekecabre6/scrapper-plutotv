#importamos todo lo necesario
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager



def scrapearCanales():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)

    unique_channel_names = set()

    try:
        driver.get('https://pluto.tv/latam/live-tv')

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.dockPlayerExpandButton-0-2-120")))

        expand_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dockPlayerExpandButton-0-2-120"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", expand_button)
        time.sleep(1)  # Espera breve para asegurar que el scroll esté completo
        expand_button.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//ul[contains(@class, "list-0-2-240")]')))

        # Definimos una lista con los nombres especificos de las categorias
        section_texts = [
            "Destacado", "Pluto TV", "Películas", "Series", "Retro", "Novelas", "Reality",
            "Competencia", "Curiosidad", "Investigación", "Noticias", "Deportes",
            "South Park", "Comedia", "Entretenimiento", "Estilo de Vida", "Anime & Gaming",
            "Teen", "Kids", "Música"
        ]

        # Función para hacer clic en la sección y obtener los nombres de los canales
        def get_channel_names_in_section(section_text):
            try:
                # Encuentra y hace clic en el botón de la sección por su texto[añadimos el nombre y lo usamos para filtrar en el xpath]
                section_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//ul[contains(@class, 'list-0-2-240')]//span[contains(text(), '{section_text}')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", section_button)
                time.sleep(1)  
                section_button.click()

                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="image"]')))
                time.sleep(3)  

                # encontramos todos los elementos de los canales en la sección
                channel_elements = driver.find_elements(By.XPATH, '//div[@class="image"]')

                # Extraemos los nombres de los canales del atributo aria-label
                for channel in channel_elements:
                    aria_label = channel.get_attribute("aria-label")
                    if aria_label:
                        unique_channel_names.add(aria_label)  # Usa el conjunto para evitar duplicados

            except (ElementClickInterceptedException, TimeoutException) as e:
                print(f"Error al obtener nombres de canales en la sección '{section_text}': {e}")

        # Iterar sobre los textos de las secciones y obtiene los nombres de los canales
        for section_text in section_texts:
            print(f"Procesando sección '{section_text}'...")
            get_channel_names_in_section(section_text)

    finally:
        driver.quit()

    # escribimos los nombres de los canales en un archivo CSV
    with open('canales_pluto_tv.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Nombre del Canal:'])
        for name in unique_channel_names:
            writer.writerow([name])

    print("Los nombres de los canales se han guardado en 'canales_pluto_tv.csv'")


def configurar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-cache") #borramos cache para que siempre cargue igual y no afecte al scrapper(puede ser un poco mas lento)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window() #al maximizar la ventana podemos cargar mas peliculas o series
    return driver

def click_element(driver, by, value):
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", element)

def cerrar_overlay(driver, wait):
    try:
        close_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="overlay-container"]//button | //*[@id="overlay-container"]/div/div/div/header/button/svg/path')))
        time.sleep(1)
        close_button.click()
    except Exception:
        print("Botón de cierre no encontrado. Intentando presionar Escape...")
        driver.back()
        time.sleep(1)

def regresar_a_seccion_peliculas(driver, wait):
    try:
        pelis_back_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div/a[contains(@class, 'backButton')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", pelis_back_button)
        pelis_back_button.click()
        time.sleep(1)
    except Exception as e:
        print(f"Error al regresar a la sección de películas: {e}")

def scrape_movies_from_section(driver, section_xpath, writer, seen_movies):
    wait = WebDriverWait(driver, 10)

    try:
        # Espera a que el botón "ver todo" esté visible y clickeable
        click_element(driver, By.XPATH, section_xpath)
        time.sleep(1)  # Pequeña pausa para asegurar que el botón esté visible

        # Encuentra los elementos de película
        movie_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="overlay-container"]//a')))
        total_movies = len(movie_elements)
        print(f"Total de películas encontradas: {total_movies}")

        # Itera a través de todas las películas
        for i in range(1, total_movies  ):  # Comienza desde la primera película
            print(f"pelicula: {i} de {total_movies}")
            try:
                xpath = f'//*[@id="overlay-container"]/div/div/div[1]/ul/li[{i}]/a'
                click_element(driver, By.XPATH, xpath)

                # Extraemos los detalles de la película
                title = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="overlay-container"]//h1'))).text
                print(f'titulo: {title}')
                description = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="overlay-container"]//p'))).text
                print('descripcion correcta')
                
                try:
                    duracion = driver.find_element(By.XPATH, "//li[contains(text(), 'hr')] | //li[contains(text(), 'Temporada')] | //li[contains(text(), 'min')]").text
                except:
                    try:
                        print('fallo buscar duracion 1')
                        duracion = driver.find_element(By.XPATH, "//li[contains(text(), 'Temporada')]").text
                    except:
                        print('fallo buscar duracion 2')
                        duracion="no hay"
                enlace_a =driver.find_element(By.XPATH, "//*[@id='overlay-container']//div//a")
                enlace=enlace_a.get_attribute('href')
                print(enlace)
                
                movie_key = (title, description)  # Crea una clave única para cada película

                if movie_key not in seen_movies:
                    writer.writerow([ title, description, duracion,enlace])  # Escribe los datos en el CSV
                    seen_movies.add(movie_key)  # Añade la película al conjunto de películas vistas
                else:
                    print(f"Película ya encontrada: {title}")

                cerrar_overlay(driver, wait)

            except Exception as e:
                print(f"Error en la película {i}: {e}")

        regresar_a_seccion_peliculas(driver, wait)

    except Exception as e:
        print(f"Error en la sección: {str(e)}")

def scrape_series_from_section(driver, section_xpath_series, writer, seen_movies):
    wait = WebDriverWait(driver, 10)

    try:
        # Espera a que el botón "ver todo" esté visible y clickeable
        click_element(driver, By.XPATH, section_xpath_series)
        time.sleep(1)  # Pequeña pausa para asegurar que el botón esté visible

        # Encuentra los elementos de series
        movie_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="overlay-container"]//a')))
        total_movies = len(movie_elements)
        print(f"Total de series encontradas: {total_movies}")

        # Itera a través de todas las series
        for i in range(1, total_movies ):  
            print(f"serie: {i} de {total_movies}")
            try:
                xpath = f'//*[@id="overlay-container"]/div/div/div[1]/ul/li[{i}]/a'
                click_element(driver, By.XPATH, xpath)

                # Extraemos los detalles de la serie
                try:
                    title = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="overlay-container"]//h1 | //header/h1'))).text
                except:
                    print("error en titulo")
                print(f'titulo {title}')
                try:
                    description = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="overlay-container"]//p'))).text
                    print('descripcion correcta')
                except:
                    print("Error en descripcion")
                try:
                    print('primera opcion duracion')
                    duracion = driver.find_element(By.XPATH, "//li[contains(text(), 'hr')] | //li[contains(text(), 'Temporada')] | //li[contains(text(), 'min')]").text
                except:
                    print('fallo buscar duracion 2')

                    duracion="no hay"
                
                enlace_a =driver.find_element(By.XPATH, "//*[@id='overlay-container']//div//a")
                enlace=enlace_a.get_attribute('href')
                print(enlace)
                
                serie_key = (title, description)  # Creamos una clave única para cada serie

                if serie_key not in seen_movies:
                    writer.writerow([ title, description, duracion,enlace])  # Escribe los datos en el CSV
                    seen_movies.add(serie_key)  # añade las peliculas a un objeto para no agregarlas dos veces
                else:
                    print(f"Serie ya encontrada: {title}")

                cerrar_overlay(driver, wait)

            except Exception as e:
                print(f"Error en la serie {i}: {e}")
                


        regresar_a_seccion_peliculas(driver, wait)

    except Exception as e:
        print(f"Error en la sección: {str(e)}")

def main():
    inicio = time.time()
    scrapearCanales()
    
    
    # cargando seccion peliculas
    driver = configurar_driver()
    driver.get('https://pluto.tv/latam/on-demand')
    driver.implicitly_wait(60)
    time.sleep(5)

    

    # Definir las secciones, utilizando xpath especificos debido a que no suelen cambiar y tiene generacion reactiva con scroll
    secciones_pelis = [
    "//a[@class='viewAllLink-0-2-254' and @type='button' and @tabindex='0' and @href='/on-demand/618da9791add6600071d68b0/6419c584dbdaaa000845cad0']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/631a0596822bbc000747c340']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/604a66306fb8e0000718b7d5']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/6245e3e75b72240007129448']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e98badabe135f0007f6fd38']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/6245bf61a380fd00075eb902']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e2efdab7606430009a60684']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e664a3d461ef80007c74a4b']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e2f057012f8f9000947823a']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e664ad54d9608000711bf62']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e98ba08d29fad000774d8f1']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e45b93b0226550009f458f0']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e45b6c57cbf380009c9fd3c']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e45bb571dbf7b000935ab55']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/60cb966907f6370007c0e05e']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/5e664aac9cbc7000077f8ad9']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/60c0cc32c72308000700c61a']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/60cb97ae9f11af0007902c42']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/62473fdd9c333900071c587e']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/6539313c67bd1a00084d8023']",
    "//a[@href='/on-demand/618da9791add6600071d68b0/6144cbd27bdf170007e1ea12']"
]
    secciones_series = [
    "//a[@href='/on-demand/619043246d03190008131b89/62473ee1a8099000076c0783']",
    "//a[@href='/on-demand/619043246d03190008131b89/625db92c5c4b590007b808c6']",
    "//a[@href='/on-demand/619043246d03190008131b89/63dd2358a8b22700082367ff']",
    "//a[@href='/on-demand/619043246d03190008131b89/60941e09db549e0007ef2dc9']",
    "//a[@href='/on-demand/619043246d03190008131b89/60941dfa8ab0970007f41c59']",
    "//a[@href='/on-demand/619043246d03190008131b89/60941de9e03c74000701ed4f']",
    "//a[@href='/on-demand/619043246d03190008131b89/60941dc7fd0bc30007db1b6d']",
    "//a[@href='/on-demand/619043246d03190008131b89/5e2f061eeb7c04000967bf70']",
    "//a[@href='/on-demand/619043246d03190008131b89/5e45bbf395fb000009945cf0']",
    "//a[@href='/on-demand/619043246d03190008131b89/5f908026a44d9c00081fd41d']"
]



    with open('contenido-pluto.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        
        writer.writerow(['Título', 'Descripción', 'Duración','Enlace'])

        
        seen_movies = set()
    

        # Click en la pestaña de películas
        click_element(driver, By.XPATH, "//span[contains(text(), 'Películas')]")
        for section_xpath in secciones_pelis:
            scrape_movies_from_section(driver, section_xpath, writer, seen_movies)
            # (recarga para que no se buguee)
        driver.execute_script("location.reload()")
        click_element(driver, By.XPATH, "//span[contains(text(), 'Series')]")
        for section_xpath_series in secciones_series:
            scrape_series_from_section(driver, section_xpath_series, writer, seen_movies)
        
    driver.quit()
    # Marca el final del tiempo
    fin = time.time()

    # Calcula el tiempo transcurrido en segundos
    tiempo_transcurrido = fin - inicio

    # Convierte el tiempo transcurrido a horas y minutos
    if tiempo_transcurrido < 3600:
        minutos = tiempo_transcurrido / 60
        print(f"El tiempo transcurrido es: {minutos:.2f} minutos")
    else:
        horas = tiempo_transcurrido / 3600
        print(f"El tiempo transcurrido es: {horas:.2f} horas")

if __name__ == "__main__":
    main()
