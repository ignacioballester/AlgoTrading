import backtrader as bt

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

class TwoSMA(bt.Indicator):
    lines = ('dummyline',)


    params = (('value', 5), ('periods', [14, 50]))

    def __init__(self):
        self.isUp = False
        self.isDown = False

        self.sma1 = bt.indicators.SimpleMovingAverage(
            self.data, period=self.p.periods[0])

        self.sma2 = bt.indicators.SimpleMovingAverage(
            self.data, period=self.p.periods[1])


    def next(self):
        sma1 = self.sma1[0]
        sma2 = self.sma2[0]

        try:
            if self.isUp is False and sma2 < sma1:
                self.lines.dummyline[0] = 1
                self.isUp = True
            elif self.isDown is False and sma2 > sma1:
                self.lines.dummyline[0] = -1
                self.isDown = True
            else:
                self.lines.dummyline[0] = 0
        except:
            self.lines.dummyline[0] = 0