function encode(text) {
  const forbiddenTokens = ['<|endoftext|>'];
  forbiddenTokens.forEach(token => {
    if (text.includes(token)) {
      throw new Error(`CAPIError: The text contains a special token that is not allowed: ${token}`);
    }
  });
  // Proceed with encoding logic
  return encodeLogic(text);
}
