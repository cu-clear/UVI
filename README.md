# UVI
Repo for the Unified Verbs Index Project

### Project Requirements

* Python 3.7.3 or above
* pip 19.0.3 or above
* MongoDB 4.2.0 or above

### Project Set-Up

* git clone git@github.com:cu-clear/UVI.git
* cd UVI
* git submodule init
* git submodule update --remote --merge
* (Optional) If virtual environment needs to be created:
    * cd uvi_web
    * python -m venv <virtual_env_name>
    * source <virtual_env_name>/bin/activate
* Get requirements.txt file from project collaborators for package installations.
* Get mailing config from project collaborators for successful run.
* python3 -m pip install -r requirements.txt

To run the code:
* If a virtual environment has been created:
    * cd uvi_web
    * source <virtual_env_name>/bin/activate
* sh run_local.sh

To update the projects:
* UVI: git pull
* VerbNet Repo: git submodule update --init --recursive

#### Note: No changes should be made in vn_repo folder in corpora. It is a sub module for UVI and the changes should be made in the respective github repo only [here](https://github.com/cu-clear/verbnet).