import pytest
from app.readability import compute_readability

def test_compute_readability_empty():
    res = compute_readability("")
    assert res["score"] == 100.0

def test_compute_readability_simple_text():
    # This is a very simple sentence, should score high (easy to read)
    text = "The cat sat on the mat."
    res = compute_readability(text)
    assert res["score"] > 80.0

def test_compute_readability_complex_text():
    # This is complex legal text, should score lower
    text = "The aforementioned parties hereby mutually agree to indemnify and hold harmless the other from any and all liabilities, damages, claims, and expenses arising out of the execution of this agreement."
    res = compute_readability(text)
    assert res["score"] < 60.0
