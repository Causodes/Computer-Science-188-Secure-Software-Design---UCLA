# Password Vault Chrome Extension

This section corresponds to code for the Chrome Extension.

How to get the Chrome extension working with the application:
1. First, the entire application has to be located under /Applications/
	a. This is because it's the easy way to give the necessary permissions in OSX to get Native Messaging working
2. Go to Google Chrome -> More Tools -> Extensions, enable Developer mode, and load the unpacked extension.
	a. Give the folder of chrome_extension for loading the unpacked extension.
3. Under the Noodle Extension 1.0, copy the ID, which we will use to give permissions to.
4. In chrome_extension folder, cd over to sample_host.
5. Use the following command to give permissions to the correct folder: chmod a+rx install_host.sh message_proxy.py
6. In com.google.chrome.example.echo.json file, change "allowed_origins" to "chrome-extension://[your extension ID]/"
7. Run install_host.sh with: ./install_host.sh
8. If you want to test the application, first close Chrome all the way by hovering up top, clicking Chrome, and exiting.
9. Next, run this command to launch chrome from Terminal: 
	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --enable-logging=stderr --v=1
10. Run ui.py and try to go to a website where a password is stored and has a password field, then click the extension popup.
