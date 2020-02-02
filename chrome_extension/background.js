// Copyright 2018 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

'use strict';

chrome.runtime.onInstalled.addListener(function() {
  chrome.storage.sync.set({color: '#3aa757'}, function() {
    console.log('The color is green.');
  });
  chrome.declarativeContent.onPageChanged.removeRules(undefined, function() {
    chrome.declarativeContent.onPageChanged.addRules([{
      conditions: [new chrome.declarativeContent.PageStateMatcher({
        pageUrl: {hostEquals: 'developer.chrome.com'},
      })],
      actions: [new chrome.declarativeContent.ShowPageAction()]
    }]);
  });
});

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
