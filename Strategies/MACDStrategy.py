import backtrader as bt
import datetime
import Strategies.StrategyTemplate as st

class MACDStrategy(st.StrategyTemplate):
    params = (('buySignal', 0),
              ('sellSignal', 0),
              ('closeShortSignal', 0.1),
              ('closeLongSignal', -0.3),
              ('reverseShortSignals', False),
              ('shorting', True),
              ('shortingbudget', 0.1),
              ('minCash', 8000),
              ('percentage', 0.1),
              ('pentry', 0.015),
              ('stopprofit', 0.999),
              ('stoploss', 0.999),
              ('valid', 10),
              ('printAllLogs', False),
              ('printImportantLogs', False),
              )

    def __init__(self):
        # To keep track of pending orders
        self.orefs = dict()
        self.shortedcash = 0
        # Add 3 MovingAverageSimple indicator per stock
        self.macd = dict()
        self.shortingbudget = self.p.shortingbudget * self.broker.getcash()
        self.lowestcash = self.broker.getcash()
        for data in self.datas:
            self.macd[data] = bt.indicators.MACDHisto(data).histo
            self.orefs[data] = [None, None, None,None,None,None,None,None]



    def next(self):
        # Simply log the closing price of the series from the reference
        for d in self.datas:
            # Check if an order is pending ... if yes, we cannot send a 2nd one

            self.shortingbudget = self.p.shortingbudget * self.broker.getcash()
            macd = self.macd[d]
            openLongCondition = macd[0] >= self.p.buySignal and (not macd[-1] >= self.p.buySignal)
            closeLongCondition = macd[0] <= self.p.closeLongSignal and (not macd[-1] <= self.p.closeLongSignal)

            openShortCondition = macd[0] <= self.p.sellSignal and (not macd[-1] <= self.p.sellSignal)
            closeShortCondition = macd[0] >= self.p.closeShortSignal and (not macd[-1] >= self.p.closeShortSignal)

            self.newOrders(d, openLongCondition, openShortCondition, closeLongCondition, closeShortCondition)