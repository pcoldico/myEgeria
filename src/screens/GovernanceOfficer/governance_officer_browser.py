# Python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides the main Screen for the Governance Officer related functions of my_egeria module.


"""
from textual.message import Message
from textual.widgets import DataTable
from textual.widgets import Button, Input, Static, Tree
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from ..base_screen import BaseScreen
from services.governance_officer_service import GovernanceOfficerService
from .add_governance_definition import AddGovernanceDefinitionScreen
from .delete_governance_definition import DeleteGovernanceDefinitionScreen
import asyncio
from textual import on
from utils.config import EgeriaConfig, get_global_config

class GovernanceOfficerBrowserScreen(BaseScreen):
    CSS_PATH = ["../../styles/common.css", "../../styles/governance_officer_browser.css"]

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "back", "Back"),
        ("escape", "back", "Back"),
    ]

    class build_marketplace_tree(Message):
        def __init__(self, selected_guid):
            super().__init__()
            self.selected_guid = selected_guid

    def compose(self):
        yield from super().compose()
        # Simple vertical layout: top (list), search (fixed 5 rows), spacer, bottom (buttons)
        yield Vertical(
            # Top: Title + Table
            ScrollableContainer(
                Vertical(
                    Static("Governance Officer - Governance Definitions", id="go_title"),
                    DataTable(id="governance-officer-table"),
                    id="go_top_content",
                ),
                id="go_top_row",
            ),
            # Search (fixed 5 rows)
            Container(
                Horizontal(
                    Input(placeholder="Search Governance Definitions...", id="gd-search-input"),
                    Button("Search", id="gd-search-button"),
                    id="go_search_row",
                ),
                id="go_search_row_container",
            ),
            # Flexible spacer to push buttons to bottom
            Container(id="go_spacer"),
            # Bottom: action buttons
            Container(
                Horizontal(
                    Button("Select Definition", id="gd-select-button"),
                    Button("Add Governance Definition", id="gd-new-button", disabled=True),
                    Button("Delete Selected Definition", id="gd-delete-button", disabled=True),
                    Button("Refresh", id="refresh-button"),
                    Button("Back", id="back-button"),
                    id="go_action_row",
                ),
                id="go_action_row_container",
            ),
            id="go_v_root",
        )

    async def on_mount(self):
        await super().on_mount()
        # Root fills available space
        vroot = self.query_one("#go_v_root", Vertical)
        vroot.styles.width = "100%"
        vroot.styles.height = "100%"
        vroot.styles.gap = 0

        # Top row: fixed percentage so the table is always visible
        top_row = self.query_one("#go_top_row", ScrollableContainer)
        top_row.styles.width = "100%"
        top_row.styles.height = "60%"  # take the top ~60% of the screen
        top_row.styles.padding = (1, 2)

        top_content = self.query_one("#go_top_content", Vertical)
        top_content.styles.width = "100%"
        top_content.styles.height = "100%"
        top_content.styles.gap = 1

        title = self.query_one("#go_title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Table fills remaining space within top_row
        self.table = self.query_one("#governance-officer-table", DataTable)
        self.table.styles.height = "100%"
        self.table.styles.min_height = 8
        self.table.cursor_type = "row"

        # Search row: fixed ~5 lines height
        sbox = self.query_one("#go_search_row_container", Container)
        sbox.styles.width = "100%"
        sbox.styles.height = 5
        sbox.styles.padding = (0, 1)
        sbox.styles.border = ("solid", "blue")

        srow = self.query_one("#go_search_row", Horizontal)
        srow.styles.align_horizontal = "center"
        srow.styles.gap = 1

        sinput = self.query_one("#gd-search-input", Input)
        sinput.styles.width = "40%"
        sinput.styles.margin = (1, 0, 1, 0)

        sbtn = self.query_one("#gd-search-button", Button)
        sbtn.styles.margin = (1, 0, 1, 0)

        # Spacer flexes to keep buttons at bottom
        spacer = self.query_one("#go_spacer", Container)
        spacer.styles.height = "1fr"

        # Bottom action bar
        abox = self.query_one("#go_action_row_container", Container)
        abox.styles.width = "100%"
        abox.styles.height = "auto"
        abox.styles.padding = (1, 2)

        arow = self.query_one("#go_action_row", Horizontal)
        arow.styles.align_horizontal = "center"
        arow.styles.gap = 1

        # Service and initial load
        self.service = GovernanceOfficerService(config=get_global_config())
        self.table.clear()
        ''' "Governance Definitions",
                           "Display Name",
                           "Qualified Name",",
                           "Category",
                           "Description",
                           "Type Name",
                           "Classifications ([])",
                           "Created By",
                           "Create Time",
                           "Updated By",
                           "Update Time",
                           "Containing Members ([])",
                           "Member Of ([])",
                           "GUID"
                           '''
        self.table.add_columns("GUID", "Display Name", "Category", "Type Name", "Qualified Name", "Description")
        self.table.cursor_type = "row"
        self.last_selected_guid = ""
        await self.load_governance_officer_definitions()
        # Ensure the table has focus for key handling (use Screen API)
        # self.set_focus(self.table)

    # # Defensive row highlight/selection handlers
    # async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
    #     """
    #     Textual may emit RowHighlighted with a None/invalid row_key during updates.
    #     Guard get_row with a try/except to avoid crashes.
    #     """
    #     try:
    #         row_data = self.table.get_row(event.row_key)
    #     except Exception:
    #         return
    #     if row_data:
    #         self.last_selected_guid = row_data[0] or ""

    async def on_data_table_row_selected(self, event: DataTable.RowSelected):
        try:
            row_data = self.table.get_row(event.row_key)
        except Exception:
            return
        if row_data:
            self.last_selected_guid = row_data[0] or ""
            self.app.post_message(self.build_marketplace_tree(self.last_selected_guid))

    @on(Button.Pressed, "#gd-select-button")
    # split out updating and displaying tree and post a message same as above.
    async def handle_select_button(self, event: Button.Pressed) -> None:
        if self.last_selected_guid:
            self.app.post_message(self.build_marketplace_tree(self.last_selected_guid))

    def not_marketplace_guid(self, root_guid: str):
        self.log(f"Found non-marketplace guid of {root_guid}")
        return

    @on(Button.Pressed, "#gd-new-button")
    async def handle_new_button(self, event: Button.Pressed) -> None:
        """Open the Create New Collection screen (non-blocking)."""
        self.log(f"Add definition button pressed, add_open: {self._add_open}")
        if self._add_open:
            return
        self._add_open = True
        await self.app.push_screen(AddGovernanceDefinitionScreen())

    @on(Button.Pressed, "#gd-delete-button")
    async def handle_delete_button(self, event: Button.Pressed) -> None:
        """Open the Create New Collection screen (non-blocking)."""
        self.log(f"Delete definition button pressed, del_open: {self._del_open}")
        if self._del_open:
            return
        self._del_open = True
        await self.app.push_screen(DeleteGovernanceDefinitionScreen(self.last_selected_guid))

    @on(Button.Pressed, "#back-button")
    async def handle_back_button(self, event: Button.Pressed) -> None:
        """Go back to the previous screen."""
        await self.app.pop_screen()

    async def action_back(self) -> None:
        """Hotkeys q / Esc to go back."""
        await self.app.pop_screen()

    async def on_screen_resume(self):
        """
        When returning from the Add or Delete Collection screen, refresh the list and restore focus.
        """
        await asyncio.sleep(0)  # let the screen stack settle
        self._add_open = False  # reset guard on return
        self._del_open = False # reset guard on return

        # Refresh immediately (don't wait for any message)
        try:
            await self._refresh_and_focus()
        except Exception:
            # If anything goes wrong, still try to restore focus so hotkeys and input work
            try:
                self.set_focus(self.table)
            except Exception:
                pass

    # Helper defined BEFORE handlers that call it to avoid "unresolved reference" warnings
    async def _refresh_and_focus(self):
        await self.load_governance_officer_definitions()
        try:
            if self.table.row_count > 0:
                try:
                    self.table.move_cursor(row=0, column=0)
                except Exception:
                    # Fallback removed to avoid Coordinate dependency
                    pass
            self.set_focus(self.table)
        except Exception:
            pass

    @on(AddGovernanceDefinitionScreen.GovernanceDefinitionCreated)
    async def process_definition_created(self, msg: AddGovernanceDefinitionScreen.GovernanceDefinitionCreated):
        """
        Refresh after a collection is created and restore a working input context.
        """
        await self._refresh_and_focus()

    @on(DeleteGovernanceDefinitionScreen.GovernanceDefinitionDeleted)
    async def process_definition_deleted(self, msg: DeleteGovernanceDefinitionScreen.GovernanceDefinitionDeleted):
        """
        Refresh after a collection is created and restore a working input context.
        """
        await self._refresh_and_focus()

    async def action_refresh(self):
        """
        Hotkey handler for 'r' to reload collections.
        """
        await self._refresh_and_focus()

    async def load_governance_officer_definitions(self, search: str = ""):
        self.table.clear()
        try:
            collections = await asyncio.to_thread(self.service.find_governance_definitions, search or "*")
            self.log(f"Found {len(collections)} collections")
            self.log(f"Collections: {collections}")
            if collections:
                for c in collections:
                    guid = c.get("GUID", "")
                    display_name = c.get("Display Name", "")
                    qname = c.get("Qualified Name", "")
                    category = c.get("category", "")
                    desc = c.get("Description", "")
                    type_name = c.get("Type Name", "")
                    self.table.add_row(guid, display_name, category, type_name, qname, desc)
            else:
                self.table.add_row("", "No results found", "", "")
        except Exception as e:
            self.table.add_row("", f"Error: {e}", "", "")
        self.last_selected_guid = ""
        # try:
        #     if self.table.row_count > 0:
        #         try:
        #             self.table.move_cursor(row=0)
        #         except Exception:
        #             pass
        #     self.set_focus(self.table)
        # except Exception:
        #     pass
