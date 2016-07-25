import requests
import xml.etree.ElementTree as ET
import sys
import math
import getpass

xmlns = {'t': 'http://tableau.com/api'}


def _encode_for_display(text):
    """
    Encodes strings so they can display as ASCII in a Windows terminal window.
    This function also encodes strings for processing by xml.etree.ElementTree functions.

    Returns an ASCII-encoded version of the text.
    Unicode characters are converted to ASCII placeholders (for example, "?").
    """
    return text.encode('ascii', errors="backslashreplace").decode('utf-8')


def _check_status(server_response, success_code):
    """
    Checks the server response for possible errors.

    'server_response'       the response received from the server
    'success_code'          the expected success code for the response
    """
    if server_response.status_code != success_code:
        print(_encode_for_display(server_response.text))
        sys.exit(1)
    return


def sign_in(site=""):
    """
    Signs in to the server specified in the global SERVER variable with
    credentials specified in the global USER and PASSWORD variables.

    'site'     is the ID (as a string) of the site on the server to sign in to. The
               default is "", which signs in to the default site.

    Returns the authentication token and site ID.
    """
    url = SERVER + "/api/2.3/auth/signin"

    # Builds the request
    xml_request = ET.Element('tsRequest')
    credentials_element = ET.SubElement(xml_request, 'credentials', name=USER, password=PASSWORD)
    ET.SubElement(credentials_element, 'site', contentUrl=site)
    xml_request = ET.tostring(xml_request)

    # Make the request to server
    server_response = requests.post(url, data=xml_request)
    _check_status(server_response, 200)

    # ASCII encode server response to enable displaying to console
    server_response = _encode_for_display(server_response.text)

    # Reads and parses the response
    parsed_response = ET.fromstring(server_response)

    # Gets the auth token and site ID
    token = parsed_response.find('t:credentials', namespaces=xmlns).attrib.get('token')
    site_id = parsed_response.find('.//t:site', namespaces=xmlns).attrib.get('id')
    return token, site_id


def sign_out():
    """
    Destroys the active session and invalidates authentication token.
    """
    url = SERVER + "/api/2.3/auth/signout"
    server_response = requests.post(url, headers={'x-tableau-auth': AUTH_TOKEN})
    _check_status(server_response, 204)
    return


def get_workbook_id():
    """
    Gets the id of the desired workbook to relocate.

    Returns the workbook id and the project id that contains the workbook.
    """
    url = SERVER + "/api/2.3/sites/{0}/workbooks".format(SITE_ID)
    server_response = requests.get(url, headers={'x-tableau-auth': AUTH_TOKEN})
    _check_status(server_response, 200)
    xml_response = ET.fromstring(_encode_for_display(server_response.text))

    workbooks = xml_response.findall('.//t:workbook', namespaces=xmlns)
    for workbook in workbooks:
        if workbook.get('name') == WORKBOOK:
            source_project_id = workbook.find('.//t:project', namespaces=xmlns).attrib.get('id')
            return source_project_id, workbook.get('id')
    print("\tWorkbook named '{0}' not found.".format(WORKBOOK))
    sys.exit(1)


def get_project_id():
    """
    Returns the project ID of the desired project
    """
    page_num, page_size = 1, 100   # Default paginating values

    # Builds the request
    url = SERVER + "/api/2.3/sites/{0}/projects".format(SITE_ID)
    paged_url = url + "?pageSize={0}&pageNumber={1}".format(page_size, page_num)
    server_response = requests.get(paged_url, headers={'x-tableau-auth': AUTH_TOKEN})
    _check_status(server_response, 200)
    xml_response = ET.fromstring(_encode_for_display(server_response.text))

    # Used to determine if more requests are required to find all projects on server
    total_projects = int(xml_response.find('t:pagination', namespaces=xmlns).attrib.get('totalAvailable'))
    max_page = int(math.ceil(total_projects / page_size))

    projects = xml_response.findall('.//t:project', namespaces=xmlns)

    # Continue querying if more projects exist on the server
    for page in range(2, max_page + 1):
        paged_url = url + "?pageSize={0}&pageNumber={1}".format(page_size, page)
        server_response = requests.get(paged_url, headers={'x-tableau-auth': AUTH_TOKEN})
        _check_status(server_response, 200)
        xml_response = ET.fromstring(_encode_for_display(server_response.text))
        projects.extend(xml_response.findall('.//t:project', namespaces=xmlns))

    # Look through all projects to find the 'default' one
    for project in projects:
        if project.get('name') == NEW_PROJECT:
            return project.get('id')
    print("\tProject named '{0}' was not found on server".format(NEW_PROJECT))
    sys.exit(1)


def move_workbook(project_id):
    """
    Moves the specified workbook to another project.
    """
    url = SERVER + "/api/2.3/sites/{0}/workbooks/{1}".format(SITE_ID, WORKBOOK_ID)
    # Build the request to move workbook
    xml_request = ET.Element('tsRequest')
    workbook_element = ET.SubElement(xml_request, 'workbook')
    ET.SubElement(workbook_element, 'project', id=project_id)
    xml_request = ET.tostring(xml_request)

    server_response = requests.put(url, data=xml_request, headers={'x-tableau-auth': AUTH_TOKEN})
    _check_status(server_response, 200)


if __name__ == "__main__":
    ##### STEP 0: INITIALIZATION #####
    if len(sys.argv) != 3:
        print("2 arguments needed (server, username)")
        sys.exit(1)
    SERVER = sys.argv[1]
    USER = sys.argv[2]
    WORKBOOK = raw_input("\nName of workbook to move: ")
    NEW_PROJECT = raw_input("\nDestination project: ")

    print("\n*Moving '{0}' workbook to '{1}' project as {2}*".format(WORKBOOK, NEW_PROJECT, USER))
    PASSWORD = getpass.getpass("Password: ")

    ##### STEP 1: Sign in #####
    print("\n1. Singing in as " + USER)
    AUTH_TOKEN, SITE_ID = sign_in()

    ##### STEP 2: Find new project id #####
    print("\n2. Finding project id of '{0}'".format(NEW_PROJECT))
    DEST_PROJECT_ID = get_project_id()

    ##### STEP 3: Find workbook id #####
    print("\n3. Finding workbook id of '{0}'".format(WORKBOOK))
    SOURCE_PROJECT_ID, WORKBOOK_ID = get_workbook_id()

    # Check if the workbook is already in the desired project
    if SOURCE_PROJECT_ID == DEST_PROJECT_ID:
        print("\tWorkbook already in destination project")
        sys.exit(1)

    ##### STEP 4: Move workbook #####
    print("\n4. Moving workbook to '{0}'".format(NEW_PROJECT))
    move_workbook(DEST_PROJECT_ID)

    ##### STEP 5: Sign out #####
    print("\n5. Signing out and invalidating the authentication token")
    sign_out()