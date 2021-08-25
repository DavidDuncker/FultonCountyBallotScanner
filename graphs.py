import json
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates


if __name__ == "__main__":
    filepath = "/home/dave/PycharmProjects/FultonCountyBallotScanner/data/rolling_average_2000.json"
    file = open(filepath, 'r')
    rolling_average = json.loads(file.read())
    file.close()

    tabulator = "5164"

    for column in rolling_average[tabulator].keys():
        while(0 in rolling_average[tabulator][column]):
            rolling_average[tabulator][column].remove(0)

    datetimes = [datetime.strptime(date, "%m/%d/%y %H:%M:%S") for date in rolling_average[tabulator]["time"]]

    fig, ax = plt.subplots()
    ax.plot(datetimes, rolling_average[tabulator]["Biden"])
    plt.xticks(rotation=70)
    plt.xlabel("Time of current ballot")
    plt.ylabel("Biden average in previous 2000 ballots")
    plt.title(f"2000-ballot trailing average percentage of Biden votes\nTabulator {tabulator}")
    observer_incident = "11/03/20 22:40:00"
    observer_incident = datetime.strptime(observer_incident, "%m/%d/%y %H:%M:%S")
    vlabel = "11/03/20 10:40:00; when observers were kicked out"
    plt.vlines(observer_incident, 0, 100, linestyles="dashed", label=vlabel)
    plt.legend()
    ax.tick_params(axis="x", which="both", rotation=70)
    ax.tick_params(axis="x", which="minor", labelsize=8)
    ax.tick_params(axis="x", which="major", labelsize=12)

    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    plt.show()

