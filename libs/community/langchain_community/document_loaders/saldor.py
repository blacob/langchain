from typing import Iterator, Literal, Optional

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_core.utils import get_from_env
from pydantic import BaseModel
from typing import List


class SaldorLoader(BaseLoader):
    """Load web pages as Documents using Saldor.

    Must have the Python package `saldor-client` installed and a Saldor API key.
    See https://saldor.com for more.
    """

    def __init__(
        self,
        url: str,
        *,
        api_key: Optional[str] = None,
        goal: str = "",
        max_pages: Optional[int] = None,
        max_depth: Optional[int] = None,
        render: Optional[bool] = None,
        children_paths: Optional[List[str]] = None,
        json_schema: Optional[BaseModel] = None,
    ):
        """Initialize with API key and URL.

        Args:
            url: The URL to be processed.
            api_key: The Saldor API key. If not specified, will be read from env
            var `SALDOR_API_KEY`.
            params: Additional parameters for the Saldor API.
        """
        if params is None:
            params = {
                "return_format": "markdown",
                "metadata": True,
            }  # Using the metadata param slightly slows down the output

        try:
            from saldor import SaldorClient
        except ImportError:
            raise ImportError(
                "`saldor-scraper` package not found, please run `pip install saldor`"
            )
            
        # Use the environment variable if the API key isn't provided
        api_key = api_key or get_from_env("api_key", "SALDOR_API_KEY")
        self.saldor_client = SaldorClient(api_key=api_key)
        self.url = url
        self.goal = goal 
        self.max_pages = max_pages 
        self.max_depth = max_depth
        self.render = render 
        self.children_paths = children_paths
        self.json_schema = json_schema

    def lazy_load(self) -> Iterator[Document]:
        """Load documents."""
        try:
            response = self.saldor_client.crawl(self.url, goal=self.goal, max_pages=self.max_pages, 
                                                max_depth=self.max_depth, render=self.render, 
                                                json_schema=self.json_schema, children_paths=self.children_paths)
            
            if response.errors:
                raise Exception(f"Errors occurred during crawling: {response.errors}")
            
            saldor_docs = response.documents or []
                
            for doc in saldor_docs:
                # Ensure page_content is also not None
                page_content = doc.get("content", "")
                # Ensure metadata is also not None and add the URL
                metadata = doc.get("metadata", {})
                metadata["url"] = doc.get("url", "")

                if page_content:
                    yield Document(page_content=page_content, metadata=metadata)
        except Exception as e:
            raise RuntimeError(f"Failed to load documents: {e}")

