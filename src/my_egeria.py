# Python

"""

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

"""

import os

# Set safe defaults BEFORE importing anything that might import pyegeria
os.environ.setdefault("EGERIA_USER", "erinoverview")
os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
os.environ.setdefault("EGERIA_PLATFORM_URL", "https://localhost:9443")

from textual.app import App, ComposeResult
from textual.widgets import Footer
from screens.login_screen import LoginScreen
from screens.main_menu import MainMenuScreen
from screens.glossary.glossary_browser import GlossaryBrowserScreen
from screens.collections.collection_browser import CollectionBrowserScreen
from screens.collections.collection_members_screen import CollectionMemberScreen
from screens.collections.collection_details import CollectionDetailsScreen
from screens.collections.add_collection import AddCollectionScreen
from screens.collections.delete_collection import DeleteCollectionScreen
from screens.glossary.glossary_list_screen import GlossaryListScreen
from screens.glossary.term_details import TermDetailsScreen
from screens.glossary.term_list_screen import TermListScreen
from screens.GovernanceOfficer.governance_officer_browser import GovernanceOfficerBrowserScreen
from screens.GovernanceOfficer.add_governance_definition import AddGovernanceDefinitionScreen
from screens.GovernanceOfficer.delete_governance_definition import DeleteGovernanceDefinitionScreen
from screens.GovernanceOfficer.marketplace_tree import MarketPlaceTree
from screens.ProductManager.product_manager_browser import ProductManagerBrowser
from utils.egeria_client import close_all_managers
from screens.splash_screen import SplashScreen  # your existing splash screen
from services.term_service import get_terms_for_glossary

class MyEgeria(App):
    """Main app class of my_egeria."""
    CSS_PATH = ["./styles/common.css"]

    # Only register screens that do NOT need constructor arguments here
    SCREENS = {
        "splash": SplashScreen,
        "login": LoginScreen,
        "main_menu": MainMenuScreen,
        "glossary_browser": GlossaryBrowserScreen,
        "glossary_list_screen": GlossaryListScreen,
        "term_details": TermDetailsScreen,
        "term_list_screen": TermListScreen,
        "collection_details": CollectionDetailsScreen,
        "add_collection": AddCollectionScreen,
        "collection_members": CollectionMemberScreen,
        "collection_browser": CollectionBrowserScreen,
        "delete_collection": DeleteCollectionScreen,
        "governance_officer_browser": GovernanceOfficerBrowserScreen,
        "add_governance_definition": AddGovernanceDefinitionScreen,
        "delete_governance_definition": DeleteGovernanceDefinitionScreen,
        "marketplace_tree": MarketPlaceTree,
        "product_manager_browser": ProductManagerBrowser,
        # Details screens require arguments; push them with instances at runtime
        # "term_details": lambda: TermDetailsScreen("<guid>"),
        # "collection_details": lambda: CollectionDetailsScreen("<guid>"),
        # "add_collection": AddCollectionScreen,   # can be registered or pushed directly
    }

    def compose(self) -> ComposeResult:
        yield Footer()

    async def on_mount(self) -> None:
        # Start at splash
        await self.push_screen("splash")

    # Optional: handle a "login successful" message from LoginScreen if you use one
    # Provide a generic hook to go to main menu after login
    async def on_login_screen_login_success(self, _message: object) -> None:
        await self.push_screen("main_menu")

    # Convenience helpers for pushing details screens
    async def show_term_details(self, term_guid: str):
        await self.push_screen(TermDetailsScreen(term_guid))

    async def show_term_list(self, glossary_name: str):
        await self.push_screen(TermListScreen(glossary_name = glossary_name))

    async def show_collection_details(self, collection_guid: str):
        await self.push_screen(CollectionDetailsScreen(collection_guid))

    async def show_add_collection(self):
        await self.push_screen(AddCollectionScreen())

    async def show_governance_officer_browser(self):
        await self.push_screen(GovernanceOfficerBrowserScreen())

    async def on_shutdown(self) -> None:
        try:
            close_all_managers()
        except Exception:
            pass


if __name__ == "__main__":
    # Optionally preload env defaults for demo
    os.environ.setdefault("EGERIA_PLATFORM_URL", "https://localhost:9443")
    os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
    MyEgeria().run()
