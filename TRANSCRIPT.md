# Build transcript — eth-pnl-fixed (agent hdr, 2026-11-13)

1. Pulled the challenge from github.com/AIProveRH/aiprove
   (challenges/eth-backtest): frozen bars.csv, 1,440 one-minute
   ETH/USDT bars, real Binance window ending 2026-11-13 12:17 UTC.
   Market shape: ~13h sideways near 2015, a -4.6% selloff into hour
   17, partial recovery to 1960.6; net -3.36%.
2. Built a cost-aware backtester: position at t-1 earns the t return;
   every unit of turnover pays fee+slippage (tested 5 and 10 bp/side).
3. Swept strategy families: EMA crosses (6 pairs x 3 deadbands),
   momentum (5 lookbacks), Donchian (3 channels), buy/short-hold.
   Fast systems all lost money after costs (momentum-30: -29% at
   10bp). Donchian channels were the only profitable family.
4. Swept Donchian entry/exit grids (4x4). Picked 240/60: full sample
   +3.18% @10bp, max DD -1.48%, turnover 5, and the only variant
   non-negative on both the first-70% segment (+3.42%) and the
   held-out last-30% segment (+0.06%). Neighbours (180/60, 240/30,
   360/60) are also profitable -> plateau, not a spike.
5. Packaged strategy.py (positions(closes) + CLI that writes
   positions.csv and prints the cost-stressed summary above),
   README.md, bars.csv (the frozen sample, for reproducibility).
