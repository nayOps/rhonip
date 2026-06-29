##### INSTALLATION NOTE #####

**********************************************************************************************************************************************************
*       Please note that TeamViewer is not free of charge for a commercial use and will require contacting TeamViewer's teams to establish a contract.   *
*                                                                                                                                                        *
*       IDEMIA provides TeamViewer's apks in this CustomerSupportPackage only to help MorphoTablet's users in the installation process.                  *
*                                                                                                                                                        *
*       IDEMIA will not be in charge of support for any issues regarding using TeamViewer.                                                               *
*                                                                                                                                                        *
*       If you have any issues running TeamViewer, please contact TeamViewer's support.                                                                  *
**********************************************************************************************************************************************************


##### How to add TeamViewerHost in your customization package #####

1- Sign the addon with your own key
	cd Contents/Customization_Package/
	./MTabletCustoPackTool -s YOUR_KEYNAME ../Demo_APK/TeamViewer/TeamViewerAddon_idemia_mt2.apk ../Demo_APK/TeamViewer/TeamViewerAddon_idemia_mt2_signed_YOUR_KEYNAME.apk
	
2- Copy the 2 apks (TeamViewerAddon and TeamViewerHost)
	mkdir integration/priv-app/TeamViewerAddon
	cp ../Demo_APK/TeamViewer/TeamViewerAddon_idemia_mt2_signed_YOUR_KEYNAME.apk integration/priv-app/TeamViewerAddon/
	
	mkdir integration/app/TeamViewerHost
	cp ../Demo_APK/TeamViewer/TeamViewerHost.apk integration/app/TeamViewerHost/
	
3- Generate your customization package
	./MTabletCustoPackTool -p YOUR_KEYNAME update_TeamViewerHost.zip
	
4- Copy your customization package on your MorphoTablet
	adb push update_TeamViewerHost.zip /sdcard/
	
5- Install your customization package
	Go to Settings -> About tablet -> System updtaes (storage) 
	Tap "OK"
	You should see a line with update_TeamViewerHost.zip, tap "Install"
	Your tablet will reboot and TeamViewerHost will be installed
	

##### Installing the "controller" application on your device #####

If you want to remotely control your MorphoTablets, you need to install TeamViewer on another device.
- On Android, you can use the provided TeamViewer_14.1.87.apk 
- On any other devices, please check on TeamViewer's website
