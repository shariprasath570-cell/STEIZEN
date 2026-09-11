from src.data_loader.csv_loader import CSVLoader
from src.broker.paper_broker import PaperBroker
from src.core.automated_trading_engine import AutomatedTradingEngine
from src.models.instrument import InstrumentSpec


print()
print("=" * 70)
print("        STEIZEN - ENGINE INTEGRATION SMOKE TEST")
print("=" * 70)

# ============================================================
# CONFIG
# ============================================================

STARTING_BALANCE = 10_000.0
RISK_PERCENT = 1.0
RISK_REWARD = 2.0

MAX_CANDLES = 25_000

# ============================================================
# LOAD DATA
# ============================================================

print()
print("Step 1 - Loading historical data...")

candles = CSVLoader().load(
    "data/Dataset_NQ_1min_2022_2025.csv"
)

test_candles = candles[:MAX_CANDLES]

print(
    f"          Total dataset : {len(candles):,}"
)

print(
    f"          Test candles  : {len(test_candles):,}"
)

print(
    f"          Range         : "
    f"{test_candles[0].timestamp} → "
    f"{test_candles[-1].timestamp}"
)

# ============================================================
# INSTRUMENT
# ============================================================

MNQ = InstrumentSpec(
    symbol="MNQ",
    tick_size=0.25,
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
    max_daily_loss=5_000.0,
    max_trades_per_day=50,
    max_consecutive_losses=50,
)

# ============================================================
# STATISTICS
# ============================================================

opened = 0
closed = 0
rejected = 0

entry_zone_created = 0
trading_locked = 0

max_contracts = 0
max_balance = STARTING_BALANCE
min_balance = STARTING_BALANCE

rejection_reasons = {}

# ============================================================
# RUN
# ============================================================

print()
print("Step 2 - Running engine...")
print()

for i, candle in enumerate(test_candles):

    event = engine.process_candle(
        candle
    )

    # --------------------------------------------------------
    # BALANCE
    # --------------------------------------------------------

    balance = broker.balance

    max_balance = max(
        max_balance,
        balance,
    )

    min_balance = min(
        min_balance,
        balance,
    )

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    if event is None:
        continue

    event_type = getattr(
        event,
        "event_type",
        "",
    )

    # --------------------------------------------------------
    # TRADE OPEN
    # --------------------------------------------------------

    if event_type == "TRADE_OPENED":

        opened += 1

        data = (
            event.data
            if isinstance(
                event.data,
                dict,
            )
            else {}
        )

        position = data.get(
            "position"
        )

        if position is not None:

            contracts = getattr(
                position,
                "quantity",
                getattr(
                    position,
                    "contracts",
                    0,
                ),
            )

            try:
                contracts = abs(
                    int(contracts)
                )
            except (
                TypeError,
                ValueError,
            ):
                contracts = 0

            max_contracts = max(
                max_contracts,
                contracts,
            )

    # --------------------------------------------------------
    # TRADE CLOSED
    # --------------------------------------------------------

    elif event_type == "TRADE_CLOSED":

        closed += 1

    # --------------------------------------------------------
    # ENTRY ZONE
    # --------------------------------------------------------

    elif (
        event_type
        == "ENTRY_ZONE_CREATED"
    ):

        entry_zone_created += 1

    # --------------------------------------------------------
    # REJECTION
    # --------------------------------------------------------

    elif (
        event_type
        == "TRADE_REJECTED"
    ):

        rejected += 1

        reason = str(
            getattr(
                event,
                "message",
                "UNKNOWN",
            )
        )

        rejection_reasons[
            reason
        ] = (
            rejection_reasons.get(
                reason,
                0,
            )
            + 1
        )

    # --------------------------------------------------------
    # LOCK
    # --------------------------------------------------------

    elif (
        event_type
        == "TRADING_LOCKED"
    ):

        trading_locked += 1

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    if (
        (i + 1) % 5_000
        == 0
    ):

        print(
            f"          "
            f"{i + 1:>7,} / "
            f"{MAX_CANDLES:,} | "
            f"Opened: {opened:>4} | "
            f"Closed: {closed:>4} | "
            f"Balance: "
            f"${balance:>12,.2f} | "
            f"Pending: "
            f"{engine.entry_engine.pending_count():>3}"
        )

# ============================================================
# RESULTS
# ============================================================

print()
print("=" * 70)
print("                    SMOKE TEST RESULTS")
print("=" * 70)

print()

print(
    f"Starting balance       : "
    f"${STARTING_BALANCE:,.2f}"
)

print(
    f"Ending balance         : "
    f"${broker.balance:,.2f}"
)

print(
    f"Net P/L                : "
    f"${broker.balance - STARTING_BALANCE:+,.2f}"
)

print()

print(
    f"Candles processed      : "
    f"{MAX_CANDLES:,}"
)

print(
    f"Trades opened          : "
    f"{opened:,}"
)

print(
    f"Trades closed          : "
    f"{closed:,}"
)

print(
    f"Entry zones created    : "
    f"{entry_zone_created:,}"
)

print(
    f"Pending zones          : "
    f"{engine.entry_engine.pending_count():,}"
)

print(
    f"Registered zones       : "
    f"{engine.entry_engine.registered_count():,}"
)

print(
    f"Consumed zones         : "
    f"{engine.entry_engine.consumed_count():,}"
)

print()

print(
    f"Rejected trades        : "
    f"{rejected:,}"
)

print(
    f"Trading locked events  : "
    f"{trading_locked:,}"
)

print(
    f"Maximum contracts      : "
    f"{max_contracts:,}"
)

print(
    f"Maximum balance        : "
    f"${max_balance:,.2f}"
)

print(
    f"Minimum balance        : "
    f"${min_balance:,.2f}"
)

# ============================================================
# REJECTION BREAKDOWN
# ============================================================

if rejection_reasons:

    print()
    print("Rejection reasons")
    print("-" * 50)

    for reason, count in sorted(
        rejection_reasons.items(),
        key=lambda x: -x[1],
    ):

        print(
            f"{reason:<40} : "
            f"{count:>7,}"
        )

# ============================================================
# SANITY CHECK
# ============================================================

print()
print("=" * 70)
print("                    SANITY CHECK")
print("=" * 70)
print()

problems = []

if max_contracts > 20:

    problems.append(
        "MAX CONTRACT LIMIT EXCEEDED"
    )

if max_balance > (
    STARTING_BALANCE * 10
):

    problems.append(
        "BALANCE EXPLOSION DETECTED"
    )

if opened > 10_000:

    problems.append(
        "EXCESSIVE TRADE COUNT"
    )

if problems:

    print(
        "❌ SMOKE TEST FAILED"
    )

    print()

    for problem in problems:

        print(
            f"   - {problem}"
        )

else:

    print(
        "✅ SMOKE TEST PASSED"
    )

print()
print("=" * 70)
print()