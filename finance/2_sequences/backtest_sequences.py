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

# fetch data
data = vbfin.Data({
    '^SPX': vbfin.fetch_ticker('^SPX'),
})

# track time
monthly_alarm = vbtime.Alarm(
    rd.relativedelta(day=1),
    rd.relativedelta(months=1),
)
time = vbfin.DataInfo()
new_month = vbfin.DataInfo('Time', 'New month')
seq_time = vbfin.Sequence([
    vbfin_ops.Call(function=lambda t: monthly_alarm.is_triggered(t[-1]),
                   kwargs={'t': time},
                   ret=new_month),
])

INITIAL_ASSETS = 1000
MONTHLY_DEPOSIT = 1000

# saving
saving_usd = vbfin.DataInfo('Saving', 'USD',
                            first_value=INITIAL_ASSETS)
seq_saving = vbfin.Sequence([
    # move assets from previous datetime
    vbfin_ops.Call(function=lambda x: x[-2],
                   kwargs={'x': saving_usd},
                   ret=saving_usd),
    # receive monthly deposit
    vbfin_ops.Call(function=lambda m, x: \
                   (x[-1] + MONTHLY_DEPOSIT) if m[-1] else x[-1],
                   kwargs={'m': new_month,
                           'x': saving_usd},
                   ret=saving_usd),
])

SLIPPAGE_PCT = 0.5

# prices
spx_close = vbfin.DataInfo('^SPX', 'Close')
spx_buy_price = vbfin.DataInfo('^SPX', 'Buy price')
spx_sell_price = vbfin.DataInfo('^SPX', 'Sell price')
seq_price = vbfin.Sequence([
    # get buy price
    vbfin_ops.Call(function=lambda x: x[-1] * (100 + SLIPPAGE_PCT)/100.0,
                   kwargs={'x': spx_close},
                   ret=spx_buy_price),
    # get sell price
    vbfin_ops.Call(function=lambda x: x[-1] * (100 - SLIPPAGE_PCT)/100.0,
                   kwargs={'x': spx_close},
                   ret=spx_sell_price),
])

# buy and hold
bnh_usd = vbfin.DataInfo('Buy and hold', 'USD',
                         first_value=INITIAL_ASSETS)
bnh_spx = vbfin.DataInfo('Buy and hold', '^SPX',
                         first_value=0)
bnh_total_usd = vbfin.DataInfo('Buy and hold', 'Total USD')
bnh_buy_signal = vbfin.DataInfo('Buy and hold', 'Buy signal')
seq_bnh = vbfin.Sequence([
    # move assets from previous datetime
    vbfin_ops.Call(function=lambda x: x[-2],
                   kwargs={'x': bnh_usd},
                   ret=bnh_usd),
    vbfin_ops.Call(function=lambda x: x[-2],
                   kwargs={'x': bnh_spx},
                   ret=bnh_spx),
    vbfin_ops.Call(function=lambda x: x[-2],
                   kwargs={'x': bnh_total_usd},
                   ret=bnh_total_usd),
    # receive monthly deposit
    vbfin_ops.Call(function=lambda m, x: \
                   (x[-1] + MONTHLY_DEPOSIT) if m[-1] else x[-1],
                   kwargs={'m': new_month,
                           'x': bnh_usd},
                   ret=bnh_usd),
    # buy signal
    vbfin_ops.Call(function=lambda m: m[-1] or len(m) == 1,
                   kwargs={'m': new_month},
                   ret=bnh_buy_signal),
    # spx
    vbfin_ops.Call(function=lambda b, spx, usd, spx_price: \
                   (spx[-1] + usd[-1]/spx_price[-1]) if b[-1] else spx[-1],
                   kwargs={'b': bnh_buy_signal,
                           'spx': bnh_spx,
                           'usd': bnh_usd,
                           'spx_price': spx_buy_price},
                   ret=bnh_spx),
    # usd
    vbfin_ops.Call(function=lambda b, usd: \
                   0 if b[-1] else usd[-1],
                   kwargs={'b': bnh_buy_signal,
                           'usd': bnh_usd},
                   ret=bnh_usd),
    # total usd
    vbfin_ops.Call(function=lambda usd, spx, spx_price: \
                usd[-1] + (spx[-1] * spx_price[-1]),
                kwargs={'usd': bnh_usd,
                        'spx': bnh_spx,
                        'spx_price': spx_sell_price},
                ret=bnh_total_usd),
])

