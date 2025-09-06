# Python

"""

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

"""

import os

from textual.containers import Container

from .services.glossary_service import GlossaryService
from utils.config import get_global_config
from governance_officer_service import GovernanceOfficerService

# Set safe defaults BEFORE importing anything that might import pyegeria
os.environ.setdefault("EGERIA_USER", "erinoverview")
os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
os.environ.setdefault("EGERIA_PLATFORM_URL", "https://localhost:9443")

from textual.app import App, ComposeResult
from textual.widgets import Footer, Tree
from screens.login_screen import LoginScreen
from screens.main_menu import MainMenuScreen
from screens.glossary.glossary_browser import GlossaryBrowserScreen
from screens.a_collections.collection_browser import CollectionBrowserScreen
from screens.a_collections.collection_members_screen import CollectionMemberScreen
from screens.a_collections.collection_details import CollectionDetailsScreen
from screens.a_collections.add_collection import AddCollectionScreen
from screens.a_collections.delete_collection import DeleteCollectionScreen
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
# from pyegeria import EgeriaTech


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

    # handle a message requesting login to egeria to verify user credentials
    async def on_login_screen_egeria_login_requested(self,payload) -> bool:
        from pyegeria import EgeriaTech
        username = payload["username"]
        password = payload["password"]
        platform_url = payload["platform_url"]
        view_server = payload["view_server"]
        try:
            client = EgeriaTech(
                user_id=username,
                user_pwd=password,
                platform_url=platform_url,
                view_server=view_server
            )
            tokendata = client.create_egeria_bearer_token(
                user_id=username,
                user_pwd=password)
            client.close_session()
            ok = True
        except Exception as e:
            self.log(f"Log in to egeria error: {e}")
            ok = False
        finally:
            return ok

    # Handle a "login successful" message from LoginScreen
    # Provide a generic hook to go to main menu after login
    async def on_login_screen_login_success(self, _message: object) -> None:
        await self.push_screen("main_menu")

    # Convenience helpers for pushing details screens
    async def _show_term_details(self, term_guid: str):
        await self.push_screen(TermDetailsScreen(term_guid))

    async def _show_term_list(self, glossary_name: str):
        await self.push_screen(TermListScreen(glossary_name = glossary_name))

    async def _show_collection_details(self, collection_guid: str):
        await self.push_screen(CollectionDetailsScreen(collection_guid))

    async def _show_add_collection(self):
        await self.push_screen(AddCollectionScreen())

    async def _show_governance_officer_browser(self):
        await self.push_screen(GovernanceOfficerBrowserScreen())

    async def on_governance_officer_browser_screen_show_marketplace_tree(self, tree_id):
        #concatenate # to front of tree_id for self.query_one funtion
        await self.push_screen(MarketPlaceTree(tree_id))

    async def on_governance_officer_browser_build_marketplace_tree(self, collection_guid) -> str:
        """ Build a tree of the marketplace folders and members for a governance collection
            in;put is the guid of the collection selected
            return status """
        self.collection_guid = collection_guid
        self.service = GovernanceOfficerService(config=get_global_config())
        if self.collection_guid:
            """Find the Root(s) for that selected type and display a tree of them to select from,
                for further supported governance actions"""
            root = await self.service.get_collections_by_name(self.collection_guid)
            root_guid = root.get("GUID", None)
            root_name = root.get("display_name", None)
            root_qname = root.get("qualified_name", None)
            root_desc = root.get("description", None)
            root_type = root.get("category", None)
            root_classifications = root.get("classifications", None)
            root_members = root.get("members", None)
            if ("marketplace" in root_name.lower()) or ("marketplace" in root_qname.lower()):
                marketplace_guid = root_guid
                self.log(f"Found marketplace guid of {marketplace_guid}, {root_name}")
                #set up Textual Tree structure for display
                market_tree: Tree =Tree(root_name, data=root_guid, id="marketplace_tree")
                # now query for all the collection members, probably 2 levels for initial display
                marketplace_folders = await self.service.get_collections_by_name(marketplace_guid)
                if marketplace_folders:
                    for folder in marketplace_folders:
                        folder_guid = folder.get("GUID", None)
                        folder_name = folder.get("display_name", None)
                        folder_qname = folder.get("qualified_name", None)
                        folder_desc = folder.get("description", None)
                        folder_type = folder.get("category", None)
                        folder_classifications = folder.get("classifications", None)
                        folder_members = folder.get("members", None)
                        market_tree.root.expand()
                        if "Folder" in folder_qname:
                            self.log(f"Found folder guid of {folder_guid}, {folder_name}")
                            entries = market_tree.root.add(folder_name, data= folder_guid, expasnd = True)
                            if folder_members:
                                for member in folder_members:
                                    member_guid = member.get("GUID", None)
                                    member_name = member.get("title", None)

                                    #process level 3
                                    entries.add(member_name, member_guid, expand = True)
                                    continue
                            else:
                                entries.add(f"No members found for {folder_name}")
                                continue
                        else:
                            market_tree.root.add(folder_name, data = folder_guid, expand = True)
                else:
                    # marketplace is empty
                    self.log(f"Marketplace guid {marketplace_guid} is empty")
                    self.spacer_container = self.query_one("#go_spacer", Container)
                    market_tree.root.add(f"Marketplace {marketplace_guid} is empty")
                    return "Marketplace is empty"
            else:
                return "No marketplace found"
        else:
            # display error and stay on base screen until a different action is selected
            # or a selection is made
            self.log("No definition selected")
            # await self._refresh_and_focus()
            return "No selection made"
        #
        # self.post_message(self.show_marketplace_tree("marketplace_tree"))
        return "Success"

    async def on_glossery_browser_screen_build_glossary_tree(self, glossary_name: str) -> str:
        """ Build a tree of the glossary folders and members for a glossary
            input is the name of the glossary selected
            return status """
        self.glossary_name = glossary_name
        self.service = GlossaryService(config=get_global_config())
        if self.glossary_name:
            """Find the Root(s) for that selected type and display a tree of them to select from,
                for further supported governance actions"""
            root = await self.service.display_glossaries(search_string=self.glossary_name)
            root_guid = root.get("GUID", None)
            root_name = root.get("display_name", None)
            root_qname = root.get("qualified_name", None)
            root_desc = root.get("description", None)
            root_type = root.get("category", None)
            root_classifications = root.get("classifications", None)
            root_members = root.get("members", None)
            if ("marketplace" in root_name.lower()) or ("marketplace" in root_qname.lower()):
                marketplace_guid = root_guid
                self.log(f"Found marketplace guid of {marketplace_guid}, {root_name}")
                # set up Textual Tree structure for display
                market_tree: Tree = Tree(root_name, data=root_guid, id="marketplace_tree")
                # now query for all the collection members, probably 2 levels for initial display
                marketplace_folders = await self.service.get_collections_by_name(marketplace_guid)
                if marketplace_folders:
                    for folder in marketplace_folders:
                        folder_guid = folder.get("GUID", None)
                        folder_name = folder.get("display_name", None)
                        folder_qname = folder.get("qualified_name", None)
                        folder_desc = folder.get("description", None)
                        folder_type = folder.get("category", None)
                        folder_classifications = folder.get("classifications", None)
                        folder_members = folder.get("members", None)
                        market_tree.root.expand()
                        if "Folder" in folder_qname:
                            self.log(f"Found folder guid of {folder_guid}, {folder_name}")
                            entries = market_tree.root.add(folder_name, data=folder_guid, expasnd=True)
                            if folder_members:
                                for member in folder_members:
                                    member_guid = member.get("GUID", None)
                                    member_name = member.get("title", None)

                                    # process level 3
                                    entries.add(member_name, member_guid, expand=True)
                                    continue
                            else:
                                entries.add(f"No members found for {folder_name}")
                                continue
                        else:
                            market_tree.root.add(folder_name, data=folder_guid, expand=True)
                else:
                    # marketplace is empty
                    self.log(f"Marketplace guid {marketplace_guid} is empty")
                    self.spacer_container = self.query_one("#go_spacer", Container)
                    market_tree.root.add(f"Marketplace {marketplace_guid} is empty")
                    return "Marketplace is empty"
            else:
                return "No marketplace found"
        else:
            # display error and stay on base screen until a different action is selected
            # or a selection is made
            self.log("No definition selected")
            # await self._refresh_and_focus()
            return "No selection made"
            #
            # self.post_message(self.show_marketplace_tree("marketplace_tree"))
        return "Success"


    async def on_shutdown(self) -> None:
        try:
            close_all_managers()
        except Exception:
            pass

if __name__ == "__main__":
    # Optionally preload env defaults for demo
    os.environ.setdefault("EGERIA_PLATFORM_URL", "https://localhost:9443")
    os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
    os.environ.setdefault("EGERIA_USER", "erinoverview")
    os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
    MyEgeria().run()
