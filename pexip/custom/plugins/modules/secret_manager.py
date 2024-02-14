#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: secret_manager

short_description: Retrieve a secret from gcp secret manager

version_added: "1.0.1"

description: Retrieve a secret from gcp secret manager

options:
    project:
        description: The name of the gcp project.
        required: true
        type: str
    secret:
        description: The key of the secret
        type: str
    version:
        description: The version of the secret
        type: str
    content:
        description: If no secret id is set but content is, we return content
        type: str

extends_documentation_fragment:
    - pexip.custom.my_doc_fragment_name

author:
    - Even Galland Alander (@deificx)
"""

EXAMPLES = r"""
# Retrieve a secret
- name: Test with a key
  pexip.custom.secret_manager:
    project: project-12345
    secret: super_secret_black_hole
    version: 1
"""

RETURN = r"""
path:
    description: The secret location
    type: str
    returned: always
    sample: 'key'
secret:
    description: The secret value
    type: str
    returned: always
    sample: 'val'
"""

from ansible.module_utils.basic import AnsibleModule
from google.cloud import secretmanager


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        content=dict(type="str", default="", required=False),
        project=dict(type="str", required=True),
        secret=dict(type="str", default="", required=False),
        version=dict(type="str", required=False),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, path="", secret="")

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    if module.params["content"] and not module.params["secret"]:
        result["secret"] = module.params["content"]
        result["changed"] = True
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    version = module.params["version"] if module.params["version"] else "latest"
    result[
        "path"
    ] = f"projects/{module.params['project']}/secrets/{module.params['secret']}/versions/{version}"
    result["secret"] = ""

    # Access the secret.
    try:
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": result["path"]})
        result["secret"] = response.payload.data.decode("UTF-8")
        result["changed"] = True
    except Exception as err:
        module.fail_json(msg=f"failed to fetch secret: {err}", **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
