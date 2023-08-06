'''
Backtest example using the `vbfin` module.
'''
import dateutil.relativedelta as rd
import talib as ta
import vbcore
import vbfin
import vbfin_ops
import vbplot
import vbtime

FILENAME = 'fig_backtest_candlestick_vbplot.svg'
WIDTH = 1000
HEIGHT = 750
INITIAL_ASSETS = 1000
MONTHLY_DEPOSIT = 1000
SLIPPAGE_PCT = 1

# fetch data
data = vbfin.Data({
    '^SPX': vbfin.fetch_ticker('^SPX'),
})

# initiate objects used by test operations
monthly_alarm = vbtime.Alarm(
    rd.relativedelta(day=1),
    rd.relativedelta(months=1),
)
time = vbfin.DataInfo()
new_month = vbfin.DataInfo('Signals', 'New month')
assets_usd = vbfin.DataInfo('Assets', 'USD',
                            first_value=INITIAL_ASSETS)
assets_spx = vbfin.DataInfo('Assets', '^SPX',
                            first_value=0)
assets_total_usd = vbfin.DataInfo('Assets', 'Total USD')
buy_and_hold_spx = vbfin.DataInfo('Assets', 'Buy and hold ^SPX')
buy_and_hold_spx_usd = vbfin.DataInfo('Assets', 'Buy and hold ^SPX USD')
spx_close = vbfin.DataInfo('^SPX', 'Close')
spx_close_sma5 = vbfin.DataInfo('^SPX', 'Close SMA5')
spx_close_sma20 = vbfin.DataInfo('^SPX', 'Close SMA20')
buy_signal_cont = vbfin.DataInfo('Signals', 'Buy continuous')
sell_signal_cont = vbfin.DataInfo('Signals', 'Sell continuous')
buy_signal = vbfin.DataInfo('Signals', 'Buy')
sell_signal = vbfin.DataInfo('Signals', 'Sell')
spx_buy_price = vbfin.DataInfo('^SPX', 'Buy price')
spx_sell_price = vbfin.DataInfo('^SPX', 'Sell price')

# run a simple test
vbfin.BacktestEngine(
    data,
    [
        # account management
        # move assets from previous datetime
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': assets_usd},
                       ret=assets_usd),
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': assets_spx},
                       ret=assets_spx),
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': assets_total_usd},
                       ret=assets_total_usd),
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': buy_and_hold_spx},
                       ret=buy_and_hold_spx),
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': buy_and_hold_spx_usd},
                       ret=buy_and_hold_spx_usd),
        # make monthly deposit
        vbfin_ops.Call(function=lambda t: monthly_alarm.is_triggered(t[-1]),
                       kwargs={'t': time},
                       ret=new_month),
        vbfin_ops.Call(function=lambda m, x: \
                       (x[-1] + MONTHLY_DEPOSIT) if m[-1] else x[-1],
                       kwargs={'m': new_month,
                               'x': assets_usd},
                       ret=assets_usd),

        # sma
        vbfin_ops.Call(function=lambda x: ta.SMA(x, 5)[-1],
                       kwargs={'x': spx_close},
                       ret=spx_close_sma5),
        vbfin_ops.Call(function=lambda x: ta.SMA(x, 20)[-1],
                       kwargs={'x': spx_close},
                       ret=spx_close_sma20),
        # buy signal: sma5 > sma20
        # continuous signal
        vbfin_ops.Call(function=lambda sma5, sma20: sma5[-1] > sma20[-1],
                       kwargs={'sma5': spx_close_sma5,
                               'sma20': spx_close_sma20},
                       ret=buy_signal_cont),
        # signal on change
        vbfin_ops.Call(function=lambda t, x: \
                       (not x[-2]) and x[-1] if len(t) > 1 else x[-1],
                       kwargs={'t': time,
                               'x': buy_signal_cont},
                       ret=buy_signal),
        # sell signal: sma5 < sma20
        # continuous signal
        vbfin_ops.Call(function=lambda sma5, sma20: sma5[-1] < sma20[-1],
                       kwargs={'sma5': spx_close_sma5,
                               'sma20': spx_close_sma20},
                       ret=sell_signal_cont),
        # signal on change
        vbfin_ops.Call(function=lambda t, x: \
                       (not x[-2]) and x[-1] if len(t) > 1 else x[-1],
                       kwargs={'t': time,
                               'x': sell_signal_cont},
                       ret=sell_signal),
        # get broker price
        vbfin_ops.Call(function=lambda x: x[-1] * (100 + SLIPPAGE_PCT)/100.0,
                       kwargs={'x': spx_close},
                       ret=spx_buy_price),
        vbfin_ops.Call(function=lambda x: x[-1] * (100 - SLIPPAGE_PCT)/100.0,
                       kwargs={'x': spx_close},
                       ret=spx_sell_price),
        # buy
        vbfin_ops.Call(function=lambda b, spx, usd, spx_price: \
                       (spx[-1] + usd[-1]/spx_price[-1]) if b[-1] else spx[-1],
                       kwargs={'b': buy_signal,
                               'spx': assets_spx,
                               'usd': assets_usd,
                               'spx_price': spx_buy_price},
                       ret=assets_spx),
        vbfin_ops.Call(function=lambda t, usd: \
                       0 if t[-1] else usd[-1],
                       kwargs={'t': buy_signal,
                               'usd': assets_usd},
                       ret=assets_usd),
        # sell
        vbfin_ops.Call(function=lambda t, spx, usd, spx_price: \
                       (usd[-1] + (spx[-1] * spx_price[-1])) if t[-1] else usd[-1],  # noqa: E501
                       kwargs={'t': sell_signal,
                               'spx': assets_spx,
                               'usd': assets_usd,
                               'spx_price': spx_sell_price},
                       ret=assets_usd),
        vbfin_ops.Call(function=lambda t, spx: \
                       0 if t[-1] else spx[-1],
                       kwargs={'t': sell_signal,
                               'spx': assets_spx},
                       ret=assets_spx),
        # total
        vbfin_ops.Call(function=lambda usd, spx, spx_price: \
                       usd[-1] + (spx[-1] * spx_price[-1]),
                       kwargs={'usd': assets_usd,
                               'spx': assets_spx,
                               'spx_price': spx_sell_price},
                       ret=assets_total_usd),
    ],
).run()

