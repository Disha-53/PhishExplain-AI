chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_PAGE_CONTEXT') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      if (!tab || !tab.id) {
        sendResponse({ text: '', url: '' });
        return;
      }
      chrome.scripting.executeScript(
        {
          target: { tabId: tab.id },
          func: () => ({
            text: document.body.innerText,
            url: window.location.href,
          }),
        },
        (results) => {
          const outcome = results && results[0] ? results[0].result : { text: '', url: '' };
          sendResponse(outcome);
        }
      );
    });
    return true;
  }

  return false;
});
