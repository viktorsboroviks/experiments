# TODO

- vbfin v2
  - rewrite to Engine - Algorithm - Operations
  - run() = optimize (create big table) + run
  - optimization
    - input check: error on duplicates in one list
    - create dag from paths
    - dag check: error if loop created
    - remove shortcut edges
    - merge leaves right next to its node[-2]
    - merge separate subgraps based on the original indices of their first/last elements (add weights?)

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

- calculate probabilities at different pount in time for different moves
- try graphing a heatmap of probabilities (experiment with resolution) - where the price would end based on combination of triggered strategies
- multiplication of such heatmaps based on triggers

- find some weak/simple working strategy (ma, rsi)

- add tests?

- describe in article
- create ibkr or binance account
- setup bot

suggestions:

- performance test - graph table size/execution time
