from typing import Dict

from google.cloud import secretmanager
from google.protobuf.duration_pb2 import Duration

# Communicate with google secret manager
class Secrets(object):
    def __init__(self, project_id="") -> None:
        self.sm = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id

    def sanetize(self, input):
        return input.replace(".", "___")

    def get_name(self, secret_id, version="skip"):
        if version == "skip":
            return self.sm.secret_path(
                project=self.project_id, secret=self.sanetize(secret_id)
            )
        return self.sm.secret_version_path(
            project=self.project_id,
            secret=self.sanetize(secret_id),
            secret_version=version,
        )

    def fetch_secret(self, secret_id, version="latest"):
        try:
            response = self.sm.access_secret_version(
                request=secretmanager.AccessSecretVersionRequest(
                    name=self.get_name(secret_id, version=version),
                )
            )
            return response.payload.data.decode("UTF-8")
        except Exception as err:
            print(err)
            return None

    def set_secret(self, secret_id, secret, labels: Dict = None, ttl_seconds=None):
        if labels is None:
            labels = {}
        # check if secret exists
        current_secret = self.fetch_secret(secret_id)
        print(
            f"secret id: {secret_id}, sanetized: {self.sanetize(secret_id)}, project: {self.project_id}")
        print(f"current secret = {current_secret}")
        # create the secret if it doesn't exist
        if current_secret is None:
            try:
                print(f"creating secret")
                self.sm.create_secret(
                    request=secretmanager.CreateSecretRequest(
                        parent=f"projects/{self.project_id}",
                        secret_id=self.sanetize(secret_id),
                        secret={
                            "labels": {**labels, "cert": "generated"},
                            "replication": {"automatic": {}},
                            "ttl": Duration(seconds=ttl_seconds),
                        },
                    )
                )
                print(f"saved: {secret_id} as {(self.sanetize(secret_id))}")
            except TypeError as err:
                print(
                    f"did not manage to save secret {secret_id}. \n this can be because of boll in labels")
                raise TypeError(err)

        # store a new version of the secret
        try:
            self.sm.add_secret_version(
                request=secretmanager.AddSecretVersionRequest(
                    parent=self.get_name(secret_id),
                    payload={"data": secret},
                )
            )
        except Exception as err:
            print(err)
            raise err

        return self.sanetize(secret_id)
