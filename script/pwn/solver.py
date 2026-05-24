from __future__ import annotations

import math
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from attack import AttackModel
from game import CTF_GOAL, CTF_RADIUS, EPISODE_TIMEOUT, GameState
from policy import load_default_policy

MAX_WEIGHT = 10.0
PROJECT_DIR = Path(__file__).resolve().parent
ATTACK_SHAPES = {
    "W0": (16, 8),
    "b0": (16,),
    "W1": (8, 16),
    "b1": (8,),
}
ATTACK_PARAMETER_SIZE = 16 * 8 + 16 + 8 * 16 + 8


@dataclass(frozen=True)
class SearchConfig:
    seed: int = 7
    iterations: int = 600
    population: int = 96
    elite_count: int = 12
    noise_scale: float = 0.28
    dt: float = 0.02  # 远程环境步长 ~0.02；0.1 本地可过但远程 timeout
    max_time: float = EPISODE_TIMEOUT


def default_attack_arrays() -> dict[str, np.ndarray]:
    return {
        "W0": np.zeros((16, 8), dtype=np.float32),
        "b0": np.zeros((16,), dtype=np.float32),
        "W1": np.zeros((8, 16), dtype=np.float32),
        "b1": np.zeros((8,), dtype=np.float32),
    }


def flatten_attack_arrays(arrays: dict[str, np.ndarray]) -> np.ndarray:
    return np.concatenate(
        [
            arrays["W0"].astype(np.float32).ravel(),
            arrays["b0"].astype(np.float32).ravel(),
            arrays["W1"].astype(np.float32).ravel(),
            arrays["b1"].astype(np.float32).ravel(),
        ]
    )


def unflatten_attack_vector(vector: np.ndarray) -> dict[str, np.ndarray]:
    x = np.asarray(vector, dtype=np.float32)
    assert x.shape == (ATTACK_PARAMETER_SIZE,)
    i = 0
    w0 = x[i : i + 128].reshape(16, 8)
    i += 128
    b0 = x[i : i + 16]
    i += 16
    w1 = x[i : i + 128].reshape(8, 16)
    i += 128
    b1 = x[i : i + 8]
    return {"W0": w0.copy(), "b0": b0.copy(), "W1": w1.copy(), "b1": b1.copy()}


def clamp_attack_arrays(arrays: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {
        key: np.clip(value, -MAX_WEIGHT, MAX_WEIGHT).astype(np.float32)
        for key, value in arrays.items()
    }


def save_attack_npz(path: str | Path, arrays: dict[str, np.ndarray]) -> None:
    safe_arrays = clamp_attack_arrays(arrays)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    np.savez(target, **safe_arrays)


def parse_args(argv: list[str] | None = None) -> tuple[SearchConfig, Path]:
    parser = ArgumentParser(description="Search for a rush-hour attack candidate.")
    parser.add_argument("--iterations", type=int, default=SearchConfig.iterations)
    parser.add_argument("--dt", type=float, default=SearchConfig.dt,
                        help="Simulation timestep (default: %(default)s). "
                             "Remote env uses ~0.02; 0.1 passes locally but times out remotely.")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_DIR / "artifacts" / "best_attack.npz",
    )
    args = parser.parse_args(argv)
    return SearchConfig(
        iterations=args.iterations,
        dt=args.dt,
    ), args.output


def score_result(result: dict[str, Any]) -> float:
    if result["goal_reached"]:
        return 1_000_000.0 - float(result["steps"])
    return -1000.0 * float(result["min_distance"]) - float(result["final_distance"])


def evaluate_attack(
    arrays: dict[str, np.ndarray], dt: float = 0.02, max_time: float = EPISODE_TIMEOUT
) -> dict[str, Any]:
    state = GameState(load_default_policy())
    state.install_attack(AttackModel(arrays))

    initial_dx = state.car.x - CTF_GOAL[0]
    initial_dz = state.car.z - CTF_GOAL[1]
    min_distance = math.hypot(initial_dx, initial_dz)
    steps = 0
    truncated = False
    enforce_horizon = max_time < EPISODE_TIMEOUT
    while (
        not state.goal_reached
        and not state.timed_out
        and (not enforce_horizon or state.time + dt <= max_time)
    ):
        state.step(dt)
        dx = state.car.x - CTF_GOAL[0]
        dz = state.car.z - CTF_GOAL[1]
        min_distance = min(min_distance, math.hypot(dx, dz))
        steps += 1

    if (
        enforce_horizon
        and not state.goal_reached
        and not state.timed_out
        and state.time + dt > max_time
    ):
        truncated = True

    final_dx = state.car.x - CTF_GOAL[0]
    final_dz = state.car.z - CTF_GOAL[1]
    final_distance = math.hypot(final_dx, final_dz)

    return {
        "goal_reached": state.goal_reached,
        "timed_out": state.timed_out,
        "truncated": truncated,
        "steps": steps,
        "final_distance": final_distance,
        "min_distance": min_distance,
        "final_position": (state.car.x, state.car.z),
        "inside_goal_radius": final_distance < CTF_RADIUS,
    }


def run_search(config: SearchConfig) -> dict[str, Any]:
    rng = np.random.default_rng(config.seed)
    center = np.zeros(ATTACK_PARAMETER_SIZE, dtype=np.float32)
    best_vector = center.copy()
    best_result = evaluate_attack(
        unflatten_attack_vector(best_vector), dt=config.dt, max_time=config.max_time
    )
    best_score = score_result(best_result)

    for _ in range(config.iterations):
        population: list[tuple[float, np.ndarray, dict[str, Any]]] = []
        for _ in range(config.population):
            candidate = center + rng.normal(0.0, config.noise_scale, size=center.shape).astype(
                np.float32
            )
            arrays = clamp_attack_arrays(unflatten_attack_vector(candidate))
            vector = flatten_attack_arrays(arrays)
            result = evaluate_attack(arrays, dt=config.dt, max_time=config.max_time)
            score = score_result(result)
            population.append((score, vector, result))
            if score > best_score:
                best_score = score
                best_vector = vector.copy()
                best_result = result

        population.sort(key=lambda item: item[0], reverse=True)
        elite_vectors = [item[1] for item in population[: config.elite_count]]
        center = np.mean(np.stack(elite_vectors, axis=0), axis=0).astype(np.float32)

    best_arrays = clamp_attack_arrays(unflatten_attack_vector(best_vector))
    return {
        "best_score": float(best_score),
        "best_vector": best_vector,
        "best_arrays": best_arrays,
        "best_result": best_result,
    }


def main(argv: list[str] | None = None) -> int:
    config, output_path = parse_args(argv)
    result = run_search(config)
    save_attack_npz(output_path, result["best_arrays"])
    print(
        {
            "best_score": result["best_score"],
            "goal_reached": result["best_result"]["goal_reached"],
            "final_position": result["best_result"]["final_position"],
            "output_path": str(output_path),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
