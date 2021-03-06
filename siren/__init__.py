import request
import toolbelt

# This Object handles Cache


class Cache(object):

    def __init__(self):

        self.data = None
        self._limit = None

    def set_dat(self, data, limit):

        self.data = data
        self._limit = limit

    def read(self, amount=None):
        if bool(amount):
            return (self.data[:amount])
        else:
            return self.data

    def check(self, nLimit):
        # Returns True if cache needes to be updated, false if otherwise.
        if (self._limit) and (nLimit):
            return (nLimit <= self._limit)
        elif nLimit is None and not (self.data is None):
            return True
        else:
            return False

    def clean_out(self):
        # Needed for check()
        self.data = None
        self._limit = None

# Alert Object. Made to make using this module easier.
# Wraps around the module.


class Siren(object):

    def __init__(self, **kwargs):

        # Sets up the arguments for the object
        self.arg_loader(kwargs)

        # Creates a request instance.
        self.request_obj = request.nws(self.state, self.auto_load, self.loc)

        # Sets limit on how much of the result should be processed. Needs
        # request_obj to work
        self._limit = kwargs.get("limit", None)  # default is 20

        if self.auto_load:
            self.load()

    def __getitem__(self, name):
        if name is "cap":
            return self.get_cap()
        elif name is "id":
            return self.get_id()
        elif name is "summary":
            return self.get_id()
        elif name is "title":
            return self.get_summary()
        else:
            if isinstance(name, str):
                raise KeyError("'{}'".format(name))

    # Implent len() for Siren object
    def __len__(self):
        return self._limit if self._limit else len(self.get_entries())

    @property
    def limit(self):
        return self.request_obj.limit

    # Handles changes to limit
    @limit.setter
    def limit(self, limit):
        self._limit = limit if (
            limit or limit is None) else self.request_obj.limit

    # Sets up the arguments for the object.
    def arg_loader(self, args):

        # Auto_load, decides if this object should load data from NWS servers
        # on creation
        self.auto_load = args.get("state", False)  # Default is False

        # Determines the state
        self.state = args.get("state", "us")  # default is "us"

        # If this is zone/county id rather than a state, this must be set to
        # true.
        self.loc = args.get("loc", False)

        # Cache System
        self.cap = Cache()
        self.summary = Cache()
        self.title = Cache()
        self.id = Cache()

    # requests the data for our object
    def load(self):
        # empty the cache system.
        self.cap.clean_out()
        self.summary.clean_out()
        self.title.clean_out()
        self.id.clean_out()
        return self.request_obj.load()

    def parse(self, limit=None):  # If called, it will parse the entire feed.
        limit = self.decide_limit(limit)
        self.get_cap(limit)
        self.get_summary(limit)
        self.get_title(limit)
        self.get_id(limit)
        return True

    def change_area(self, **kwargs):  # Changes area request info
        area = kwargs.get("area")
        self.loc = bool(kwargs.get("is_loc"))
        onload = kwargs.get("onload")
        self.request_obj.change_state(loc)

    def decide_limit(self, _limit_):
        return _limit_ if _limit_ else self._limit

    def get_entries(self):
        return self.request_obj.entries

    def get_raw_xml(self):
        return self.request_obj.alert_raw

    def get_cap(self, limit=None):
        limit = self.decide_limit(limit)
        if self.cap.check(limit):
            return self.cap.read(limit)
        else:
            self.cap.set_dat(self.request_obj.get_cap(limit), limit)
            return self.cap.read(limit)

    def get_summary(self, limit=None):
        limit = self.decide_limit(limit)
        if self.summary.check(limit):
            return self.summary.read(limit)
        else:
            self.summary.set_dat(self.request_obj.get_summary(limit), limit)
            return self.summary.read(limit)

    def get_title(self, limit=None):
        limit = self.decide_limit(limit)
        if self.title.check(limit):
            return self.title.read(limit)
        else:
            self.title.set_dat(self.request_obj.get_title(limit), limit)
            return self.title.read(limit)

    def get_id(self, limit=None):
        limit = self.decide_limit(limit)
        if self.id.check(limit):
            return self.id.read(limit)
        else:
            self.id.set_dat(self.request_obj.get_id(limit), limit)
            return self.id.read(limit)
    # END Request Methods

    # The report and get_all() related methods need a cleanup.
    # Currently code is only slightly changed.
    # Moved out of toolbelt to __init__.py. Needs a Cleanup
    def _id_report(self, id_url, entryint=0):
        url = (id_url)[entryint][entryint]["id"]
        return request.report(url.replace("http://", "https://"))

    def get_report(self, **kwargs):
        raw_id = (kwargs.get("id"))
        limit = (self.decide_limit(kwargs.get("limit")))
        _id_ = raw_id if (raw_id) else self.request_obj.get_id(limit)
        entryint = kwargs.get("key", 0)
        return self._id_report(_id_, entryint)

    def _all_gen(self, greport, only_report, limit=1):
        limit = limit if not (
            limit is None) else (
            self.limit if self.limit is not None else 25)
        _cap_ = self.get_cap()
        _id_ = self.get_id()
        _title_ = self.get_title()
        _summary_ = self.get_summary()
        if greport and not only_report:
            for x in range(limit if len(_cap_) > limit else len(_cap_)):
                report = _id2report(_id_, x)
                report.load()
                yield {"report": {"meta": siren.request.report.get_meta(),
                                  "info": report.get_info()},
                       "id": _id_[x]["id"],
                       "title": _title_[x]["title"],
                       "summary": _summary_[x]["summary"],
                       "cap": _cap_[x]}

        elif greport and only_report:
            for x in xrange(0, limit if len(_cap_) > limit else len(_cap_)):
                report = id2report(_id_, x)
                report.load()
                yield {"report": {
                    "meta": siren.request.report.get_meta(),
                    "info": report.get_info()

                },
                    "id": _id_[x]["id"]}

        else:
            for x in xrange(0, limit if len(_cap_) > limit else len(_cap_)):
                yield {"id": _id_[x]["id"], "title": _title_[x]["title"],
                       "summary": _summary_[x]["summary"], "cap": _cap_[x]}

    def _get_all(self, limit=5, greport=False, only_report=False):
        return list(self._all_gen(greport, only_report, limit))

    def get_all(self, **kwargs):
        include_report = bool(kwargs.get("reports"))
        only_reports = bool(kwargs.get("only_reports"))
        limit = self.decide_limit(kwargs.get("limit"))
        return self._get_all(
            limit=limit,
            greport=include_report,
            only_report=only_reports)

    # Returns True if request returned back any warnings, False if not. (Only
    # returns False Valid states with no current warnings, 404 errors will
    # still raise an error)
    def warnings(self):
        try:
            return self.request_obj.has_warnings
        except:
            print("Warning: Server returned 404")
            return False
