import pytest
from utils import split_text_into_chunks

def test_split_text_into_chunks_small():
    text = "Small text"
    chunks = split_text_into_chunks(text, max_size=100)
    assert chunks == ["Small text"]

def test_split_text_into_chunks_at_newline():
    text = "Line 1\nLine 2\nLine 3"
    # "Line 1\n" is 7 bytes
    chunks = split_text_into_chunks(text, max_size=10)
    assert chunks == ["Line 1\n", "Line 2\n", "Line 3"]

def test_split_text_into_chunks_force_split():
    text = "Abcdefghij"
    chunks = split_text_into_chunks(text, max_size=5)
    assert chunks == ["Abcde", "fghij"]

def test_split_text_into_chunks_unicode():
    text = "こんにちは世界" # 21 bytes
    # "こんに" is 9 bytes
    chunks = split_text_into_chunks(text, max_size=10)
    assert chunks[0] == "こんに"
    assert "".join(chunks) == text

def test_split_text_into_chunks_empty():
    assert split_text_into_chunks("") == [""]
