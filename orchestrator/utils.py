from datetime import datetime
from os import makedirs
from os import path as ospath
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from itertools import count
import sched, time
import unittest
import doctest
import glob


class Tester:
    def __init__(self, *args, **kwargs):
        self.username = kwargs['username']
        self.model = kwargs['model']
        self.path = ospath.join(settings.BASE_DIR, 'media/', kwargs['path'])
        self.environment = kwargs['environment']
        self.interface = kwargs['interface']

    def run(self):
        # environment is unittest
        if self.environment == 'UT':
            failures, desc, errors = self.run_unittest()
        # environment is doctest
        elif self.environment == 'DT':
            failures, desc, errors = self.run_doctest()

        if failures:
            state = 'Failed'
        else:
            state = 'Finished'
        
        self.model.update_state(new_state=state,
                                failures=failures,
                                desc=desc,
                                errors=errors)


    def run_doctest(self):
        suite = unittest.TestSuite()
        suite.addTest(doctest.DocFileSuite(*glob.glob('{}/*'.format(self.path)),
                      module_relative=False))

        runner = unittest.TextTestRunner(verbosity=2)
        r = runner.run(suite)
        failures = r.failures
        desc = r.descriptions
        errors = r.errors
        return failures, desc, errors

    def run_unittest(self):
        suite = unittest.TestLoader().discover(self.path)
        # suite = unittest.TestLoader().loadTestsFromModule(testfile)
        r = unittest.TextTestRunner().run(suite)
        failures = r.failures
        desc = r.descriptions
        errors = r.errors
        return failures, desc, errors


class FileHandler:
    def __init__(self, *args, **kwargs):
        self.files = kwargs['files']
        self.username = kwargs['username']
        self.model = kwargs['model']
        self.environment = kwargs['environment']
        self.interface = kwargs['interface']
        self.path = None
        self.file_names = []
        self.save_delay = settings.SAVE_DELAY
    
    def create_tester(self):
        tester = Tester(username=self.username,
                        model=self.model,
                        path=self.path,
                        environment=self.environment,
                        interface=self.interface)
        return tester

    def create_path(self):
        """Creating a directory based on username in order to preserver the files in it."""

        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        dirpath = ospath.join(self.username, date)
        if not ospath.isdir(dirpath):
            makedirs(dirpath)
        return dirpath

    def save_files(self):
        self.path = base = self.create_path()
        for f in self.files:
            name = f.name
            self.file_names.append(name)
            # self.check_name(name) # no need for check name at test mode
            path = ospath.join(base, name)

            if f.size > settings.MAX_FILE_SIZE:
                # File is too large to be readed at once
                # Thus, we read/write the file in cunks
                with default_storage.open(path, 'wb') as inp:
                    for chunk in f.chunks():
                        inp.write(chunk)
            else:
                # file is not that large
                default_storage.save(path, ContentFile(f.read()))

    def check_name(self, name):
        """ Check for valid names."""
        # this is just a test 
        if not name.endswith('.py'):
            raise Exception("Invalid File Format")
    
    def scheduler(self, delay, func):
        """ Start the function after a given delay."""

        s = sched.scheduler(time.time, time.sleep)
        s.enter(delay, 1, func)
        s.run()
    
    def run_tester(self):
        self.tester = self.create_tester()
        self.tester.run()

    def run(self):
        self.scheduler(self.save_delay, self.save_files)
        self.scheduler(self.save_delay + 5, self.run_tester)
        print("finish file handler")

class Paginator:
    """ A paginator object that for paginating huge amout of records."""

    def __init__(self, *args, **kwargs):
        self.results = args[0]
        self.rows_number = kwargs['rows_number']
        self.range_frame = kwargs['range_frame']
        self.counter = count(1)
        self.cache = {}
        self.current = self.create_page()
    
    def create_page(self, number=False):
        if not number:
            number = next(self.counter)
        # should use deque with max_len == self.row_number
        items = [next(self.results, None) for _ in range(self.rows_number)]
        if items[0] is None:
            raise StopIteration

        page = Page(items=items,
                    number=number,
                    range_frame=self.range_frame)
        self.cache[number] = page
        return page
    
    def __next__(self):
        number = next(self.counter)
        try:
            page = self.cache[number]
        except KeyError:
            try:
                page = self.create_page(number=number)
            except StopIteration:
                raise
            else:
                print("create page {}".format(number))
                return page
        else:
            return page

    def __iter__(self):
        return self
    
    def __getitem__(self, index):
        try:
            page = self.cache[index]
        except KeyError:
            page = self.create_page(index)
        else:
            print("call from cache {}".format(index))
        finally:
            self.current = page
            return page
            

    def has_other_pages(self):
        try:
            return self.current.last_item is not None
        except IndexError:
            return True



class Page:
    def __init__(self, *args, **kwargs):
        self.number = kwargs['number']
        self.range_frame = kwargs['range_frame']
        self.items = kwargs['items']
        self.last_item = self.items[-1]
        self.previous_page_number = self.number - self.range_frame
        self.next_page_number = self.number + self.range_frame
        self.index = 0

    def __next__(self):
        try:
            result = self.items[self.index]
        except IndexError:
            self.index = 0
            raise StopIteration
        self.index += 1
        return result

    def __iter__(self):
        return self
    
    def has_previous(self):
        return self.number != 1

    def has_next(self):
        try:
            return self.last_item is not None
        except IndexError:
            return True
    
    def page_range(self):
        """
        Using a page range while the paginator is dealing with
        iterators and presumably is not aware of the length of
        records, is like a paradox but this is what that people
        can't figure out unless they are in one page before the
        last page! In real products that deals with outsider
        users it's better to not use this or think of another
        correct method, tho.
        """
        lower = max(self.number - self.range_frame, 1)
        # for a more precise result we should always cache
        # pages within the range_frame so that we can easily
        # detect wheter there are any upper pages or not 
        upper = lower + (2*self.range_frame)
        return range(lower, upper)
