#!/usr/bin/python

from __future__ import absolute_import, division, print_function
from .Secrets import Secrets
from ansible.module_utils._text import to_text
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleUndefinedVariable, AnsibleLookupError

__metaclass__ = type

# This documentation is not just documentation, it is also defining the interface of the lookup function. So any changes to get_option() needs to be reflected in the documentation or ansible will fail.
DOCUMENTATION = r"""
---
name: gcp_secrets
version_added: 1.2.3
short_description: Looking up gcp secrets 
description: Looking up gcp secrets 

options:
    project:
        description: The name of the gcp project.
        required: true
        type: str
    version:
        description: Version of the secret.
        required: false
        type: int
"""

EXAMPLES = r"""
# Retrieve a secret
- name: Basic usage
  ansible.builtin.debug:
    msg: "{ lookup('pexip.custom.gcp_secrets', <name of secret>, project=lookup('env', 'TF_VAR_project')) }}"
- name: Versioned usage
  ansible.builtin.debug:
    msg: "{ lookup('pexip.custom.gcp_secrets', <name of secret>, project=lookup('env', 'TF_VAR_project')), version=2 }}"
"""


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        project = self.get_option("project")
        version = self.get_option("version")
        if version is None:
            version = "latest"
        self._display.display(f"fetching: {terms}")
        ret = []
        for term in terms:
            try:
                # setup secret manager
                secrets = Secrets(project_id=project)
                res = secrets.fetch_secret(term, version=version)
                if res is None:
                    ret.append(None)
                    # raise AnsibleLookupError(
                    #     f"No sercret {term=} found, got: {res=}"
                    # )
                else:
                    ret.append(to_text(res))
            except Exception as err:
                raise AnsibleLookupError(
                    "failed to get secret: %s" % err
                )
        return ret
