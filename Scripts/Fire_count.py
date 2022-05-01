from Class_list import *
params = {
    "City name": "Nuevo_Leon",
    "Number color": "white",
    "Select nominal data": True,
}
Fire_algorithm = Fire_Count(params)
Fire_algorithm.read_map()
Fire_algorithm.algorithm()
# Fire_algorithm.create_animation(delete=False)
