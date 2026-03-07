# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A fork of [sandialabs/spack-manager](https://github.com/sandialabs/spack-manager) that provides the Spack environment and package definitions for the Exawind wind energy simulation stack. It is consumed by `exawind-build` (the sibling repo at `../exawind-build/`) — `build.sh` clones this repo into the build directory as `exawind-manager`.

The key distinction from upstream: the environment variable is `EXAWIND_MANAGER` (not `SPACK_MANAGER`).

## Initialization

```bash
# Source this to activate Spack with all Exawind extensions
source start.sh

# Detects the current machine automatically
python find-exawind-manager.py
```

`start.sh` bootstraps Spack, registers the custom package repo (`repos/spack_repo/exawind/`), installs the spack-manager plugin, and loads quick-command shortcuts.

## Repository Structure

- **`configs/<machine>/`**: Per-cluster Spack config. Each directory can contain `packages.yaml`, `compilers.yaml`, `config.yaml`, `template.yaml`, `env.sh`. Cluster configs inherit from `configs/base/`.
- **`repos/spack_repo/exawind/packages/`**: Custom Spack package definitions (22 packages). Core packages: `exawind`, `amr_wind`, `nalu_wind`, `trilinos`, `tioga`, `openturbine`.
- **`scripts/deploy.py`**: Main build orchestrator — creates Spack environments, concretizes, builds, generates modules, optionally submits to SLURM.
- **`scripts/run-nightly-tests.sh`**: Nightly CI on Ellis cluster — updates repos, cleans cache, prunes old environments, runs tests, submits to CDash.
- **`spack/`**: Git submodule — Spack itself.
- **`spack-manager/`**: Git submodule — sandialabs/spack-manager plugin.
- **`golds.yaml`** + **`gold_getter.py`**: Maps build specs to reference output directories for regression testing per machine.
- **`find-exawind-manager.py`**: Machine auto-detection (17+ HPC systems) using hostname patterns, environment variables, and platform checks.

## Supported Clusters

Detected automatically by `find-exawind-manager.py`:

| Machine | Detection Method |
|---------|-----------------|
| pine | hostname contains "pine" |
| pecan | hostname contains "pecan" |
| pangea4 | hostname matches p4intlog01–04 |
| kestrel-cpu / kestrel-gpu | `NREL_CLUSTER` env var |
| frontier | `LMOD_SYSTEM_NAME` |
| summit | `LMOD_SYSTEM_NAME` |
| aurora / sunspot | `LMOD_SYSTEM_NAME` |
| cee | `SNLSITE` / `SNLSYSTEM` |
| darwin | `sys.platform == "darwin"` |

## Adding or Modifying a Cluster Config

1. Create `configs/<machine>/` with at minimum `packages.yaml` and `compilers.yaml`.
2. Add machine detection logic to `find-exawind-manager.py` (`detector()` and `get_current_machine()`).
3. If the cluster needs a non-default spec list, add `template.yaml` (otherwise `configs/base/template.yaml` is used).

## Custom Package Development

Packages live in `repos/spack_repo/exawind/packages/<name>/package.py`. Key base classes:

- **`CtestPackage`** (`ctest_package/package.py`): Base class for all simulation packages. Provides CTest/CDash integration, gold-file regression testing, ASAN support, GPU MPI configuration (Frontier ROCm, Kestrel CUDA), and compilation database export.
- All simulation packages (`amr_wind`, `nalu_wind`, `exawind`, etc.) inherit from `CtestPackage`.

## Deployment Script

```bash
# Basic usage (environment named by today's date)
python scripts/deploy.py

# Common options
python scripts/deploy.py --name my-env
python scripts/deploy.py --pre-fetch          # Download sources first
python scripts/deploy.py --depfile            # Generate Makefile for parallel builds
python scripts/deploy.py --slurm-args "..."  # Submit via SLURM
python scripts/deploy.py --ranks 36
python scripts/deploy.py --cdash "amr-wind nalu-wind"
python scripts/deploy.py --overwrite          # Remove existing env first
```

Environments are installed under `$EXAWIND_MANAGER/opt/<env_name>/`.

## Regression Testing

Gold reference files (expected outputs) are mapped in `golds.yaml` per machine and spec pattern. `gold_getter.py` finds the correct gold directory given a Spack spec and machine name. Tests run via CTest and results submit to CDash.
