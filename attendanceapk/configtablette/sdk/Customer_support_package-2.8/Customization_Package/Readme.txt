-----------------------------------------------------------
	Add your app in the integration partion
-----------------------------------------------------------
1. Add in the integration/app each application that shouldn't be removed by user and that doesn't need system permissions.
2. Add in the integration/priv-app each application that shouldn't be removed by user and that needs system permissions.
3. Add in the integration/preinstall each application that need no system permission and that could be removed by user.

Each application should be added in a separate folder, for example integration/app/myapp1/myapp1.apk.
Sign your apks with --system-sign-apk option if you need more higher rights than system rights.

-----------------------------------------------------------
		Command line
-----------------------------------------------------------
$ ./MTabletCustoPackTool OPTIONS

OPTIONS:
-k, --generate-key-set KEYNAME                                	generate a customization package key set named KEYNAME, as well associated Android Studio keystore
-s, --system-sign-apk KEYNAME INAPKFILE OUTAPKFILE            	provide system right to INAPKFILE using KEYNAME keyset
-e, --export-unsigned-public-key KEYNAME OUTFILE              	export OUTFILE to provide KEYNAME public key to Mtablet manufacturer for signature
-i, --import-signed-public-key KEYNAME INFILE                 	import INFILE from Mtablet manufacturer to use as KEYNAME public signed key
-p, --generate-customization-package KEYNAME OUTZIP [OPTIONS2] 	generate a ready to flash customization package OUTZIP using KEYNAME key set
-h, --help                                                    	display this help

OPTIONS2:
-a, --alternative-key-set ALTKEYNAME                           	generate a customization package allowing further update by KEYNAME or ALTKEYNAME signed customization packages
-v, --customization-package-version VERSION                   	sets customization package version (0-4294967295, 0 by default)
-d, --downgrade-policy POLICY                                 	after flashing generated customization package, next update will be impacted by downgrade POLICY, see below
-x, --key-check-disable                                       	after flashing generated customization package, any integrator key will be accepted

POLICY:
DOWNGRADE_ALLOWED                                            	no restriction after flashing customization package (by default)
NO_VERSION_DOWNGRADE                                         	once flashed, customization package will refuse inferior version updates
NO_DATE_DOWNGRADE                                            	once flashed, customization package will refuse inferior generation date updates
NO_DATE_NOR_VERSION_DOWNGRADE                                	enable both NO_VERSION_DOWNGRADE and NO_DATE_DOWNGRADE

Usual process:

- Generating customer own keys:
     $ ./MTabletCustoPackTool --generate-key-set mycompany1

- Signing customer public keys:
     $ ./MTabletCustoPackTool --export-unsigned-public-key mycompany1 mycompany1.bin
     
	 Note:
	 ------------------------------------------------------------
	 Please provide "mycompany1.bin" to MorphoTablet™ manufacturer
     and get "mycompany1_signed.bin" back before proceeding ...
	 ------------------------------------------------------------
	 
     $ ./MTabletCustoPackTool --import-signed-public-key mycompany1 mycompany1_signed.bin

- Generating customer customization pack:
     $ ./MTabletCustoPackTool --generate-customization-package mycompany1 mycustpack_update.zip