# convert data to big table
big_table = data.big_table()
print(big_table)
print(big_table.columns)

# plot
big_table = big_table[-100:][:]

buy_signals_table = big_table[big_table['Signals.Buy'] > 0]
sell_signals_table = big_table[big_table['Signals.Sell'] > 0]
vbplot.PlotlyPlot(
    height=HEIGHT,
    width=WIDTH,
    row_heights=[0.45, 0.1, 0.1, 0.1, 0.15],
    lines=[
        vbplot.Lines(
            x=buy_signals_table.index,
            color=vbcore.CSSColor.GREEN),
        vbplot.Lines(
            x=sell_signals_table.index,
            color=vbcore.CSSColor.RED),
    ],
    subplots=[
        vbplot.Subplot(
            legendgroup_name='^SPX',
            col=1,
            row=1,
            traces=[
                vbplot.Candlestick(
                    x=big_table.index,
                    yopen=big_table['^SPX.Open'],
                    yhigh=big_table['^SPX.High'],
                    ylow=big_table['^SPX.Low'],
                    yclose=big_table['^SPX.Close'],
                    width=1.0),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Close'],
                    color=vbcore.CSSColor.BLACK,
                    width=1.0,
                    mode='lines',
                    name='Close'),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Close SMA5'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    mode='lines',
                    name='Close SMA5'),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Close SMA20'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    mode='lines',
                    name='Close SMA20'),
                vbplot.Scatter(
                    x=buy_signals_table.index,
                    y=buy_signals_table['^SPX.Close SMA5'],
                    color=vbcore.CSSColor.GREEN,
                    width=1.0,
                    mode='markers',
                    marker_symbol=vbplot.MarkerSymbol.TRIANGLE_UP,
                    name='Buy'),
                vbplot.Scatter(
                    x=sell_signals_table.index,
                    y=sell_signals_table['^SPX.Close SMA5'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    mode='markers',
                    marker_symbol=vbplot.MarkerSymbol.TRIANGLE_DOWN,
                    name='Buy'),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Buy price'],
                    color=vbcore.CSSColor.GREEN,
                    width=1.0,
                    name='Buy price'),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Sell price'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    name='Sell price'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Assets',
            col=1,
            row=2,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Assets.USD'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='USD'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Assets',
            col=1,
            row=3,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Assets.^SPX'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='^SPX'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Assets',
            col=1,
            row=4,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Assets.Total USD'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='Total USD'),
            ]),
        vbplot.LogicSignalSubplot(
            legendgroup_name='Signals',
            col=1,
            row=5,
            yshift=1.2,
            steps=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Signals.Buy'],
                    color=vbcore.CSSColor.GREEN,
                    width=1.0,
                    name='Buy'),
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Signals.Buy continuous'],
                    color=vbcore.CSSColor.GREEN,
                    width=1.0,
                    name='Buy continuous'),
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Signals.Sell'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    name='Sell'),
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Signals.Sell continuous'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    name='Sell continuous'),
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Signals.New month'],
                    color=vbcore.CSSColor.BLACK,
                    width=1.0,
                    name='New month'),
            ]),
    ]).svg(FILENAME)
