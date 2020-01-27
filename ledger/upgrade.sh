#!/bin/bash
rm output.log

NEW_NETWORK_VERSION=0.2.1

composer archive create --sourceType dir --sourceName digid -a digid@$NEW_NETWORK_VERSION.bna >> output.log

composer network install --card PeerAdmin@hlfv1 --archiveFile digid@$NEW_NETWORK_VERSION.bna >> output.log

composer network upgrade -c PeerAdmin@hlfv1 -n digid -V $NEW_NETWORK_VERSION >> output.log

composer network ping -c admin@digid >> output.log