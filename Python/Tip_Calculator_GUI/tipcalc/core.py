from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, getcontext
from decimal import ROUND_HALF_UP, ROUND_CEILING, ROUND_FLOOR

getcontext().prec = 28  # plenty for currency math

@dataclass(frozen=True)
class TipResult:
    bill: Decimal
    tip_pct: Decimal
    tip_amount: Decimal
    total: Decimal
    per_person: Decimal
    people: int
    rounded: bool
    round_target: str | None
    round_step: Decimal | None
    round_mode: str | None

def _to_decimal(x) -> Decimal:
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x))

def _round_to_step(value: Decimal, step: Decimal, mode: str) -> Decimal:
    value = _to_decimal(value)
    step = _to_decimal(step)
    if step <= 0:
        raise ValueError("step must be > 0")
    q = value / step
    if mode == "nearest":
        rounded_units = q.to_integral_value(rounding=ROUND_HALF_UP)
    elif mode == "up":
        rounded_units = q.to_integral_value(rounding=ROUND_CEILING)
    elif mode == "down":
        rounded_units = q.to_integral_value(rounding=ROUND_FLOOR)
    else:
        raise ValueError("mode must be one of: nearest|up|down")
    return rounded_units * step

def compute_tip(
    bill,
    tip_pct,
    people: int = 1,
    round_to: float | Decimal | None = None,
    round_target: str = "none",
    round_mode: str = "nearest",
) -> TipResult:
    bill = _to_decimal(bill)
    tip_pct = _to_decimal(tip_pct)

    if bill < 0:
        raise ValueError("bill must be >= 0")
    if tip_pct < 0:
        raise ValueError("tip_pct must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if round_target not in {"none", "total", "per_person", "tip"}:
        raise ValueError("round_target must be one of: none|total|per_person|tip")

    tip_amount = (bill * tip_pct) / Decimal("100")
    total = bill + tip_amount
    per_person = total / people

    rounded = False
    rt = None
    rs = None
    rm = None

    if round_target != "none" and round_to is not None:
        step = _to_decimal(round_to)

        if round_target == "total":
            total = _round_to_step(total, step, round_mode)
            per_person = total / people
        elif round_target == "per_person":
            per_person = _round_to_step(per_person, step, round_mode)
            total = per_person * people
        elif round_target == "tip":
            tip_amount = _round_to_step(tip_amount, step, round_mode)
            total = bill + tip_amount
            per_person = total / people

        rounded = True
        rt = round_target
        rs = step
        rm = round_mode

    return TipResult(
        bill=bill,
        tip_pct=tip_pct,
        tip_amount=tip_amount,
        total=total,
        per_person=per_person,
        people=people,
        rounded=rounded,
        round_target=rt,
        round_step=rs,
        round_mode=rm,
    )

def format_money(x: Decimal) -> str:
    return f"${x:.2f}"