"""
File Parsing Utility
Supports comprehensive text and data extraction from:
- Documents: PDF, DOCX, DOC, TXT, MD, RTF
- Spreadsheets & Tabular: XLSX, XLS, CSV, TSV
- Structured Data & Markup: JSON, JSONL, XML, HTML, YAML
- Multimodal Images: PNG, JPG, JPEG, WEBP, BMP, TIFF, SVG (LLM Vision + Metadata fallback)
- Code & Scripts: PY, JS, TS, SQL, SH
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger('lokantra.file_parser')


def _read_text_with_fallback(file_path: str) -> str:
    """
    Read text file with fallback encoding detection if UTF-8 fails.
    
    Multi-level fallback strategy:
    1. Try UTF-8 decoding
    2. Use charset_normalizer to detect encoding
    3. Fallback to chardet to detect encoding
    4. Ultimate fallback using UTF-8 + errors='replace'
    """
    data = Path(file_path).read_bytes()
    
    # 1. First try UTF-8
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        pass
    
    # 2. Try charset_normalizer
    encoding = None
    try:
        from charset_normalizer import from_bytes
        best = from_bytes(data).best()
        if best and best.encoding:
            encoding = best.encoding
    except Exception:
        pass
    
    # 3. Fallback to chardet
    if not encoding:
        try:
            import chardet
            result = chardet.detect(data)
            encoding = result.get('encoding') if result else None
        except Exception:
            pass
    
    # 4. Ultimate fallback: UTF-8 with replace
    if not encoding:
        encoding = 'utf-8'
    
    return data.decode(encoding, errors='replace')


class FileParser:
    """Universal Multi-Format File Parser for Lokantra Knowledge Ingestion"""
    
    SUPPORTED_EXTENSIONS = {
        # Documents
        '.pdf', '.docx', '.doc', '.txt', '.md', '.markdown', '.rtf',
        # Spreadsheets & Tabular
        '.xlsx', '.xls', '.csv', '.tsv',
        # Structured Data & Markup
        '.json', '.jsonl', '.xml', '.html', '.htm', '.yaml', '.yml',
        # Images (Multimodal Vision / OCR / Metadata)
        '.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.svg',
        # Code & Scripts
        '.py', '.js', '.ts', '.sql', '.sh'
    }
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Check if file format is supported"""
        suffix = Path(file_path).suffix.lower()
        return suffix in cls.SUPPORTED_EXTENSIONS
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """
        Extract text from file based on extension
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text content
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format: {suffix}")
        
        # 1. Documents
        if suffix == '.pdf':
            return cls._extract_from_pdf(file_path)
        elif suffix in {'.docx', '.doc'}:
            return cls._extract_from_docx(file_path)
        elif suffix in {'.md', '.markdown', '.txt', '.rtf', '.py', '.js', '.ts', '.sql', '.sh', '.yaml', '.yml'}:
            return cls._extract_from_txt(file_path)
        
        # 2. Spreadsheets & Tabular
        elif suffix in {'.xlsx', '.xls'}:
            return cls._extract_from_xlsx(file_path)
        elif suffix in {'.csv', '.tsv'}:
            return cls._extract_from_csv(file_path)
        
        # 3. Structured Data & Markup
        elif suffix in {'.json', '.jsonl'}:
            return cls._extract_from_json(file_path)
        elif suffix in {'.html', '.htm', '.xml'}:
            return cls._extract_from_html(file_path)
        
        # 4. Images
        elif suffix in {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.svg'}:
            return cls._extract_from_image(file_path)
        
        # Fallback to text reading
        return _read_text_with_fallback(file_path)
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF is required: pip install PyMuPDF")
        
        text_parts = []
        with fitz.open(file_path) as doc:
            for page in doc:
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text and tables from Word documents (.docx/.doc)"""
        try:
            import docx
            doc = docx.Document(file_path)
            parts = []
            
            for p in doc.paragraphs:
                text = p.text.strip()
                if text:
                    parts.append(text)
            
            for table in doc.tables:
                table_lines = []
                for row in table.rows:
                    row_data = [cell.text.strip().replace("\n", " ") for cell in row.cells if cell.text.strip()]
                    if row_data:
                        table_lines.append(" | ".join(row_data))
                if table_lines:
                    parts.append("[Table Content]\n" + "\n".join(table_lines))
            
            if parts:
                return "\n\n".join(parts)
        except Exception as docx_err:
            logger.warning(f"python-docx error on {file_path}: {docx_err}. Trying zip XML fallback...")

        # Fallback: Open as Zip archive and extract word/document.xml
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(file_path) as z:
                xml_data = z.read("word/document.xml")
                root = ET.fromstring(xml_data)
                texts = [node.text for node in root.iter() if node.text and node.text.strip()]
                return "\n".join(texts)
        except Exception as zip_err:
            logger.warning(f"Zip XML fallback failed on {file_path}: {zip_err}")

        # Ultimate fallback
        return _read_text_with_fallback(file_path)

    @staticmethod
    def _extract_from_xlsx(file_path: str) -> str:
        """Extract tabular data from Excel spreadsheets (.xlsx, .xls)"""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet_outputs = []
            for sheetname in wb.sheetnames:
                ws = wb[sheetname]
                rows_text = []
                for row in ws.iter_rows(values_only=True):
                    row_vals = [str(val).strip() for val in row if val is not None and str(val).strip()]
                    if row_vals:
                        rows_text.append(" | ".join(row_vals))
                if rows_text:
                    sheet_outputs.append(f"=== Sheet: {sheetname} ===\n" + "\n".join(rows_text))
            if sheet_outputs:
                return "\n\n".join(sheet_outputs)
        except Exception as xl_err:
            logger.warning(f"openpyxl failed on {file_path}: {xl_err}. Trying pandas fallback...")

        try:
            import pandas as pd
            excel_file = pd.ExcelFile(file_path)
            outputs = []
            for sheet in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet)
                csv_str = df.to_csv(index=False)
                outputs.append(f"=== Sheet: {sheet} ===\n" + csv_str)
            return "\n\n".join(outputs)
        except Exception as pd_err:
            logger.warning(f"pandas failed on {file_path}: {pd_err}")

        return _read_text_with_fallback(file_path)

    @staticmethod
    def _extract_from_csv(file_path: str) -> str:
        """Extract CSV or TSV data with fallback encoding"""
        return _read_text_with_fallback(file_path)

    @staticmethod
    def _extract_from_json(file_path: str) -> str:
        """Extract and format JSON data"""
        raw = _read_text_with_fallback(file_path)
        try:
            data = json.loads(raw)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            return raw

    @staticmethod
    def _extract_from_html(file_path: str) -> str:
        """Extract clean readable text from HTML / XML"""
        raw = _read_text_with_fallback(file_path)
        try:
            import re
            # Strip script and style blocks
            cleaned = re.sub(r'<(script|style)[^>]*>[\s\S]*?</\1>', '', raw, flags=re.IGNORECASE)
            # Replace tags with spaces
            cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
            # Collapse whitespace
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return cleaned
        except Exception:
            return raw

    @staticmethod
    def _extract_from_image(file_path: str) -> str:
        """
        Extract text, information, and context from images.
        1. If SVG: extract text nodes directly.
        2. If raster image: Call LLM Vision API if configured.
        3. Fallback: Extract image metadata via PIL (dimensions, format, mode).
        """
        suffix = Path(file_path).suffix.lower()
        if suffix == '.svg':
            return _read_text_with_fallback(file_path)

        # 1. Try Multimodal Vision via LLMClient / OpenAI
        vision_text = None
        try:
            from ..config import Config
            if Config.LLM_API_KEY:
                import base64
                from openai import OpenAI
                
                with open(file_path, "rb") as img_file:
                    b64_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                mime = "jpeg" if suffix in {'.jpg', '.jpeg'} else suffix.lstrip('.')
                if mime == 'jpg':
                    mime = 'jpeg'
                
                client = OpenAI(
                    api_key=Config.LLM_API_KEY,
                    base_url=Config.LLM_BASE_URL
                )
                
                prompt = (
                    "You are a multimodal information extraction agent for Lokantra Swarm Intelligence. "
                    "Examine this image carefully. Extract and transcribe ALL visible text, data points, labels, "
                    "diagram nodes/relationships, tables, and entities in comprehensive detail for knowledge graph construction."
                )
                
                response = client.chat.completions.create(
                    model=Config.LLM_MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/{mime};base64,{b64_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1500
                )
                if response.choices and response.choices[0].message.content:
                    vision_text = response.choices[0].message.content.strip()
        except Exception as vision_err:
            logger.info(f"LLM vision extraction bypassed or failed on {file_path}: {vision_err}")

        if vision_text:
            return f"[Extracted from Image {Path(file_path).name}]:\n{vision_text}"

        # 2. Fallback: PIL metadata inspection
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                width, height = img.size
                fmt = img.format
                mode = img.mode
                return f"[Image Document: {Path(file_path).name} | Format: {fmt} | Dimensions: {width}x{height} | Mode: {mode}]"
        except Exception as e:
            return f"[Image Document: {Path(file_path).name} - Extraction unavailable: {e}]"

    @staticmethod
    def _extract_from_md(file_path: str) -> str:
        """Extract text from Markdown with automatic encoding detection"""
        return _read_text_with_fallback(file_path)
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extract text from TXT with automatic encoding detection"""
        return _read_text_with_fallback(file_path)
    
    @classmethod
    def extract_from_multiple(cls, file_paths: List[str]) -> str:
        """
        Extract and merge text from multiple files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Merged text content
        """
        all_texts = []
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                text = cls.extract_text(file_path)
                filename = Path(file_path).name
                all_texts.append(f"=== Document {i}: {filename} ===\n{text}")
            except Exception as e:
                all_texts.append(f"=== Document {i}: {file_path} (Extraction failed: {str(e)}) ===")
        
        return "\n\n".join(all_texts)


def split_text_into_chunks(
    text: str, 
    chunk_size: int = 500, 
    overlap: int = 50
) -> List[str]:
    """
    Split text into chunks
    
    Args:
        text: Original text
        chunk_size: Character count per chunk
        overlap: Overlap character count
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to split at sentence boundaries
        if end < len(text):
            for sep in ['.\n', '!\n', '?\n', '\n\n', '. ', '! ', '? ']:
                last_sep = text[start:end].rfind(sep)
                if last_sep != -1 and last_sep > chunk_size * 0.3:
                    end = start + last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Next chunk starts from overlap position
        start = end - overlap if end < len(text) else len(text)
    
    return chunks
