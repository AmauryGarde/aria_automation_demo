# Imports
import json
from urllib.request import urlopen
import urllib.request
import urllib.error
import ssl
import base64
import os
import argparse


class DsmClient:
    """
    A client class for interacting with the DSM (Data Services Manager) API.

    Args:
        server (str): The DSM server URL.
        username (str): The username for authentication.
        password (str): The password for authentication.
    """

    GROUP_INFRA = "infrastructure.dataservices.vmware.com"
    GROUP_INFRAVER = "v1alpha1"
    GROUP_DB = "databases.dataservices.vmware.com"
    GROUP_DBVER = "v1alpha1"

    def __init__(self, server, username, password) -> None:
        self.httpCtx = ssl._create_unverified_context()
        self.server = server
        self.username = username
        self.password = password
        self.login()

    def headers(self):
        """
        Returns the headers for API requests.

        Returns:
            dict: The headers dictionary.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json, text/plain, */*",
        }

    def login(self):
        """
        Logs in to the DSM server and retrieves the authentication token.
        Raises an exception if the login doesn't return a Bearer token.
        """
        loginInfo = json.dumps(
            {
                "email": self.username,
                "password": self.password,
            }
        ).encode("utf-8")
        url = f"https://{self.server}/provider/session"
        headers = {
            "Content-Type": "application/json",
        }
        request = urllib.request.Request(url, headers=headers, data=loginInfo)
        with urlopen(request, context=self.httpCtx) as response:
            auth = response.headers.get("Authorization")
            prefix = "Bearer "
            if not auth.startswith(prefix):
                raise Exception("Login didn't return a Bearer token")
            self.token = auth[len(prefix):]

    def get(self, path):
        """
        Sends a GET request to the DSM server.

        Args:
            path (str): The API endpoint path.

        Returns:
            dict: The JSON response from the server.
        """
        url = f"https://{self.server}{path}"
        request = urllib.request.Request(url, headers=self.headers())
        with urlopen(request, context=self.httpCtx) as response:
            return json.load(response)

    def getDBConnectionString(self, inputs):
        """
        Retrieves the database connection string based on the inputs.

        Args:
            inputs (dict): The input parameters for the connection string.

        Returns:
            str: The database connection string.
        """
        dbengine = (inputs["dbengine"]).lower()
        admin_username = inputs["adminUsername"]
        conn_host, conn_port = self.getDBConnectionInfo(inputs)
        deployment_name = inputs["deploymentName"]

        path = f"/api/v1/namespaces/default/secrets/{deployment_name}"
        out = self.get(path)

        if dbengine == "postgres":
            db_name = deployment_name
        else:
            db_name = "mysqlappuser_data"

        password = out["data"]["password"]
        decoded_password = base64.b64decode(password)
        db_password = decoded_password.decode("utf-8")

        connection_string = dbengine + "://" + admin_username + ":" + db_password + "@" + conn_host + ":" + conn_port + "/" + db_name
        return connection_string

    def getDBConnectionInfo(self, inputs):
        """
        Retrieves the database connection string based on the inputs.

        Args:
            inputs (dict): The input parameters for the connection info.

        Returns:
            str: The database connection info.
        """
        dbengine = (inputs["dbengine"]).lower()
        deployment_name = inputs["deploymentName"]

        if dbengine == "postgres":
            deployment_engine = "postgresclusters"
        else:
            deployment_engine = "mysqlclusters"

        path = f"/apis/databases.dataservices.vmware.com/v1alpha1/namespaces/default/{deployment_engine}/{deployment_name}"
        out = self.get(path)

        return out["status"]["connection"]["host"], out["status"]["connection"]["port"]


def checkDsmParams(envlist):
    """
    Validate the length of envlist and also the length of
    individual items in the env list
    Args:
        envlist:
    Returns: True or False(if envList is not proper)
    Valid env list is [DsmIP,DsmUserID,DsmPassword]
    """
    if len(envlist) == 3:
        if all(len(element) > 0 for element in envlist):
            return True
        else:
            return False
    else:
        return False


def getDsmConnectionConfig(input):
    """
    Returns a dictionary containing the DSM connection configuration.

    Args:
        input (list): A list containing the DSM host, user ID, and password.

    Returns:
        dict: A dictionary containing the DSM connection configuration with keys 'dsmHost', 'dsmUserID', and 'dsmPassword'.
    """
    connectionConfig = {
        "dsmHost": input[0],
        "dsmUserID": input[1],
        "dsmPassword": input[2],
    }
    return connectionConfig


def getDsmParamsForVro(site):
    """
    Retrieves the DSM connection parameters for a given site.

    Args:
        site (str): The site for which to retrieve the DSM parameters.

    Returns:
        dict: A dictionary containing the DSM connection configuration.

    Raises:
        ValueError: If the DSM connection parameters are invalid.
    """
    dsmUserID = os.environ[f"{site}_dsm_user_id"]
    dsmPassword = os.environ[f"{site}_dsm_password"]
    dsmHost = os.environ[f"{site}_dsm_hostname"]
    envList = [dsmHost, dsmUserID, dsmPassword]
    if not checkDsmParams(envList):
        raise ValueError(
            "Dsm Connection parameters are invalid, Check action's environment"
        )

    return getDsmConnectionConfig(envList)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get DSM Database Connection String")
    parser.add_argument('--dsmHost', required=True, help="DSM Host URL")
    parser.add_argument('--username', required=True, help="Username for DSM")
    parser.add_argument('--password', required=True, help="Password for DSM")
    parser.add_argument('--dbEngine', required=True, help="Database Engine")
    parser.add_argument('--adminUsername', required=True, help="Admin Username")
    parser.add_argument('--deploymentName', required=True, help="Deployment Name")

    args = parser.parse_args()
    # checks if the targetSite is chosen
    try:
        outputs = []
        # create a DSM client instance
        dsmClient = DsmClient(
            args.dsmHost,
            args.username,
            args.password
        )

        inputs = {
            "dbengine": args.dbEngine,
            "adminUsername": args.adminUsername,
            "deploymentName": args.deploymentName
        }

        connectionString = dsmClient.getDBConnectionString(inputs)
        print(connectionString)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import argparse

    try:
        dsmParams = getDsmParamsForVro(site)
        dsmClient = DsmClient(dsmParams['dsmHost'], dsmParams['dsmUserID'], dsmParams['dsmPassword'])
        # Replace 'inputs' with actual inputs required for getDBConnectionString
        inputs = {
            'dbengine': 'mysql',  # Or 'postgres', depending on your requirements
            'adminUsername': 'admin',
            'conn_host': 'localhost',
            'conn_port': 3306,
            'deploymentName': 'your_deployment_name'
        }
        connectionString = dsmClient.getDBConnectionString(inputs)
        print(connectionString)
    except Exception as e:
        print(f"An error occurred: {e}")
