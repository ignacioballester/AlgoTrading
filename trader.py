import backtrader as bt
import datetime as datetime
from Strategies import MACDStrategy, RSI_strategy, SMAstrategy
import Analysis
import os
import sys

# Information to print at the beginning of running the trader for future reference.
def printInfo():
    nameStrat = str(cerebro.strats[0][0][0]).split(".")[2]
    print("*"*30 + "  STRATEGY: "+ nameStrat[:len(nameStrat)-2]+"  " + "*"*30)
    directoryName = directory[5:len(directory)-1]
    if directoryName == "Testing":
        print("Tested on: {}".format(os.listdir(directory)))
    else:
        print("Tested on: "+ directoryName)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Save all data in console in corresponding folder: ./Stats/<Strategy>
def saveToTxt():
    nameStrat = str(cerebro.strats[0][0][0]).split(".")[2]
    filename  = "Stats/" +nameStrat[:len(nameStrat)-2] + ".txt"
    lastresult = ""
    results = ""
    with open('Stats/last_result.txt') as fp:
        lastresult = fp.read()
        fp.close()

    if os.path.isfile(filename):
        with open(filename) as fp:
            results = fp.read()
            fp.close()

    lastresult += "\n"
    lastresult += results

    with open(filename, 'w') as fp:
        fp.write(lastresult)
        fp.close()


if __name__ == '__main__':
    # start saving console prints to Stats/last_result.txt.
    # Uncomment to print results in console.
    sys.stdout = open('Stats/last_result.txt', 'w')

    # choose end and start date for the trader to compute
    startdate = datetime.datetime(2017, 8, 4)
    enddate = datetime.date.today()

    # initialize Cerebro
    cerebro = bt.Cerebro()

    # choose stock market directory to test strategy
    directory = "data/S&P 500/"

    # Create a Data Feed for each file in directory
    data=[]
    for filename in os.listdir(directory):
        if filename == 'AAPL.csv':
            plot = True
            data = bt.feeds.YahooFinanceCSVData(
                dataname=directory + filename,
                fromdate=startdate,
                todate=enddate,
                reverse=False,
                plot = True )
        else:
            data = bt.feeds.YahooFinanceCSVData(
                dataname=directory + filename,
                fromdate=startdate,
                todate=enddate,
                reverse=False,
                plot=False)
        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(50000)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0055)

    # add analyzers
    Analysis.startAnalyzing(cerebro)

    # Add a strategy
    cerebro.addstrategy(MACDStrategy.MACDStrategy)

    printInfo()

    # Run over everything
    strategies = cerebro.run(max_cpu=4, optreturn=True)
    print()
    # print analysis
    try:
        Analysis.printAnalysis(strategies[0])
    except:
        print("No analysis possible!")

    # Get final portfolio Value
    portvalue = cerebro.broker.getvalue()

    # save data in console
    sys.stdout.close()
    saveToTxt()

    # Uncomment if you wan to plot the end results
    # cerebro.plot(style='candlestick')

