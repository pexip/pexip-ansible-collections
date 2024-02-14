#!/usr/bin/python
# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase


from ..lookup.Secrets import Secrets


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        ret = dict()
        print(tmp)
        s = Secrets(project_id=task_vars["gcp_project_id"])

        s.set_secret(
            secret_id=self._task.args["secret_id"],
            secret=self._task.args["secret"],
            labels=self._task.args["labels"],
        )

        ret['updated'] = True
        ret['failed'] = False

        return dict(ansible_facts=dict(ret))
