import backtrader as bt
import datetime
from collections import defaultdict
import Strategies.StrategyTemplate as st
from Indicators import ThreeSMA

class VolumeWeightedAveragePrice(bt.Indicator):
    plotinfo = dict(subplot=False)

    params = (('period', 30), )

    alias = ('VWAP', 'VolumeWeightedAveragePrice',)
    lines = ('VWAP',)
    plotlines = dict(VWAP=dict(alpha=0.50, linestyle='-.', linewidth=2.0))



    def __init__(self):
        # Before super to ensure mixins (right-hand side in subclassing)
        # can see the assignment operation and operate on the line
        cumvol = bt.ind.SumN(self.data.volume, period = self.p.period)
        typprice = ((self.data.close + self.data.high + self.data.low)/3) * self.data.volume
        cumtypprice = bt.ind.SumN(typprice, period=self.p.period)
        self.lines[0] = cumtypprice / cumvol

        super(VolumeWeightedAveragePrice, self).__init__()
# Create a Stratey
class SMAstrategy(st.StrategyTemplate):
    params = (('periods', [14, 50, 200]),
              ('shorting', False),
              ('shortingbudget', 10000),
              ('minCash', 8000),
              ('percentage', 0.1),
              ('pentry', 0.015),
              ('stopprofit', 0.99),
              ('stoploss', 0.99),
              ('valid', 10),
              ('printAllLogs', False),
              ('printImportantLogs', False),
              )

    def __init__(self):
        # To keep track of pending orders
        self.orefs = dict()
        self.shortingbudget = self.p.shortingbudget
        # Add 3 MovingAverageSimple indicator per stock
        self.sma = dict()
        self.indicator = dict()
        self.lowestcash = self.broker.getcash()
        self.signalbuy = dict()
        self.signalclose = dict()
        self.volumeIndicator = dict()
        self.smaVolume = dict()
        self.closeList = []
        self.openList = []

        self.closeListHoy = []
        self.openListHoy = []

        for data in self.datas:
            sma1 = bt.indicators.SMA(data, period=self.p.periods[0])
            sma2 = bt.indicators.SMA(data, period=self.p.periods[1])
            sma3 = bt.indicators.SMA(data, period=self.p.periods[2])

            self.smaVolume[data] = bt.indicators.SMA(data.volume, period=30)
            x = data.volume
            #self.volumeIndicator[data] = VolumeWeightedAveragePrice(data, period=30)
            self.signalbuy[data] = bt.indicators.CrossOver(sma1, sma2)
            self.signalclose[data] = bt.indicators.CrossOver(sma1, sma3)

            self.sma[data] = [sma1, sma2, sma3]
            self.orefs[data] = [None, None, None,None,None,None,None,None]
            self.indicator[data] = ThreeSMA(data)
            self.dateAyer = None
            self.dateHoy = None


    def next(self):
        # Simply log the closing price of the series from the reference
        for i, d in enumerate(self.datas):

            # Check if an order is pending ... if yes, we cannot send a 2nd one

            sma1 = self.sma[d][0]
            sma2 = self.sma[d][1]
            sma3 = self.sma[d][2]

            if self.datetime.date() == (datetime.date.today() - datetime.timedelta(days=1)):
                self.dateAyer = self.datetime.date()
                print(datetime.date.today(), self.datetime.dateAyer())
                openLongCondition = self.signalbuy[d] >0 and sma3[0]< sma1[0] and sma3[0]< sma2[0] #and d.volume[0]>self.smaVolume[d][0]*1.05
                if(openLongCondition):
                    self.openList.append(d._name)
                closeLongCondition = self.signalbuy[d] <0 #or self.signalclose[d] <0
                if (closeLongCondition):
                    self.closeList.append(d._name)

            if (self.datetime.date() == datetime.date.today()):
                self.dateHoy = self.datetime.date()
                print(datetime.date.today(), self.datetime.dateAyer())
                openLongCondition = self.signalbuy[d] > 0 and sma3[0] < sma1[0] and sma3[0] < sma2[
                    0]  # and d.volume[0]>self.smaVolume[d][0]*1.05
                if (openLongCondition):
                    self.openListHoy.append(d._name)
                closeLongCondition = self.signalbuy[d] < 0  # or self.signalclose[d] <0
                if (closeLongCondition):
                    self.closeListHoy.append(d._name)


            # openShortCondition = self.signalbuy[d] <0 and d.volume[0]>self.smaVolume[d][0]*1.05and sma4[0]> sma1[0] and sma4[0]> sma2[0]
            # closeShortCondition = self.signalclose[d] >0 or self.signalbuy[d] >0
            # self.newOrders(d, openLongCondition, openShortCondition, closeLongCondition, closeShortCondition)

    def stop(self):
        if self.dateAyer is not None:
            print("Señales del {} (ayer)".format(self.dateAyer))
            print("Lista de señales de compra: {}".format(self.openList))
            print("Lista de señales de venta: {}\n".format(self.closeList))
        else:
            print("No hay datos de ayer")

        if self.dateHoy is not None:
            print("Señales del {} (hoy)".format(self.dateAyer))
            print("Lista de señales de compra: {}".format(self.openListHoy))
            print("Lista de señales de venta: {}\n".format(self.closeListHoy))
        else:
            print("No hay datos de hoy")