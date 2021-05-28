"""Plugin additions to the Nautobot navigation menu."""

from nautobot.extras.plugins import PluginMenuItem, PluginMenuButton
from nautobot.utilities.choices import ButtonColorChoices


menu_items = (
    PluginMenuItem(
        link="plugins:nautobot_ssot:sync_list",
        link_text="History",
        permissions=["nautobot_ssot.view_sync"],
    ),
    PluginMenuItem(
        link="plugins:nautobot_ssot:synclogentry_list",
        link_text="Logs",
        permissions=["nautobot_ssot.view_synclogentry"],
    ),
)