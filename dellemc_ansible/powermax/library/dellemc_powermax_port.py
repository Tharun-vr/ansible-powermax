#!/usr/bin/python
# Copyright: (c) 2019, DellEMC

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.storage.dell \
    import dellemc_ansible_powermax_utils as utils
import logging

__metaclass__ = type
ANSIBLE_METADATA = {"metadata_version": "1.1",
                    "status": ["preview"],
                    "supported_by": "community"
                    }

DOCUMENTATION = r"""
---
module: dellemc_powermax_port
version_added: '2.6'
short_description:  Manage ports on PowerMax/VMAX Storage System
description:
- Managing ports on PowerMax Storage System includes getting details of a port
extends_documentation_fragment:
  - dellemc_powermax.dellemc_powermax
author:
- Ashish Verma (@vermaa31) <ansible.team@dell.com>
options:
  ports:
    description:
    - List of port's director and port id
    required: true
"""

EXAMPLES = r"""
  - name: Get details of single/multiple ports
    dellemc_powermax_port:
      unispherehost: "{{unispherehost}}"
      verifycert: "{{verifycert}}"
      user: "{{user}}"
      password: "{{password}}"
      serial_no: "{{array_id}}"
      ports:
      - director_id: "FA-1D"
        port_id: "5"
      - director_id: "SE-1F"
        port_id: "29"
"""

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
port_details:
    description: Details of the port.
    returned: When the port exist.
    type: list
    contains:
		symmetrixPort:
			description: Type of volume.
			type: list
			contains:
				aclx:
					description: Indicates whether access control logic
					             enabled or disabled.
					type: bool
				avoid_reset_broadcast:
					description: Indicates whether Avoid Reset Broadcasting
					             feature is enabled or disabled.
					type: bool
				common_serial_number:
					description: Indicates whether Common Serial Number
					             feature is enabled or disabled.
					type: bool
				director_status:
					description: Director status.
					type: str
				disable_q_reset_on_ua:
					description: Indicates whether the Disable Q Reset on UA
					             (Unit Attention) is enabled or disabled.
					type: bool
				enable_auto_negotiate:
					description: Indicates whether the Enable Auto Negotiate
					             feature is enabled or disabled.
					type: bool
				environ_set:
					description: Indicates whether environmental error
					             reporting feature is enabled or disabled.
					type: bool
				hp_3000_mode:
					description: Indicates whether HP 3000 Mode is enabled or
					             disabled.
					type: bool
				identifier:
					description: Unique identifier for port.
					type: str
				init_point_to_point:
					description: Indicates whether Init Point to Point is
					             enabled or disabled.
					type: bool
				iscsi_target:
					description: Indicates whether ISCSI target is enabled or
					             disabled.
					type: bool
				maskingview:
					description: List of Masking views where port is a part
					             of.
					type:
				max_speed:
					description: Maximum port speed in GB/Second.
					type: str
				negotiate_reset:
					description: Indicates whether Negotiate Reset feature is
					             enabled or disabled. 
					type: bool
				negotiated_speed:
					description: Negotiated speed in GB/Second.
					type: str
				no_participating:
					description: Indicates whether No Participate feature is
					             enabled or disabled.
					type: bool
				num_of_cores:
					description:Number of cores for the director.
					type: int
				num_of_mapped_vols:
					description: Number of volumes mapped with the port.
					type: int
				num_of_masking_views:
					description: Number of masking views associated with the
					             port.
					type: int
				num_of_port_groups:
					description: Number of port groups associated with the port.
					type: int
				port_status:
					description: Port status, ON/OFF.
					type: str
				portgroup:
					description: List of masking views associated with the
					             port.
					type: list
				scsi_3:
					description: Indicates whether SCSI-3 protocol is enabled
					             or disabled.
					type: bool
				scsi_support1:
					description: Indicates whether SCSI Support1 is enabled or
					             disabled.
					type: bool
				siemens:
					description: Indicates whether Siemens feature is enabled
					             or disabled. 
					type: bool
				soft_reset:
					description: Indicates whether Soft Reset feature is 
					             enabled or disabled.
					type: bool
				spc2_protocol_version:
					description: Indicates whether SPC2 Protocol Version
					             feature is enabled or disabled.
					type: bool
				sunapee:
					description: Indicates whether Sunapee feature is enabled
					             or disabled.
					type: bool
				symmetrixPortKey:
					description: Symmetrix system director and port in the 
					             port group.
					type: list
					contains:
						directorId:
							description: Director ID of the port.
							type: str
						portId:
							description: Port number of the port.
							type: str
				type:
					description: Type of port.
					type: str
				unique_wwn:
					description: Indicates whether Unique WWN feature is 
					             enabled or disabled.
					type: bool
				vnx_attached:
					description: Indicates whether VNX attached feature is
					             enabled or disabled.
					type: bool
				volume_set_addressing:
					description: Indicates whether Volume Vet Addressing is
					             enabled or disabled.
					type: bool
				wwn_node:
					description: WWN node of port.
					type: str
