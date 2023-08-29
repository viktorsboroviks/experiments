'''
Backtest example using the `vbfin` module.
'''
import dateutil.relativedelta as rd
import plotly.graph_objects as go
import plotly.subplots
import talib as ta
import vbfin
import vbfin_ops
import vbtime

INITIAL_ASSETS = 1000
MONTHLY_DEPOSIT = 1000

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
total_assets = vbfin.DataInfo('Assets', 'Total',
                              first_value=INITIAL_ASSETS)
spx_close = vbfin.DataInfo('^SPX', 'Close')
spx_close_sma5 = vbfin.DataInfo('^SPX', 'Close SMA5')
spx_close_sma20 = vbfin.DataInfo('^SPX', 'Close SMA20')
buy_signal_cont = vbfin.DataInfo('Signals', 'Buy continuous')
sell_signal_cont = vbfin.DataInfo('Signals', 'Sell continuous')
buy_signal = vbfin.DataInfo('Signals', 'Buy')
sell_signal = vbfin.DataInfo('Signals', 'Sell')


# run a simple test
vbfin.BacktestEngine(
    data,
    [vbfin.Sequence([
        # account management
        # move assets from previous datetime
        vbfin_ops.Call(function=lambda x: x[-2],
                       kwargs={'x': total_assets},
                       ret=total_assets),
        # make monthly deposit
        vbfin_ops.Call(function=lambda t: monthly_alarm.is_triggered(t[-1]),
                       kwargs={'t': time},
                       ret=new_month),
        vbfin_ops.Call(function=lambda m, x: \
                       (x[-1] + MONTHLY_DEPOSIT) if m[-1] else x[-1],
                       kwargs={'m': new_month,
                               'x': total_assets},
                       ret=total_assets),
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
    ])],
).run()

# convert data to big table
big_table = data.big_table()
print(big_table)
print(big_table.columns)

# plot
# candlesticks + close + sma5 + sma20 + buy green arrow + sell red arrow
# ref:
# - https://plotly.com/python-api-reference/plotly.graph_objects.html#graph-objects     # noqa: E501
# - adding new plots to figure
#   - https://community.plotly.com/t/best-method-to-add-trace-to-existing-figure/48059  # noqa: E501
FILENAME = 'backtest_plotly'
# FILETYPE = 'html'
FILETYPE = 'svg'
if FILETYPE == 'svg':
    big_table = big_table[-100:][:]
WIDTH = 1000
HEIGHT = 750
fig = plotly.subplots.make_subplots(rows=3,
                                    cols=1,
                                    row_heights=[0.7, 0.15, 0.15])
# set dimensions
fig.update_layout(width=WIDTH, height=HEIGHT)
# best theme in plotly
fig.update_layout(template='simple_white')

# plot candlesticks
fig.add_trace(
    go.Candlestick(x=big_table.index,
                   open=big_table['^SPX.Open'],
                   high=big_table['^SPX.High'],
                   low=big_table['^SPX.Low'],
                   close=big_table['^SPX.Close'],
                   legendgroup="Plot",
                   legendgrouptitle_text="Main plot",
                   name='^SPX'))
# rangeslider at the bottom is not needed for .svg
if FILETYPE == 'svg':
    fig.update(layout_xaxis_rangeslider_visible=False)
# candlestick lines are too thick by default
fig.update_traces(line_width=1, selector=dict(type='candlestick'))

# plot close
# ref:
# - https://plotly.com/python/line-and-scatter/
# - colors
#   - https://www.w3schools.com/tags/ref_colornames.asp
#   - https://plotly.com/python/discrete-color/
fig.add_trace(go.Scatter(x=big_table.index,
                         y=big_table['^SPX.Close'],
                         mode='lines',
                         legendgroup="Plot",
                         name='^SPX.Close',
                         line_color='black',
                         line_width=0.7),
              col=1,
              row=1)

