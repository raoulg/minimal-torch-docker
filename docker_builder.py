import argparse
import concurrent.futures
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass
from string import Template
from typing import Dict

import requests
from loguru import logger

logger.add("docker_build.log", rotation="100 MB")


def load_config(config_file: str = "build_config.toml") -> dict:
    with open(config_file, "rb") as f:
        return tomllib.load(f)


def get_latest_versions() -> Dict[str, str]:
    response = requests.get("https://pypi.org/pypi/torch/json")
    response.raise_for_status()
    releases = response.json()["releases"]

    version_map = {}
    for version in releases.keys():
        if not any(f in version for f in ["a", "b", "rc"]):  # Skip alpha/beta/rc
            major_minor = ".".join(version.split(".")[:2])
            if major_minor not in version_map:
                version_map[major_minor] = version
            elif version > version_map[major_minor]:
                version_map[major_minor] = version

    return version_map


@dataclass
class BuildConfig:
    python_version: str
    pytorch_version: str
    use_uv: bool

    @property
    def tag(self) -> str:
        uv_suffix = "-uv" if self.use_uv else ""
        return f"py{self.python_version}-torch{self.pytorch_version}{uv_suffix}"


def generate_dockerfile(config: BuildConfig) -> str:
    base_template = Template("FROM python:${python_version}-slim\n" "WORKDIR /app\n")

    if config.use_uv:
        install_template = Template(
            "COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/\n"
            "RUN uv pip install --system torch==${pytorch_version} numpy "
            "--index-url https://download.pytorch.org/whl/cpu\n"
        )
    else:
        install_template = Template(
            "RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \\\n"
            "    uv pip install --system torch==${pytorch_version} numpy "
            "--index-url https://download.pytorch.org/whl/cpu\n"
        )

    return base_template.substitute(
        python_version=config.python_version
    ) + install_template.substitute(pytorch_version=config.pytorch_version)


def build_and_push(
    config: BuildConfig, dockername: str, image_name: str, dry_run: bool = False
):
    tag = config.tag
    full_tag = f"{dockername}/{image_name}:{tag}"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".dockerfile") as df:
        dockerfile_content = generate_dockerfile(config)
        df.write(dockerfile_content)
        df.flush()

        if dry_run:
            logger.info(f"[DRY RUN] Would build {full_tag} with Dockerfile:")
            logger.info(f"\n{dockerfile_content}")
            return

        try:
            logger.info(f"Building {full_tag}")
            subprocess.run(
                ["docker", "build", "-t", full_tag, "-f", df.name, "."], check=True
            )

            logger.info(f"Pushing {full_tag}")
            subprocess.run(["docker", "push", full_tag], check=True)

            logger.success(f"Successfully built and pushed {full_tag}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build/push {full_tag}: {str(e)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without actually doing it",
    )
    args = parser.parse_args()

    config = load_config()
    dockername = config["dockername"]
    image_name = config["image_name"]

    # Get latest versions for each major.minor
    latest_versions = get_latest_versions()
    logger.info(f"Found latest PyTorch versions: {latest_versions}")

    build_configs = []
    for py_version in config["python_versions"]:
        for torch_base_version in config["pytorch_versions"]:
            if not torch_base_version.endswith(".x"):
                continue
            major_minor = torch_base_version[:-2]  # Remove '.x'
            if major_minor in latest_versions:
                latest_version = latest_versions[major_minor]
                for use_uv in [True, False]:
                    build_configs.append(
                        BuildConfig(py_version, latest_version, use_uv)
                    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(build_and_push, cfg, dockername, image_name, args.dry_run)
            for cfg in build_configs
        ]
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()
