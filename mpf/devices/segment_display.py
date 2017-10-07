"""Physical segment displays."""
from collections import namedtuple
from operator import attrgetter
from typing import List

from mpf.core.device_monitor import DeviceMonitor
from mpf.core.placeholder_manager import TextTemplate
from mpf.core.system_wide_device import SystemWideDevice

MYPY = False
if MYPY:   # pragma: no cover
    from mpf.platforms.interfaces.segment_display_platform_interface import SegmentDisplayPlatformInterface

TextStack = namedtuple("TextStack", ["text", "priority", "key"])


@DeviceMonitor("text")
class SegmentDisplay(SystemWideDevice):

    """A physical segment display in a pinball machine."""

    config_section = 'segment_displays'
    collection = 'segment_displays'
    class_label = 'segment_display'

    def __init__(self, machine, name: str) -> None:
        """Initialise segment display device."""
        super().__init__(machine, name)
        self.hw_display = None              # type: SegmentDisplayPlatformInterface
        self.platform = None
        self._text_stack = []               # type: List[TextStack]
        self._current_placeholder = None    # type: TextTemplate
        self.text = ""                      # type: str
        self.flashing = False               # type: bool

    def _initialize(self):
        """Initialise display."""
        # load platform
        self.platform = self.machine.get_platform_sections('segment_displays', self.config['platform'])
        # configure hardware
        self.hw_display = self.platform.configure_segment_display(self.config['number'])

    def add_text(self, text: str, priority: int = 0, key: str = None) -> None:
        """Add text to display stack."""
        self._text_stack.append(TextStack(text, priority, key))
        self._update_stack()

    def set_flashing(self, flashing: bool):
        """Enable/Disable flashing."""
        self.flashing = flashing
        # invalidate text to force an update
        self.text = None
        self._update_display()

    def remove_text_by_key(self, key: str):
        """Remove entry from text stack."""
        self._text_stack[:] = [x for x in self._text_stack if x.key != key]
        self._update_stack()

    def _update_stack(self) -> None:
        """Sort stack and show top entry on display."""
        # do nothing if stack is emtpy. set display empty
        if not self._text_stack:
            self.hw_display.set_text("", flashing=False)
            if self._current_placeholder:
                self.text = ""
                self._current_placeholder.stop_monitor()
                self._current_placeholder = None
            return

        # sort stack by priority
        self._text_stack.sort(key=attrgetter("priority"), reverse=True)
        # get top entry
        top_entry = self._text_stack[0]

        if self._current_placeholder:
            self._current_placeholder.stop_monitor()

        self._current_placeholder = TextTemplate(self.machine, top_entry.text)
        self._current_placeholder.monitor_changes(self._update_display)
        self._update_display()

    def _update_display(self) -> None:
        """Update display to current text."""
        if not self._current_placeholder:
            new_text = ""
        else:
            new_text = self._current_placeholder.evaluate()

        # set text to display if it changed
        if new_text != self.text:
            self.text = new_text
            self.hw_display.set_text(self.text, flashing=self.flashing)
