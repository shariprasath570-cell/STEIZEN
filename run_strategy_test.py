"""
STEIZEN - ICT Strategy Backtest
================================

STANDARD USD ACCOUNTING VERSION

Starting balance : $10,000
MNQ tick size     : 0.25
MNQ tick value    : $0.50
Risk per trade    : 1%
Risk:Reward       : 1:2

Trade Quality:
    Minimum score : 60
    Enforcement   : ON

IMPORTANT:
    - No INR conversion.
    - No currency conversion.
    - Strategy logic is unchanged.
    - Entry logic is unchanged.
    - Exit logic is unchanged.
    - Risk percentage is unchanged.
    - Quality threshold remains >=60.
"""

import sys
import time
import csv
from collections import defaultdict
from datetime import datetime

# ============================================================
# PROJECT PATH
# ============================================================

sys.path.insert(0, ".")


# ============================================================
# CONFIGURATION
# ============================================================

STARTING_BALANCE = 10_000.0

RISK_PERCENT = 1.0
RISK_REWARD = 2.0

MAX_DAILY_LOSS = 5_000.0
MAX_TRADES_PER_DAY = 50
MAX_CONSEC_LOSSES = 50


# ============================================================
# TRADE QUALITY
# ============================================================

QUALITY_THRESHOLD = 60
QUALITY_ENFORCEMENT = True


# ============================================================
# TEST SIZE
# ============================================================

# Use 25_000 first for validation.
#
# For the complete 3-year backtest:
#
# TEST_CANDLES = None
#
TEST_CANDLES = 250_000

# ============================================================
# JOURNAL
# ============================================================

TRADE_JOURNAL_FILE = (
    "backtest_trade_quality.csv"
)


# ============================================================
# HEADER
# ============================================================

print()

print("=" * 72)

print(
    "        STEIZEN - ICT STRATEGY BACKTEST"
)

print(
    "        TRADE QUALITY + JOURNAL ANALYSIS"
)

print("=" * 72)

