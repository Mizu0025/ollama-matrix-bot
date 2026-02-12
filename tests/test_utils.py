import pytest
from utils import split_text_into_chunks

def test_single_paragraph_returns_one_chunk():
    # Arrange
    text = "This is a single paragraph."
    
    # Act
    chunks = split_text_into_chunks(text)
    
    # Assert
    assert len(chunks) == 1
    assert chunks[0] == text

def test_two_paragraphs_return_one_chunk_default():
    # Arrange
    text = "Graph 1.\n\nGraph 2."
    
    # Act
    chunks = split_text_into_chunks(text)
    
    # Assert
    assert len(chunks) == 1
    assert chunks[0] == text

def test_three_paragraphs_return_two_chunks_default():
    # Arrange
    text = "Graph 1.\n\nGraph 2.\n\nGraph 3."
    
    # Act
    chunks = split_text_into_chunks(text)
    
    # Assert
    assert len(chunks) == 2
    assert chunks[0] == "Graph 1.\n\nGraph 2."
    assert chunks[1] == "Graph 3."

def test_four_paragraphs_return_two_chunks_default():
    # Arrange
    text = "Graph 1.\n\nGraph 2.\n\nGraph 3.\n\nGraph 4."
    
    # Act
    chunks = split_text_into_chunks(text)
    
    # Assert
    assert len(chunks) == 2
    assert chunks[0] == "Graph 1.\n\nGraph 2."
    assert chunks[1] == "Graph 3.\n\nGraph 4."

def test_empty_text_returns_empty_list():
    # Arrange
    text = ""
    
    # Act
    chunks = split_text_into_chunks(text)
    
    # Assert
    assert chunks == []

def test_custom_chunk_size():
    # Arrange
    text = "G1.\n\nG2.\n\nG3."
    
    # Act
    chunks = split_text_into_chunks(text, paragraphs_per_chunk=1)
    
    # Assert
    assert len(chunks) == 3
    assert chunks[0] == "G1."
    assert chunks[1] == "G2."
    assert chunks[2] == "G3."

def test_handles_multiple_newlines_gracefully():
    # Arrange
    # Even if there are extra newlines, split('\n\n') might create empty strings,
    # which we should probably filter out or handle.
    # Current impl filters out empty strings.
    text = "G1.\n\n\n\nG2."
    
    # Act
    # "G1.\n\n\n\nG2.".split('\n\n') -> ["G1.", "", "G2."]
    # My impl: iterates, skips empty if I added the check.
    # Let's verify my impl logic in thought.
    chunks = split_text_into_chunks(text)
    
    # Assert
    # Logic:
    # "G1." -> added to current_chunk ["G1."]
    # "" -> skipped (if proper check exists)
    # "G2." -> added to current_chunk ["G1.", "G2."]
    # len(current_chunk) == 2 -> append "\n\n".join -> "G1.\n\nG2."
    assert len(chunks) == 1
    assert chunks[0] == "G1.\n\nG2."

