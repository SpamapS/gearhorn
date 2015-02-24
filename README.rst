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

    {"sequence": 2,
     "payload": "foobarbaz"}

Clients would consume this, and then submit a new job with the
new_seq. This allows a stream of sync jobs to become a stream of
broadcasted payloads with a good chance of a client receiving all
sequences.

TODO
----

* True functional tests

* Make all the things configurable

  * Work queue name(s)

  * Tuning backlog and flush frequency

* Consider a work queue that workers can use to share the current sequence
  they should be using.

  * Would this be too racy or given the "best effort" is it enough to
    just try hard?

  * Do we need a UUID of some kind just to allow clients to detect if
    all the workers went away and sequences reset at 0?

* Add a client helper module which implements the sequence fetching to
  make it easier to write a consumer in python
