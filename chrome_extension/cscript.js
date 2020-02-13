/*
cscript.js:

This script is a content script that is injected into the current, active tab to gather information about it, modify it,
etc. In our case, we will be using the content script to check whether the current page's DOM has a password field.

cscript.js is first initialized by main.js, which injects the script. This script is also waiting for a message from
backgroun.js, which contains the following field:

{
    message: ID for specifying destination
}

After confirming the ID of the message, then it checks the current DOM, and sends a response with the url back to
main.js.
 */
var injected;

// Make sure content script is not injected twice
if(!injected){
    injected = true;
    // Create a listener for messages
    chrome.runtime.onMessage.addListener(
        function(request, sender, sendResponse) {
            // listen for messages sent from background.js
            if (request.message === 'URLChange') {
                //Check for password field in the current tab
                var x = document.querySelectorAll(`input[type="password"]`);
                if (x != undefined && x.length != 0) {
                    // If there is a password field, send a response back with url
                    sendResponse({password: true, url: request.url});
                }
                else {
                    // Else, notify background that this page doesn't have a password field
                    sendResponse({password: false});
                }
            }
        });
}