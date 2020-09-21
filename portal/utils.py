from functools import total_ordering, wraps
from typing import Any, Callable
import lazy_object_proxy
import operator
from django.apps import apps

def lazy_config(key: str) -> Callable[[str], Any]:
    """ Lazily get a config value from constance. Useful to bind constance
    configs to other global settings to make them available to third-party
    apps that are not aware of constance.
    """
    from django.conf import settings

    def _get_config(key: str) -> Any:
        from constance import config  # noqa
        return getattr(config, key)
    
    
    
    # The type is guessed from the default value to improve lazy()'s behaviour
    var_type = type(settings.CONSTANCE_CONFIG[key][0])
    return lazy(_get_config, var_type)(key)



class Promise:
    """
    Base class for the proxy class created in the closure of the lazy function.
    It's used to recognize promises in code.
    """
    pass


def lazy(func, type_class):
    """
    Turn any callable into a lazy evaluated callable. result classes or types
    is required -- at least one is needed so that the automatic forcing of
    the lazy evaluation code is triggered. Results are not memoized; the
    function is evaluated on every access.
    """

    @total_ordering
    class __proxy__(Promise):
        """
        Encapsulate a function call and act as a proxy for methods that are
        called on the result of that function. The function is not evaluated
        until one of the methods on the result is called.
        """
        __prepared = False

        def __init__(self, args, kw):
            self.__args = args
            self.__kw = kw
            if not self.__prepared:
                self.__prepare_class__()
            self.__class__.__prepared = True
        
        def __getattribute__(self, name):
            if name in ['__class__', '__name__', '__qualname__'] and super(__proxy__, self).__getattribute__('_proxy____prepared') :
                res = func(super(__proxy__, self).__getattribute__('_proxy____args')[0])
                val = getattr(res, name)
                return val
            else:
                return super(__proxy__, self).__getattribute__(name)

        def __reduce__(self):
            return (
                _lazy_proxy_unpickle,
                (func, self.__args, self.__kw) + type_class
            )

        def __repr__(self):
            return repr(self.__cast())

        @classmethod
        def __prepare_class__(cls):
 
            for type_ in type_class.mro():
                for method_name in type_.__dict__:
                    # All __promise__ return the same wrapper method, they
                    # look up the correct implementation when called.
                    if hasattr(cls, method_name):
                        continue
                    meth = cls.__promise__(method_name)
                    setattr(cls, method_name, meth)
            cls._delegate_bytes = type_class is bytes
            cls._delegate_text = type_class is str
            assert not (cls._delegate_bytes and cls._delegate_text), (
                "Cannot call lazy() with both bytes and text return types.")
            if cls._delegate_text:
                cls.__str__ = cls.__text_cast
            elif cls._delegate_bytes:
                cls.__bytes__ = cls.__bytes_cast

        @classmethod
        def __promise__(cls, method_name):
            # Builds a wrapper around some magic method
            def __wrapper__(self, *args, **kw):
                # Automatically triggers the evaluation of a lazy value and
                # applies the given magic method of the result type.
                res = func(*self.__args, **self.__kw)
                return getattr(res, method_name)(*args, **kw)
            return __wrapper__

        def __text_cast(self):
            return func(*self.__args, **self.__kw)

        def __bytes_cast(self):
            return bytes(func(*self.__args, **self.__kw))

        def __bytes_cast_encoded(self):
            return func(*self.__args, **self.__kw).encode()

        def __cast(self):
            if self._delegate_bytes:
                return self.__bytes_cast()
            elif self._delegate_text:
                return self.__text_cast()
            else:
                return func(*self.__args, **self.__kw)

        def __str__(self):
            # object defines __str__(), so __prepare_class__() won't overload
            # a __str__() method from the proxied class.
            return str(self.__cast())

        def __eq__(self, other):
            if isinstance(other, Promise):
                other = other.__cast()
            return self.__cast() == other

        def __lt__(self, other):
            if isinstance(other, Promise):
                other = other.__cast()
            return self.__cast() < other

        def __hash__(self):
            return hash(self.__cast())

        def __mod__(self, rhs):
            if self._delegate_text:
                return str(self) % rhs
            return self.__cast() % rhs

        def __deepcopy__(self, memo):
            # Instances of this class are effectively immutable. It's just a
            # collection of functions. So we don't need to do anything
            # complicated for copying.
            memo[id(self)] = self
            return self

    @wraps(func)
    def __wrapper__(*args, **kw):
        # Creates the proxy object, instead of the actual value.
        return __proxy__(args, kw)

    return __wrapper__


def _lazy_proxy_unpickle(func, args, kwargs, *resultclasses):
    return lazy(func, *resultclasses)(*args, **kwargs)