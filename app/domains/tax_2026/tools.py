from __future__ import annotations


def calculate_personal_income_tax_2026(monthly_taxable_income: float) -> dict:
    brackets = [
        (5_000_000.0, 0.05),
        (5_000_000.0, 0.10),
        (8_000_000.0, 0.15),
        (14_000_000.0, 0.20),
        (20_000_000.0, 0.25),
        (28_000_000.0, 0.30),
        (float("inf"), 0.35),
    ]

    remaining = max(0.0, monthly_taxable_income)
    total_tax = 0.0
    details: list[dict] = []
    for bucket, rate in brackets:
        if remaining <= 0:
            break
        taxable_at_rate = min(remaining, bucket)
        tax_at_rate = taxable_at_rate * rate
        details.append(
            {
                "taxable_amount": round(taxable_at_rate, 2),
                "rate": rate,
                "tax": round(tax_at_rate, 2),
            }
        )
        total_tax += tax_at_rate
        remaining -= taxable_at_rate

    return {
        "monthly_taxable_income": round(monthly_taxable_income, 2),
        "tax": round(total_tax, 2),
        "details": details,
    }
