from app.domains.registry import Domain
from app.domains.router import route_domain


def test_route_domain_tax():
    assert (
        route_domain("Lương gross 25 triệu thì thuế tncn bao nhiêu?")
        == Domain.TAX_2026
    )


def test_route_domain_policy():
    assert route_domain("Nội quy nghỉ phép năm như thế nào?") == Domain.POLICY


def test_route_domain_unknown():
    assert route_domain("Hôm nay thời tiết thế nào?") == Domain.UNKNOWN
