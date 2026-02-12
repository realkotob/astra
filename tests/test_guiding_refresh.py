from types import SimpleNamespace
from unittest.mock import MagicMock

from astra.guiding import GuiderManager
from astra.observatory import Observatory


def _guider_params(min_guide_interval: float = 30.0) -> dict:
    return {
        "PIX2TIME": {"+x": 100.0, "-x": 100.0, "+y": 100.0, "-y": 100.0},
        "DIRECTIONS": {
            "+x": "East",
            "-x": "West",
            "+y": "North",
            "-y": "South",
        },
        "RA_AXIS": "x",
        "PID_COEFFS": {
            "x": {"p": 0.8, "i": 0.1, "d": 0.1},
            "y": {"p": 0.8, "i": 0.1, "d": 0.1},
            "set_x": 0.0,
            "set_y": 0.0,
        },
        "MIN_GUIDE_INTERVAL": min_guide_interval,
    }


def _fake_observatory(min_guide_interval: float = 30.0):
    telescope = SimpleNamespace(device_name="T1")
    logger = MagicMock()
    db = MagicMock()
    return SimpleNamespace(
        devices={"Telescope": {"T1": telescope}},
        config={
            "Telescope": [
                {
                    "device_name": "T1",
                    "guider": _guider_params(
                        min_guide_interval=min_guide_interval,
                    ),
                }
            ]
        },
        logger=logger,
        database_manager=db,
    )


def test_refresh_telescope_from_config_updates_guider_instance():
    observatory = _fake_observatory(min_guide_interval=30.0)
    manager = GuiderManager.from_observatory(observatory)

    old_guider = manager.guider["T1"]
    observatory.config["Telescope"][0]["guider"] = _guider_params(
        min_guide_interval=12.5
    )

    refreshed = manager.refresh_telescope_from_config(observatory, "T1")

    assert refreshed is True
    assert "T1" in manager.guider
    assert manager.guider["T1"] is not old_guider
    assert manager.guider["T1"].MIN_GUIDE_INTERVAL == 12.5


def test_guiding_calibration_sequence_refreshes_guider(monkeypatch):
    call_order = []

    class DummyCalibrator:
        def __init__(self, astra_observatory, action, paired_devices, image_handler):
            self._obs = astra_observatory

        def slew_telescope_one_hour_east_of_sidereal_meridian(self):
            call_order.append("slew")

        def perform_calibration_cycles(self):
            call_order.append("perform")

        def complete_calibration_config(self):
            call_order.append("complete")

        def save_calibration_config(self):
            call_order.append("save")

        def update_observatory_config(self):
            call_order.append("update")

    import astra.observatory as observatory_module

    monkeypatch.setattr(observatory_module, "GuidingCalibrator", DummyCalibrator)

    fake_obs = SimpleNamespace()
    fake_obs.logger = MagicMock()
    fake_obs.pre_sequence = MagicMock()
    fake_obs.open_observatory = MagicMock()
    fake_obs.check_conditions = MagicMock(return_value=True)
    fake_obs.get_image_handler = MagicMock(return_value=MagicMock())
    fake_obs.guider_manager = SimpleNamespace(
        refresh_telescope_from_config=MagicMock(return_value=True)
    )

    action = SimpleNamespace(device_name="Cam1")
    paired_devices = {"Telescope": "T1"}

    success = Observatory.guiding_calibration_sequence(fake_obs, action, paired_devices)

    assert success is True
    assert call_order == ["slew", "perform", "complete", "save", "update"]
    fake_obs.guider_manager.refresh_telescope_from_config.assert_called_once_with(
        observatory=fake_obs,
        telescope_name="T1",
    )


def test_guiding_calibration_sequence_does_not_refresh_on_failure(monkeypatch):
    class FailingCalibrator:
        def __init__(self, astra_observatory, action, paired_devices, image_handler):
            pass

        def slew_telescope_one_hour_east_of_sidereal_meridian(self):
            pass

        def perform_calibration_cycles(self):
            raise RuntimeError("calibration failed")

        def complete_calibration_config(self):
            pass

        def save_calibration_config(self):
            pass

        def update_observatory_config(self):
            pass

    import astra.observatory as observatory_module

    monkeypatch.setattr(observatory_module, "GuidingCalibrator", FailingCalibrator)

    fake_obs = SimpleNamespace()
    fake_obs.logger = MagicMock()
    fake_obs.pre_sequence = MagicMock()
    fake_obs.open_observatory = MagicMock()
    fake_obs.check_conditions = MagicMock(return_value=True)
    fake_obs.get_image_handler = MagicMock(return_value=MagicMock())
    fake_obs.guider_manager = SimpleNamespace(
        refresh_telescope_from_config=MagicMock(return_value=True)
    )

    action = SimpleNamespace(device_name="Cam1")
    paired_devices = {"Telescope": "T1"}

    success = Observatory.guiding_calibration_sequence(fake_obs, action, paired_devices)

    assert success is False
    fake_obs.guider_manager.refresh_telescope_from_config.assert_not_called()
