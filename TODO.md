# TODO

- split
  - tools
    - fin
    - plot
    - examples (leave #1 and #2, convert #3 to experiment)
  - experiments
    - strategies
    - experiments
    - make for all (fetch version of tools and build)
- add first experiment - sma cross via investing
  - strategies - in experiments
    - saving
    - buy and hold
    - sma cross
  - every table has standard columns for every strategy
    - total_value
    - total_cash
    - total_used
  - function to parse table and plot
    - total_value, free, used for different strategies
  - find optimal sma cross parameters for daily
    - SPX, BTC, F, TSLA, NVDIA
    - plot beautiful visuals

- publish tool
- publish sma cross experiment

- add simple broker simulation
- add summary statistics
- compare to known framework

- test RSI strategy
- test parameter optimization
- run parameter optimization

- run profiling
- find bottlenecks
- try compiling
- try separating calls: vectors / sequences
  - run vectors first over all data at once
  - run sequrnces after
- try optimizing

- find decision making points, where market slows down to make a decision
  and either goes up or down
  - best place to enter/exit
- try different options for best entry/exist points
- try different strategies relative to such points

- calculate probabilities at different point in time for different moves
- try graphing a heatmap of probabilities (experiment with resolution) - where the price would end based on combination of triggered strategies
- multiplication of such heatmaps based on triggers

- find some weak/simple working strategy (ma, rsi)

- try market heatmap strategy

- add tests?

- describe in article
- create ibkr or binance account
- setup bot

suggestions:

- performance test - graph table size/execution time
