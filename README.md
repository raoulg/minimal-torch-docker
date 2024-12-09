# PyTorch CPU Docker Images

Pre-built Docker images with PyTorch CPU-only installations, optimized for size and build speed using `uv`.

## Available Tags

Images are available for:
- Python versions: 3.11, 3.12
- PyTorch versions: Latest patches for 2.3.x, 2.4.x, 2.5.x
- Two variants: with and without permanent uv installation (-uv suffix)

Format: `raoulgrouls/torch-python-slim:py<python_version>-torch<torch_version>[-uv]`

Example tags:
```
raoulgrouls/torch-python-slim:py3.11-torch2.3.1
raoulgrouls/torch-python-slim:py3.11-torch2.3.1-uv
raoulgrouls/torch-python-slim:py3.12-torch2.5.1
```

## Features

- Based on official Python slim images
- CPU-only PyTorch builds for minimal size
- Fast installation using `uv`
- Two variants per version:
  - Standard: Uses `uv` only during build
  - UV (-uv suffix): Includes `uv` in final image

## Usage
Add to your Dockerfile:
```dockerfile
# Standard variant
FROM raoulgrouls/torch-python-slim:py3.11-torch2.5.1
```
or
```dockerfile
# With UV installed
FROM raoulgrouls/torch-python-slim:py3.11-torch2.5.1-uv
```

## Building

To build all variants yourself:

```bash
python docker_builder.py
```

Add `--dry-run` to preview builds without executing them.

Configure versions in `build_config.toml`:
```toml
dockername = "your-docker-hub-name"
image_name = "torch-python-slim"

python_versions = [
    "3.11",
    "3.12"
]

pytorch_versions = [
    "2.3.x",
    "2.4.x",
    "2.5.x"
]
```
