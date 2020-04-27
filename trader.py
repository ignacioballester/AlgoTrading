import argparse

import backtrader as bt
import datetime as datetime
from RSI_strategy import RSI_strategy
from SMA_strategy import SMA_strategy
from IndicatorBacktesting import IndicatorBacktesting
from TestStrategy import TestStrategy
#from DownloadData import *

import os


class MarginSizer(bt.sizers.FixedSize):
    params = (('percent', 0.10),
            )
    def _getsizing(self, comminfo, cash, data, isbuy):
        margin = comminfo.get_margin(data.close[0])
        print(margin)
        #size =(cash*self.p.percent)/(margin*(1/leverage))
        position = self.broker.getposition(data)
        return 1

def printTradeAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    # Get the results we are interested in
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total, 2)
    strike_rate = round((total_won / total_closed) * 100, 2)
    # Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]
    # Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    # Print the rows
    print_list = [h1, r1, h2, r2]
    row_format = "{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('', *row))


def printSQN(analyzer):
    sqn = round(analyzer.sqn, 2)
    print('SQN: {}'.format(sqn))


if __name__ == '__main__':
    startdate = datetime.datetime(2015, 12, 20)
    enddate = datetime.datetime(2019, 12, 31)

    cerebro = bt.Cerebro()

    # Create a Data Feed for each file in directory

    directory = "data/EURO STOXX 50/"
    data=[]
    for filename in os.listdir(directory):
        data = bt.feeds.YahooFinanceCSVData(
            dataname=directory + filename,
            fromdate=startdate,
            todate=enddate,
            reverse=False)
        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100)

    # Set the commission
    cerebro.broker.setcommission(margin=100)
    # Add a FixedSize sizer according to the cash
    # Add a strategy
    cerebro.addsizer(MarginSizer,  percent=0.1)
    #cerebro.addsizer(bt.sizers.FixedSize,  stake=1)

    cerebro.optstrategy(IndicatorBacktesting, barsAfterSignal=range(19, 25), average=False)


    # Run over everything
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # Run over everything
    strategies = cerebro.run(max_cpu=4, optreturn=True)
    firstStrat = strategies[0]

    # # print the analyzers
    # printTradeAnalysis(firstStrat.analyzers.ta.get_analysis())
    # printSQN(firstStrat.analyzers.sqn.get_analysis())

    # Get final portfolio Value
    portvalue = cerebro.broker.getvalue()

    # Print out the final result
    print('Final Portfolio Value: ${}'.format(portvalue))

    # Finally plot the end results
    cerebro.plot(style='candlestick', data=data[0])

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
