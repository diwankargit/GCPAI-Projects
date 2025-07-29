class Chunker:
    def chunk_text(self, text, max_words=200):
        words = text.split()
        return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words) if words[i:i + max_words]]
