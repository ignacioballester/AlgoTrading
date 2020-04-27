import backtrader as bt
import datetime
from collections import defaultdict

from Indicators import  TwoSMA, ThreePercent

class ThreeSMA(bt.Indicator):
    lines = ('dummyline',)
    params = (('periods', [14, 50, 200]),)

    def __init__(self):
        self.isUp = False
        self.isDown = False

        self.sma1 = bt.indicators.SimpleMovingAverage(
            self.data, period=self.p.periods[0])

        self.sma2 = bt.indicators.SimpleMovingAverage(
            self.data, period=self.p.periods[1])

        self.sma3 = bt.indicators.SimpleMovingAverage(
            self.data, period=self.p.periods[2])

    def next(self):
        sma1 = self.sma1[0]
        sma2 = self.sma2[0]
        sma3 = self.sma3[0]

        try:
            if self.isUp is False and  sma3 < sma2 < sma1:
                self.lines.dummyline[0] = 1
                self.isUp = True
            elif self.isDown is False and sma3> sma2 > sma1:
                self.lines.dummyline[0] = -1
                self.isDown = True
            else:
                self.lines.dummyline[0] = 0
        except:
            self.lines.dummyline[0] = 0

# Create a Stratey
class IndicatorBacktesting(bt.Strategy):
    params = (('buySignal', 1),
              ('sellSignal', -1),
              ('barsAfterSignal', 10),
              ('average', False)
              )

    def log(self, txt, important=False, data=None):
        if self.p.printAllLogs or (self.p.printImportantLogs and important):
            print(txt)

    def __init__(self):
        # To keep track of pending orders
        self.signalsBuy = dict()
        self.signalsSell = dict()

        self.idBuy = dict()
        self.idSell = dict()

        self.sma = dict()
        self.sma1 = bt.indicators.SimpleMovingAverage(
            self.data, period=14)

        self.sma2 = bt.indicators.SimpleMovingAverage(
            self.data, period=50)
        # Add 3 MovingAverageSimple indicator per stock
        self.indicator = dict()
        for d in self.datas:
            self.signalsBuy[d] = dict()
            self.signalsSell[d] = dict()

            self.idBuy[d] = 0
            self.idSell[d] = 0
            self.indicator[d] = ThreeSMA(d)


    def next(self):
        # Simply log the closing price of the series from the reference
        for i, d in enumerate(self.datas):
            # Check if an order is pending ... if yes, we cannot send a 2nd one
            dt, dn, p = self.datetime.date(), d._name, d.close[0]

            indicator = self.indicator[d]
            if (indicator[0]==self.p.buySignal):
                barSignal = len(self)
                priceSignal = d.close[0]
                data = [barSignal, priceSignal, None, None]
                self.signalsBuy[d][self.idBuy[d]] = data
                self.idBuy[d] +=1

            for id in range(0, self.idBuy[d]):
                barSignal = self.signalsBuy[d][id][0]
                if len(self) >= barSignal + 1+ self.p.barsAfterSignal and self.signalsBuy[d][id][3] is None:
                    priceSignal = self.signalsBuy[d][id][1]
                    priceNow = d.close[0]
                    if self.p.average:
                        priceNow = (d.close[0] + d.close[-1] + d.close[-2]) / 3.0

                    self.signalsBuy[d][id][2] = priceNow
                    self.signalsBuy[d][id][3] = priceNow / priceSignal


            if (indicator[0]==self.p.sellSignal):
                barSignal = len(self)
                priceSignal = d.close[0]
                data = [barSignal, priceSignal, None, None]
                self.signalsSell[d][self.idSell[d]] = data
                self.idSell[d] +=1

            for id in range(0, self.idSell[d]):
                barSignal = self.signalsSell[d][id][0]
                if len(self) >= barSignal + self.p.barsAfterSignal and self.signalsSell[d][id][3] is None:
                    priceSignal = self.signalsSell[d][id][1]
                    priceNow = d.close[0]
                    if self.p.average:
                        priceNow = (d.close[0] + d.close[-1] + d.close[-2]) / 3.0
                    self.signalsSell[d][id][2] = priceNow
                    self.signalsSell[d][id][3] = priceSignal / priceNow


    def stop(self):
        averageBuy = 0
        averageSell = 0
        average = 0

        numberOfBuySignals = 0
        numberOfSellSignals = 0

        for d in self.datas:
            lastPrice = d.close[0]
            for id in range(0, self.idBuy[d]):
                if(self.signalsBuy[d][id][3] == None):
                    priceSignal = self.signalsBuy[d][id][1]
                    self.signalsBuy[d][id][3] = lastPrice / priceSignal
                averageBuy += self.signalsBuy[d][id][3]
                numberOfBuySignals+=1

            for id in range(0, self.idSell[d]):
                if(self.signalsSell[d][id][3] == None):
                    priceSignal = self.signalsSell[d][id][1]
                    self.signalsSell[d][id][3] =  priceSignal / lastPrice
                averageSell += self.signalsSell[d][id][3]
                numberOfSellSignals+=1
        if(numberOfBuySignals != 0):
            averageBuy = averageBuy / numberOfBuySignals

        if(numberOfSellSignals != 0):
            averageSell = averageSell / numberOfSellSignals

        if(numberOfSellSignals != 0 and numberOfBuySignals != 0):
            average = (averageSell + averageBuy) / 2

        print("Average {} \ Average Buy/Sell: {} - {} \ # Buy Sell Signals: {} - {}\ BuySellSignal: {}-{} \ # Bars After Signal: {} "
              .format(round(average, 5), averageBuy, averageSell, numberOfBuySignals, numberOfSellSignals, self.p.buySignal, self.p.sellSignal, self.p.barsAfterSignal))