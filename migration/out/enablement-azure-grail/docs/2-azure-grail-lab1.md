# Azure Grail Workshop Lab 1 - OneAgent Observability

## Lab Setup
<!-- Duration: 2 min -->
Referring to the picture below, here are the components for lab 1.

  **#1 . Sample Application**

  Sample app representing a simple architecture of a frontend and backend implemented as Docker containers that we will review in this lab.

  **#2 . Dynatrace monitoring**

  The Dynatrace OneAgent has been installed by the workshop provisioning scripts and is communicating to your Dynatrace tenant.

  **#3 . Load generator process**

  A docker processes that sends simulated user traffic to the sample app using [ Jmeter ](https://github.com/dt-orders/load-traffic){target="_blank"} run within a Docker container.  You will not need to interact with this container; it just runs in the background.

    ![lab1 setup](img/azure-grail-lab1/lab1-setup.png)

!!! tip
    💥A real-world scenario would often start with the application components running on a physical or virtualized host in on-prem and not "Dockerized". 

    To simplify the workshop, we "Dockerized" the application into a front-end and back-end. In Dynatrace, these Docker containers all show up as "processes" on a host just like a "non-Dockerized" application will.

## Review OneAgent
<!-- Duration: 4 min -->
The host running the sample application was created using scripts to install and run the Sample Application and to install the Dynatrace OneAgent. 

All these scripts you can review [ here ](https://github.com/dt-alliances-workshops/azure-modernization-dt-orders-setup.git){target="_blank"} within the `provision-scripts` subfolder.

!!! tip
    📓 The Dynatrace OneAgent was preinstalled and is sending data to your Dynatrace environment using the [Dynatrace OneAgent VM Extension for Azure ](https://www.dynatrace.com/support/help/technology-support/cloud-platforms/microsoft-azure-services/oneagent-integration/integrate-oneagent-on-azure-virtual-machines/){target="_blank"}

!!! tip
    `Additional Ways to deploy OneAgent`
    1. The Azure CLI command for setting up the OneAgent VM extension looks like:
        ```
        az vm extension set \
            --publisher dynatrace.ruxit \
            --name "$AGENT" \
            --resource-group "$AZURE_RESOURCE_GROUP" \
            --subscription "$AZURE_SUBSCRIPTION" \
            --vm-name "$HOSTNAME" \
            --settings "{\"tenantId\":\"$DT_ENVIRONMENT_ID\",\"token\":\"$DT_PAAS_TOKEN\", \"server\":\"$DT_BASEURL/api\", \"hostGroup\":\"$HOSTGROUP_NAME\"}" 
        ```

    2. The `Hub` option from the left side menu to open the OneAgent deployment page. 
    ![lab1 dynatrace hub](img/azure-grail-lab1/lab1-dynatrace-hub.png)
    - Explore all the capabilities of Dynatrace while you are in the Hub
    - Pick the `OneAgent` under the `Start monitoring` section, then click the `Download Agent` at the bottom of the page to open the `Download agent` page.
    ![lab1 deploy dynatrace](img/azure-grail-lab1/lab1-deploy-dynatrace.png)
    - On the `Download agent` page, pick the platform `Linux` to view the commands will download and run the OneAgent installer.
    ![lab1 download dynatrace](img/azure-grail-lab1/lab1-download-dynatrace.png)
        <aside class="positive"> 📓NOTE:<br>
            - The URL and Token is unique to your Dynatrace tenant.  If you expand the `Set customized options (optional)`. section you can review other options for the OneAgent installer.
            <br>- Setting the hostname via  `/bin/sh Dynatrace-OneAgent-Linux-1.207.184.sh --set-host-name=monolith` is just [ one of the ways ](https://www.dynatrace.com/support/help/how-to-use-dynatrace/hosts/configuration/set-custom-host-names-in-dynamic-environments/){target="_blank"} to customize host naming.

- These are the commands used to download, verify, and install the OneAgent.  **That is it!**
![lab1 install dynatrace](img/azure-grail-lab1/lab1-install-dynatrace.png)
- Go back the `Download agent` page and review other options like Windows or Kubernetes.

3. To learn more about the various ways the OneAgent can be installed, check out the [ Dynatrace Documentation](https://www.dynatrace.com/support/help/setup-and-configuration/dynatrace-oneagent/){target="_blank"}

</aside>

### Tasks to complete this step
#### Review OneAgent Status for Monolith VM

1. Login into Dynatrace UI

2. From the left menu, Choose the `Apps -> Deployment Status` to open the OneAgent deployment app.

3. Check to ensure the `dt-orders-monolith` VM is reporting in under OneAgents
![lab1 deployment status](img/azure-grail-lab1/lab1-deployment-status.png)



## Review Sample app
<!-- Duration: 4 min -->
The sample application is called Dynatrace Orders.  A more detailed overview can be found here - [https://github.com/dt-orders/overview](https://github.com/dt-orders/overview).  

All the source code can be found here - [https://github.com/dt-orders](https://github.com/dt-orders)

### Tasks to complete this step
1. Get the Public IP to the frontend of the Sample Application
    - Open up the Azure Portal and navigate to the Virtual Machine page.  You can use the search feature as shown below.
    ![lab1 azure find vm](img/azure-grail-lab1/lab1-azure-find-vm.png)
    - Once on the Virtual Machine page, click on the VM named `dt-orders-monolith`.  You can explore details about this VM, but you will want to copy the public IP as shown below.
    ![lab1 azure get public ip](img/azure-grail-lab1/lab1-azure-get-public-ip.png)
2. Navigate the Sample app in a Browser
    - To view the application, copy the public IP into a browser. It will look like this:
    ![lab1 app](img/azure-grail-lab1/lab1-app.png)
    - Use the menu on the home page to navigate around the application and notice the URL for key functionality.  You will see these URLs later as we analyze the application.
        - Customer List = `customer/list.html`
        - Customer Detail - Each customer has a unique page = `customer/5.html`
        - Catalog List = `catalog/list.html`
        - Catalog Search Form = `catalog/searchForm.html`
        - Order List = `order/list.html`
        - Order Form = `order/form.html`

<!--
!!! tip
    🏫 - Please update the Tracking Spreadsheet upon completing this task. 
-->

## Review Infrastructure & Operations App (New)
<!-- Duration: 4 min -->
In this section, you will review what the OneAgent automatically discovered for the host, services, processes, and the complete dependency mapping for the sample application using the new [Infrastructure & Operations](https://www.dynatrace.com/hub/detail/infrastructure-operations/) app now available on Grail.  

### Tasks to complete this step

1. From the left menu, Choose the `Apps -> Infrastructure & Operations` apps.

1. On the initial view, you'll see two views one by Datacenters and the other by Hosts.  
    - Under the datacenters view you will see the Azure region your VM's are currently deployed in
        ![lab1 infraops main](img/azure-grail-lab1/lab1-infraops-main.png)
1. Click hosts view and select the `dt-orders-monolith` VM
        ![lab1 infraops hosts](img/azure-grail-lab1/lab1-infraops-hosts.png)

1.  On the Overview tab, you will notice high level cpu, memory, disk usage, etc metrics for the host.  At the bottom you'll see properties, tags and ownership data related to this host.
    !!! tip

        👍 `How this helps` 
            As you click to the Technologies, processes, problems, vulnerabilities, slo, logs, events, metrics tabs you'll notice this new app offers a consolidated view of your monitored host. The app helps you to quickly identify areas that require attention and drill down to the host level, where all necessary information is provided to quickly address any issue


## Review Host Classic view
<!-- Duration: 2 min -->
In the next few sections, you will review what the OneAgent automatically discovered for the host, services, processes, and the complete dependency mapping for the sample application.  

!!! tip
    👍 `How this helps`

    As you plan your migration, each of these views will give insights into accessing the profile, consumption and dependencies to other systems and services. 

### Tasks to complete this step

#### Review the Data on the Hosts screen

- From the left menu, Choose the `Apps -> Hosts Classic` apps. Then click on the host with the name `dt-orders-monolith`.
![lab1 hostlist](img/azure-grail-lab1/lab1-hostlist.png)
- On host page, you will see basic infrastructure information for the host.
    1. Now expand the `Properties` section to see data about the host:
    1. Host resource metrics (CPU, memory)
    1. Host availability
    1. Discovered processes. In this case the front end is running Node.js and the backend is running Java in Apache Tomcat.  JMeter is running in Java providing the automated user interactions
    ![lab1 host view upd](img/azure-grail-lab1/lab1-host-view-upd.png)
    ![lab1 host view proc](img/azure-grail-lab1/lab1-host-view-proc.png)

## Review Smartscape
<!-- Duration: 4 min -->
Enterprises have many hosts, services, and application that are ever changing. The ability to automatically discover and change as the environment changes is a key feature that Smartscape delivers.  

Dynatrace's near real-time environment-topology visualization tool, Smartscape, is where Dynatrace's auto-discovery is delivered into a quick and efficient visualization of all the topological dependencies in your infrastructure, processes, and services.

!!! tip
    👍 `How this helps`

    Smartscape shows all the dependencies of a given service. Those include connections to queues, web servers, app servers, and a native process. The host view shows historical and live time-series data for usage as well as the consuming processes. This information allows us to better plan the migration, as all depending services must be considered during the migration.

    ![lab1 smartscape](img/azure-grail-lab1/lab1-smartscape.png)

    Referring to the picture above: 
    - On the horizontal axis, it visualizes all ingoing and outgoing call relationships within each tier
    - On the vertical axis, it displays full-stack dependencies across all tiers
        * Data center
        * Hosts
        * Process
        * Service
        * Application

### Tasks to complete this step

#### Review the data on the Smartscape screen
- Let’s see how Dynatrace can visualize these processes using Smartscape.
    1. Be sure you are on the `dt-orders-monolith` host page
    1. Just click on the `...` box on the to the right of the host name
    1. pick `Smartscape view` menu option
    1. this will open Smartscape filtered to this Host Instance
    ![lab1 host smartscape](img/azure-grail-lab1/lab1-host-smartscape.png)
- Feel free to explore the Smartscape.



## Process
<!-- Duration: 4 min -->
In the Smartscape view, we saw the visualizations of the relationships in vertical stack and as well as the relationships spatially. Now let’s view the processes and services running on the host.

As you plan your migration, you need more than just host level metrics.  Knowing the details for each service, **BEFORE** you change it, will lower the risk of impacting the business.

!!! tip
    👍 `How this helps`

    Very quickly you have seen what processes and services are running on a host AND more importantly, what processes and services call (outbound) and are being called (inbound).  Having a real-time picture is certainly more accurate than an out of date documentation.

### Tasks to complete this step

1. Review the data on the Process screen 
    - Return back to the host view for the host with the prefix of `dt-orders-monolith` and locate the `Processes Analysis` section on far right hand side of the screen.
    - Click on the 2nd `monolith-frontend` process to open the process detail view.
    ![lab1 host view proc](img/azure-grail-lab1/lab1-host-view-proc.png)
    - You should be on the process page where you will see information for this process.  Follow the picture below to locate the following:
        1. Click on the `Properties and tags` line to toggle on/off to see additional data 
        1. Notice the properties such as open ports
        1. On the info graphic:
            * Click to view the processes that call this process (Inbound)
            * Click to view the services that are served by this process. In this case there are multiple
            * Click to view the processes that this process calls (Outbound)
            * Click to view the Process specific metrics
        1. Did you notice Docker??
        ![lab1 process view](img/azure-grail-lab1/lab1-process-view.png)
            !!! tip
    📓  Dynatrace automatically recognizes many common processes like Tomcat and will capture process specific metrics such as JVM garbage collection. See a list of supported technologies, languages and containers in the [ Dynatrace documentation](https://docs.dynatrace.com/docs/setup-and-configuration/technology-support){target="_blank"} 

            !!! tip
    📓`Dynatrace and containers`

                In the picture above, the arrow shows the properties for Docker.

                Our sample app was built as a Docker container and Dynatrace hooks into containers and provides code for injecting OneAgent into containerized process.  

                `How Dynatrace monitors containers`

                ![lab1 docker monitoring](img/azure-grail-lab1/lab1-docker-monitoring.png)

                There’s no need to modify your Docker images, modify run commands, or create additional containers to enable Docker monitoring. Simply install OneAgent on your hosts that serve containerized applications and services. Dynatrace automatically detects the creation and termination of containers and monitors the applications and services contained within those containers. 

            !!! tip
    📓
                You can read more about Dynatrace Docker Monitoring [ here ](https://www.dynatrace.com/support/help/technology-support/cloud-platforms/other-platforms/docker/basic-concepts/how-dynatrace-monitors-containers/){target="_blank"} and technical details [ here](https://docs.dynatrace.com/docs/platform-modules/infrastructure-monitoring/container-platform-monitoring/docker-monitoring){target="_blank"} 

2. Review the data on the Services screen
    - Now Let’s review a specific service.
        1. Click the `services` square above the host infographic to open the list of services
        1. From the list of services, choose the `frontend`
        ![lab1 pick service](img/azure-grail-lab1/lab1-pick-service.png)
    - You should be on the service page where you will see information for this specific service.  Follow the picture below to locate the following:
        1. Click on the `Properties` line to toggle on/off to see additional data
        1. Click to view the services that call this service (Inbound)
        1. Click to view the services that this service calls (Outbound)
        ![lab1 service view](img/azure-grail-lab1/lab1-service-view.png)

## Services
<!-- Duration: 4 min -->
Web applications consist of web pages that are served by web servers and web application processes, for example Tomcat. Web and mobile applications are built upon services that process requests like web requests, web service calls, and messaging. 

Such "server-side services" can take the form of web services, web containers, database requests, custom services, and more. Services may in turn call other services such as web services, remote services, and databases services.

!!! tip
    👍 `How this helps`

    As you plan your migration, it is important to gain a complete picture of interdependency to the rest of the environment architecture at host, processes, services, application perspectives. Since time is always scarce, being able to do this in a single place can shorten assessment timelines. 

### Tasks to complete this step
1. Review the Services being monitored. Let’s now take a look at all the services being monitored by selecting  `Services` App from the left side Dynatrace menu.
    ![lab1 apps services](img/azure-grail-lab1/lab1-apps-services.png)
    <!--
    - In the management zone drop down, choose `dt-orders-monolith`. 
    ![lab1 pick monolith mz](img/azure-grail-lab1/lab1-pick-monolith-mz.png)
    -->
    - The services list should now look like this:
    ![lab1 trans services](img/azure-grail-lab1/lab1-trans-services.png)
    
    - Choose the `frontend` service.
    - On the `frontend` service page, find the `Key Requests/endpoints` section on the right and click the `Top web Requests` button to see what it calls. 
    ![lab1 top web requests](img/azure-grail-lab1/lab1-top-web-requests.png)
        - On this page you can view the transactions as time-series charts.
            ![lab1 dynamic requests chart](img/azure-grail-lab1/lab1-dynamic-requests-chart.png)
        - On this page you can view the top web requests by count.  You should recognize the URLs from the sample app!
            ![lab1 top web request list](img/azure-grail-lab1/lab1-top-web-request-list.png)
        - You can also view top web request by Response Time by simply changing the metric to Response Time By clicking on one of the requests.
            ![lab1 resp time filter](img/azure-grail-lab1/lab1-resp-time-filter.png)


## Analyze serviceflow
<!-- Duration: 5 min -->
We just saw one way to review process and service communication, but let’s look at how Dynatrace understands your applications’ transactions from end to end and visualizes through `Service Backtraces` and `Service flows`.

* With `Service flow`, you see the flow of service calls **FROM** a service, request, or their filtered subset. Along with the specific services that are triggered, you can also see how each component of a request contributes to the overall response time.

* With `Service backtrace`, you see the calls **TO** a service.

!!! tip
    👍 `How this helps`

    Knowing the type of downstream services called, executed statements, and amount of data transferred during regular hours of operation allows for better planning and prioritization. 

### Tasks to complete this step
- Review the Service Flow 
    1. Return to the `frontend` service.  You can use the `breakcrumb` menu as shown below.
        ![lab1 navigate to frontend upd](img/azure-grail-lab1/lab1-navigate-to-frontend-upd.png)
    1. On the `frontend` service page, locate the `Topology` section on the right, and then click the `Service Flow` button. 
        ![lab1 service flow arrow upd](img/azure-grail-lab1/lab1-service-flow-arrow-upd.png)
- Response time perspective
    - You should now be on the **Service flow** page.
    - Right away, we can see how this application is structured:  
        * Frontend calls backend
        * Backend calls database
            ![lab1 service flow](img/azure-grail-lab1/lab1-service-flow.png)

    - Refer to the numbers in the picture above:
        1. The timeframe defaults to 10 minutes but can be adjusted. 
        1. We are viewing the data from a **Response time perspective**. Shortly, we will review the **Throughput perspective**.
        1. Click on the boxes to expand the response time metrics. We can see that most of the time is spent in the backend service.
        1. Even though there are a few calls to the database for every backend service request, only a very small amount of the response time is spent in the database. 

- Throughput perspective
    ![lab1 service flow tp](img/azure-grail-lab1/lab1-service-flow-tp.png)
    - Refer to the numbers in the picture above:
        1. The timeframe defaults to 10 minutes but can be adjusted
        1. Change to the **Throughput** perspective by clicking on the box
        1. Click on the boxes to expand the metrics to see the number of requests and average response times going to the backend sevice
        1.  We can see the number of requests to `backend` database

<!---

##  Analyze service backtrace
<!-- Duration: 5 min -->
Dynatrace understands your applications transactions from end to end. This transactional insight is visualized several ways like the backtrace. 

The backtrace tree view represents the sequence of services that led to this service call, beginning with the page load or user action in the browser.

!!! tip
    👍 How this helps

    Using the service flow and service backtrace, these two tools give you a complete picture of interdependency to the rest of the environment architecture at host, processes, services, application perspectives.  

### Tasks to complete this step
1. Review the Service Backtrace 
- Click on the `Services` left side Dynatrace menu.
- Pick the `backend` service.
![lab1 trans services db](img/azure-grail-lab1/lab1-trans-services-db.png)
- On the `backend` service, click on the `Analyze Backtrace` button.
![lab1 service backtrace arrow upd](img/azure-grail-lab1/lab1-service-backtrace-arrow-upd.png)

    !!! tip
    📓 You should be on the service backtrace page where you will see information for this specific service. 

    !!! tip
    📓 If you click on any of the rows in the backtrace, the bottom portion of the page will expand.

        ![lab1 service backtrace arrows](img/azure-grail-lab1/lab1-service-backtrace-arrows.png) 



!!! tip
    📓 This will get more interesting in the next lab, but for the monolith backend, we can see that the backtrace is as follows:<br>
    1. The starting point is the `backend`  <br>
    2. `backend` is called by the `frontend` service  <br>
    3. `ApacheJMeter` traffic from the load generator script <br>
    4. You may also see browser traffic to the **frontend** from the `My web application`.  If you don't that is OK. 


-->

## Databases
<!-- Duration: 3 min -->
As you plan your migration, Database observability is critical to a successful plan. Knowing the type of access, executed statements, and amount of data transferred during regular hours of operation allows for better migration planning and prioritization of the move groups. In some cases, you may decide to not migrate this database in favor of other services or databases that are less complex to migrate due to fewer dependencies.

!!! tip
    👍 How this helps

    When monitoring database activity, Dynatrace shows you which database statements are executed most often and which statements take up the most time. You can also see which services execute the database statements, what will be direct input to migration planning, and prioritization of the move groups.

    Dynatrace monitors all the popular databases like SQL Server, Oracle, and MongoDB. See [Dynatrace documentation ](https://www.dynatrace.com/platform/database-monitoring/){target="_blank"} for more details on platform support.

### Tasks to complete this step
1.  Navigate to the Database screen
    - Lets get back to the `backend` service. One way is to go back to the `Services` left side Dynatrace menu and then pick the `backend` service for the `dt-orders-monolith` management zone.
    - On the `backend` service page, click on the `[embedded]` database under the `Topology` section to open the database service page. 
    ![lab1 pick db upd](img/azure-grail-lab1/lab1-pick-db-upd.png)

2. Review the Database screen
    - The sample application uses an [In memory Java relational database](http://hsqldb.org/){target="_blank"}.  On this page you can explore the database process like
        1. What services call this database
        1. Database availability
        1. View individual SQL statements
        1. Various Database metric  
        ![lab1 database upd](img/azure-grail-lab1/lab1-database-upd.png)


## Technologies View
<!-- Duration: 3 min -->
By default, Dynatrace gives you FullStack horizontal (who talks to whom) and vertical (what runs on what) dependency visibility as part of Dynatrace Smartscape! All without a single line of code or configuration change – just by installing the OneAgent

Seeing which processes make up the monolith has been an eye-opener for many teams that have done this exercise. “Oh – we completely forgot about the dependency to this legacy process we introduced 5 years ago!” – that’s a common thing you hear!

As you plan your migration, knowing what technologies make up your eco-system is key so that you can decide whether to migrate, refactor or replace certain services.

The workshop is somewhat limited, so here is an example from another environment.

![lab1 technology demo](img/azure-grail-lab1/lab1-technology-demo.png)

!!! tip
    👍 How this helps

    This is another out the box feature that helps you understand what technologies are in your environment with a heat map presentation that shows to what degree they exist. 


### Tasks to complete this step
1. Review the Technologies view 
- Click on the **Technology and processes Classic** App on the left side menu within Dynatrace to view the technologies that OneAgent was able to automatically discover and instrument.
    ![lab1 technology](img/azure-grail-lab1/lab1-technology.png)
- Make sure your management zone filter is set to `All` so that you see everything
    ![lab1 mz filter off](img/azure-grail-lab1/lab1-mz-filter-off.png)
- In the filter box, type `tag`, choose `stage`, and the value of `production`. It should look like this:
    ![lab1 technology filter](img/azure-grail-lab1/lab1-technology-filter.png)


### Planning Ahead

You can always click into the `Hub` menu within Dynatrace to learn about the many technologies that Dynatrace supports.  This list is in sync and constantly updated in conjunction with the [Dynatrace website hub page](https://www.dynatrace.com/hub){target="_blank"}


## Summary
<!-- Duration: 2 min -->
By just installing the OneAgent, we have now gained a detailed topological view of sample application from the both the infrastructure and application tiers and we are now ready to tackle our adoption to the cloud armed with the answers we need.

* **Right Priority** - We now understand the complexity and interdependency of services and components to the rest of the environment architecture
* **Right-Sizing the environment** - We now understanding which resources are required to move along with their required resource consumption patterns
* **Best Migration Strategy** - We now understand the current end-to-end transactions through architecture and can choose the best migration strategy (rehost, refactor, rearchitect, rebuild)

### Checklist

In this section, you should have completed the following:

✅ Review Dynatrace OneAgent

✅ Review real-time data now available for the sample application

✅ Review how Dynatrace helps with modernization planning

<!--
!!! tip
    🏫 - Please update the Tracking Spreadsheet upon completing this task. 
-->
