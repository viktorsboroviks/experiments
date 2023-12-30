'''
Test correctness of strategy simulations.
'''
import datetime
import numpy as np
import vfin
import vtime
import vtable
import strategies.saving
import strategies.money_avg
import strategies.sma_cross


def test():
    '''
    Test.
    '''
    instrument = vfin.InstrumentInfo(ticker_name='^SPX',
                                     di={'close': vtable.DataInfo('^SPX', 'Close')},
                                     slippage=0.5)

    dfs = {
        '^SPX': vfin.fetch_ticker('^SPX',
                                  start=datetime.datetime(1960, 1, 1),
                                  end=datetime.datetime(2023, 11, 1))
    }
    monthly_alarm = vtime.Alarm('monthly')

    saving_opgen = strategies.saving.SavingOpGen(
        initial_cash=1000,
        add_cash=100,
        add_cash_alarm=monthly_alarm)

    money_avg_opgen = strategies.money_avg.MoneyAvgOpGen(
        price_info=instrument,
        initial_cash=1000,
        add_cash=100,
        add_cash_alarm=monthly_alarm)

    sma_cross_opgen = strategies.sma_cross.SmaCrossOpGen(
        price_info=instrument,
        initial_cash=1000,
        add_cash=100,
        add_cash_alarm=monthly_alarm,
        params={'long entry slow sma': 200,
                'long entry fast sma': 50,
                'long exit slow sma': 200,
                'long exit fast sma': 50,
                'short entry slow sma': 200,
                'short entry fast sma': 50,
                'short exit slow sma': 200,
                'short exit fast sma': 50})

    sma_cross_long_opgen = strategies.sma_cross.SmaCrossOpGen(
        price_info=instrument,
        initial_cash=1000,
        add_cash=100,
        add_cash_alarm=monthly_alarm,
        params={'long entry slow sma': 200,
                'long entry fast sma': 50,
                'long exit slow sma': 200,
                'long exit fast sma': 50})

    sma_cross_short_opgen = strategies.sma_cross.SmaCrossOpGen(
        price_info=instrument,
        initial_cash=1000,
        add_cash=100,
        add_cash_alarm=monthly_alarm,
        params={'short entry slow sma': 200,
                'short entry fast sma': 50,
                'short exit slow sma': 200,
                'short exit fast sma': 50})

    big_table = vfin.BacktestEngine(
        saving_opgen.ops() +
        money_avg_opgen.ops() +
        sma_cross_opgen.ops() +
        sma_cross_long_opgen.ops() +
        sma_cross_short_opgen.ops(),
        dfs=dfs
    ).run()

    np.testing.assert_almost_equal(
        saving_opgen.total(big_table).iloc[-1],
        77600)
    np.testing.assert_almost_equal(
        money_avg_opgen.total(big_table).iloc[-1],
        1700254.076542851)
    np.testing.assert_almost_equal(
        sma_cross_opgen.total(big_table).iloc[-1],
        558478.1005327095)
    np.testing.assert_almost_equal(
        sma_cross_long_opgen.total(big_table).iloc[-1],
        994192.0851553032)
    np.testing.assert_almost_equal(
        sma_cross_short_opgen.total(big_table).iloc[-1],
        53469.464345512264)
