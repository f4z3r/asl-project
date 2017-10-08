# Script to deploy middleware to the cloud.

scp -rp -o StrictHostKeyChecking=no /Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/project/app/build-2.0/dist bjakob@bjakobforaslvms4.westeurope.cloudapp.azure.com:~/
ssh bjakob@bjakobforaslvms4.westeurope.cloudapp.azure.com "jar xvf ~/dist/middleware-bjakob.jar"
