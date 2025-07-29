from PyPDF2 import PdfReader

class PDFProcessor:
    def extract_text_chunks(self, uploaded_files, chunker):
        chunks = []
        for file in uploaded_files or []:
            if file.type == "application/pdf":
                pdf_reader = PdfReader(file)
                full_text = " ".join(page.extract_text() or "" for page in pdf_reader.pages)
                chunks.extend(chunker(full_text))
        return chunks