# plot SMA
fig.add_trace(go.Scatter(x=big_table.index,
                         y=big_table['^SPX.Close SMA5'],
                         mode='lines',
                         legendgroup="Plot",
                         name='^SPX.Close SMA5',
                         line_color='orangered',
                         line_width=0.7),
              col=1,
              row=1)
fig.add_trace(go.Scatter(x=big_table.index,
                         y=big_table['^SPX.Close SMA20'],
                         mode='lines',
                         legendgroup="Plot",
                         name='^SPX.Close SMA20',
                         line_color='steelblue',
                         line_width=0.7),
              col=1,
              row=1)

# plot buy indicator
# ref:
# - https://plotly.com/python/marker-style/#using-standoff-to-position-a-marker
buy_signals_table = big_table[big_table['Signals.Buy'] > 0]
# standoff moved the marker x pixels below
fig.add_trace(go.Scatter(x=buy_signals_table.index,
                         y=buy_signals_table['^SPX.Close'],
                         mode='markers',
                         legendgroup="Plot",
                         name='Signals.Buy',
                         marker=dict(size=10,
                                     standoff=10,
                                     symbol='triangle-up',
                                     angle=0,
                                     color='green')),
              col=1,
              row=1)
# plot sell indicator
# standoff can only be >0, so to move the sell marker above with standoff=10,
# it is rotated 180deg and 'triangle-up' is used
sell_signals_table = big_table[big_table['Signals.Sell'] > 0]
fig.add_trace(go.Scatter(x=sell_signals_table.index,
                         y=sell_signals_table['^SPX.Close'],
                         mode='markers',
                         legendgroup="Plot",
                         name='Signals.Sell',
                         marker=dict(size=10,
                                     standoff=10,
                                     symbol='triangle-up',
                                     angle=180,
                                     color='red')),
              col=1,
              row=1)

# plot account data
fig.add_trace(go.Scatter(x=big_table.index,
                         y=big_table['Assets.Total'],
                         mode='lines',
                         line={"shape": 'hv'},
                         legendgroup="Assets",
                         legendgrouptitle_text="Assets",
                         name='Assets.Total',
                         line_color='steelblue',
                         line_width=0.7),
              col=1,
              row=2)

# plot logical signals
fig.update_yaxes(visible=False, col=1, row=3)
fig.add_trace(go.Scatter(x=big_table.index,
                         y=big_table['Signals.New month']+4.4,
                         mode='lines',
                         line={"shape": 'hv'},
                         legendgroup="Signals",
                         name='Signals.Monthly deposit',
                         line_color='black',
                         line_width=0.7),
              col=1,
              row=3)
fig.add_trace(go.Scatter(x=big_table.index,
                         y=big_table['Signals.Buy']+3.3,
                         mode='lines',
                         line={"shape": 'hv'},
                         legendgroup="Signals",
                         name='Signals.Buy',
                         line_color='green',
                         line_width=0.7),
              col=1,
              row=3)
fig.add_trace(go.Scatter(x=big_table.index,
                         y=big_table['Signals.Buy continuous']+2.2,
                         mode='lines',
                         line={"shape": 'hv'},
                         legendgroup="Signals",
                         name='Signals.Buy continuous',
                         line_color='green',
                         line_width=0.7),
              col=1,
              row=3)
fig.add_trace(go.Scatter(x=big_table.index,
                         y=big_table['Signals.Sell'] + 1.1,
                         mode='lines',
                         line={"shape": 'hv'},
                         legendgroup="Signals",
                         name='Signals.Sell',
                         line_color='red',
                         line_width=0.7),
              col=1,
              row=3)
fig.add_trace(go.Scatter(x=big_table.index,
                         y=big_table['Signals.Sell continuous'],
                         mode='lines',
                         line={"shape": 'hv'},
                         legendgroup="Signals",
                         legendgrouptitle_text="Signals",
                         name='Signals.Sell continuous',
                         line_color='red',
                         line_width=0.7),
              col=1,
              row=3)

# save the result
if FILETYPE == 'svg':
    fig.write_image(f'{FILENAME}.{FILETYPE}')
else:
    fig.write_html(f'{FILENAME}.{FILETYPE}')
