===============================
gearhorn
===============================


A gearman worker which enables efficient broadcast communication

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/gearhorn
* Source: http://git.openstack.org/cgit/openstack-infra/gearhorn
* Bugs: http://bugs.launchpad.net/gearhorn

=============
Fanout Worker
=============

Gearman has no in-built way to copy jobs to multiple workers. This worker
will do that to support the common messaging pattern known as "Fanout"

Once running, the fanout worker will subscribe to the queues
"register_fanout_subscriber" and "fanout".

register_fanout_subscriber
--------------------------

This queue will have a JSON payload consisting of a mapping with two
keys: topic, subscriber_id. The subscriber_id will be kept as a set
under the topic for use in sending messages to the appropriate subscriber
queue. It should be unique for every intended recipient queue for every
fanout request. Usually this will be unique per host.

fanout
------

This queue will have a JSON payload consisting of a mapping with two keys:
topic, payload. The topic will be used to search for a list of subscriber
ids. For each subscriber_id found, a copy of the payload will be sent
to the queue named  topic_subscriber_id. So if we had two subscribers to
"officememos" with ids "bob" and "alice", then a message to fanout with
this payload::

    {"topic": "officememos",
     "payload": "please go home early today."}

Optionally one can add a 'unique' key to make use of Gearman's
unique/coalescing features. Also the 'background' key can be used to
set a truthy value, which will tell gearhorn not to wait for receivers
before moving on to more messages.

Would result in the worker sending a copy of the payload to the queues
"officememos_bob" and "officememos_alice".

Matchmaking
~~~~~~~~~~~

In order to match up topics with subscribers workers must share a list
of subscribers for each topic. The mapping is maintained in a backend
data store. Any time new registration events are seen the list is updated
in that store and a message is sent to the __matchmaking topic. Workers
automatically add and remove themselves to/from the __matchmaking list
in order to ensure they're informed and able to clear cache whenever
the canonical list is updated. Workers that fail violently must be
manually removed.

===========
Failed Idea
===========

The following was idea #1, and fails to be any more efficient than just
runnint Redis as a pub/sub and direct comm backend. It remains here as
a reminder not to reimplement Redis.

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
