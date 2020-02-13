/*
background.js:

Startup routine and a background script for a chrome extension, won't be needing it outside of standard initialization
routine.
 */
'use strict';

// On install, create rules to determine which kinds of websites the extension can acccess
chrome.runtime.onInstalled.addListener(function() {
  chrome.declarativeContent.onPageChanged.removeRules(undefined, function() {
    chrome.declarativeContent.onPageChanged.addRules([{
      conditions: [new chrome.declarativeContent.PageStateMatcher({
        pageUrl: {schemes: ["http", "https"]},
      })],
      actions: [new chrome.declarativeContent.ShowPageAction()]
    }]);
  });
});