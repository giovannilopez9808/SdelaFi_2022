from Class_list import *


def obtain_ticks(data: DataFrame, day_separation: int):
    """
    Función que prepara dos arrays para renombrar las
    etiquetas del eje x de la grafica con las fechas
    """
    # Longitud de datos
    data_len = data["NI"].count()
    # Separación de fechas a imprimir
    loc = arange(0,
                 data_len,
                 day_separation)
    # Si no se encuentra la ultima fecha agregarla
    if data.index[loc[-1]] != data.index[data_len-1]:
        loc = append(loc, data_len-1)
    # Obtener las fechas seleccionadas
    dates = list(data.index[loc])
    return dates


def format_data(data: DataFrame):
    """
    Aplica el formato de fecha a la columna Dates y la agrega al indice del dataframe
    """
    data.index = to_datetime(data["Dates"])
    data = data.drop(columns="Dates")
    return data


parameters = {
    "file data": "NI.csv",
    "file results": "NIA.csv",
    "graphics file": "Fire_Accumulative.png",
    "City name": "Nuevo_Leon",
    "Days separation": 7,
    "Y limit": 2500,
    "Delta y": 250,
}
# Lectura de los parametros de cada ciudad
city = city_list(city=parameters["City name"])
# Lectura de los datos
filename = join(city.params["path data"],
                parameters["file data"])
data = read_csv(filename)
data = format_data(data)
data["NIA"] = data.cumsum()
filename = join(city.params["path data"],
                parameters["file results"])
data.to_csv(filename)
# Extraccion de las fechas seleccionadas
dates = obtain_ticks(data,
                     parameters["Days separation"])
# Ploteo de los datos
plt.plot(list(data.index), list(data["NIA"]),
         color="#9a031e",
         alpha=0.5)
plt.scatter(data.index, list(data["NIA"]),
            marker=".",
            c="#9a031e",
            alpha=0.5)
# Limites de las graficas
plt.xlim(dates[0],
         dates[-1])
plt.ylim(0,
         parameters["Y limit"])
# Etiqueta en el eje y
plt.ylabel("Número de Incendios Acumulados")
# Cambio en las etiquetas de los ejes x y y
# plt.xticks(dates,
#            rotation=45)
plt.yticks(arange(0,
                  parameters["Y limit"]+parameters["Delta y"],
                  parameters["Delta y"]))
# Creación del grid
plt.grid(ls="--",
         color="grey",
         alpha=0.7)
# Guardado de la grafica
filename = join(city.params["path graphics"],
                parameters["graphics file"])
plt.savefig(filename,
            dpi=400)
