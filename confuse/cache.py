from typing import Dict, List

from . import templates
from .core import ROOT_NAME, Configuration, ConfigView, RootView, Subview


class CachedHandle(object):
    """Handle for a cached value computed by applying a template on the view.
    """
    # some sentinel objects
    _INVALID = object()
    _MISSING = object()

    def __init__(self, view: ConfigView, template=templates.REQUIRED) -> None:
        self.value = self._INVALID
        self.view = view
        self.template = template

    def get(self):
        """Retreive the cached value from the handle.

        Will re-compute the value using `view.get(template)` if it has been
        invalidated.

        May raise a `NotFoundError` if the underlying view has been
        invalidated.
        """
        if self.value is self._MISSING:
            # will raise a NotFoundError if no default value was provided
            self.value = templates.as_template(self.template).get_default_value()
        if self.value is self._INVALID:
            self.value = self.view.get(self.template)
        return self.value

    def _invalidate(self):
        """Invalidate the cached value, will be repopulated on next `get()`.
        """
        self.value = self._INVALID

    def _set_view_missing(self):
        """Invalidate the handle, will raise `NotFoundError` on `get()`.
        """
        self.value = self._MISSING


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
        for handle in subview.handles:
            handle._invalidate()
        subview._invalidate_descendants(value)
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

    def _invalidate_descendants(self, new_val):
        """Invalidate the handles for (sub)keys that were updated and
        set_view_missing for keys that are absent in new_val.
        """
        for subview in self.subviews.values():
            try:
                subval = new_val[subview.key]
            except (KeyError, IndexError, TypeError):
                # the old key doesn't exist in the new value anymore- 
                # set view as missing for the handles.
                for handle in subview.handles:
                    handle._set_view_missing()
                subval = None
            else:
                # old key is present, possibly with a new value- invalidate.
                for handle in subview.handles:
                    handle._invalidate()
            subview._invalidate_descendants(subval)

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
