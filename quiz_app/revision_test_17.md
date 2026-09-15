# Resultado del test — Ingeniería de software en Python

- Fecha: 2026-09-14 15:33
- Nivel: junior
- Puntuación: **65%** (6.50/10 puntos)
- Preguntas perfectas: 5/10

## Revisión pregunta a pregunta

### ⚠️ Pregunta 1 — Type hints generics unions and static checking

Given Python 3.10 or later and the following annotations, which statements are correct?

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]

def parse(value: str | bytes) -> int:
    return int(value)
```

- [x] **The annotation str | bytes means that parse accepts either str or bytes.** — _correcta_: Since Python 3.10, the vertical-bar syntax defined by PEP 604 expresses a union of types.
- [x] **A static type checker can infer that first([1, 2]) returns an int.** — _correcta_: The generic type variable T is inferred as int from list[int], so the declared return type is int.
- [ ] **Static type checking guarantees that first([]) cannot fail at runtime.** — _incorrecta_: The annotation list[T] does not express that the list is non-empty, so first([]) can still raise IndexError.
- [ ] **T requires every call to first in the program to use the same element type.** — _incorrecta_: A type checker resolves T independently for each call, so different calls may use different element types.
- [x] **Python automatically raises a type error before first is called if the argument conflicts with its annotation.** — _incorrecta_: Annotations are not generally enforced at runtime; a separate checker or explicit runtime validation is needed.

> Type variables describe relationships between input and output types, while unions describe multiple accepted types. Type hints support tools such as mypy and Pyright but are not automatically enforced by the Python runtime, and they do not capture every runtime condition.
>
> Repasar: `TypeVar, PEP 604, static type checking`

### ✅ Pregunta 2 — Generator iteration protocol and lazy evaluation

Consider this code:

```python
def values():
    print("start")
    yield 1
    yield 2

items = values()
first = next(items)
rest = list(items)
```

Which statements are correct?

- [x] **Calling `values()` creates a generator without printing `start`.** — _correcta_: Calling a generator function creates a generator object; its body does not begin executing until iteration requests a value.
- [ ] **Both yielded values are computed when `items = values()` executes.** — _incorrecta_: Generator execution is lazy: values are produced only as the iterator is advanced.
- [x] **`next(items)` prints `start` and assigns `1` to `first`.** — _correcta_: `next()` starts execution and pauses at the first `yield`, which produces `1`.
- [x] **After `rest` is assigned, another `next(items)` raises `StopIteration`.** — _correcta_: `list(items)` consumes the remaining value and exhausts the generator, so the next request signals completion with `StopIteration`.
- [ ] **`list(items)` produces `[1, 2]` because every new iteration restarts the generator.** — _incorrecta_: A generator is a stateful iterator and does not restart. Since `1` was already consumed, the resulting list is `[2]`.

> A function containing `yield` returns a generator iterator. Execution is lazy, each `yield` suspends the frame while preserving its state, and exhaustion is reported through `StopIteration`.
>
> Repasar: `Generator protocol: yield, next, and StopIteration`

### ⚠️ Pregunta 3 — Reference counting, garbage collection, and object lifetimes

In CPython, which statements about object lifetime and memory management are correct?

- [x] **An object can usually be finalized as soon as its reference count reaches zero.** — _correcta_: CPython primarily uses reference counting, so reaching a reference count of zero normally causes immediate finalization. This behavior is an implementation detail and is not guaranteed by every Python implementation.
- [ ] **The cyclic garbage collector can detect groups of unreachable objects that reference one another.** — _correcta_: Reference counts alone cannot reclaim reference cycles. CPython's cyclic garbage collector supplements reference counting by detecting certain unreachable cycles.
- [ ] **The `del` statement always destroys the referenced object immediately.** — _incorrecta_: `del` removes a binding or container reference. The object remains alive if other strong references to it still exist.
- [ ] **Calling `gc.collect()` guarantees that every allocated Python object is destroyed.** — _incorrecta_: `gc.collect()` targets unreachable objects managed by the cyclic collector. Reachable objects remain alive, and not every allocation is governed solely by this collector.

> CPython combines reference counting with a cyclic garbage collector. Object lifetime depends on reachability and strong references: removing one name does not necessarily destroy an object, while unreachable reference cycles may require cyclic collection.
>
> Repasar: `CPython reference counting, `del`, and the `gc` module`

### ✅ Pregunta 4 — Package structure, dependencies, virtual environments, and distribution

A project declares its runtime dependencies and build configuration in `pyproject.toml`. What is the primary purpose of creating a virtual environment for the project?

- [ ] **To convert the project automatically into a wheel distribution.** — _incorrecta_: A virtual environment does not build distributions. A build frontend such as `python -m build` can create source and wheel distributions using the configuration in `pyproject.toml`.
- [ ] **To ensure the package can be imported without installing it or adding it to Python's import path.** — _incorrecta_: Creating a virtual environment alone does not make the project importable. The package must be installed, commonly with an editable install during development, or otherwise be available on the import path.
- [x] **To isolate the project's installed packages from the system Python environment and other projects.** — _correcta_: A virtual environment provides a separate package installation location and interpreter context. This reduces dependency conflicts between projects.
- [ ] **To bundle the Python interpreter and all dependencies into the published wheel.** — _incorrecta_: Ordinary wheels do not bundle a complete Python interpreter and normally declare rather than embed third-party dependencies. Installers resolve and install those dependencies separately.

> Virtual environments isolate installed dependencies, while `pyproject.toml` defines project and build metadata under modern Python packaging standards. Building distributions and making a local project importable are separate operations.
>
> Repasar: ``venv`, `pyproject.toml`, editable installs, and wheel distributions`

### ⚠️ Pregunta 5 — GIL implications for threading and CPU-bound workloads

In standard CPython, which statements about the Global Interpreter Lock (GIL) are correct?

- [x] **The GIL makes all operations on shared Python data structures safe from race conditions.** — _incorrecta_: Some individual operations may be atomic in a particular implementation, but multi-step operations can still race and require synchronization.
- [x] **Only one thread can execute Python bytecode at a time within a process.** — _correcta_: The GIL serializes the execution of Python bytecode by threads in the same CPython process.
- [ ] **Adding threads normally makes pure-Python CPU-bound code run in parallel across multiple CPU cores.** — _incorrecta_: The GIL usually prevents pure-Python threads from executing CPU-bound bytecode simultaneously.
- [x] **Threads can still improve performance when tasks spend significant time waiting for network or file I/O.** — _correcta_: CPython generally releases the GIL during blocking I/O, allowing another thread to run.

> In standard CPython, the GIL permits only one thread at a time to execute Python bytecode in a process. Threading remains useful for I/O-bound work, while CPU-bound pure-Python work generally requires another approach to use multiple cores.
>
> Repasar: `CPython Global Interpreter Lock`

### ❌ Pregunta 6 — Python data model and special method lookup

Consider this code:

```python
class Box:
    def __init__(self, value):
        self.value = value

    def __len__(self):
        return self.value

