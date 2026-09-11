from datetime import datetime, timedelta

from src.execution.entry_engine import EntryEngine
from src.models.candle import Candle
from src.models.fvg import FairValueGap
from src.models.order_block import OrderBlock
from src.models.instrument import InstrumentSpec


def main():

    print()
    print("=" * 60)
    print("ENTRY ENGINE - LIFECYCLE TEST")
    print("=" * 60)

    engine = EntryEngine(
        zone_tolerance=0.01,
        minimum_score=60,
        require_liquidity=False,
        max_zone_age=100,
    )

    instrument = InstrumentSpec(
        symbol="MNQ",
        tick_size=0.25,
        tick_value=0.50,
    )

    base_time = datetime(
        2025,
        1,
        1,
        10,
        0,
    )

    # ========================================================
    # STRUCTURES
    # ========================================================

    fvg = FairValueGap(
        timestamp=base_time,
        direction="BULLISH",
        top=101.00,
        bottom=100.00,
    )

    order_block = OrderBlock(
        timestamp=base_time,
        direction="BULLISH",
        high=100.75,
        low=99.75,
    )

    # Overlap should be:
    #
    # FVG       100.00 ───── 101.00
    # OB         99.75 ───── 100.75
    #
    # Overlap   100.00 ───── 100.75
    #
    # Midpoint = 100.375
    #
    # Rounded MNQ entry = 100.50

    # ========================================================
    # STEP 1
    # ========================================================

    created = engine.create_pending_zones(
        direction="BUY",
        fvgs=[fvg],
        order_blocks=[order_block],
        liquidity_levels=[],
        candle_index=10,
    )

    print()
    print("Step 1 - Create zone")
    print(
        "Created:",
        created,
    )
    print(
        "Pending:",
        engine.pending_count(),
    )
    print(
        "Registered:",
        engine.registered_count(),
    )

    assert created == 1
    assert engine.pending_count() == 1
    assert engine.registered_count() == 1

    # ========================================================
    # STEP 2
    # DUPLICATE STRUCTURE
    # ========================================================

    duplicate_created = (
        engine.create_pending_zones(
            direction="BUY",
            fvgs=[fvg],
            order_blocks=[order_block],
            liquidity_levels=[],
            candle_index=11,
        )
    )

    print()
    print("Step 2 - Duplicate structure")
    print(
        "Created:",
        duplicate_created,
    )
    print(
        "Pending:",
        engine.pending_count(),
    )
    print(
        "Registered:",
        engine.registered_count(),
    )

    assert duplicate_created == 0
    assert engine.pending_count() == 1

    # ========================================================
    # STEP 3
    # FUTURE CANDLE DOES NOT TOUCH ZONE
    # ========================================================

    candle_no_touch = Candle(
        timestamp=base_time + timedelta(minutes=2),
        open=102.00,
        high=102.50,
        low=101.50,
        close=102.25,
        volume=1000,
        timeframe="1m",
    )

    result = engine.check_retracement(
        direction="BUY",
        candle=candle_no_touch,
        candle_index=12,
        instrument=instrument,
    )

    print()
    print("Step 3 - No retracement")
    print(
        "Valid:",
        result.valid,
    )
    print(
        "Reason:",
        result.reason,
    )
    print(
        "Pending:",
        engine.pending_count(),
    )

    assert result.valid is False
    assert result.reason == "WAITING_FOR_RETRACEMENT"
    assert engine.pending_count() == 1

    # ========================================================
    # STEP 4
    # FUTURE CANDLE TOUCHES ZONE
    # ========================================================

    candle_retrace = Candle(
        timestamp=base_time + timedelta(minutes=3),
        open=101.25,
        high=101.50,
        low=100.25,
        close=100.50,
        volume=1000,
        timeframe="1m",
    )

    result = engine.check_retracement(
        direction="BUY",
        candle=candle_retrace,
        candle_index=13,
        instrument=instrument,
    )

    print()
    print("Step 4 - Retracement")
    print(
        "Valid:",
        result.valid,
    )
    print(
        "Entry:",
        result.entry_price,
    )
    print(
        "Zone:",
        result.zone_low,
        "→",
        result.zone_high,
    )
    print(
        "Reason:",
        result.reason,
    )
    print(
        "Pending:",
        engine.pending_count(),
    )
    print(
        "Consumed:",
        engine.consumed_count(),
    )

    assert result.valid is True
    assert result.entry_price == 100.5
    assert engine.pending_count() == 0
    assert engine.consumed_count() == 1

    # ========================================================
    # STEP 5
    # SAME STRUCTURE MUST NEVER RETURN
    # ========================================================

    recreated = engine.create_pending_zones(
        direction="BUY",
        fvgs=[fvg],
        order_blocks=[order_block],
        liquidity_levels=[],
        candle_index=14,
    )

    print()
    print("Step 5 - Recreate consumed structure")
    print(
        "Created:",
        recreated,
    )
    print(
        "Pending:",
        engine.pending_count(),
    )
    print(
        "Registered:",
        engine.registered_count(),
    )
    print(
        "Consumed:",
        engine.consumed_count(),
    )

    assert recreated == 0
    assert engine.pending_count() == 0
    assert engine.registered_count() == 1
    assert engine.consumed_count() == 1

    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("=" * 60)
    print("RESULT: ENTRY LIFECYCLE TEST PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()