'''
Backtest example using the `vbfin` module.
'''
import copy
import dateutil.relativedelta as rd
import talib as ta
import vbcore
import vbfin
import vbfin_ops
import vbplot
import vbtime

INITIAL_ASSETS = 1000
MONTHLY_DEPOSIT = 1000
SLIPPAGE_PCT = 0.5

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
new_month = vbfin.DataInfo('Common', 'New month')

spx_close = vbfin.DataInfo('^SPX', 'Close')
spx_close_sma5 = vbfin.DataInfo('^SPX', 'Close SMA5')
spx_close_sma20 = vbfin.DataInfo('^SPX', 'Close SMA20')

saving_usd = vbfin.DataInfo('Saving', 'USD',
                            first_value=INITIAL_ASSETS)

s_buy_signal_cont = vbfin.DataInfo('Strategy', 'Buy continuous')
s_sell_signal_cont = vbfin.DataInfo('Strategy', 'Sell continuous')
s_buy_signal = vbfin.DataInfo('Strategy', 'Buy')
s_sell_signal = vbfin.DataInfo('Strategy', 'Sell')
s_usd = vbfin.DataInfo('Strategy', 'USD',
                       first_value=INITIAL_ASSETS)
s_spx = vbfin.DataInfo('Strategy', '^SPX',
                       first_value=0)
s_total_usd = vbfin.DataInfo('Strategy', 'Total USD')

ops = [
    # account management
    # move assets from previous datetime
    vbfin_ops.Call(function=lambda x: x[-2],
                   kwargs={'x': saving_usd},
                   ret=saving_usd),
    # make monthly deposit
    vbfin_ops.Call(function=lambda t: monthly_alarm.is_triggered(t[-1]),
                   kwargs={'t': time},
                   ret=new_month),
    vbfin_ops.Call(function=lambda m, x: \
                   (x[-1] + MONTHLY_DEPOSIT) if m[-1] else x[-1],
                   kwargs={'m': new_month,
                           'x': saving_usd},
                   ret=saving_usd),
]

def get_broker_price_buy_name(col, slippage_pct):
    return f'Broker price {col} buy, slippage {slippage_pct}%'

def get_broker_price_sell_name(col, slippage_pct):
    return f'Broker price {col} sell, slippage {slippage_pct}%'

def get_broker_price_ops(price: vbfin.DataInfo, slippage_pct: float):
    buy_price = copy.copy(price)
    buy_price.col = get_broker_price_buy_name(price.col, slippage_pct)
    sell_price = copy.copy(price)
    sell_price.col = get_broker_price_sell_name(price.col, slippage_pct)
    return [
        vbfin_ops.Call(function=lambda x: x[-1] * (100 + slippage_pct)/100.0,
                       kwargs={'x': price},
                       ret=buy_price),
        vbfin_ops.Call(function=lambda x: x[-1] * (100 - slippage_pct)/100.0,
                       kwargs={'x': price},
                       ret=sell_price),
    ]


def get_buy_and_hold_ops(currency,
                         asset,
                         asset_price,
                         initial_currency,
                         monthly_deposit,
                         slippage_pct):
    key = f'Buy and hold, slippage {slippage_pct}'
    buy_and_hold_signal = vbfin.DataInfo(key, 'Signal')
    buy_and_hold_currency = vbfin.DataInfo(key, currency,
                                           first_value=initial_currency)
    buy_and_hold_asset = vbfin.DataInfo(key, asset.key,
                                        first_value=0)
    buy_and_hold_total_currency = vbfin.DataInfo(key, f'Total {currency}')

    ops = []
    ops = ops + get_broker_price_ops(asset_price, slippage_pct)
    ops = ops + [
        # move to the next month
        vbfin_ops.Call(function=lambda x: x[-2],
                    kwargs={'x': buy_and_hold_currency},
                    ret=buy_and_hold_currency),
        vbfin_ops.Call(function=lambda x: x[-2],
                    kwargs={'x': buy_and_hold_asset},
                    ret=buy_and_hold_asset),
        vbfin_ops.Call(function=lambda x: x[-2],
                    kwargs={'x': buy_and_hold_total_currency},
                    ret=buy_and_hold_total_currency),
        # deposit
        vbfin_ops.Call(function=lambda m, x: \
                    (x[-1] + monthly_deposit) if m[-1] else x[-1],
                    kwargs={'m': new_month,
                            'x': buy_and_hold_currency},
                    ret=buy_and_hold_currency),
        # buy and hold
        # buy signal
        vbfin_ops.Call(function=lambda m: m[-1] or len(m) == 1,
                    kwargs={'m': new_month},
                    ret=buy_and_hold),
        # spx
        vbfin_ops.Call(function=lambda b, spx, usd, spx_price: \
                    (spx[-1] + usd[-1]/spx_price[-1]) if b[-1] else spx[-1],
                    kwargs={'b': buy_and_hold,
                            'spx': buy_and_hold_spx,
                            'usd': buy_and_hold_usd,
                            'spx_price': spx_buy_price},
                    ret=buy_and_hold_spx),
        # usd
        vbfin_ops.Call(function=lambda b, usd: \
                    0 if b[-1] else usd[-1],
                    kwargs={'b': buy_and_hold,
                            'usd': buy_and_hold_usd},
                    ret=buy_and_hold_usd),
        # total usd
        vbfin_ops.Call(function=lambda usd, spx, spx_price: \
                    usd[-1] + (spx[-1] * spx_price[-1]),
                    kwargs={'usd': buy_and_hold_usd,
                            'spx': buy_and_hold_spx,
                            'spx_price': spx_sell_price},
                    ret=buy_and_hold_total_usd),
    ]

