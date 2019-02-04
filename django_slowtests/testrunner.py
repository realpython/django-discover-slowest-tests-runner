import time
import operator

from unittest import TestSuite, TestLoader
from unittest.suite import _isnotsuite
from django.test.runner import DiscoverRunner
from django.conf import settings


try:  # pragma: no cover
    import freezegun

    def _time():
        return freezegun.api.real_time()
except ImportError:  # pragma: no cover
    def _time():
        return time.time()


TIMINGS = {}


class TimingSuite(TestSuite):
    """
    TestSuite wrapper that times each test.
    """

    def run(self, result, debug=False):
        topLevel = False
        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True

        for test in self:
            if result.shouldStop:
                break

            start_time = _time()

            if _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                self._handleModuleFixture(test, result)
                self._handleClassSetUp(test, result)
                result._previousTestClass = test.__class__

                if (getattr(test.__class__, '_classSetupFailed', False) or
                        getattr(result, '_moduleSetUpFailed', False)):
                    continue

            if not debug:
                test(result)
            else:
                test.debug()

            TIMINGS[str(test)] = _time() - start_time

        if topLevel:
            self._tearDownPreviousClass(None, result)
            self._handleModuleTearDown(result)
            result._testRunEntered = False

        return result


class TimingLoader(TestLoader):
    suiteClass = TimingSuite


class DiscoverSlowestTestsRunner(DiscoverRunner):
    """
    Runner that extends Django's DiscoverRunner to time the tests.
    """
    test_suite = TimingSuite
    test_loader = TimingLoader()

    def __init__(self, generate_report=False, **kwargs):
        super(DiscoverSlowestTestsRunner, self).__init__(**kwargs)
        self.generate_report = generate_report

    @classmethod
    def add_arguments(cls, parser):
        DiscoverRunner.add_arguments(parser)
        parser.add_argument(
            '--slowreport',
            action='store_true',
            dest='generate_report',
            help='Generate a report of slowest tests',
        )

    def teardown_test_environment(self, **kwargs):
        super(DiscoverSlowestTestsRunner, self).teardown_test_environment(**kwargs)

        NUM_SLOW_TESTS = getattr(settings, 'NUM_SLOW_TESTS', 10)
        SLOW_TEST_THRESHOLD_MS = getattr(settings, 'SLOW_TEST_THRESHOLD_MS', 0)

        should_generate_report = (
            getattr(settings, 'ALWAYS_GENERATE_SLOW_REPORT', True) or
            self.generate_report
        )
        if not should_generate_report:
            return
        # Grab slowest tests
        by_time = sorted(
            iter(TIMINGS.items()),
            key=operator.itemgetter(1),
            reverse=True
        )[:NUM_SLOW_TESTS]

        test_results = by_time

        if SLOW_TEST_THRESHOLD_MS:
            # Filter tests by threshold
            test_results = []

            for result in by_time:
                # Convert test time from seconds to miliseconds for comparison
                result_time_ms = result[1] * 1000

                # If the test was under the threshold
                # don't show it to the user
                if result_time_ms < SLOW_TEST_THRESHOLD_MS:
                    continue

                test_results.append(result)

        test_result_count = len(test_results)

        if test_result_count:
            if SLOW_TEST_THRESHOLD_MS:
                print("\n{r} slowest tests over {ms}ms:".format(
                    r=test_result_count, ms=SLOW_TEST_THRESHOLD_MS)
                )
            else:
                print("\n{r} slowest tests:".format(r=test_result_count))

        for func_name, timing in test_results:
            print(("{t:.4f}s {f}".format(f=func_name, t=timing)))

        if not len(test_results) and SLOW_TEST_THRESHOLD_MS:
            print("\nNo tests slower than {ms}ms".format(ms=SLOW_TEST_THRESHOLD_MS))
