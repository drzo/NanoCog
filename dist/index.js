function encode(text) {
  const forbiddenTokens = ['<|endoftext|>'];
  
  // Filter out forbidden tokens instead of throwing an error
  let sanitizedText = text;
  forbiddenTokens.forEach(token => {
    if (sanitizedText.includes(token)) {
      // Replace forbidden tokens with a safe alternative or remove them
      sanitizedText = sanitizedText.replace(new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), '');
      console.warn(`Warning: Removed forbidden token "${token}" from text`);
    }
  });
  
  // Proceed with encoding logic using sanitized text
  return encodeLogic(sanitizedText);
}
