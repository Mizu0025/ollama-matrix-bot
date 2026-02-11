import pytest
from utils import split_text_into_chunks

def Should_ReturnSingleChunk_WhenTextIsSmallerThanMaxSize():
    # Arrange
    text = "Small text"
    max_size = 100
    
    # Act
    chunks = split_text_into_chunks(text, max_size=max_size)
    
    # Assert
    assert chunks == ["Small text"]

def Should_SplitAtNewline_WhenNewlineIsWithinMaxSize():
    # Arrange
    text = "Line 1\nLine 2\nLine 3"
    max_size = 10 # "Line 1\n" is 7 bytes
    
    # Act
    chunks = split_text_into_chunks(text, max_size=max_size)
    
    # Assert
    assert chunks == ["Line 1\n", "Line 2\n", "Line 3"]

def Should_ForceSplit_WhenNoNewlineIsWithinMaxSize():
    # Arrange
    text = "Abcdefghij"
    max_size = 5
    
    # Act
    chunks = split_text_into_chunks(text, max_size=max_size)
    
    # Assert
    assert chunks == ["Abcde", "fghij"]

def Should_RespectByteLength_WhenHandlingUnicodeCharacters():
    # Arrange
    text = "こんにちは世界" # 21 bytes total
    max_size = 10 # "こんに" is 9 bytes
    
    # Act
    chunks = split_text_into_chunks(text, max_size=max_size)
    
    # Assert
    assert chunks[0] == "こんに"
    assert "".join(chunks) == text

def Should_ReturnListWithEmptyString_WhenTextIsEmpty():
    # Arrange
    text = ""
    
    # Act
    chunks = split_text_into_chunks(text)
    
    # Assert
    assert chunks == [""]
