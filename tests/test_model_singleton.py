import joblib
import pytest
from sklearn.dummy import DummyRegressor

from src.model_singleton import ModelSingleton


def test_loads_valid_model_once(tmp_path):
    path = tmp_path / "model.pkl"
    joblib.dump(DummyRegressor().fit([[1], [2]], [10, 20]), path)

    manager = ModelSingleton(path)

    assert manager.is_loaded()
    assert manager.get_model().predict([[3]]).shape == (1,)


def test_missing_model_is_unavailable(tmp_path):
    manager = ModelSingleton(tmp_path / "missing.pkl")

    assert not manager.is_loaded()
    with pytest.raises(RuntimeError):
        manager.get_model()


def test_replacement_rejects_invalid_artifact(tmp_path):
    original = tmp_path / "original.pkl"
    invalid = tmp_path / "invalid.pkl"

    joblib.dump(DummyRegressor().fit([[1], [2]], [10, 20]), original)
    invalid.write_text("not a model")

    manager = ModelSingleton(original)
    previous = manager.get_model()

    with pytest.raises(Exception):
        manager.replace_from_path(invalid)

    assert manager.get_model() is previous


def test_replacement_accepts_valid_model(tmp_path):
    first = tmp_path / "first.pkl"
    second = tmp_path / "second.pkl"

    joblib.dump(DummyRegressor().fit([[1], [2]], [10, 20]), first)
    joblib.dump(DummyRegressor().fit([[1], [2]], [30, 40]), second)

    manager = ModelSingleton(first)
    manager.replace_from_path(second)

    assert manager.get_model().predict([[3]])[0] == pytest.approx(35)