box = Box(3)
box.__len__ = lambda: 10
```

Which statements are correct?

- [ ] **`box.__len__()` returns `10`.** — _correcta_: Explicit attribute access checks the instance, where `__len__` now refers to the assigned lambda.
- [x] **Assigning `box.__len__` raises `AttributeError` because special methods are read-only.** — _incorrecta_: Instances with a normal `__dict__` can receive an attribute named `__len__`; it simply does not control the behavior of `len(box)`.
- [ ] **`len(box)` returns `10` because instance attributes always override class attributes.** — _incorrecta_: That rule applies to ordinary attribute access, but implicit special-method lookup generally occurs on the type.
- [ ] **`len(box)` returns `3`.** — _correcta_: `len()` looks up `__len__` on the object's type, so the instance attribute assigned afterward is ignored.

> Python operations such as `len(obj)` perform implicit special-method lookup on `type(obj)`, bypassing an instance attribute with the same name. Directly calling `obj.__len__()` uses normal attribute access instead.
>
> Repasar: `Special method lookup`

### ❌ Pregunta 7 — Decorator closures and metadata preservation

Which decorator logs a call, returns the wrapped function's result, accepts arbitrary arguments, and preserves metadata such as `__name__`?

- [ ] **```python
def log_call(func):
    print(func.__name__)
    return func
```** — _incorrecta_: This prints when decoration occurs, not whenever the decorated function is called, and it creates no wrapper closure.
- [x] **```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print(func.__name__)
        func(*args, **kwargs)
    return wrapper
```** — _incorrecta_: It accepts arbitrary arguments, but it discards the wrapped function's return value and does not preserve metadata.
- [ ] **```python
from functools import wraps

def log_call(func):
    @wraps
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```** — _incorrecta_: `wraps` must be called as `@wraps(func)`. Applying `@wraps` directly does not configure it with the wrapped function.
- [x] **```python
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(func.__name__)
        return func(*args, **kwargs)
    return wrapper
```** — _correcta_: `wrapper` closes over `func`, forwards positional and keyword arguments, returns the result, and uses `functools.wraps` to copy relevant metadata.

> A function decorator typically returns a wrapper closure that retains access to the original function. `functools.wraps(func)` updates the wrapper's metadata and sets `__wrapped__`, which also helps introspection tools.
>
> Repasar: `functools.wraps`

### ✅ Pregunta 8 — pytest fixtures, mocking, and exception assertions

Which test correctly uses a pytest fixture, replaces `send_email` without calling the real function, and verifies that `register_user` raises `ValueError`?

```python
# app.py
def send_email(address): ...

def register_user(address):
    if "@" not in address:
        raise ValueError("invalid email")
    send_email(address)
```

- [ ] **```python
import app

def test_invalid_email(mocker):
    email_mock = mocker.patch("app.send_email")
    assert app.register_user("invalid") == ValueError
    email_mock.assert_not_called()
