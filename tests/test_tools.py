from app.agent import ROUTES
from app.tools import TOOLS


def test_every_tool_is_wired_to_the_backend():
    names = {t["function"]["name"] for t in TOOLS}
    assert names == set(ROUTES) | {"verify_identity"}