# run the test once to obtain generic parameters
vbfin.BacktestEngine(
    data,
    [
        # account management
        # move assets from previous datetime
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': saving_usd},
                       ret=saving_usd),
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': buy_and_hold_usd},
                       ret=buy_and_hold_usd),
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': buy_and_hold_spx},
                       ret=buy_and_hold_spx),
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': buy_and_hold_total_usd},
                       ret=buy_and_hold_total_usd),
        # get broker price
        vbfin_ops.Call(function=lambda x: x[-1] * (100 + SLIPPAGE_PCT)/100.0,
                       kwargs={'x': spx_close},
                       ret=spx_buy_price),
        vbfin_ops.Call(function=lambda x: x[-1] * (100 - SLIPPAGE_PCT)/100.0,
                       kwargs={'x': spx_close},
                       ret=spx_sell_price),
        # make monthly deposit
        vbfin_ops.Call(function=lambda t: monthly_alarm.is_triggered(t[-1]),
                       kwargs={'t': time},
                       ret=new_month),
        vbfin_ops.Call(function=lambda m, x: \
                       (x[-1] + MONTHLY_DEPOSIT) if m[-1] else x[-1],
                       kwargs={'m': new_month,
                               'x': saving_usd},
                       ret=saving_usd),
        vbfin_ops.Call(function=lambda m, x: \
                       (x[-1] + MONTHLY_DEPOSIT) if m[-1] else x[-1],
                       kwargs={'m': new_month,
                               'x': buy_and_hold_usd},
                       ret=buy_and_hold_usd),
        # buy and hold
        # buy signal
        vbfin_ops.Call(function=lambda m: m[-1] or len(m) == 1,
                       kwargs={'m': new_month},
                       ret=buy_and_hold),
        # spx
        vbfin_ops.Call(function=lambda b, spx, usd, spx_price: \
                       (spx[-1] + usd[-1]/spx_price[-1]) if b[-1] else spx[-1],
                       kwargs={'b': buy_and_hold,
                               'spx': buy_and_hold_spx,
                               'usd': buy_and_hold_usd,
                               'spx_price': spx_buy_price},
                       ret=buy_and_hold_spx),
        # usd
        vbfin_ops.Call(function=lambda b, usd: \
                       0 if b[-1] else usd[-1],
                       kwargs={'b': buy_and_hold,
                               'usd': buy_and_hold_usd},
                       ret=buy_and_hold_usd),
        # total usd
        vbfin_ops.Call(function=lambda usd, spx, spx_price: \
                       usd[-1] + (spx[-1] * spx_price[-1]),
                       kwargs={'usd': buy_and_hold_usd,
                               'spx': buy_and_hold_spx,
                               'spx_price': spx_sell_price},
                       ret=buy_and_hold_total_usd),
    ],
).run()

# convert data to big table
big_table = data.big_table()

# plot
FILENAME = 'fig_backtest_strategies'
WIDTH = 1000
HEIGHT = 750

buy_and_hold_table = big_table[big_table['Buy and hold.Buy'] > 0]
vbplot.PlotlyPlot(
    height=HEIGHT,
    width=WIDTH,
    row_heights=[0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
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
                    name='Buy price'),
                vbplot.Scatter(
                    x=big_table.index,
                    y=big_table['^SPX.Sell price'],
                    color=vbcore.CSSColor.RED,
                    width=1.0,
                    name='Sell price'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Saving',
            col=1,
            row=2,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Saving.USD'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='USD'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Buy and hold',
            col=1,
            row=3,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Buy and hold.USD'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='USD'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Buy and hold',
            col=1,
            row=4,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Buy and hold.^SPX'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='^SPX'),
            ]),
        vbplot.Subplot(
            legendgroup_name='Buy and hold',
            col=1,
            row=5,
            traces=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Buy and hold.Total USD'],
                    color=vbcore.CSSColor.BLUE,
                    width=1.0,
                    name='USD'),
            ]),
        vbplot.LogicSignalSubplot(
            legendgroup_name='Signals',
            col=1,
            row=6,
            yshift=1.2,
            steps=[
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Buy and hold.Buy'],
                    color=vbcore.CSSColor.GREEN,
                    width=1.0,
                    name='Buy'),
                vbplot.Step(
                    x=big_table.index,
                    y=big_table['Common.New month'],
                    color=vbcore.CSSColor.BLACK,
                    width=1.0,
                    name='New month'),
            ]),
    ]).svg(f'{FILENAME}_vbplot.svg')

savings = big_table['Saving.USD'][-1]
print(f'saving USD: {savings}')
total = big_table['Buy and hold.Total USD'][-1]
print(f'buy and hold USD: {total}')
