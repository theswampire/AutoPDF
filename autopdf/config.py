from pathlib import Path

root = Path(__file__).parent.parent
check_for_update = True

package_name = 'OfficeToPDF.exe'
github_owner = 'cognidox'
github_repo = 'OfficeToPDF'
package_path = root.joinpath('package/')
package_file_path = package_path.joinpath(package_name)
pickled_release_path = package_path.joinpath('release.pickle')
config_path = root.joinpath('config.json')

package_path.mkdir(exist_ok=True, parents=True)
log_path = root.joinpath('autopdf.log')

queue_polling_interval = 1
short_waiting_interval = queue_polling_interval / 5
