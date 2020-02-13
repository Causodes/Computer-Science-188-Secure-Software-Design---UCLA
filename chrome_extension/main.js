/*
main.js:

Hi, welcome to the Chrome extension for Project Noodles!
This file acts as the main line of communication between the extension and our Python Application.
This line of communication is achieved using Native Messaging API provided by Google, which communicates via stdio
after opening up a port. Furthermore, this file also injects a content script every time the pop-up is clicked,
which is able to check whether a line of communication is needed or not between the Python application.

This file is also in charge of dynamically changing the popup's status as needed. More features on the way soon(?).
*/

'use strict';

// Global port variable for Native Messaing
var port = null;

// Boot up the Native Messaging and establish a connection with the host, indicated by hostName
function connect() {
    var hostName = "com.google.chrome.example.echo";
    port = chrome.runtime.connectNative(hostName);
    port.onMessage.addListener(onNativeMessage);
    port.onDisconnect.addListener(onDisconnected);
}

// Send a Native Message to the Python Application, containing the URL of the current tab
function sendNativeMessage(message) {
    // If port is open, send message
    if (port) {
        port.postMessage(message);
        console.log("Sent message: " + JSON.stringify(message));
    }
    // Else, start up a connection and then send the message
    else {
        connect();
        port.postMessage(message);
        console.log("Sent message: " + JSON.stringify(message));
    }
}

// When it receives a message, update the fields accordingly
function onNativeMessage(message) {
    document.getElementById('username').value = message['username'];
    document.getElementById('passwd').value = message['password'];
}

// When disconnected from host, set port to null value so that it may reconnect at the next request
function onDisconnected() {
    console.log("Failed to connect: " + chrome.runtime.lastError.message);
    port = null;
}

// Flip between a hidden password field and a regular text field
function showPassword() {
    let button = document.getElementById('show-button');
    let password_field = document.getElementById('passwd');

    // If currently showing the password
    if (password_field.type == 'text') {
        password_field.type = 'password';
        button.innerHTML = 'Show';
    }
    else {
        password_field.type = 'text';
        button.innerHTML = 'Hide';
    }
}

// Listener that waits until the contents of the pop-up is loaded in
document.addEventListener('DOMContentLoaded', function () {
    // Create a link between the connect button and the connect function
    document.getElementById('connect-button').addEventListener(
        'click', connect);
    // Likewise, create a connection to the show button
    document.getElementById('show-button').addEventListener(
        'click', showPassword);

    // Query for the current tab and its information
    var queryInfo = {currentWindow: true, active: true};
    chrome.tabs.query(queryInfo, function(tabs) {
        // Send a message to the content script, asking if the current tab has a password field
        ensureSendMessage(tabs[0].id, {message: "URLChange", url: tabs[0].url}, function(response) {
            if (response && response.password) {
                // Password field is detected, send a Native Message to the Python application with the current url
                sendNativeMessage({url: response.url});
            }
        });
    });
});

// After 5 hours of debugging, I found out that sometimes the content script does not get automatically injected.
// Therefore, I ensure that the content script becomes injected by executing it explicitly.
function ensureSendMessage(tabId, message, callback){
    chrome.tabs.executeScript(tabId, {file: "cscript.js"}, function(){
        if(chrome.runtime.lastError) {
            console.error(chrome.runtime.lastError);
            throw Error("Unable to inject script into tab " + tabId);
        }
        // Now it's injected and ready, so send the message to the correct tab
        chrome.tabs.sendMessage(tabId, message, callback);
    });
}