from typing import Iterator, Literal, Optional

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_core.utils import get_from_env


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
        params: Optional[dict] = None,
    ):
        """Initialize with API key and URL.

        Args:
            url: The URL to be processed.
            api_key: The Saldor API key. If not specified, will be read from env
            var `SALDOR_API_KEY`.
            mode: The mode to run the loader in. Default is "scrape".
                 Options include "scrape" (single page) and "crawl" (with deeper
                 crawling following subpages).
            params: Additional parameters for the Saldor API.
        """
        if params is None:
            params = {
                "return_format": "markdown",
                "metadata": True,
            }  # Using the metadata param slightly slows down the output

        try:
            from saldor import SaldorScraper
        except ImportError:
            raise ImportError(
                "`saldor-scraper` package not found, please run `pip install saldor`"
            )
            
        # Use the environment variable if the API key isn't provided
        api_key = api_key or get_from_env("api_key", "SALDOR_API_KEY")
        self.saldor_scraper = SaldorScraper(api_key=api_key)
        self.url = url
        self.params = params

    def lazy_load(self) -> Iterator[Document]:
        """Load documents."""
        saldor_docs = []

        if self.mode == "scrape":
            # Scrape some url, which may scrape multiple pages depending on params
            response = self.saldor_scraper.scrape_url(self.url, params=self.params)
            if response:
                saldor_docs.extend(response)
                
        for doc in saldor_docs:

            # Ensure page_content is also not None
            page_content = doc.get("content", "")

            # Ensure metadata is also not None
            metadata = doc.get("metadata", {})

            if page_content is not None:
                yield Document(page_content=page_content, metadata=metadata)
    
