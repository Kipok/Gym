# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import subprocess
from unittest.mock import patch

import pytest

from resources_servers.scicode.setup_grading_env import ensure_grading_env


def test_failed_install_is_not_marked_ready(tmp_path):
    target = tmp_path / "grader"
    with patch("resources_servers.scicode.setup_grading_env.shutil.which", return_value="uv"):
        with patch(
            "resources_servers.scicode.setup_grading_env.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "uv"),
        ):
            with pytest.raises(subprocess.CalledProcessError):
                ensure_grading_env(target)
    assert not (target / ".requirements-sha256").exists()


def test_completed_environment_can_start_offline(tmp_path):
    target = tmp_path / "grader"
    (target / "bin").mkdir(parents=True)
    (target / "bin" / "python").touch()
    with patch("resources_servers.scicode.setup_grading_env.shutil.which", return_value="uv"):
        with patch("resources_servers.scicode.setup_grading_env.subprocess.run"):
            ensure_grading_env(target)
    with patch("resources_servers.scicode.setup_grading_env.shutil.which", return_value=None):
        with patch("resources_servers.scicode.setup_grading_env.subprocess.run") as run:
            assert ensure_grading_env(target) == target / "bin" / "python"
            run.assert_not_called()