print(
    f"   Started : "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

print("=" * 72)

print()


# ============================================================
# STEP 1 - LOAD DATA
# ============================================================

print(
    "Step 1/6  Loading historical dataset..."
)

load_start = time.time()


from src.data_loader.csv_loader import CSVLoader


candles = CSVLoader().load(
    "data/Dataset_NQ_1min_2022_2025.csv"
)


if TEST_CANDLES is None:

    test_candles = candles

else:

    test_candles = candles[
        :TEST_CANDLES
    ]


print(
    f"          Loaded "
    f"{len(candles):,} candles"
)

print(
    f"          Testing "
    f"{len(test_candles):,} candles"
)

print(
    f"          Range  "
    f"{test_candles[0].timestamp.date()} "
    f"→ "
    f"{test_candles[-1].timestamp.date()}"
)

print(
    f"          Time   "
    f"{time.time() - load_start:.1f}s"
)

print()


# ============================================================
# STEP 2 - ENGINE + BROKER
# ============================================================

print(
    "Step 2/6  Setting up engine and broker..."
)


from src.broker.paper_broker import PaperBroker

from src.core.automated_trading_engine import (
    AutomatedTradingEngine,
)

from src.models.instrument import InstrumentSpec


# ============================================================
# MNQ - ORIGINAL USD VALUES
# ============================================================

MNQ = InstrumentSpec(
    symbol="MNQ",

    # MNQ minimum price movement
    tick_size=0.25,

    # MNQ original USD tick value
    tick_value=0.50,
)


# ============================================================
# BROKER
# ============================================================

broker = PaperBroker(
    instrument=MNQ,
    starting_balance=STARTING_BALANCE,
)


# ============================================================
# ENGINE
# ============================================================

engine = AutomatedTradingEngine(
    broker=broker,
    instrument=MNQ,

    risk_percent=RISK_PERCENT,

    risk_reward=RISK_REWARD,

    max_daily_loss=MAX_DAILY_LOSS,

    max_trades_per_day=MAX_TRADES_PER_DAY,

    max_consecutive_losses=(
        MAX_CONSEC_LOSSES
    ),
)


# ============================================================
# QUALITY CONFIGURATION
# ============================================================

quality_analyzer = (
    engine.trade_quality_analyzer
)


quality_analyzer.set_minimum_score(
    QUALITY_THRESHOLD
)


quality_analyzer.set_enforcement(
    QUALITY_ENFORCEMENT
)


# ============================================================
# CONFIGURATION DISPLAY
# ============================================================

print(
    f"          Starting balance : "
    f"${STARTING_BALANCE:,.2f}"
)

print(
    f"          Risk per trade   : "
    f"{RISK_PERCENT}%"
)

print(
    f"          Risk:Reward      : "
    f"1:{RISK_REWARD}"
)

print(
    f"          Trade Quality    : "
    f"{'ENFORCED' if QUALITY_ENFORCEMENT else 'SHADOW MODE'}"
)

print(
    f"          Quality minimum  : "
    f"{QUALITY_THRESHOLD}"
)

print(
    f"          Enforcement      : "
    f"{'ON' if QUALITY_ENFORCEMENT else 'OFF'}"
)

print()


# ============================================================
# STEP 3 - BACKTEST
# ============================================================

print(
    "Step 3/6  Running backtest..."
)

print(
    "          Progress will update every "
    "100,000 candles..."
)

print()


backtest_start = time.time()

total_candles = len(
    test_candles
)

next_progress = 100_000


# ============================================================
# PROCESS CANDLES
# ============================================================

for i, candle in enumerate(
    test_candles
):

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    if (
        i >= next_progress
        and total_candles > 100_000
    ):

        elapsed = (
            time.time()
            - backtest_start
        )

        progress = (
            i
            / total_candles
            * 100
        )

        eta_seconds = (

            elapsed
            / i
            * (total_candles - i)

            if i > 0

            else 0

        )

        print(
            f"          "
            f"[{i:>9,} / "
            f"{total_candles:,}] "
            f"{progress:5.1f}% | "
            f"ETA: "
            f"{eta_seconds / 60:.1f}m"
        )

        next_progress += 100_000


    # --------------------------------------------------------
    # PROCESS CANDLE
    # --------------------------------------------------------

    engine.process_candle(
        candle
    )


# ============================================================
# BACKTEST COMPLETE
# ============================================================

elapsed = (
    time.time()
    - backtest_start
)

print()

print(
    f"          Completed in "
    f"{elapsed / 60:.1f} minutes"
)

print()



# ============================================================
# GET EXECUTIONS
# ============================================================

executions = list(broker.executions)


# ============================================================
# R-MULTIPLE HELPERS
# ============================================================

def _get_context_value(context, *names, default=None):
    """Read a value from either a dict-like or object context."""
    if context is None:
        return default

    if isinstance(context, dict):
        for name in names:
            if name in context:
                return context[name]

    for name in names:
        value = getattr(context, name, None)
        if value is not None:
            return value

    return default


def _quality_from_execution(execution):
    """Extract trade-quality information from execution context."""
    context = getattr(execution, "context", None)

    quality = _get_context_value(
        context,
        "trade_quality",
        "quality",
        default=None,
    )

    if isinstance(quality, dict):
        return quality

    # Some versions store the quality fields directly in context.
    if context is not None:
        score = _get_context_value(
            context, "quality_score", "score", default=None
        )
        grade = _get_context_value(
            context, "quality_grade", "grade", default=None
        )

        if score is not None or grade is not None:
            return {
                "score": score if score is not None else 0,
                "grade": grade if grade is not None else "UNKNOWN",
                "trend_score": _get_context_value(context, "trend_score", default=0),
                "liquidity_score": _get_context_value(context, "liquidity_score", default=0),
                "fvg_score": _get_context_value(context, "fvg_score", default=0),
                "order_block_score": _get_context_value(context, "order_block_score", default=0),
                "regime_score": _get_context_value(context, "regime_score", default=0),
                "efficiency_score": _get_context_value(context, "efficiency_score", default=0),
                "volatility_score": _get_context_value(context, "volatility_score", default=0),
                "stop_quality_score": _get_context_value(context, "stop_quality_score", default=0),
                "entry_reason": _get_context_value(context, "entry_reason", default="UNKNOWN"),
            }

    return {
        "score": 0,
        "grade": "UNKNOWN",
        "trend_score": 0,
        "liquidity_score": 0,
        "fvg_score": 0,
        "order_block_score": 0,
        "regime_score": 0,
        "efficiency_score": 0,
        "volatility_score": 0,
        "stop_quality_score": 0,
        "entry_reason": "UNKNOWN",
    }


def calculate_trade_r(execution):
    """
    Calculate realized R for a closed trade.

    R is the initial monetary risk of that individual trade.

    Because the existing engine already uses a fixed 1:2 risk/reward
    plan and the PaperBroker closes only at stop-loss or take-profit,
    the initial risk can be reconstructed exactly from entry/exit:

      STOP LOSS -> 1R risk = realized loss magnitude
      TAKE PROFIT -> 1R = profit magnitude / 2

    For an unexpected exit reason, return None rather than inventing R.
    """
    entry = float(execution.entry_price)
    exit_price = float(execution.exit_price)
    contracts = int(execution.contracts)

    if contracts <= 0:
        return None

    price_move = abs(exit_price - entry)

    if price_move <= 0:
        return 0.0

    dollar_move = (
        price_move
        / MNQ.tick_size
        * MNQ.tick_value
        * contracts
    )

    reason = str(getattr(execution, "reason", "")).upper()

    if "STOP LOSS" in reason:
        initial_risk = dollar_move

    elif "TAKE PROFIT" in reason:
        initial_risk = dollar_move / RISK_REWARD

    else:
        # Fallback: use the actual stop distance if a context field
        # is available. This is only used for non-standard exits.
        context = getattr(execution, "context", None)
        stop_distance = _get_context_value(
            context,
            "stop_distance",
            "normalized_stop_distance",
            default=None,
        )

        if stop_distance is None:
            return None

        try:
            stop_distance = abs(float(stop_distance))
        except (TypeError, ValueError):
            return None

        initial_risk = (
            stop_distance
            / MNQ.tick_size
            * MNQ.tick_value
            * contracts
        )

    if initial_risk <= 0:
        return None

    return float(execution.pnl) / initial_risk


def calculate_initial_risk(execution):
    """Return the monetary value of 1R for a closed trade."""
    r = calculate_trade_r(execution)

    if r is None:
        return None

    if abs(r) < 1e-12:
        return 0.0

    return abs(float(execution.pnl) / r)


# ============================================================
# CALCULATE REALIZED R FOR EVERY TRADE
# ============================================================

trade_rows = []

for execution in executions:
    realized_r = calculate_trade_r(execution)
    initial_risk = calculate_initial_risk(execution)

    quality = _quality_from_execution(execution)

    trade_rows.append(
        {
            "execution": execution,
            "r": realized_r,
            "initial_risk": initial_risk,
            "quality": quality,
        }
    )


valid_r_rows = [
    row for row in trade_rows
    if row["r"] is not None
]


# ============================================================
# STEP 4 - R-BASED OVERALL PERFORMANCE
# ============================================================

print()
print("Step 4/6  R-Based Overall Performance")
print()

print("=" * 72)
print("                    RISK-NORMALIZED RESULTS")
print("=" * 72)
print()

total_trades = len(executions)

wins = [
    row for row in valid_r_rows
    if row["r"] > 0
]

losses = [
    row for row in valid_r_rows
    if row["r"] < 0
]

breakeven = [
    row for row in valid_r_rows
    if row["r"] == 0
]

winning_count = len(wins)
losing_count = len(losses)

win_rate = (
    winning_count / len(valid_r_rows) * 100
    if valid_r_rows
    else 0.0
)

net_r = sum(row["r"] for row in valid_r_rows)

gross_profit_r = sum(
    row["r"] for row in wins
)

gross_loss_r = abs(
    sum(row["r"] for row in losses)
)

profit_factor = (
    gross_profit_r / gross_loss_r
    if gross_loss_r > 0
    else (
        float("inf")
        if gross_profit_r > 0
        else 0.0
    )
)

average_r = (
    net_r / len(valid_r_rows)
    if valid_r_rows
    else 0.0
)

average_win_r = (
    gross_profit_r / winning_count
    if winning_count
    else 0.0
)

average_loss_r = (
    gross_loss_r / losing_count
    if losing_count
    else 0.0
)

# With every trade normalized by its own initial risk,
# expectancy is simply mean realized R per trade.
expectancy_r = average_r


print(f"   Total trades        : {total_trades:>12,}")
print(f"   R-valid trades      : {len(valid_r_rows):>12,}")
print(f"   Wins                : {winning_count:>12,}")
print(f"   Losses              : {losing_count:>12,}")
print(f"   Breakeven           : {len(breakeven):>12,}")
print(f"   Win rate            : {win_rate:>11.2f}%")
print()

print(f"   Net result          : {net_r:>+12.2f} R")
print(f"   Gross profit        : {gross_profit_r:>+12.2f} R")
print(f"   Gross loss          : {-gross_loss_r:>+12.2f} R")
print(f"   Average R / trade   : {average_r:>+12.4f} R")
print(f"   Expectancy          : {expectancy_r:>+12.4f} R/trade")
print(f"   Average winning R   : {average_win_r:>+12.4f} R")
print(f"   Average losing R    : {-average_loss_r:>+12.4f} R")
print(f"   Profit factor       : {profit_factor:>12.3f}")


# ============================================================
# R-BASED EQUITY / DRAWDOWN
# ============================================================

cumulative_r = 0.0
peak_r = 0.0
max_drawdown_r = 0.0
drawdown_at_trade = 0.0

current_loss_streak = 0
max_consecutive_losses = 0
worst_losing_streak_r = 0.0
current_losing_streak_r = 0.0

max_single_loss_r = 0.0
max_single_win_r = 0.0

for row in valid_r_rows:
    r = row["r"]

    cumulative_r += r

    peak_r = max(peak_r, cumulative_r)

    drawdown_at_trade = peak_r - cumulative_r
    max_drawdown_r = max(
        max_drawdown_r,
        drawdown_at_trade,
    )

    if r > 0:
        current_loss_streak = 0
        current_losing_streak_r = 0.0
        max_single_win_r = max(max_single_win_r, r)

    elif r < 0:
        current_loss_streak += 1
        current_losing_streak_r += r

        max_consecutive_losses = max(
            max_consecutive_losses,
            current_loss_streak,
        )

        worst_losing_streak_r = min(
            worst_losing_streak_r,
            current_losing_streak_r,
        )

        max_single_loss_r = min(
            max_single_loss_r,
            r,
        )

    else:
        current_loss_streak = 0
        current_losing_streak_r = 0.0


print()
print("   Max drawdown        : "
      f"-{max_drawdown_r:.2f} R")
print("   Max consec losses   : "
      f"{max_consecutive_losses:>12}")
print("   Worst loss streak   : "
      f"{worst_losing_streak_r:+.2f} R")
print("   Worst single trade  : "
      f"{max_single_loss_r:+.2f} R")
print("   Best single trade   : "
      f"{max_single_win_r:+.2f} R")


# ============================================================
# RISK-OF-RUIN / FUNDED ACCOUNT SAFETY SNAPSHOT
# ============================================================

print()
print("=" * 72)
print("                 FUNDED-ACCOUNT RISK SNAPSHOT")
print("=" * 72)
print()

print(f"   Risk per trade      : {RISK_PERCENT:.2f}% of equity")
print(f"   Target R:R          : 1:{RISK_REWARD:.1f}")
print(f"   Max drawdown        : -{max_drawdown_r:.2f} R")
print(f"   Max loss streak     : -{abs(worst_losing_streak_r):.2f} R")
print(f"   Consecutive losses  : {max_consecutive_losses}")
print()

print(
    "   NOTE: R is normalized to each trade's initial risk."
)
print(
    "   This is the primary risk metric for funded-account comparison."
)


# ============================================================
# STEP 5 - QUALITY PERFORMANCE IN R
# ============================================================

print()
print("Step 5/6  Trade Quality Profitability (R)")
print()

print("=" * 72)
print("                   QUALITY GRADE PERFORMANCE")
print("=" * 72)
print()

print(
    f"{'Grade':<8}"
    f"{'Trades':>10}"
    f"{'Wins':>9}"
    f"{'Losses':>9}"
    f"{'Win %':>10}"
    f"{'Net R':>15}"
    f"{'PF':>10}"
)

print("-" * 74)

QUALITY_GRADES = ("A+", "A", "B", "C", "D", "F", "UNKNOWN")

quality_stats = {
    grade: {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "gross_profit_r": 0.0,
        "gross_loss_r": 0.0,
        "net_r": 0.0,
    }
    for grade in QUALITY_GRADES
}

for row in valid_r_rows:
    quality = row["quality"]
    grade = str(quality.get("grade", "UNKNOWN"))

    if grade not in quality_stats:
        quality_stats[grade] = {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "gross_profit_r": 0.0,
            "gross_loss_r": 0.0,
            "net_r": 0.0,
        }

    stats = quality_stats[grade]
    r = row["r"]

    stats["trades"] += 1
    stats["net_r"] += r

    if r > 0:
        stats["wins"] += 1
        stats["gross_profit_r"] += r
    elif r < 0:
        stats["losses"] += 1
        stats["gross_loss_r"] += abs(r)

for grade in QUALITY_GRADES:
    stats = quality_stats[grade]
    count = stats["trades"]

    grade_win_rate = (
        stats["wins"] / count * 100
        if count
        else 0.0
    )

    grade_pf = (
        stats["gross_profit_r"]
        / stats["gross_loss_r"]
        if stats["gross_loss_r"] > 0
        else (
            float("inf")
            if stats["gross_profit_r"] > 0
            else 0.0
        )
    )

    pf_text = (
        f"{grade_pf:.3f}"
        if grade_pf != float("inf")
        else "inf"
    )

    print(
        f"{grade:<8}"
        f"{count:>10,}"
        f"{stats['wins']:>9,}"
        f"{stats['losses']:>9,}"
        f"{grade_win_rate:>9.2f}%"
        f"{stats['net_r']:>+14.2f} R"
        f"{pf_text:>10}"
    )


# ============================================================
# QUALITY THRESHOLD ATTRIBUTION IN R
# ============================================================

print()
print("=" * 72)
print("                 QUALITY THRESHOLD ATTRIBUTION (R)")
print("=" * 72)
print()
print(
    "NOTE: Analytical attribution only."
)
print(
    "It does NOT replay the strategy with each threshold."
)
print()

print(
    f"{'Threshold':<12}"
    f"{'Trades':>10}"
    f"{'Wins':>10}"
    f"{'Win %':>10}"
    f"{'Net R':>15}"
    f"{'PF':>10}"
)

print("-" * 70)

quality_records = []

for row in valid_r_rows:
    score = row["quality"].get("score", None)

    try:
        score = float(score)
    except (TypeError, ValueError):
        continue

    quality_records.append(
        {
            "score": score,
            "r": row["r"],
        }
    )

for threshold in (50, 60, 70, 80, 90):
    selected = [
        row
        for row in quality_records
        if row["score"] >= threshold
    ]

    threshold_trades = len(selected)

    threshold_wins = sum(
        1 for row in selected if row["r"] > 0
    )

    threshold_profit_r = sum(
        row["r"] for row in selected if row["r"] > 0
    )

    threshold_loss_r = abs(
        sum(
            row["r"]
            for row in selected
            if row["r"] < 0
        )
    )

    threshold_net_r = (
        threshold_profit_r - threshold_loss_r
    )

    threshold_win_rate = (
        threshold_wins / threshold_trades * 100
        if threshold_trades
        else 0.0
    )

    threshold_pf = (
        threshold_profit_r / threshold_loss_r
        if threshold_loss_r > 0
        else (
            float("inf")
            if threshold_profit_r > 0
            else 0.0
        )
    )

    pf_text = (
        f"{threshold_pf:.3f}"
        if threshold_pf != float("inf")
        else "inf"
    )

    print(
        f"{'>=' + str(threshold):<12}"
        f"{threshold_trades:>10,}"
        f"{threshold_wins:>10,}"
        f"{threshold_win_rate:>9.2f}%"
        f"{threshold_net_r:>+14.2f} R"
        f"{pf_text:>10}"
    )


# ============================================================
# ENTRY SETUP PERFORMANCE IN R
# ============================================================

print()
print("=" * 72)
print("                   ENTRY SETUP PERFORMANCE (R)")
print("=" * 72)
print()

print(
    f"{'Setup':<42}"
    f"{'Trades':>9}"
    f"{'Win %':>10}"
    f"{'Net R':>15}"
    f"{'PF':>10}"
)

print("-" * 88)

setup_stats = defaultdict(
    lambda: {
        "trades": 0,
        "wins": 0,
        "gross_profit_r": 0.0,
        "gross_loss_r": 0.0,
        "net_r": 0.0,
    }
)

for row in valid_r_rows:
    quality = row["quality"]

    setup_name = str(
        quality.get(
            "entry_reason",
            "UNKNOWN",
        )
    )

    stats = setup_stats[setup_name]
    r = row["r"]

    stats["trades"] += 1
    stats["net_r"] += r

    if r > 0:
        stats["wins"] += 1
        stats["gross_profit_r"] += r
    elif r < 0:
        stats["gross_loss_r"] += abs(r)

setup_rows = []

for setup_name, stats in setup_stats.items():
    count = stats["trades"]

    setup_win_rate = (
        stats["wins"] / count * 100
        if count
        else 0.0
    )

    setup_pf = (
        stats["gross_profit_r"]
        / stats["gross_loss_r"]
        if stats["gross_loss_r"] > 0
        else (
            float("inf")
            if stats["gross_profit_r"] > 0
            else 0.0
        )
    )

    setup_rows.append(
        (
            setup_name,
            count,
            setup_win_rate,
            stats["net_r"],
            setup_pf,
        )
    )

setup_rows.sort(
    key=lambda row: row[3],
    reverse=True,
)

for (
    setup_name,
    count,
    setup_win_rate,
    setup_net_r,
    setup_pf,
) in setup_rows:

    pf_text = (
        f"{setup_pf:.3f}"
        if setup_pf != float("inf")
        else "inf"
    )

    print(
        f"{str(setup_name)[:42]:<42}"
        f"{count:>9,}"
        f"{setup_win_rate:>9.2f}%"
        f"{setup_net_r:>+14.2f} R"
        f"{pf_text:>10}"
    )


# ============================================================
# SAVE R-ENHANCED TRADE JOURNAL
# ============================================================

print()
print("=" * 72)
print("                    TRADE JOURNAL")
print("=" * 72)
print()

journal_file = "backtest_trade_quality_R.csv"

with open(
    journal_file,
    "w",
    newline="",
    encoding="utf-8",
) as csv_file:

    fieldnames = [
        "trade_number",
        "open_timestamp",
        "close_timestamp",
        "direction",
        "entry_price",
        "exit_price",
        "contracts",
        "reason",
        "pnl_usd",
        "initial_risk_usd",
        "realized_R",
        "quality_score",
        "grade",
        "entry_reason",
    ]

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames,
    )

    writer.writeheader()

    for number, row in enumerate(
        trade_rows,
        start=1,
    ):
        execution = row["execution"]
        quality = row["quality"]

        writer.writerow(
            {
                "trade_number": number,
                "open_timestamp": getattr(
                    execution,
                    "entry_time",
                    "",
                ),
                "close_timestamp": getattr(
                    execution,
                    "exit_time",
                    "",
                ),
                "direction": getattr(
                    execution,
                    "direction",
                    "",
                ),
                "entry_price": getattr(
                    execution,
                    "entry_price",
                    "",
                ),
                "exit_price": getattr(
                    execution,
                    "exit_price",
                    "",
                ),
                "contracts": getattr(
                    execution,
                    "contracts",
                    "",
                ),
                "reason": getattr(
                    execution,
                    "reason",
                    "",
                ),
                "pnl_usd": getattr(
                    execution,
                    "pnl",
                    "",
                ),
                "initial_risk_usd": (
                    row["initial_risk"]
                    if row["initial_risk"] is not None
                    else ""
                ),
                "realized_R": (
                    row["r"]
                    if row["r"] is not None
                    else ""
                ),
                "quality_score": quality.get(
                    "score",
                    0,
                ),
                "grade": quality.get(
                    "grade",
                    "UNKNOWN",
                ),
                "entry_reason": quality.get(
                    "entry_reason",
                    "",
                ),
            }
        )

