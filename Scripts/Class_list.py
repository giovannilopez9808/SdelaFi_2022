from numpy import array, shape, flipud, round, arange, size, zeros, sum, append
import moviepy.video.io.ImageSequenceClip as Movie_maker
from pandas import DataFrame, read_csv, to_datetime
import matplotlib.pyplot as plt
from os.path import join
import datetime
import os


class city_list:

    def __init__(self, city: str) -> None:
        """

        ##### Contiene los parametros del periodo y zona de análisis de cada región

        ### Inputs
        + city -> nombre de la ciudad de la cual se cargaran los parámetros (str) 

        ### Return

        + self.params -> diccionario con los siguientes atributos:
            + day inital -> día inicial del periodo (str)
            + day final -> dia final del periodo (str)
            + lon -> lista con la longitud del área por analizar [float,float]
            + lat -> lista con la latitud del área por analizar [float,float]
            + delta -> divisiones de las grillas del mapa (float)
            + path data -> direccion donde se encuentran los datos
            + file data -> nombre del archivo de datos
            + path graphics -> direccion donde se guardaran las imagenes

        """
        self.params = {
            "path data": "../Data",
            "file data": "data.csv",
            "path graphics": "../Graphics"
        }
        self.citys = {
            "Parana_2020": {
                "day initial": "2020-06-03",
                "day final": "2020-09-28",
                "lon": [-61, -60],
                "lat": [-33.5, -32.5],
                "delta": 0.25,
            },
            "Parana_2021_May": {
                "day initial": "2021-05-01",
                "day final": "2021-06-01",
                "lon": [-60.75, -60],
                "lat": [-33.25, -32.5],
                "delta": 0.25,
            },
            "Parana_2021_Jun": {
                "day initial": "2021-06-10",
                "day final": "2021-06-17",
                "lon": [-60.25, -60.0],
                "lat": [-33.25, -33.0],
                "delta": 0.05,
            },
            "Nuevo_Leon": {
                "day initial": "2021-03-10",
                "day final": "2021-03-27",
                "city": "Nuevo_Leon",
                "lon": [-100.50, -99.50],
                "lat": [24.50, 25.50],
                "delta": 0.25,
            },
        }
        self.select_city_parameters(city_name=city)

    def select_city_parameters(self, city_name: str) -> None:
        """
        Realiza una union del diccionario con las direcciones de los datos con el diccionario de los parametros para cada ciudad
        """
        self.params.update(self.citys[city_name])

    def get_parameters(self) -> dict:
        return self.params.copy()


class FIRMS_data:

    def __init__(self, parameters: dict, select_nominal_data: bool):
        self.params = parameters
        self.format_dates()
        # Lectura y formateo de los datos
        self.read_data()
        self.select_data()
        if select_nominal_data:
            self.select_data_from_confidence_data()

    def format_dates(self):
        """
        Aplica el formato de fecha a los parametros day initial y day final
        """
        self.params["day initial"] = to_datetime(
            self.params["day initial"])
        self.params["day final"] = to_datetime(
            self.params["day final"])

    def read_data(self):
        """
        Funcion para la lectura de los datos de FIRMS
        """
        filename = join(self.params["path data"],
                        self.params["file data"])
        data = read_csv(filename,
                        usecols=[0, 1, 5, 9])
        self.data = self.format_date_data(data)

    def format_date_data(self, data=DataFrame):
        """
        Funcion que realiza el formato en las fechas y las asigna al indice del dataframe
        """
        data.index = to_datetime(data["acq_date"])
        data = data.drop(columns="acq_date")
        return data

    def select_data(self):
        """
        Selecciona los datos a partir tomando en cuenta el periodo de analisis y la localizacion
        """
        # Seleccion de los datos en el periodo introducido
        self.select_data_from_period()
        # Selección de los datos de acuerdo a el area a analizar
        self.select_data_from_location()

    def select_data_from_period(self):
        """
        Funcion que selecciona los datos en un periodo de tiempo
        """
        self.data = self.data[self.data.index >= self.params["day initial"]]
        self.data = self.data[self.data.index <= self.params["day final"]]

    def select_data_from_location(self):
        """
        Funcion que seleciona los datos en un a partir de la localización
        """
        self.data = self.select_data_from_positions(
            data=self.data,
            name_position="longitude",
            positions=self.params["lon"]
        )
        self.data = self.select_data_from_positions(
            data=self.data,
            name_position="latitude",
            positions=self.params["lat"]
        )

    def select_data_from_positions(self,
                                   data: DataFrame,
                                   name_position: str,
                                   positions: list):
        """
        Funcion que selecciona los datos en un intervalo de posiciones
        """
        data = data[data[name_position] >= positions[0]]
        data = data[data[name_position] <= positions[1]]
        return data

    def select_data_from_confidence_data(self):
        """
        Selecciona solo un tipo de dato del FIRMS dependiendo su confiabilidad
        """
        self.data = self.data[self.data["confidence"] == "n"]

    def get_data_from_date(self, date: str) -> DataFrame:
        return self.data.loc[date].copy()