# sma
spx_close_sma5 = vbfin.DataInfo('^SPX', 'Close SMA5')
spx_close_sma20 = vbfin.DataInfo('^SPX', 'Close SMA20')
spx_sma5_gt_sma20 = vbfin.DataInfo('^SPX', 'SMA5>SMA20')
spx_sma5_gt_sma20_rise = vbfin.DataInfo('^SPX', 'SMA5>SMA20 rise')
spx_sma5_gt_sma20_fall = vbfin.DataInfo('^SPX', 'SMA5>SMA20 fall')
seq_sma = vbfin.Sequence([
    vbfin_ops.Call(function=lambda x: ta.SMA(x, 5)[-1],
                    kwargs={'x': spx_close},
                    ret=spx_close_sma5),
    vbfin_ops.Call(function=lambda x: ta.SMA(x, 20)[-1],
                    kwargs={'x': spx_close},
                    ret=spx_close_sma20),
    # continuous signal
    vbfin_ops.Call(function=lambda sma5, sma20: sma5[-1] > sma20[-1],
                    kwargs={'sma5': spx_close_sma5,
                            'sma20': spx_close_sma20},
                    ret=spx_sma5_gt_sma20),
    # rise signal
    vbfin_ops.Call(function=lambda t, x: \
                    (not x[-2]) and x[-1] if len(t) > 1 else x[-1],
                    kwargs={'t': time,
                            'x': spx_sma5_gt_sma20},
                    ret=spx_sma5_gt_sma20_rise),
    # fall signal
    vbfin_ops.Call(function=lambda t, x: \
                    (x[-2]) and not x[-1] if len(t) > 1 else x[-1],
                    kwargs={'t': time,
                            'x': spx_sma5_gt_sma20},
                    ret=spx_sma5_gt_sma20_fall),
])

# strategy
strategy_usd = vbfin.DataInfo('Strategy', 'USD',
                              first_value=INITIAL_ASSETS)
strategy_spx = vbfin.DataInfo('Strategy', '^SPX',
                              first_value=0)
strategy_total_usd = vbfin.DataInfo('Strategy', 'Total USD')
strategy_buy_signal = vbfin.DataInfo('Strategy', 'Buy signal')
strategy_sell_signal = vbfin.DataInfo('Strategy', 'Sell signal')
seq_strategy = vbfin.Sequence([
    # move assets from previous datetime
    vbfin_ops.Call(function=lambda x: x[-2],
                   kwargs={'x': strategy_usd},
                   ret=strategy_usd),
    vbfin_ops.Call(function=lambda x: x[-2],
                   kwargs={'x': strategy_spx},
                   ret=strategy_spx),
    vbfin_ops.Call(function=lambda x: x[-2],
                   kwargs={'x': strategy_total_usd},
                   ret=strategy_total_usd),
    # receive monthly deposit
    vbfin_ops.Call(function=lambda m, x: \
                   (x[-1] + MONTHLY_DEPOSIT) if m[-1] else x[-1],
                   kwargs={'m': new_month,
                           'x': strategy_usd},
                   ret=strategy_usd),
    # buy signal: sma5 > sma20
    vbfin_ops.Call(function=lambda x: x[-1],
                   kwargs={'x': spx_sma5_gt_sma20_rise},
                   ret=strategy_buy_signal),
    # sell signal: sma5 <= sma20
    vbfin_ops.Call(function=lambda x: x[-1],
                   kwargs={'x': spx_sma5_gt_sma20_fall},
                   ret=strategy_sell_signal),
    # spx buy
#    vbfin_ops.Call(function=lambda b, spx, usd, spx_price: \
#                   (spx[-1] + usd[-1]/spx_price[-1]) if b[-1] else spx[-1],
#                   kwargs={'b': strategy_buy_signal,
#                           'spx': strategy_spx,
#                           'usd': strategy_usd,
#                           'spx_price': spx_buy_price},
#                   ret=strategy_spx),
    # spx sell
#    vbfin_ops.Call(function=lambda b, spx, usd, spx_price: \
#                   (spx[-1] + usd[-1]/spx_price[-1]) if b[-1] else spx[-1],
#                   kwargs={'b': strategy_buy_signal,
#                           'spx': strategy_spx,
#                           'usd': strategy_usd,
#                           'spx_price': spx_buy_price},
#                   ret=strategy_spx),
#    # usd
#    vbfin_ops.Call(function=lambda b, usd: \
#                   0 if b[-1] else usd[-1],
#                   kwargs={'b': strategy_buy_signal,
#                           'usd': strategy_usd},
#                   ret=strategy_usd),
    # total usd
    vbfin_ops.Call(function=lambda usd, spx, spx_price: \
                usd[-1] + (spx[-1] * spx_price[-1]),
                kwargs={'usd': strategy_usd,
                        'spx': strategy_spx,
                        'spx_price': spx_sell_price},
                ret=strategy_total_usd),
])

