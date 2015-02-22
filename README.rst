===============================
gearhorn
===============================


A gearman worker which enables efficient broadcast communication

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/gearhorn
* Source: http://git.openstack.org/cgit/openstack-infra/gearhorn
* Bugs: http://bugs.launchpad.net/gearhorn

The expected way to use it is to have a gearman client that wants to
receive broadcasts request the given broadcast function with a unique ID
that is the last seen sequence ID. When this daemon receives that work,
it looks for any items with sequence number greater than this ID, and
if it finds them, reply with a json payload of::

    {"new_seq": 2,
     "payload": "foobarbaz"}

Clients would consume this, and then submit a new job with the
new_seq. This allows a stream of sync jobs to become a stream of
broadcasted payloads with a good chance of a client receiving all
sequences.