```** — _incorrecta_: Raised exceptions are not returned as values. The call exits by raising `ValueError`, so it must be checked with `pytest.raises` or an equivalent exception-catching mechanism.
- [ ] **```python
import pytest
import app

@pytest.fixture
def email_mock(mocker):
    return mocker.patch("app.register_user")

def test_invalid_email(email_mock):
    with pytest.raises(ValueError):
        app.register_user("invalid")
```** — _incorrecta_: This patches `register_user` itself, so the real validation code does not run. A default mock does not raise `ValueError`, causing the exception assertion to fail.
- [ ] **```python
import pytest
import app

@pytest.fixture
def email_mock(mocker):
    return mocker.patch("app.send_email")

def test_invalid_email(email_mock):
    pytest.raises(ValueError, app.register_user("invalid"))
```** — _incorrecta_: `app.register_user("invalid")` is evaluated before `pytest.raises` is called, so the exception escapes immediately. The context-manager form is the clearest correct approach here.
- [x] **```python
import pytest
import app

@pytest.fixture
def email_mock(mocker):
    return mocker.patch("app.send_email")

def test_invalid_email(email_mock):
    with pytest.raises(ValueError, match="invalid email"):
        app.register_user("invalid")
    email_mock.assert_not_called()
```** — _correcta_: The fixture patches the name used by `register_user`, and `pytest.raises` verifies both the exception type and message. The mock assertion also confirms that execution stopped before sending an email.

> A pytest fixture can provide reusable setup such as a mock created by the `pytest-mock` plugin's `mocker` fixture. Patch the symbol where the code under test looks it up, and use `pytest.raises` as a context manager to assert an exception; its `match` argument checks the message using a regular expression.
>
> Repasar: `pytest fixtures, pytest.raises, and mocker.patch`

### ✅ Pregunta 9 — Multiprocessing versus asyncio concurrency use cases

Which choice is generally most appropriate for running several independent, CPU-intensive pure-Python calculations across multiple CPU cores?

- [ ] **Use asyncio because each task automatically runs in a separate operating-system process.** — _incorrecta_: Asyncio tasks normally share one thread and one process; they do not automatically provide multicore parallelism.
- [x] **Use a multiprocessing process pool.** — _correcta_: Separate processes have separate Python interpreters and can execute CPU-bound Python work concurrently on multiple cores.
- [ ] **Use one coroutine and insert await expressions into ordinary arithmetic operations.** — _incorrecta_: Ordinary arithmetic is not awaitable, and adding coroutine syntax does not make CPU work parallel.
- [ ] **Use asyncio tasks without moving the calculations to an executor.** — _incorrecta_: CPU-intensive synchronous calculations block the event loop and prevent other asyncio tasks from progressing.

> Multiprocessing is generally suitable for independent CPU-bound pure-Python work because processes can use multiple cores. Asyncio is primarily designed for cooperatively scheduled I/O-bound operations and requires tasks to yield control with await.
>
> Repasar: `multiprocessing.Pool versus asyncio`

### ✅ Pregunta 10 — NumPy vectorization, broadcasting, dtypes, and performance pitfalls

Consider the following NumPy code:

```python
import numpy as np

matrix = np.ones((1000, 3), dtype=np.float32)
offset = np.array([1, 2, 3], dtype=np.float64)
result = matrix + offset
```

Which statements are correct?

- [x] **`result` has shape `(1000, 3)`.** — _correcta_: Broadcasting conceptually applies the three-element offset to every row without changing the matrix's shape.
- [ ] **Broadcasting first creates a full `(1000, 3)` copy of `offset`, so it always has the same memory cost as manually tiling the array.** — _incorrecta_: Broadcasting generally avoids materializing a tiled input array by using compatible shapes and strides. The output array still requires its own storage.
- [x] **`result` has dtype `float64` because NumPy promotes the mixed `float32` and `float64` operands to a compatible dtype.** — _correcta_: For these two array operands, NumPy's type-promotion rules select `float64`, so the output uses more memory than a `float32` result would.
- [x] **`offset` is broadcast across the 1000 rows because its shape `(3,)` is compatible with the trailing dimension of `matrix`.** — _correcta_: NumPy compares shapes from the right. The dimensions `3` and `3` match, while the missing leading dimension of `offset` behaves like a dimension of size one.
- [ ] **Replacing the expression with nested Python loops is normally faster because it avoids NumPy's broadcasting checks.** — _incorrecta_: For element-wise numerical work, NumPy's compiled loops are normally much faster than per-element Python loops. Temporary arrays and unsuitable dtypes can still create performance or memory costs.

> NumPy broadcasting permits element-wise operations when dimensions are equal or one of them is `1`, with missing leading dimensions treated as `1`. Vectorized operations usually outperform Python loops, but dtype promotion can increase memory use and computation cost, and vectorized expressions may allocate output or temporary arrays.
>
> Repasar: `NumPy broadcasting, dtype promotion, and vectorization`