# run the test once to obtain generic parameters
vbfin.BacktestEngine(
    data,
    [
        seq_time,
        seq_price,
        seq_saving,
        seq_bnh,
        seq_sma,
        seq_strategy,
    ],
).run()

# convert data to big table
big_table = data.big_table()

# plot
FILENAME = 'fig_backtest_sequences'
WIDTH = 1000
HEIGHT = 750
FONT_SIZE = 10

# debug: show only last 100 items
big_table = big_table[-100:]

vbplot.PlotlyPlot(
    height=HEIGHT,
    width=WIDTH,
    row_heights=[2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    font_size=FONT_SIZE,
    subplots=[
        vbplot.Subplot(
            legendgroup_name='^SPX',
            col=1,
            row=1,
            traces=[
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Close'],
                    color=vbcore.CSSColor.BLACK,
                    width=1.0,
                    mode='lines',
                    name='Close'),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Buy price'],
                    color=vbcore.CSSColor.GREEN,
                    width=1.0,
                    dash=vbplot.Dash.DOT,
                    name='Buy price'),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Sell price'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    dash=vbplot.Dash.DOT,
                    name='Sell price'),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Close SMA5'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    name='SMA5'),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Close SMA20'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='SMA20'),
            ]),
        vbplot.LogicSignalSubplot(
            legendgroup_name='Signals',
            col=1,
            row=2,
            yshift=1.2,
            steps=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Time.New month'],
                    color=vbcore.CSSColor.BLACK,
                    width=1.0,
                    name='New month'),
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Buy and hold.Buy signal'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='Buy and hold.Buy'),
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Strategy.Buy signal'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    name='Strategy.Buy'),
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Strategy.Sell signal'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    name='Strategy.Sell'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Saving',
            col=1,
            row=3,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Saving.USD'],
                    color=vbcore.CSSColor.GREEN,
                    width=1.0,
                    name='Total USD'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Buy and hold',
            col=1,
            row=4,
            traces=[
               vbplot.Step(
                   x=big_table.index,
                   y=big_table['Buy and hold.USD'],
                   color=vbcore.CSSColor.BLUE,
                   width=1.0,
                   dash=vbplot.Dash.DOT,
                   name='USD'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Buy and hold',
            col=1,
            row=5,
            traces=[
               vbplot.Step(
                   x=big_table.index,
                   y=big_table['Buy and hold.^SPX'],
                   color=vbcore.CSSColor.BLUE,
                   width=1.0,
                   dash=vbplot.Dash.DASH,
                   name='^SPX'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Buy and hold',
            col=1,
            row=6,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Buy and hold.Total USD'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='Total USD'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Strategy',
            col=1,
            row=7,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Strategy.USD'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    dash=vbplot.Dash.DOT,
                    name='USD'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Strategy',
            col=1,
            row=8,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Strategy.^SPX'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    dash=vbplot.Dash.DASH,
                    name='^SPX'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Strategy',
            col=1,
            row=9,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Strategy.Total USD'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    name='Total USD'),
            ]),
    ]).svg(f'{FILENAME}_vbplot.svg')

savings = big_table['Saving.USD'][-1]
print(f'saving USD: {savings}')
total = big_table['Buy and hold.Total USD'][-1]
print(f'buy and hold USD: {total}')
