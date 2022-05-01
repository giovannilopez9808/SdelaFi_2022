from Class_list import *


def obtain_ticks(data: DataFrame):
    """
    Función que prepara dos arrays para renombrar las
    etiquetas del eje x de la grafica con las fechas
    """
    years = [index.year
             for index in data.index]
    years = sorted(set(years))
    dates = [to_datetime("{}-01-01".format(year))
             for year in years]
    return dates, years


def format_data(data: DataFrame):
    """
    Aplica el formato de fecha a la columna Dates y la agrega al indice del dataframe
    """
    data.index = to_datetime(data["Dates"])
    data = data.drop(columns="Dates")
    return data


parameters = {
    "file data": "NI.csv",
    "graphics file": "Fire_Per_Year.png",
    "City name": "Nuevo_Leon",
    "Days separation": 7,
    "Y limit": 3000,
    "Delta y": 250,
}
# Lectura de los parametros de cada ciudad
city = city_list(city=parameters["City name"])
# Lectura de los datos
filename = join(city.params["path data"],
                parameters["file data"])
data = read_csv(filename)
data = format_data(data)
data = data.resample("YS").sum()
# Extraccion de las fechas seleccionadas
dates, years = obtain_ticks(data)
# Limites de las graficas
plt.subplots_adjust(left=0.121,
                    right=0.952,
                    bottom=0.162,
                    top=0.924)
# Ploteo de los datos
plt.plot(data.index,
         data["NI"],
         color="#9a031e",
         alpha=0.5)
plt.scatter(data.index,
            data["NI"],
            marker=".",
            c="#9a031e",
            alpha=0.5)
# Limites de las graficas
plt.xlim(dates[0],
         dates[-1])
plt.ylim(0,
         parameters["Y limit"])
# Etiqueta en el eje y
plt.ylabel("Número de Incendios diarios")
# # Cambio en las etiquetas de los ejes x y y
plt.xticks(dates,
           years,
           rotation=45)
plt.yticks(arange(0,
                  parameters["Y limit"]+parameters["Delta y"],
                  parameters["Delta y"]))
# Creación del grid
plt.grid(ls="--",
         color="grey",
         alpha=0.7)
plt.tight_layout()
# Guardado de la grafica
filename = join(city.params["path graphics"],
                parameters["graphics file"])
plt.savefig(filename,
            dpi=400)
