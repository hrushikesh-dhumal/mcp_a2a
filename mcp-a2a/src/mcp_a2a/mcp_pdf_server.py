# pdf_server.py
# This script sets up a FastMCP server that can parse PDF files and return their text content.
# It uses the PyPDFLoader from LangChain to load the PDF and extract text from it.
from mcp.server.fastmcp import FastMCP
# from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader

# Initialize the MCP server
mcp = FastMCP("pdf-parser", description="PDF parsing tool", port=8080)

@mcp.tool()
def parse_pdf(path: str) -> str:
    """
    Load a PDF from the given file path and return its full text.
    """
    loader = PyPDFLoader(path)
    docs = loader.load()
    # Concatenate text from all pages
    return "\n\n".join(doc.page_content for doc in docs)

if __name__ == "__main__":
    # Run server over standard I/O (stdio) transport
    mcp.run(transport="stdio")
