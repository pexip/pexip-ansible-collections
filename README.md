# pexip-ansible-collections
A collection of Pexip's Ansible collections

## Installation

### Command line

Install using command line:

```
$ ansible-galaxy collection install ./pexip/
```

Or if anything changed:

```
$ ansible-galaxy collection install ./pexip/ --upgrade
```

### Ansible

```yaml
  collections:
    - name: https://github.com/pexip/pexip-ansible-collections.git
      type: git
      version: master
```

## Usage

Example fetching secret from GCP secrets manager:

```yaml
# if need to fetch
- name: copy secret key to file
  copy:
    content: "{{ lookup('pexip.custom.gcp_secrets', secret_id, project=gcp_project_id ) }}"
    dest: "/tmp/key.crt"
```