It's working 100% in Linux Ubuntu 24.4 Nobel Numbat. If anyone facing license issue. Follow the below steps.

1.  sudo chmod a+rwx /Path/to/your_Nuke_Folder/Nuke14.v02.run
2.  cd /Path/to/your_Nuke_Folder/
3.  ls (For copy the file name of nuke)
4.  sudo ./Nuke14.v02.run or sudo bash Nuke14.v02.run
5.  choose the path and install in the /opt folder
6.  cd /Path/to/your_FLT7_Folder/FLT7.1v1-linux-x86-release-64.tgz
7.  tar xvzf FLT7.1v1-linux-x86-release-64.tgz
8.  cd FLT7.1v1-linux-x86-release-64RH
9.  sudo chmod a+rwx ./install.sh
10. sudo ./install.sh or sudo bash install.sh
11. Open firefox if you are using vpn disable it first then go to the link " http://127.0.0.1:4102 or http://127.0.0.1:5053 or http://127.0.0.1:4101 " until you get the page "Reprise License Server Administration"
12. Click "Shutdown" button on left side and click "SHUT DOWN SERVER" don't change anything in "ISV". By default it should be "-all"
13. sudo rm /usr/local/foundry/RLM/rlm.foundry
14. sudo rm /usr/local/foundry/LicensingTools7.1/bin/RLM/rlm.foundry
15. sudo rm /usr/local/foundry/RLM/foundry.set
16. sudo rm /usr/local/foundry/LicensingTools7.1/bin/RLM/foundry.set
17. sudo cp /Path/to/your_rlm.foundry_Crack_Folder/rlm.foundry /usr/local/foundry/RLM
18. sudo cp /Path/to/your_rlm.foundry_Crack_Folder/rlm.foundry /usr/local/foundry/LicensingTools7.1/bin/RLM
19. sudo cp /Path/to/your_foundry.set_Crack_Folder/foundry.set /usr/local/foundry/RLM
20. sudo cp /Path/to/your_foundry.set_Crack_Folder/foundry.set /usr/local/foundry/LicensingTools7.1/bin/RLM
21. Edit xf_foundry.lic replacing "HOST_NAME MAC_ADDRESS PORT" For EX: "CXMA04 00f635v57202 4101" You can get those informations using rlmutil (cd to the folder first then "./rlmutil rlmhostid host and ./rlmutil rlmhostid") Note : Edit the xf_foundry.lic in notepad++ using the wine is recommended. Don't open license file in linux before edit make copy and do it.
22. sudo cp /Path/to/your_edited_xf_foundry.lic_Folder/xf_foundry.lic  /usr/local/foundry/RLM
23. sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM
24. sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM
25. sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM
26. cd /opt/Nuke14.0v2/
27. ./Nuke14.0 &

Note : Everytime you have to execute the step 23 to step 27 to run the nuke or any other foundry product. Now download the latest version and just install. It should work.


Note : Everytime you have to execute the step 23 to step 27 to run the nuke or any other foundry product. Now download the latest version and just install. It should work.



To automate this create Any_name_you_want.sh bash file like below and save in that "/etc/init.d". So this script will run in the system start up.

###########################################################################################
#!/bin/bash

#Starting RLM.Foundry

clear
echo "Starting RLM License server"

sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM

P1=$!

sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM

P1=$!

sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM


echo "Started RLM License server successfully"

exit 0
###########################################################################################




If you only want to run this license server when you open or need the nuke then create alias in the "/home/YourUserName/.bashrc" ( To see .bashrc enable the hidden files )

###########################################################################################

alias nuke14="cd /Any_where/Your_Own_License_Server_Script.sh_Folder/ && ./Your_Start_License_Script.sh && cd /opt/Nuke14.0v2/ && ./Nuke14.0 &" ( Based on the Foundry product change the folder and name )

###########################################################################################




If you get permission denied error. It means sudo commands need password to execute the command. Do the following to remove password for Your_User_Name

sudo visudo

###########################################################################################

$YOUR_USER_NAME ALL=(ALL) NOPASSWD: ALL

###########################################################################################



control + x then save it. Now just run sudo apt update in new shell to check.

Enjoy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!