from pandas import read_csv, DataFrame
import matplotlib.pyplot as plt
from os.path import join


def select_period_data(data: DataFrame, params: dict) -> DataFrame:
    subdata = data[data.index >= params["day initial"]]
    subdata = subdata[subdata.index < params["day final"]]
    return subdata


def format_headers(data: DataFrame) -> DataFrame:
    headers = {"SE": "Sureste",
               "NE": "Noreste",
               "CE": "Centro",
               "NO": "Noroeste",
               "SO": "Suroeste",
               "NO2": "Noroeste 2",
               "NTE": "Norte",
               "NE2": "Noreste 2",
               "SE2": "Sureste 2",
               "SO2": "Suroeste 2",
               "SE3": "Sureste 3",
               "SUR": "SUR",
               "NTE2": "Norte 2",
               "NE3": "Noreste 3",
               }
    data = data.rename(columns=headers)
    return data


params = {"path data": "../Data",
          "path graphics": "../Graphics",
          "file data": "PM10_2021.csv",
          "file graphics": "PM10.png",
          "day initial": "2021-03-01",
          "day final": "2021-04-01",
          "Stations": {"Suroeste": "#f72585",
                       "Suroeste 2": "#480ca8",
                       "Centro": "#3f37c9",
                       "Norte 2": "#9d0208",
                       "Noroeste 2": "#e85d04",
                       "Sureste": "#76c893",
                       "Noreste 2": "#006400"}}

filename = join(params["path data"],
                params["file data"])
data = read_csv(filename,
                index_col=0,
                parse_dates=True)
data = select_period_data(data,
                          params)
data = format_headers(data)
data = data.resample("D").mean()
index_list = [0, 6, 13, 19, 25, -1]
dates = [data.index[index]
         for index in index_list]
yticks = [value
          for value in range(0, 300, 25)]
plt.subplots(figsize=(10, 5))
for station in params["Stations"]:
    plt.plot(data.index,
             data[station],
             ls="--",
             marker=".",
             markersize=7,
             label=station)
plt.legend(frameon=False,
           ncol=7,
           fontsize=9,
           loc="upper left")
plt.ylim(0, 250)
plt.xlim(data.index[0],
         data.index[-1])
plt.xticks(dates)
plt.yticks(yticks)
plt.ylabel("PM$_{10}$ $(\\mu g/m^3)$")
plt.grid(ls="--",
         color="#000000",
         alpha=0.5)
plt.tight_layout()
filename = join(params["path graphics"],
                params["file graphics"])
plt.savefig(filename,
            dpi=400)
