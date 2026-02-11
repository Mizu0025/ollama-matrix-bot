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

def test_data_manager_init_empty(temp_data_file):
    dm = DataManager()
    assert dm.room_contexts == {}
    assert dm.current_model == "gemma3:12b" # Default from config

def test_data_manager_get_room_context(temp_data_file):
    dm = DataManager()
    ctx = dm.get_room_context("room1")
    assert ctx["messages"] == []
    assert "room1" in dm.room_contexts

def test_data_manager_set_model(temp_data_file):
    dm = DataManager()
    dm.set_model("new-model")
    assert dm.current_model == "new-model"
    
    # Check if saved
    with open(temp_data_file, "r") as f:
        data = json.load(f)
        assert data["current_model"] == "new-model"

def test_data_manager_clear_history(temp_data_file):
    dm = DataManager()
    ctx = dm.get_room_context("room1")
    ctx["messages"].append({"role": "user", "content": "hi"})
    dm.save_data()
    
    dm.clear_history("room1")
    assert dm.room_contexts["room1"]["messages"] == []
    
    with open(temp_data_file, "r") as f:
        data = json.load(f)
        assert data["contexts"]["room1"]["messages"] == []
