
Requirements
---------------
* Python 2.7 or 3.x
* Python 'requests' library (http://docs.python-requests.org/en/latest/)

Running the samples
---------------
* All samples can be run using the command prompt or terminal
* All samples require 2 arguments: server adress (without a trailing slash) and username
* Run by executing ```python sample_file_name.py <server_address> <username>```
* Specific information for each sample are included at the top of each file
* API version is set to 2.5 by default for Tableau server 10.2, but it can be changed in [version.py](./version.py)
* For Tableau Server 9.0, the REST API namespace must be changed (refer to comment in each sample where namespace, xmlns, is defined)

REST API Samples
---------------
These are created and maintained by Tableau.

Demo | Source Code | Description
-------- |  -------- |  --------
Publish Workbook | [publish_workbook.py](./publish_workbook.py) | Shows how to upload a Tableau workbook using both a single request as well as chunking the upload.
Move Workbook | [move_workbook_projects.py](./move_workbook_projects.py)<br />[move_workbook_sites.py](./move_workbook_sites.py)</br />[move_workbook_server.py](./move_workbook_server.py) | Shows how to move a workbook from one project/site/server to another. Moving across different sites and servers require downloading the workbook. 2 methods of downloading are demonstrated in the sites and servers samples.<br /><br />Moving to another project uses an API call to update workbook.<br />Moving to another site uses in-memory download method.<br />Moving to another server uses a temporary file to download workbook.
Add Permissions | [user_permission_audit.py](./user_permission_audit.py) | Shows how to add permissions for a given user to a given workbook.
Global Workbook Permissions | [update_permission.py](./update_permission.py) | Shows how to add or update user permissions for every workbook on a given site or project.


Move workbook from one server to another passign parameters
1. move_workbook_server.py {server_source, server_target, server_source_username, server_source_password, server_target_username, server_target_password, site_source_name, site_target_name, project_source_name, project_target_name, workbook_source_name}
    argv[1] = server_source
    argv[2] = server_target
    argv[3] = server_source_username
    argv[4] = server_source_password
    argv[5] = server_target_username
    argv[6] = server_target_password
    argv[7] = site_source_name
    argv[8] = site_target_name
    argv[9] = project_source_name
    argv[10] = project_target_name
    argv[11] = workbook_source_name

To authenticated in the default source/target site, put 0 as value
