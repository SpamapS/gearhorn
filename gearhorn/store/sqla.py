# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sqlalchemy as sa
from sqlalchemy import exc as sa_exc
from sqlalchemy import orm
from sqlalchemy.orm import exc

from gearhorn.store import sqla_models as models
from gearhorn import util

_session = None


class Store(object):
    def __init__(self, details):
        self._engine = sa.create_engine(details)
        self._sessionmaker = orm.sessionmaker(bind=self._engine)

    @property
    def session(self):
        return orm.scoped_session(self._sessionmaker)

    def initialize_schema(self):
        models.Base.metadata.create_all(self._engine)

    def subscribe(self, client_id, topic):
        # Storing as binary for more efficient usage in MySQL particularly
        s = models.Subscriber(topic=util.to_utf8(topic),
                              client_id=util.to_utf8(client_id))
        sess = self.session()
        try:
            sess.add(s)
            # XXX: allow commit in batches some day
            sess.commit()
        except sa_exc.IntegrityError:
            sess.rollback()
            # We don't actually care, because it means we already have this
            # subscription
            pass

    def unsubscribe(self, client_id, topic):
        s = models.Subscriber(topic=util.to_utf8(topic),
                              client_id=util.to_utf8(client_id))
        sess = self.session()
        sess.delete(s)
        sess.commit()

    def get_subscribers(self, topic):
        sess = self.session()
        try:
            for sub in sess.query(
                models.Subscriber.client_id).filter_by(topic=topic):
                yield sub[0]
        except exc.NoResultFound:
            return
