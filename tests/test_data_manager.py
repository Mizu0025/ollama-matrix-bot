import os
import json
import pytest
from data_manager import DataManager

@pytest.fixture
def temp_data_file(tmp_path, monkeypatch):
    d = tmp_path / "data"
    d.mkdir()
    f = d / "test_data.json"
    monkeypatch.setattr("data_manager.DATA_FILE", str(f))
    return f

def Should_InitializeWithDefaults_WhenNoDataFileExists(temp_data_file):
    # Arrange & Act
    dm = DataManager()
    
    # Assert
    assert dm.room_contexts == {}
    assert dm.current_model == "gemma3:12b"

def Should_CreateAndReturnNewContext_WhenRoomIdIsRequestedForFirstTime(temp_data_file):
    # Arrange
    dm = DataManager()
    room_id = "room1"
    
    # Act
    ctx = dm.get_room_context(room_id)
    
    # Assert
    assert ctx["messages"] == []
    assert room_id in dm.room_contexts

def Should_UpdateCurrentModelAndSaveToFile_WhenSetModelIsCalled(temp_data_file):
    # Arrange
    dm = DataManager()
    new_model = "new-model"
    
    # Act
    dm.set_model(new_model)
    
    # Assert
    assert dm.current_model == new_model
    with open(temp_data_file, "r") as f:
        data = json.load(f)
        assert data["current_model"] == new_model

def Should_WipeRoomMessages_WhenClearHistoryIsCalled(temp_data_file):
    # Arrange
    dm = DataManager()
    room_id = "room1"
    ctx = dm.get_room_context(room_id)
    ctx["messages"].append({"role": "user", "content": "hi"})
    dm.save_data()
    
    # Act
    dm.clear_history(room_id)
    
    # Assert
    assert dm.room_contexts[room_id]["messages"] == []
    with open(temp_data_file, "r") as f:
        data = json.load(f)
        assert data["contexts"][room_id]["messages"] == []
