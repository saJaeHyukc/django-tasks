from django.test import SimpleTestCase, override_settings
from django_core_tasks import tasks, default_task_backend, TaskStatus
from django_core_tasks.backends.dummy import DummyBackend
from django_core_tasks.backends.base import BaseTaskBackend
from . import tasks as test_tasks
import inspect
from django.utils import timezone


@override_settings(
    TASKS={"default": {"BACKEND": "django_core_tasks.backends.dummy.DummyBackend"}}
)
class DummyBackendTestCase(SimpleTestCase):
    def setUp(self):
        default_task_backend.clear()

    def test_using_correct_backend(self):
        self.assertEqual(default_task_backend, tasks["default"])
        self.assertIsInstance(tasks["default"], DummyBackend)

    def test_enqueue_task(self):
        self.assertTrue(default_task_backend.supports_enqueue())

        task = default_task_backend.enqueue(test_tasks.noop_task)

        self.assertEqual(task.status, TaskStatus.NEW, task.result)
        self.assertIsNone(task.result)
        self.assertIsNone(task.when)
        self.assertEqual(task.func, test_tasks.noop_task)
        self.assertEqual(task.args, [])
        self.assertEqual(task.kwargs, {})

        self.assertEqual(default_task_backend.tasks, [task])

    async def test_enqueue_task_async(self):
        task = await default_task_backend.aenqueue(test_tasks.noop_task)

        self.assertEqual(task.status, TaskStatus.NEW, task.result)
        self.assertIsNone(task.result)
        self.assertEqual(task.func, test_tasks.noop_task)
        self.assertEqual(task.args, [])
        self.assertEqual(task.kwargs, {})

        self.assertEqual(default_task_backend.tasks, [task])

    def test_executes_async_task(self):
        task = default_task_backend.enqueue(test_tasks.noop_task_async)

        self.assertEqual(task.status, TaskStatus.NEW, task.result)
        self.assertIsNone(task.result)
        self.assertEqual(task.func, test_tasks.noop_task_async)
        self.assertEqual(task.args, [])
        self.assertEqual(task.kwargs, {})

        self.assertEqual(default_task_backend.tasks, [task])

    async def test_executes_async_task_async(self):
        task = await default_task_backend.aenqueue(test_tasks.noop_task_async)

        self.assertEqual(task.status, TaskStatus.NEW, task.result)
        self.assertIsNone(task.result)
        self.assertEqual(task.func, test_tasks.noop_task_async)
        self.assertEqual(task.args, [])
        self.assertEqual(task.kwargs, {})

        self.assertEqual(default_task_backend.tasks, [task])

    def test_defer_task(self):
        self.assertTrue(default_task_backend.supports_defer())

        when = timezone.now()

        task = default_task_backend.defer(test_tasks.noop_task, when=when)

        self.assertEqual(task.status, TaskStatus.NEW, task.result)
        self.assertIsNone(task.result)
        self.assertEqual(task.when, when)
        self.assertEqual(task.func, test_tasks.noop_task)
        self.assertEqual(task.args, [])
        self.assertEqual(task.kwargs, {})

        self.assertEqual(default_task_backend.tasks, [task])

    async def test_defer_task_async(self):
        when = timezone.now()

        task = await default_task_backend.adefer(test_tasks.noop_task, when=when)

        self.assertEqual(task.status, TaskStatus.NEW, task.result)
        self.assertIsNone(task.result)
        self.assertEqual(task.func, test_tasks.noop_task)
        self.assertEqual(task.when, when)
        self.assertEqual(task.args, [])
        self.assertEqual(task.kwargs, {})

        self.assertEqual(default_task_backend.tasks, [task])

    def test_defer_async_task(self):
        when = timezone.now()

        task = default_task_backend.defer(test_tasks.noop_task_async, when=when)

        self.assertEqual(task.status, TaskStatus.NEW, task.result)
        self.assertIsNone(task.result)
        self.assertEqual(task.func, test_tasks.noop_task_async)
        self.assertEqual(task.when, when)
        self.assertEqual(task.args, [])
        self.assertEqual(task.kwargs, {})

        self.assertEqual(default_task_backend.tasks, [task])

    async def test_defer_async_task_async(self):
        when = timezone.now()

        task = await default_task_backend.adefer(test_tasks.noop_task_async, when=when)

        self.assertEqual(task.status, TaskStatus.NEW, task.result)
        self.assertIsNone(task.result)
        self.assertEqual(task.func, test_tasks.noop_task_async)
        self.assertEqual(task.when, when)
        self.assertEqual(task.args, [])
        self.assertEqual(task.kwargs, {})

        self.assertEqual(default_task_backend.tasks, [task])

    def test_get_task(self):
        task = default_task_backend.enqueue(test_tasks.noop_task)

        new_task = default_task_backend.get_task(task.id)

        self.assertIs(task, new_task)

    async def test_get_task_async(self):
        task = await default_task_backend.aenqueue(test_tasks.noop_task)

        new_task = await default_task_backend.aget_task(task.id)

        self.assertIs(task, new_task)

    async def test_cannot_refresh_task(self):
        task = default_task_backend.enqueue(test_tasks.noop_task)

        with self.assertRaisesMessage(
            NotImplementedError,
            "This task cannot be refreshed",
        ):
            task.refresh()

        with self.assertRaisesMessage(
            NotImplementedError,
            "This task cannot be refreshed",
        ):
            await task.arefresh()

    def test_enqueue_signature(self):
        self.assertEqual(
            inspect.signature(DummyBackend.enqueue),
            inspect.signature(BaseTaskBackend.enqueue),
        )

    def test_defer_signature(self):
        self.assertEqual(
            inspect.signature(DummyBackend.defer),
            inspect.signature(BaseTaskBackend.defer),
        )
