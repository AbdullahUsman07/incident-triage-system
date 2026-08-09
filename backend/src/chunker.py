import re
import os
from typing import List, Dict, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LogAwareChunker:
    """Unified frontmatter and markdown chunker that handles YAML frontmatter files,
    standard Markdown post-mortems, and multi-line log stack traces"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int =150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.chunk_size,
            chunk_overlap = self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def parse_metadata_and_body(self, content: str, source_name: str)-> Tuple[Dict, List]:
        """Unified parser: handles YAML frontmatter (13 files) AND standard Markdown headers (7 custom files)."""
        metadata = {}
        body_text = content.strip()

        # Step 1: Check for YAML Frontmatter (For the 13 downloaded repo files)
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if fm_match:
            yaml_str = fm_match.group(1)
            body_text = fm_match.group(2).strip()

            for line in yaml_str.splitlines():
                if ':' in line:
                    key, val= line.split(':', 1)
                    key = key.strip().lower()
                    val = val.strip().strip('"\'')
                    if key in ['title', 'company', 'product', 'summary', 'url']:
                        if val:
                            metadata[key] = val

            # Step 2: If no title from frontmatter, check for # Header (For our custom files)
            if "title" not in metadata or not metadata["title"]:
                header_match = re.search(r'^#\s+(.+)$', body_text, re.MULTILINE)
                if header_match:
                    metadata["title"] = header_match.group(1).strip()

            # Step 3: Final Fallback to summary or cleaned filename
            if "title" not in metadata or not metadata["title"]:
                if "summary" in metadata and metadata["summary"]:
                    metadata["title"] = metadata["summary"][:80] + "..."
                else:
                    clean_name = os.path.splitext(source_name)[0]
                    metadata["title"] = re.sub(r'[_\-]+', ' ', clean_name).title()

            metadata["company"] = metadata.get("company", "Infrastructure")
        
            return metadata, body_text

    def chunk_post_mortem(self, content: str, source_name: str) -> List[Dict]:
        """Parses document structure, extracts metadata, and chunks body text recursively"""
        metadata, body_text = self.parse_metadata_and_body(content, source_name)

        #split body text recursively into clean context chunks
        raw_chunks = self.text_splitter.split_text(body_text)

        chunks = []
        for idx, chunk_text in enumerate(raw_chunks):
            cleaned = chunk_text.strip()
            if cleaned:
                chunks.append({
                    "id": f"{os.path.splitext(source_name)[0]}_chunk_{idx}",
                    "text": cleaned,
                    "metadata": {
                        "title": metadata.get("title", "Incident Report"),
                        "company": metadata.get("company", "Infrastructure"),
                        "summary": metadata.get("summary", ""),
                        "source": source_name,
                        "type": "post_mortem",
                        "chunk_index": idx
                    }
                })
        return chunks

    def chunk_raw_log(self, content: str, source_name: str) -> List[Dict]:
        """Groups raw logs while keeping stack traces attached to parent entries."""
        log_boundary_pattern = r'\n(?=\d{4}-\d{2}-\d{2}|\b[A-Z][a-z]{2}\s+\d+|\bTraceback\b|\bException in thread\b)'
        log_entries = re.split(log_boundary_pattern, content)
        
        chunks = []
        for idx, entry in enumerate(log_entries):
            cleaned = entry.strip()
            if cleaned:
                chunks.append({
                    "id": f"{os.path.splitext(source_name)[0]}_log_{idx}",
                    "text": cleaned,
                    "metadata": {
                        "source": source_name,
                        "type": "raw_log",
                        "chunk_index": idx
                    }
                })
        return chunks