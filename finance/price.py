'''
Experiment for generating buy/sell prices.
'''
import datetime
import vfin
import vfin_ops

data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2020, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
})

price_opgen = vfin_ops.PriceOpGen(src_di=vfin.DataInfo('^SPX', 'Close'),
                                  slippage_pct=0.5)
# debug name
print(price_opgen.name)

vfin.BacktestEngine(
    data,
    price_opgen.ops()
).run()

price_opgen.debug_plot(data.big_table(), 'test_price.svg')
price_opgen.debug_plot(data.big_table(), 'test_price.html')