class Fire_Count:

    def __init__(self, params: dict) -> None:
        """
        Conteo de los datos de FIRMS en una localización fijada.
        Parameters
        ----------
        #### Inputs
        + City_name -> Nombre de la ciudad donde se cargaran los parametros
        + select_nominal_data -> valor para seleccionar solamente los datos de tipo nominal
        + color -> color del numero por imprimir en las graficas
        ---------
        """
        city_name = params["City name"]
        select_nominal_data = params["Select nominal data"]
        color = params["Number color"]
        self.obtain_city_parameters(city_name=city_name)
        self.FIRMS_data = FIRMS_data(parameters=self.params,
                                     select_nominal_data=select_nominal_data)
        self.color = color

    def obtain_city_parameters(self, city_name: str):
        """
        Selecciona los parametros dependiendo del nombre de la ciudad
        """
        city_parameters = city_list(city_name)
        self.params = city_parameters.get_parameters()

    def read_map(self, name="map.png"):
        """
        Lectura del mapa de la region donde se esta realizando el estudio
        """
        # Lectura de la imagen
        filename = join(self.params["path graphics"],
                        name)
        self.map = plt.imread(filename)
        # Obtener las dimensiones de la imagen en pixeles
        self.fig_y, self.fig_x, _ = shape(self.map)
        # Reflexion vertical de la imagen
        self.map = flipud(self.map)
        # Calculo de las grillas de la region por analizar
        self.create_grids()

    def create_grids(self):
        """
        Funcion que crea las grillas de busqueda y realiza la transformacion para el espacio de la imagen
        """
        self.lon_division, self.lon_n = self.delimiter_grids(self.params["lon"],
                                                             self.params["delta"])
        self.lat_division, self.lat_n = self.delimiter_grids(self.params["lat"],
                                                             self.params["delta"])
        self.lon_division_tras = self.traslation_positions(self.lon_division,
                                                           self.params["lon"], self.fig_x)
        self.lat_division_tras = self.traslation_positions(self.lat_division,
                                                           self.params["lat"], self.fig_y)

    def delimiter_grids(self, pos_points: list, delta: float):
        """
        Funcion para obtener el numero de grillas
        """
        pos = round(arange(pos_points[0],
                           pos_points[1] + delta,
                           delta),
                    3)
        n = size(pos)
        return pos, n

    def traslation_positions(self, pos_data: list, pos_parameter: list, resize: int):
        """
        Funcion para redefinir las posiciones de las longitudes y latitudes al espacio de la imagen
        """
        resize = resize / abs(pos_parameter[1] - pos_parameter[0])
        n = size(pos_data)
        pos_data_tras = zeros(n)
        pos_data_tras = (pos_data - pos_parameter[0])*resize
        return pos_data_tras

    def algorithm(self):
        """
        Funcion que realiza el algoritmo de conteo en los distintos archivos e FIRMS y dos formatos de archivos
        NI.csv -----> Conteo de los incencos para distintas fechas
        """
        # Dirección donde se creara la animacion
        self.path_movie = join(self.params["path graphics"],
                               "Movie")
        print("Realizando conteo de incendios")
        # Archivo NI
        results_file = join(self.params["path data"],
                            "NI.csv")
        results_file = open(results_file,
                            "w")
        results_file.write("{},{}\n".format("Dates", "NI"))
        dates = self.obtain_dates()
        print("Inicio del conteo del día {} al {}".format(dates[0].date(),
                                                          dates[-1].date()))
        daily_count = self.FIRMS_data.data.resample("D").count()
        for date in dates:
            # Seleccion de los datos por dia
            try:
                data_per_day = self.FIRMS_data.get_data_from_date(date)
                filename = "{}.csv".format(date.date())
                filename = join(self.params["path data"],
                                "Dates_data",
                                filename)
                data_per_day.to_csv(filename,
                                    index=False)
                # Conteo de los incendios para cada grilla
                self.count_fire(data_per_day)
                # Conteo de los incendios para todo el dia
                daily_sum = sum(self.count)
                # Lectura de la latitud y longitud
                lat = array(data_per_day["latitude"])
                lon = array(data_per_day["longitude"])
            except KeyError:
                lon = array([])
                lat = array([])
                self.count = array([])
                daily_sum = 0
            # Escritura de los resultados
            results_file.write("{},{}\n".format(date.date(),
                                                daily_sum))
            # Traslacion de las cordenadas hacia el espacio de la imagen
            lon = self.traslation_positions(lon,
                                            self.params["lon"],
                                            self.fig_x)
            lat = self.traslation_positions(lat,
                                            self.params["lat"],
                                            self.fig_y)
            # Ploteo del numero de incendios por grilla
            self.number_plot(self.lon_division_tras,
                             self.lat_division_tras,
                             self.count,
                             self.color)
            # Ploteo de cada incendio
            self.plot_points(lon, lat)
            # Ploteo del mapa
            self.plot_map(daily_sum,
                          date.date(),
                          self.path_movie)
        results_file.close()

    def count_fire(self, data):
        """
        Algoritmo para el conteo de los incendios en cada grilla
        """
        # Inicializacion del conteo
        self.count = zeros([self.lon_n, self.lat_n], dtype=int)
        # Longitud de los datos
        for lon_i in range(self.lon_n - 1):
            # Limites de la grilla en la longitud
            lon_j = [self.lon_division[lon_i], self.lon_division[lon_i + 1]]
            for lat_i in range(self.lat_n - 1):
                # Limites de la grilla en la latitud
                lat_j = [
                    self.lat_division[lat_i], self.lat_division[lat_i + 1]
                ]
                # Localizacion de los datos a partir de su longitud
                data_loc = self.FIRMS_data.select_data_from_positions(
                    data, "longitude", lon_j)
                # Localizacion de los datos a partir de su latitud
                data_loc = self.FIRMS_data.select_data_from_positions(
                    data_loc, "latitude", lat_j)
                self.count[lon_i, lat_i] = data_loc["latitude"].count()

    def obtain_dates(self):
        """
        Obtiene las fechas consecutivas en el periodo
        """
        days = (self.params["day final"] -
                self.params["day initial"]).days
        dates = []
        for day in range(days + 1):
            date = self.params["day initial"] + datetime.timedelta(
                days=day)
            dates.append(date)
        return dates

    def plot_points(self, lon=array, lat=array):
        """
        Funcion para plotear los puntos de cada incendio
        """
        plt.scatter(lon, lat, alpha=1, color="#ff0000", marker=".")

    def plot_map(self, sum=10, name="", path=""):
        """
        Funcion para plotear el mapa y guardar la grafica
        """
        plt.xlabel("Longitud")
        plt.ylabel("Latitud ")
        # Ploteo del mapa
        plt.imshow(self.map)

        plt.title("Date {}\nTotal de incendios: {}".format(name, sum))
        # Cambio en las ticks de cada eje
        plt.xticks(self.lon_division_tras, self.lon_division)
        plt.yticks(self.lat_division_tras, self.lat_division)
        plt.xlim(self.lon_division_tras[0], self.lon_division_tras[-1])
        plt.ylim(self.lat_division_tras[0], self.lat_division_tras[-1])
        # Ploteo de el grid
        plt.grid(color="black", ls="--")
        # Guardado de la imagen
        filename = "{}.png".format(name)
        filename = join(path, filename)
        plt.tight_layout()
        plt.savefig(filename,
                    dpi=400)
        plt.clf()

    def number_plot(self,
                    lon_list=[],
                    lat_list=[],
                    count_list=50,
                    color="white"):
        """
        Funcion para plotear el numero de incendios, si este es 0, no ploteara nada
        """
        lon_n = size(lon_list)
        lat_n = size(lat_list)
        for lon_i, counts in zip(range(lon_n - 1), count_list):
            # Localizacion en x
            r_lon = (lon_list[lon_i + 1] + lon_list[lon_i]) / 2
            for lat_i, count in zip(range(lat_n - 1), counts):
                # Localizacion en y
                r_lat = (lat_list[lat_i + 1] + lat_list[lat_i]) / 2
                if count != 0:
                    # Ploteo del texto
                    plt.text(r_lon,
                             r_lat,
                             str(count),
                             fontsize=12,
                             color=color)

    def create_animation(self, name="Fire", delete=True, fps=3):
        """
        Funcion que ejecuta la creacion de la animacion
        """
        print("Creación del video en {}".format(self.params["path graphics"]))
        filenames = sorted(os.listdir(self.path_movie))
        filenames = [join(self.path_movie, filename)
                     for filename in filenames]
        output_file = "{}.mp4".format(name)
        output_file = join(self.path_movie,
                           output_file)
        movie = Movie_maker.ImageSequenceClip(
            filenames,
            fps=fps,
        )
        movie.write_videofile(output_file,
                              logger=None)
        filename = "{}.mp4".format(name)
        filename = join(self.path_movie,
                        filename)
        os.system("mv {} {}".format(filename,
                                    self.params["path graphics"]))
        if delete:
            os.system("rm {}*.png".format(self.path_movie))
