import json
import os
import pandas


def createJSON():
    # This code calculates the accumulated percentage of returns
    print("Input the starting date")
    currentYear, currentMonth = inputDate()

    print("Input the percentages month by month")
    print("Type a non number to stop entering percentages - format is 8.15%")

    percentages = []
    jsonData = []
    while True:
        try:
            percentage = float(input("{0}-{1}: ".format(currentYear, currentMonth))) / 100
            percentages.append(percentage)

            jsonData.append({"date": "{0}-{1}-{2}".format(currentYear, currentMonth, 1), "return": percentage})
            currentYear, currentMonth = incrementDates(currentYear, currentMonth)
        except ValueError:
            print("Do you wish to stop entering percentages?")
            print("Type 'y' to exit, anything else to continue.")
            if 'y' in input("Confirm: ").lower():
                break
    saveJSON(jsonData)
    print("\nAll inputs for verification purposes")
    print(percentages)


def analiseJSON(dataList=None):
    if dataList is None:
        dataList = openJSON()

    numberOfYears = round(len(dataList) / 12, 2)
    print("\nData is {0} years old".format(numberOfYears))
    totalReturn = round(getTotalReturn(dataList) * 100, 2)
    monthlyReturn = round(getAverageReturn(dataList) * 100, 2)
    print("\nAll time")
    print("Total return: {0}%\nAverage monthly return: {1}%\n".format(totalReturn, monthlyReturn))
    if numberOfYears > 5:
        totalReturn = round(getTotalReturn(dataList, months=60) * 100, 2)
        monthlyReturn = round(getAverageReturn(dataList, months=60) * 100, 2)
        print("\nPast 5 years")
        print("Total return: {0}%\nAverage monthly return: {1}%\n".format(totalReturn, monthlyReturn))
    if numberOfYears > 1:
        totalReturn = round(getTotalReturn(dataList, months=12) * 100, 2)
        monthlyReturn = round(getAverageReturn(dataList, months=12) * 100, 2)
        print("\nPast year")
        print("Total return: {0}%\nAverage monthly return: {1}%\n".format(totalReturn, monthlyReturn))


def getTotalReturn(dataList, months=0):
    total = 1

    i = 0
    for data in reversed(dataList):
        total = total * (1 + data["return"])
        i += 1
        if i == months:
            break
    return total


def getAverageReturn(dataList, months=0):
    pastXMonths = dataList[-months:]
    sumOfReturn = 0
    for monthlyReturn in pastXMonths:
        sumOfReturn += monthlyReturn["return"]
    averageReturn = sumOfReturn / len(pastXMonths)
    return averageReturn


def inputDate():
    date = input("Enter date in YYYY-MM format: ")
    year, month = map(int, date.split('-'))
    # return datetime.date(year, month, 1)
    return year, month


def incrementDates(year, month, incrementInMonth=1):
    month += incrementInMonth
    if month > 12:
        month -= 12
        year += 1
    return year, month


def saveJSON(data, name=None):
    if name is None:
        name = input("Input a filename: ")
    name.replace(".json", "")
    name += ".json"
    with open(name, 'w') as outfile:
        json.dump(data, outfile)


def openJSON(name=None):
    global dataDir
    if name is None:
        jsonFiles = getJSONs()
        option = menu(jsonFiles, title="Input a filename")
        name = dataDir + jsonFiles[option]
    elif dataDir not in name:
        name = dataDir + name

    with open(name) as json_file:
        try:
            jsonAsDict = json.load(json_file)
            print("\nOpened: {0}".format(name))
        except FileNotFoundError:
            print("\nFile '{0}' doesn't exist".format(name))
            jsonAsDict = {}
        return jsonAsDict


def plotGraph():
    xAxis = []
    dataList = []

    # Choose data to plot
    while True:
        jsonNames = getJSONs()
        jsonNames.insert(0, "Finish adding data")
        option = menu(jsonNames)
        if option == 0:
            break
        else:
            filename = jsonNames[option]
            dataList.append(openJSON(filename))

    print(dataList)


def convertJSONtoPandas():
    data = {}
    jsonFiles = getJSONs()
    longestJSON = {"size": 0, "name": "NAN"}

    # Collect data
    for file in jsonFiles:
        name = file.replace(".json", "")
        jsonFile = openJSON(file)

        # Change the key 'return' for every bit of data
        for month in jsonFile:
            value = month.pop("return")
            month[name] = str(round(value, 4))

        data[name] = jsonFile

        if len(jsonFile) > longestJSON["size"]:
            longestJSON["size"] = len(jsonFile)
            longestJSON["name"] = name

    # Use the longest json file to create dates
    # Iterate through each date in the longest json
    sortedData = []
    for longestMonth in data[longestJSON["name"]]:
        newDict = {"date": longestMonth["date"]}

        for jsonFile in jsonFiles:
            name = jsonFile.replace(".json", "")
            for month in data[name]:
                if newDict["date"] == month["date"]:
                    newDict[name] = month[name]

        sortedData.append(newDict)

    df = pandas.DataFrame(data=sortedData)
    print(df)
    df.to_csv(path_or_buf="data.csv")


def getJSONs():
    global dataDir
    # returns a list of JSONs
    jsonFiles = []
    dirList = os.listdir(dataDir)
    for file in dirList:
        if ".json" in file:
            jsonFiles.append(file)

    return jsonFiles


def main():
    menuList = ["Create JSON", "JSON analysis", "Plot Data", "Convert json to pandas"]
    functionsList = [createJSON, analiseJSON, plotGraph, convertJSONtoPandas]
    menu(menuList, title="Menu", functions=functionsList)


def menu(menuList, title=None, functions=None):
    # Todo run functions if it exists as an option

    menuItems = menuList.copy()  # This separates the two variables
    menuItems.insert(0, "Exit")
    print("")
    if title is not None:
        print("{0} {1} {0}".format("=" * 5, title))
    for i in range(len(menuItems)):
        print("{0}\t{1}".format(i, menuItems[i]))
    option = inputInt(prompt="Option: ")
    if 0 <= option < len(menuItems):
        if option == 0:
            exit()
        else:
            # Everything is valid
            selectedOption = option - 1
            if functions is None:
                return selectedOption
            else:
                functions[selectedOption]()
                return selectedOption

    else:
        option = invalidMenuSelection(menuItems)

    return option


def inputInt(prompt="Input: "):
    while True:
        try:
            inputtedInt = int(input(prompt))
            return inputtedInt
        except ValueError:
            print("Invalid input")


def invalidMenuSelection(menuList):
    # Remove "exit" from list
    menuList.pop(0)
    print("Invalid selection")
    return menu(menuList)


if __name__ == '__main__':
    dataDir = "data/"
    while True:
        main()
