from app.domains.tax_2026.tools import calculate_personal_income_tax_2026


def test_calculate_personal_income_tax_2026_basic():
    result = calculate_personal_income_tax_2026(10_000_000)
    assert result["monthly_taxable_income"] == 10_000_000
    assert result["tax"] == 750_000
    assert len(result["details"]) == 2
