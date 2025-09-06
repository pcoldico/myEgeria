# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Governance Officer related functions of my_egeria module.


"""
import asyncio
from typing import Any, Dict, List, Optional
from .base_service import BaseService
from utils.config import EgeriaConfig


class GovernanceOfficerService(BaseService):
    def __init__(self, config: Optional[EgeriaConfig] = None, manager=None):
        super().__init__(config=config, manager=manager)
        self.config = config
        self.definition_guid:str = ""

    def display_glossaries(self, search_string:str = "*") -> List[Dict[str, Any]]:
        """Call the service to get a list of the children of the selected glossary."""
        self.search_string = search_string
        result = self._invoke("display_glossaries", args=(search_string,  self.search_string,), kwargs={"output_format": "DICT"})
        return result

    def get_collections_by_name(self, payload):
        self.payload = payload
        return self.manager.get_collections_by_name(self.payload)

    def create_governance_definition(self, payload):
        # return self.config.manager.create_governance_definition(self.definition_guid)
        pass
    def delete_governance_definition(self, payload):
        # return self.config.manager.delete_governance_definition(self.definition_guid)
        pass
    def update_governance_definition(self, payload):
        # return self.config.manager.update_governance_definition(self.definition_guid)
        pass
    def find_governance_definitions(self, search: str = "*") -> List[Dict[str, Any]]:
        # need those collections with digital product in their collection name
        # move to Dan's new method of handing him a list with what output columns are needed
        output_struct: list = [
            "collection_name",
            "collection_qname",
            "collection_guid",
            "collection_category",
            "initial_classifications",
            "members"]
        res = self._invoke("find_collections", args=(search,), kwargs={"output_format": "DICT"})
        # res = self._invoke("find_collections", args=(search,), kwargs={"output_format": "DICT", "output_format_set" : {output_struct}})
        # return self.config.manager.find_governance_definition(res)
        # return self._ensure_list_like(res, keys=("collection_name", "collection_qname", "collection_guid", "collection_type", "initial_classifications", "members"))
        return res

    # def _ensure_list_like(self, res: Any, keys: tuple[str, ...]) -> List[Dict[str, Any]]:
    #     """
    #     Normalize various possible list-like shapes to a list[dict].
    #     """
    #     if isinstance(res, list):
    #         return res
    #     if isinstance(res, dict):
    #         for k in keys:
    #             v = res.get(k)
    #             if isinstance(v, list):
    #                 return v
    #     # Fallback: wrap non-list truthy into a list
    #     return [] if res is None else ([res] if res else [])

    #example service definition from collection services
    # def list_collections(self, search: str = "*") -> List[Dict[str, Any]]:
    #     """
    #     Use pyegeria.find_collections with a DICT response.
    #     """
    #     res = self._invoke("find_collections", args=(search,), kwargs={"output_format": "DICT"})
    #     return self._ensure_list_like(res, keys=("collections", "elements", "results", "items"))