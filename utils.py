def split_text_into_chunks(text, paragraphs_per_chunk=2):
    """
    Splits text into chunks of approximately `paragraphs_per_chunk` paragraphs.
    Preserves the entire text content across chunks.
    """
    if not text:
        return []
        
    # Split by double newline to identify paragraphs
    # We use a placeholder to avoid losing the separator during split if we want to be exact,
    # but strictly splitting by \n\n and re-joining with \n\n is robust for markdown.
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
             continue
             
        current_chunk.append(paragraph)
        
        if len(current_chunk) >= paragraphs_per_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = []
            
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks
