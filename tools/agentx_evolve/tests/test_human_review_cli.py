import pytest
from agentx_evolve.human_review.review_cli import main


def test_main_no_args():
    with pytest.raises(SystemExit):
        main()
