
"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides the main Screen for the Governance Officer related functions of my_egeria module.


"""
from ..base_screen import BaseScreen
from textual.widgets import Button, Tree, Static, Input
from textual import on
from textual.containers import Container, Horizontal

class MarketPlaceTree(BaseScreen):
    """Screen showing a Data Product MarketPlace in a Tree structure"""

    CSS_PATH = ["../../styles/common.css", "../../styles/governance_officer_browser.css"]

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "back", "Back"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self):
        self.m_tree = self.query_one("marketplace_tree", Tree)
        yield from super().compose()
        # Simple vertical layout: top (list), search (fixed 5 rows), spacer, bottom (buttons)
        Static("Governance Officer - Data Product MarketPlace", id="go_title"),
        yield Container(self.m_tree, id="marketplace_tree_container")
        # Search (fixed 5 rows)
        Container(
            Horizontal(
                Input(placeholder="Search Tree...", id="pt-search-input", disabled=True),
                Button("Search", id="pt-search-button", disabled=True),
                id="mt_search_row",
            ),
            id="mt_search_row_container",
        ),
        # Flexible spacer to push buttons to bottom
        Container(id="mt_spacer"),
        # Bottom: action buttons
        Container(
            Horizontal(
                Button("Select Definition", id="pt-select-button"),
                Button("Back", id="back-button"),
                id="mt_action_row",
            ),
            id="mt_action_row_container",
        ),
        id = "mt_root",

    def action_refresh(self, event):
        self.market_tree.refresh(layout=True)

    def action_back(self) -> None:
        self.app.pop_screen()

    @on (Button.Pressed, "#mt-select-button")
    def process_select_button(self, event: Button.Pressed) -> None:
        # check which tree element selected and then take that element and expand ina new tree
        self.log(f"Processing Selection: {self.market_tree_node_selected} of {self.market_tree}")
        # self.market_tree.expand(self.market_tree_node_selected)
        self.app.push_screen("collection_members_screen", self.market_tree_node_selected)

    def on_tree_node_selected(self, market_tree, market_tree_node_selected):
        self.market_tree = market_tree
        self.market_tree_node_selected = market_tree_node_selected
        self.log(f"Selected node: {market_tree_node_selected} of {market_tree}")
        # self.market_tree.expand(market_tree_node_selected)

