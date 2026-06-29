#!/bin/bash

set -e
#set -x

Init()
{
	MORPHO=0
	rm -rf integration/*
	KEY=../../../../PC/Integrator_tools/PROD1_Morpho1/
	[ -e $KEY ] && MORPHO=1	&& return
	[ -z $1 ] && echo -e "Usage : $0 keyname\nSee customization package documentation to generate one key"
	KEY=$1
}

SignApk()
{
	./MTabletCustoPackTool -s $KEY $1 $2
}

InstallSystemApk()
{
	local apk=$(basename $1)
	local dir="integration/priv-app/"$apk"_dir"
	mkdir -p $dir
	SignApk $1 $dir/$apk
}

InstallPriviledgedApk()
{
	local apk=$(basename $1)
	local dir="integration/priv-app/"$apk"_dir"
	mkdir -p $dir
	cp $1 $dir
}

InstallApk()
{
	local apk=$(basename $1)
	local dir="integration/priv-app/"$apk"_dir"
	mkdir -p $dir
	cp $1 $dir
}

InstallTeamViewer()
{
	InstallSystemApk ../Demo_APK/TeamViewer/TeamViewerAddon_idemia_mt2.apk
	InstallApk ../Demo_APK/TeamViewer/TeamViewerHost.apk
	InstallApk ../Demo_APK/TeamViewer/TeamViewer_14.1.87.apk
}

InstallMultiProtect()
{
	InstallApk ../Demo_APK/Multiprotect_License_Protection-release.apk
	InstallApk ../Demo_APK/Multiprotect_License_Manager-release.apk
}

InstallCSPSample()
{
	InstallApk ../Demo_APK/Main_Demo_2.8.apk
	InstallSystemApk ../Demo_APK/IrisSensor_Demo_2.8.apk
	InstallSystemApk ../Demo_APK/Multi_SIM_Demo_2.8.apk
	[ $MORPHO = 1 ] && InstallSystemApk ../../../ExternalApk/Mobiris/app-morphoTabletProdNative-release.apk
}

GenDemoCustPack()
{
	InstallTeamViewer
	InstallCSPSample
	InstallMultiProtect
	./MTabletCustoPackTool -p $KEY update_demoCSP.zip -x
	echo "Done, CSP demo was generated : update_demoCSP.zip"
}

Init $1
GenDemoCustPack

