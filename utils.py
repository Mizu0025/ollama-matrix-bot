def split_text_into_chunks(text, max_size=40000):
    """
    Splits text into chunks of max_size bytes, trying to split at newlines to preserve formatting.
    """
    if len(text.encode('utf-8')) <= max_size:
        return [text]

    chunks = []
    while text:
        # Check if remaining text fits in one chunk
        if len(text.encode('utf-8')) <= max_size:
            chunks.append(text)
            break

        # Find the maximum number of characters that fit into max_size bytes
        # Using binary search to find the cut-off point
        low = 0
        high = len(text)
        split_idx = 0
        while low <= high:
            mid = (low + high) // 2
            if len(text[:mid].encode('utf-8')) <= max_size:
                split_idx = mid
                low = mid + 1
            else:
                high = mid - 1

        # Look for the last newline within the split_idx boundary
        newline_idx = text.rfind('\n', 0, split_idx)
        
        if newline_idx != -1 and newline_idx > 0:
            # Split at the newline
            chunks.append(text[:newline_idx + 1])
            text = text[newline_idx + 1:]
        else:
            # If no newline is found, split at the maximum possible character count
            chunks.append(text[:split_idx])
            text = text[split_idx:]

    return chunks
