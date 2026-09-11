from src.broker.broker_reconciler import BrokerReconciler
from src.broker.paper_broker import PaperBroker

from src.core.automated_trading_engine import (
    AutomatedTradingEngine,
)
from src.core.candle_checkpoint import CandleCheckpoint
from src.core.event_logger import EventLogger
from src.core.paper_bot_runner import PaperBotRunner
from src.core.processing_journal import ProcessingJournal
from src.core.recovery_manager import RecoveryManager
from src.core.runtime_paths import build_runtime_paths
from src.core.startup_guard import StartupGuard
from src.core.state_store import StateStore

from src.data_loader.csv_loader import CSVLoader
from src.data_loader.replay_candle_source import (
    ReplayCandleSource,
)

from src.models.instrument import InstrumentSpec

from src.risk.kill_switch import KillSwitch


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "data/mnq_test_500.csv"

STARTING_BALANCE = 10000.0

RISK_PERCENT = 1.0
RISK_REWARD = 2.0

MAX_DAILY_LOSS = 300.0
MAX_TRADES_PER_DAY = 5
MAX_CONSECUTIVE_LOSSES = 3


# ============================================================
# LOCAL RUNTIME PATHS
# ============================================================

runtime_paths = build_runtime_paths(
    "ICT_BOT"
)

STATE_FILE = str(
    runtime_paths.state
)

CHECKPOINT_FILE = str(
    runtime_paths.checkpoint
)

EVENT_FILE = str(
    runtime_paths.events
)

PROCESSING_JOURNAL_FILE = str(
    runtime_paths.processing_journal
)

KILL_FILE = str(
    runtime_paths.kill_switch
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
# LOAD MARKET DATA
# ============================================================

candles = CSVLoader().load(
    DATA_FILE
)


# ============================================================
# BROKER
# ============================================================

broker = PaperBroker(
    starting_balance=STARTING_BALANCE,
    instrument=MNQ,
)


# ============================================================
# PERSISTENCE
# ============================================================

state_store = StateStore(
    STATE_FILE
)

checkpoint = CandleCheckpoint(
    CHECKPOINT_FILE
)

processing_journal = ProcessingJournal(
    PROCESSING_JOURNAL_FILE
)


# ============================================================
# RECOVERY
# ============================================================

recovery_manager = RecoveryManager(
    checkpoint=checkpoint,
    processing_journal=processing_journal,
)


# ============================================================
# EVENT LOGGER
# ============================================================

event_logger = EventLogger(
    EVENT_FILE
)


# ============================================================
# KILL SWITCH
# ============================================================

kill_switch = KillSwitch(
    KILL_FILE
)


# ============================================================
# AUTOMATED TRADING ENGINE
# ============================================================

engine = AutomatedTradingEngine(
    broker=broker,
    instrument=MNQ,
    risk_percent=RISK_PERCENT,
    risk_reward=RISK_REWARD,
    max_daily_loss=MAX_DAILY_LOSS,
    max_trades_per_day=MAX_TRADES_PER_DAY,
    max_consecutive_losses=(
        MAX_CONSECUTIVE_LOSSES
    ),
    state_store=state_store,
    kill_switch=kill_switch,
)


# ============================================================
# STARTUP BROKER RECONCILIATION
# ============================================================

reconciler = BrokerReconciler()

expected_position = (
    reconciler.load_expected_position(
        STATE_FILE
    )
)

startup_guard = StartupGuard(
    reconciler=reconciler,
    kill_switch=kill_switch,
)

startup_result = startup_guard.validate(
    expected_position=expected_position,
    broker=broker,
)


# ============================================================
# FAIL-CLOSED STARTUP
# ============================================================

if not startup_result.allowed:

    print()

    print(
        "BOT STARTUP BLOCKED"
    )

    print(
        "=" * 70
    )

    print(
        "Reason      :",
        startup_result.reason,
    )

    print(
        "Kill Switch :",
        kill_switch.state.active,
    )

    print(
        "Kill Reason :",
        kill_switch.state.reason,
    )

    raise SystemExit(
        "TRADING ENGINE STARTUP REFUSED"
    )


# ============================================================
# STARTUP RECOVERY ANALYSIS
# ============================================================

recovery_required = (
    recovery_manager.requires_recovery()
)

processing_state = (
    processing_journal.load()
)

recovery_timestamp = None

if recovery_required:

    recovery_timestamp = (
        recovery_manager.get_recovery_timestamp()
    )


# ============================================================
# MARKET STATE WARM-UP
# ============================================================

warmup_count = 0

if checkpoint.last_timestamp is not None:

    for candle in candles:

        if (
            recovery_timestamp is not None
            and candle.timestamp >= recovery_timestamp
        ):
            break

        if (
            candle.timestamp
            > checkpoint.last_timestamp
        ):
            break

        engine.warm_up_candle(
            candle
        )

        warmup_count += 1


# ============================================================
# SELECT REPLAY START INDEX
# ============================================================

start_index = 0

if recovery_required:

    start_index = len(
        candles
    )

    for index, candle in enumerate(
        candles
    ):

        if (
            candle.timestamp
            == recovery_timestamp
        ):

            start_index = index

            break


elif checkpoint.last_timestamp is not None:

    start_index = len(
        candles
    )

    for index, candle in enumerate(
        candles
    ):

        if (
            candle.timestamp
            > checkpoint.last_timestamp
        ):

            start_index = index

            break


# ============================================================
# REPLAY SOURCE
# ============================================================

replay_candles = candles[
    start_index:
]

candle_source = ReplayCandleSource(
    candles=replay_candles,
    batch_size=1,
)


# ============================================================
# PAPER BOT RUNNER
# ============================================================

runner = PaperBotRunner(
    engine=engine,
    candle_source=candle_source,
    checkpoint=checkpoint,
    event_logger=event_logger,
    poll_interval=0.1,
    stop_when_exhausted=True,
    processing_journal=processing_journal,
)


# ============================================================
# STARTUP STATUS
# ============================================================

print()

print(
    "MNQ ICT AUTOMATED PAPER BOT"
)

print(
    "=" * 70
)

print(
    "Runtime Directory :",
    runtime_paths.root,
)

print(
    "State Restored    :",
    engine.state_restored,
)

print(
    "Starting Balance  : $",
    broker.balance,
)

print(
    "Kill Switch       :",
    kill_switch.check(),
)

print(
    "Startup Guard     :",
    startup_result.allowed,
)

print(
    "Reconciliation    :",
    startup_result.reason,
)

print(
    "Last Checkpoint   :",
    checkpoint.last_timestamp,
)

print(
    "Recovery Required :",
    recovery_required,
)

print(
    "Recovery Timestamp:",
    recovery_timestamp,
)

print(
    "Warm-up Candles   :",
    warmup_count,
)

print(
    "Replay Start Index:",
    start_index,
)


if processing_state is None:

    print(
        "Processing State  : None"
    )

else:

    print(
        "Processing State  :",
        processing_state.get(
            "status"
        ),
        "|",
        processing_state.get(
            "timestamp"
        ),
    )


print()


# ============================================================
# START PAPER BOT
# ============================================================

runner.run()


# ============================================================
# FINAL BOT STATE
# ============================================================

print()

print(
    "=" * 70
)

print(
    "FINAL PAPER BOT STATE"
)

print(
    "=" * 70
)

print(
    "Balance           : $",
    broker.balance,
)

print(
    "Executions        :",
    len(
        broker.executions
    ),
)

print(
    "Daily P/L         : $",
    engine.risk_governor.state.daily_pnl,
)

print(
    "Daily Trades      :",
    engine.risk_governor.state.trades_taken,
)

print(
    "Consecutive Loss  :",
    engine.risk_governor.state.consecutive_losses,
)

print(
    "Trading Locked    :",
    engine.risk_governor.state.locked,
)

print(
    "Lock Reason       :",
    engine.risk_governor.state.lock_reason,
)

print(
    "Open Position     :",
    broker.has_open_position,
)

print(
    "Last Checkpoint   :",
    checkpoint.last_timestamp,
)


final_processing_state = (
    processing_journal.load()
)


if final_processing_state is None:

    print(
        "Processing State  : None"
    )

else:

    print(
        "Processing State  :",
        final_processing_state.get(
            "status"
        ),
        "|",
        final_processing_state.get(
            "timestamp"
        ),
    )