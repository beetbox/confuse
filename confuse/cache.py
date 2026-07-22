from typing import Dict, List

from . import templates
from .core import ROOT_NAME, Configuration, ConfigView, RootView, Subview


class CachedHandle(object):
    """Handle for a cached value computed by applying a template on the view.
    """
    _INVALID = object()
    """Sentinel object to denote that the cached value is out-of-date."""

    def __init__(self, view: ConfigView, template=templates.REQUIRED) -> None:
        self.value = self._INVALID
        self.view = view
        self.template = template

    def get(self):
        """Retreive the cached value from the handle.

        Will re-compute the value using `view.get(template)` if it has been
        invalidated.

        May raise a `NotFoundError` if the underlying view is missing.
        """
        if self.value is self._INVALID:
            self.value = self.view.get(self.template)
        return self.value

    def _invalidate(self):
        """Invalidate the cached value, will be repopulated on next `get()`.
        """
        self.value = self._INVALID


class CachedViewMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # keep track of all the handles from this view
        self.handles: List[CachedHandle] = []
        # need to cache the subviews to be able to access their handles
        self.subviews: Dict[str, CachedConfigView] = {}

    def __getitem__(self, key) -> "CachedConfigView":
        try:
            return self.subviews[key]
        except KeyError:
            val = CachedConfigView(self, key)
            self.subviews[key] = val
            return val

    def __setitem__(self, key, value):
        subview: CachedConfigView = self[key]
        # invalidate the existing handles up and down the view tree
        subview._invalidate_descendants()
        self._invalidate_ancestors()

        return super().__setitem__(key, value)

    def _invalidate_ancestors(self):
        """Invalidate the cached handles for all the views up the chain.

        This is to ensure that they aren't referring to stale values.
        """
        parent = self
        while True:
            for handle in parent.handles:
                handle._invalidate()
            if parent.name == ROOT_NAME:
                break
            parent = parent.parent

    def _invalidate_descendants(self):
        """Invalidate the handles for (sub)keys that were updated.
        """
        for handle in self.handles:
            handle._invalidate()
        for subview in self.subviews.values():
            subview._invalidate_descendants()

    def get_handle(self, template=templates.REQUIRED):
        """Retreive a `CachedHandle` for the current view and template.
        """
        handle = CachedHandle(self, template)
        self.handles.append(handle)
        return handle


class CachedConfigView(CachedViewMixin, Subview):
    pass


class CachedRootView(CachedViewMixin, RootView):
    pass


class CachedConfiguration(CachedViewMixin, Configuration):
    pass
