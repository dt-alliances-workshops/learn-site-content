# AWS Lab Cleanup

## Overview

Depending on what you provisioned there maybe a few things to cleanup.

If you plan to keep things running so you can examine the workshop a bit more please remember to do the cleanup when you are done. 

## Remove Dynatrace config build by Automation

Run this command to remove Dynatrace configuration:

```
cd ~/aws-modernization-dt-orders-setup/workshop-config
./cleanup-workshop-config.sh
```

The start of the script output will look like this:

```
===================================================================
About to Delete Workshop Dynatrace configuration
===================================================================
Proceed? (y/n) : y

...
...
Done Removing Dynatrace config
```

When you are back at the command prompt, then continue to the next step.

## Remove manually added Dynatrace config

Within Dynatrace, navigate to `Settings -> CLoud and Virtualization -> AWS` and remove the `dynatrace-modernize-workshop` connection created earlier.


## Delete AWS resources create by CloudFormation

To remove the resources created earlier with CloudFormation, just navigate to the CloudFormation page in the [AWS console](https://console.aws.amazon.com/cloudformation/home){target="_blank"}, highlight a stack, and click the `Delete` button.

Plan for a few minutes for the EC2 instances, and 20-30 minutes for the EKS Cluster to be completely removed.

## Remove manually added AWS IAM config

If you created a IAM policy for the AWS monitor integration lab, then follow these steps.

1 . Navigate to IAM policies and delete the policy named `dynatrace_monitoring_policy` that you created earlier.

2 . Navigate to IAM role and delete the `Dynatrace_monitoring_user` user that you created earlier.

## Next Steps

You have a fully feature enabled 15 day Dynatrace trial, so keep using it to monitor and manage your infrastructure and applications!!

Here are resources to get your started:

* [Learn more about your tenant and install more OneAgents](https://www.dynatrace.com/support/help/get-started/get-started-with-dynatrace-saas/){target="_blank"}
* [Add other users to your tenant](https://www.dynatrace.com/support/help/how-to-use-dynatrace/user-management-and-sso/manage-groups-and-permissions/){target="_blank"}
* [YouTube Videos](https://www.youtube.com/channel/UCcYJ-5q_AfmjQ4XTjTS0o3g){target="_blank"}
* [More Support resources](https://www.dynatrace.com/services-support/#support-resources-section){target="_blank"}
