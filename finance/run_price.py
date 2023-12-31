'''
Experiment for generating buy/sell prices.
'''
import datetime
import vfin
import vfin_ops
import vtable

dfs = {
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2020, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
}

price_opgen = vfin_ops.PriceOpGen(src_di=vtable.DataInfo('^SPX', 'Close'),
                                  slippage_pct=0.5)
# debug name
print(price_opgen.name)

big_table = vfin.BacktestEngine(
    price_opgen.ops(),
    dfs
).run()

price_opgen.debug_plot(big_table, 'test_price.svg')
price_opgen.debug_plot(big_table, 'test_price.html')