'''

LOG = utils.get_logger("dellemc_powermax_port", log_devel=logging.INFO)

HAS_PYU4V = utils.has_pyu4v_sdk()

PYU4V_VERSION_CHECK = utils.pyu4v_version_check()

# Application Type
APPLICATION_TYPE = 'ansible_v1.2'


class PowerMaxPort(object):
    """ Class with port operations"""

    u4v_conn = None
    def __init__(self):
        """ Define all the parameters required by this module"""
        self.module_params = utils.get_powermax_management_host_parameters()
        self.module_params.update(get_powermax_port_parameters())
        # initialize the ansible module
        self.module = AnsibleModule(
            argument_spec=self.module_params,
            supports_check_mode=False
        )
        # result is a dictionary that contains changed status and port details
        self.result = {"changed": False, "port_details": {}}
        if HAS_PYU4V is False:
            self.show_error_exit(msg="Ansible modules for PowerMax require "
                                      "the PyU4V python library to be "
                                      "installed. Please install the library "
                                      "before using these modules.")

        if PYU4V_VERSION_CHECK is not None:
            self.show_error_exit(msg=PYU4V_VERSION_CHECK)

        if self.module.params['universion'] is not None:
            universion_details = utils.universion_check(
                self.module.params['universion'])
            LOG.info("universion_details: {0}".format(universion_details))

            if not universion_details['is_valid_universion']:
                self.show_error_exit(msg=universion_details['user_message'])

        # Getting PyU4V instance for provisioning on to VMAX
        try:
            self.u4v_conn = utils.get_U4V_connection(
                    self.module.params, application_type=APPLICATION_TYPE)
        except Exception as e:
            self.show_error_exit(msg=str(e))
        self.provisioning = self.u4v_conn.provisioning
        LOG.info("Got PyU4V instance for provisioning on to VMAX")

    def get_port_details(self):
        """
        Getting details of a port
        """
        LOG.info("Getting the details of port")
        ports = self.module.params['ports']
        try:
            details = {}
            message = "Director ID and Port ID is mandatory for listing " \
                      "port information"
            for port in ports:
                if len(port) < 2 or port["director_id"] is None or \
                        port["port_id"] is None or \
                        len(port["director_id"]) == 0 or \
                        len(port["port_id"]) == 0:
                    self.show_error_exit(msg=message)

                director_id = port["director_id"]
                port_id = port["port_id"]

                details[director_id + ":" + port_id] = \
                    self.provisioning.get_director_port(director_id, port_id)
                self.result["port_details"] = details
            return
        except Exception as e:
            error_message = "Failed to get details of port {0}:{1} with " \
                            "error {2}"
            self.show_error_exit(msg=error_message.format(director_id,
                                                           port_id, str(e)))

    def show_error_exit(self, msg):
        if self.u4v_conn is not None:
            try:
                LOG.info("Closing unisphere connection {0}".format(
                    self.u4v_conn))
                utils.close_connection(self.u4v_conn)
                LOG.info("Connection closed successfully")
            except Exception as e:
                err_msg= "Failed to close unisphere connection with error:" \
                         " {0}".format(str(e))
                LOG.error(err_msg)
        LOG.error(msg)
        self.module.fail_json(msg=msg)

    def perform_module_operation(self):
        """
        Perform different actions on port based on user parameter
        chosen in playbook
        """

        changed = False
        self.get_port_details()
        # Finally update the module changed state
        self.result["changed"] = changed
        LOG.info("Closing unisphere connection {0}".format(self.u4v_conn))
        utils.close_connection(self.u4v_conn)
        LOG.info("Connection closed successfully")
        self.module.exit_json(**self.result)


def get_powermax_port_parameters():
    """This method provide parameter required for the ansible port modules on PowerMax"""
    return dict(
        ports=dict(required=True, type='list')
    )


def main():
    """
    Create PowerMax port object and perform action on it
    based on user input from playbook
    """
    obj = PowerMaxPort()
    obj.perform_module_operation()

if __name__ == "__main__":
    main()
