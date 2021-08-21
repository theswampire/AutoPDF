import pickle
import re
import subprocess

import github3
import packaging.version
import requests
from github3 import GitHub
from github3.repos import Repository
from github3.repos.release import Release, Asset

import autopdf.config as config
from autopdf.logs import get_logger

log = get_logger(__name__)


def check_package_existence() -> bool:
    return config.package_file_path.exists()


def get_current_package_version() -> packaging.version.Version:
    process = subprocess.run(
        [str(config.package_file_path.absolute()), '/version'],
        stdout=subprocess.PIPE, universal_newlines=True
    )
    version = packaging.version.parse(process.stdout)
    log.info(f'Current OfficeToPDF Version: {version}')
    return version


def is_up_to_date(release: Release) -> bool:
    version_installed = get_current_package_version()
    version_latest = packaging.version.parse(release.tag_name)
    return version_installed >= version_latest


def get_latest_release() -> Release:
    repo: Repository
    release: Release
    asset: Asset

    try:
        gh = GitHub()
        repo = gh.repository(config.github_owner, config.github_repo)
        try:
            release = repo.latest_release()
            log.info(f"Version: {release.name}")
        except github3.exceptions.NotFoundError:
            release = next(repo.releases(1))
            log.info(f"There are not full releases available yet, using {release.name}")
        with open(config.pickled_release_path, "wb") as pf:
            pickle.dump(release, pf)
    except github3.exceptions.ForbiddenError:
        if not config.pickled_release_path.exists():
            log.info(
                f"Couldn't fetch latest {config.package_name}-Release: Please Check your Internet-Connection or try again later.")
            exit()
        log.info("Loading cached release")
        with open(config.pickled_release_path, "rb") as pf:
            release = pickle.load(pf)
    return release


def get_download_url(release: Release) -> str:
    asset: Asset
    for asset in release.assets():
        if re.search(config.package_name, asset.name):
            return asset.browser_download_url


def download_app(release: Release) -> bool:
    log.info(f"Downloading {config.package_name}")
    data = requests.get(get_download_url(release))
    with open(config.package_file_path, "wb") as file:
        file.write(data.content)

    success = check_package_existence()
    if success:
        log.info("Successfully installed OfficeToPDF")
    else:
        log.critical("Installation failed")
    return success


def install_app() -> bool:
    release = None

    if check_package_existence():
        if config.check_for_update:
            release = get_latest_release()
            if is_up_to_date(release):
                log.info("OfficeToPDF executable is up to date")
                return True
            log.info("OfficeToPDF executable is outdated")
    else:
        release = get_latest_release()

    return download_app(release)


if __name__ == '__main__':
    install_app()