print(
    f"   R-based journal saved : {journal_file}"
)

print(
    f"   R-valid trades        : {len(valid_r_rows):,}"
)


# ============================================================
# REJECTIONS
# ============================================================

rejections = getattr(
    engine,
    "rejections",
    None,
)

if rejections:
    print()
    print("=" * 72)
    print("                         REJECTIONS")
    print("=" * 72)
    print()

    for reason, count in sorted(
        rejections.items(),
        key=lambda x: -x[1],
    ):
        print(
            f"   {str(reason):<60}"
            f" : {count:>8,}"
        )


# ============================================================
# STEP 6 - FINAL DECISION
# ============================================================

print()
print("=" * 72)
print("                         NEXT DECISION")
print("=" * 72)
print()

print("   Primary accounting  : R-MULTIPLES")
print(f"   Risk per trade      : {RISK_PERCENT:.2f}%")
print(f"   Risk:Reward         : 1:{RISK_REWARD:.1f}")
print(f"   Quality minimum     : {QUALITY_THRESHOLD}")
print(
    "   Quality mode        : "
    f"{'ENFORCED' if QUALITY_ENFORCEMENT else 'SHADOW MODE'}"
)
print()
print(f"   Net result          : {net_r:+.2f} R")
print(f"   Expectancy          : {expectancy_r:+.4f} R/trade")
print(f"   Max drawdown        : -{max_drawdown_r:.2f} R")
print(f"   Worst loss streak   : {worst_losing_streak_r:+.2f} R")
print(f"   Profit factor       : {profit_factor:.3f}")
print()
print(f"   Trade journal       : {journal_file}")
print()
print(
    "   USD values are retained only inside the R journal"
    " as a secondary audit field."
)
print(
    "   No INR conversion is applied."
)
print()
print(
    f"   Completed : "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
print("=" * 72)
print()
