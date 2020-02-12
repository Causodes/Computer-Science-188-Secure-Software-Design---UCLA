'use strict';
var port = null;

function connect() {
  var hostName = "com.google.chrome.example.echo";
  port = chrome.runtime.connectNative(hostName);
  port.onMessage.addListener(onNativeMessage);
  port.onDisconnect.addListener(onDisconnected);
  updateUiState();
}

function sendNativeMessage(message) {
  port.postMessage(message);
  console.log("Sent message: " + JSON.stringify(message));
}

function onNativeMessage(message) {
  alert("Received message: " + JSON.stringify(message));
}

function onDisconnected() {
  console.log("Failed to connect: " + chrome.runtime.lastError.message);
  port = null;
}

chrome.runtime.onInstalled.addListener(function() {
  chrome.declarativeContent.onPageChanged.removeRules(undefined, function() {
    chrome.declarativeContent.onPageChanged.addRules([{
      conditions: [new chrome.declarativeContent.PageStateMatcher({
        pageUrl: {schemes: ["http", "https"]},
      })],
      actions: [new chrome.declarativeContent.ShowPageAction()]
    }]);
  });
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
      // read changeInfo data and do something with it
      // like send the new url to contentscripts.js
      if (changeInfo.url) {
        ensureSendMessage(tabId, {message: "URLChange", url: changeInfo.url}, function(response) {
          if (response) {
            alert("Received message back: " + response.url);
            sendNativeMessage({url: response.url});
          }
        });
      }
    }
);
// No function definition yet since I don't know Javascript, but here's the TODO:

// runtime.connectNative: connect the extension to Native Messaging

// parseHTML: detect password field in the current page by parsing the HTML

// runtime.listenForURLChange: read current url

// runtime.sendNativeMessage: send Python app the current url using Native Messaging via stdio

// Receive messages via a listener at stdin using Native Messaging:
// var port = chrome.runtime.connectNative('com.my_company.my_application');
// port.onMessage.addListener(function(msg) {
//   console.log("Received" + msg);
// });
