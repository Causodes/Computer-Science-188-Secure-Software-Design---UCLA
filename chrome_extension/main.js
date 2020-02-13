'use strict';

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
    document.getElementById('username').value = message['username'];
    document.getElementById('passwd').value = message['password'];

}

function onDisconnected() {
    console.log("Failed to connect: " + chrome.runtime.lastError.message);
    port = null;
}

function updateUiState() {
    if (port) {
        document.getElementById('connect-button').style.display = 'none';
    } else {
        document.getElementById('connect-button').style.display = 'block';
    }
}

function showPassword() {
    let button = document.getElementById('show-button');
    let password_field = document.getElementById('passwd');
    if (password_field.type == 'text') {
        password_field.type = 'password';
        button.innerHTML = 'Show';
    }
    else {
        password_field.type = 'text';
        button.innerHTML = 'Hide';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('connect-button').addEventListener(
        'click', connect);
    document.getElementById('show-button').addEventListener(
        'click', showPassword);
    updateUiState();
    var queryInfo = {currentWindow: true, active: true};
    chrome.tabs.query(queryInfo, function(tabs) {
        ensureSendMessage(tabs[0].id, {message: "URLChange", url: tabs[0].url}, function(response) {
            if (response && response.password) {
                sendNativeMessage({url: response.url});
            }
        });
    });
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

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.message === "popup") {
            let text = "<b>" + JSON.stringify(request) + "</b>";
            document.getElementById('response').innerHTML += "<p>" + text + "</p>";
        }
  });