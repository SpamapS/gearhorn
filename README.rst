A gearman worker which turns its jobs into a spool of responses to
other jobs. The purpose is to work with coalescing to provide broadcast
functionality.

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
