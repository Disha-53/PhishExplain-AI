chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_SELECTED_TEXT') {
    const selection = window.getSelection ? window.getSelection().toString() : '';
    const text = (selection || document.body.innerText || '').trim();
    sendResponse({ text, url: window.location.href });
  }
  return true;
});
