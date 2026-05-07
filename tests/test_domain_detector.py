from app.domains.registry import Domain
from app.ingestion.domain_detector import detect_domain_from_file


def test_detect_domain_policy_from_filename():
    assert (
        detect_domain_from_file("noi_quy_lao_dong.pdf", "")
        == Domain.POLICY
    )


def test_detect_domain_tax_from_content():
    assert (
        detect_domain_from_file(
            "reference.md", "Hướng dẫn thuế tncn và giảm trừ người phụ thuộc"
        )
        == Domain.TAX_2026
    )


def test_detect_domain_unknown():
    assert detect_domain_from_file("general.txt", "hello world") == Domain.UNKNOWN
