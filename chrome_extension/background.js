'use strict';

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

/*
var port = null;

function connect() {
  var hostName = "com.google.chrome.example.echo";
  port = chrome.runtime.connectNative(hostName);
  port.onMessage.addListener(onNativeMessage);
  port.onDisconnect.addListener(onDisconnected);
}

function sendNativeMessage(message) {
  if (port) {
    port.postMessage(message);
    console.log("Sent message: " + JSON.stringify(message));
  }
  else {
    connect();
    port.postMessage(message);
    console.log("Sent message: " + JSON.stringify(message));
  }
}

function onNativeMessage(message) {
  message["message"] = "popup";
  alert("Sending message: " + JSON.stringify(message));
  chrome.runtime.sendMessage(message);
}

function onDisconnected() {
  console.log("Failed to connect: " + chrome.runtime.lastError.message);
  port = null;
}

chrome.runtime.onStartup.addListener(function() {
  // Connect to the Native Messaging port
  connect();
});

function ensureSendMessage(tabId, message, callback){
  chrome.tabs.executeScript(tabId, {file: "cscript.js"}, function(){
    if(chrome.runtime.lastError) {
      console.error(chrome.runtime.lastError);
      throw Error("Unable to inject script into tab " + tabId);
    }
    // OK, now it's injected and ready
    chrome.tabs.sendMessage(tabId, message, callback);
  });
}

chrome.tabs.onUpdated.addListener(
  function(tabId, changeInfo, tab) {
    // read changeInfo data
    if (changeInfo.url) {
      ensureSendMessage(tabId, {message: "URLChange", url: changeInfo.url}, function(response) {
         if (response && response.password) {
           sendNativeMessage({url: response.url});
         }
      });
    }
  }
);

// Temp function to manually connect to the Native Messaging app
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if (request.message === "background") {
      connect();
    }
  });
*/