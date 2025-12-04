questions = {
    "General Questions": [
        
  {
    "id": 1,
    "question": "Project Name",
    "description": "Project Name",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 2,
    "question": "Business Purpose",
    "description": "Storage migration/ Project Business Objective",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 3,
    "question": "Business Criticality",
    "description": "Business Criticality (with description about the priority)",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "Lower priority applications"},
      {"weight": 2, "text": "High Criticality Applications without sustaining serious damage to operations and revenue"},
      {"weight": 3, "text": "Mission Critical with significant business impact to revenue and reputation"}
    ]
  },
  {
    "id": 4,
    "question": "Business Owner(s)",
    "description": "Business /Project Owner",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 5,
    "question": "Storage Owner(s)",
    "description": "Storage Owner",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 6,
    "question": "SME: Storage Infrastructure contact (one or multiple)",
    "description": "Infrastructure Support Team (Email ID / DL of Infrastructure support contacts)",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 7,
    "question": "SME: Networking contact and vendor (one or multiple)",
    "description": "Networking Support Team (Email ID / DL of Networking support contacts)",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 8,
    "question": "SME: App Data Tier contact (one or multiple)",
    "description": "Application Database Team (Email ID / DL of Application Database support contacts)",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 9,
    "question": "Estimated total end-users",
    "description": "Number of users accessing the application",
    "type": "NUMBER",
    "options": []
  },
  {
    "id": 10,
    "question": "Estimated total remote users",
    "description": "Remote users- working remotely (geographically)",
    "type": "NUMBER",
    "options": []
  },
  {
    "id": 11,
    "question": "Is the architecture well known and documented? If documented, please provide link to the architecture diagram if available or attach the document to this excel.",
    "description": "",
    "type": "FILE_UPLOAD",
    "options": []
  },
  {
    "id": 12,
    "question": "Frequency of use by end-users (e.g. daily or certain time of a month)",
    "description": "",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "24/7 Continuous Use"},
      {"weight": 2, "text": "Intermittent Use"},
      {"weight": 3, "text": "Business Hours Use"},
      {"weight": 4, "text": "Peak-Time Use"},
      {"weight": 5, "text": "Seasonal Use"},
      {"weight": 6, "text": "Event-Driven Use"},
      {"weight": 7, "text": "Continuous Use"},
      {"weight": 8, "text": "Global Use Across Time Zones"},
      {"weight": 9, "text": "Other (specify)"}
    ]
  },
  {
    "id": 13,
    "question": "List Regulatory Requirements (if any)",
    "description": "",
    "type": "MULTISELECT",
    "options": [
      {"weight": 1, "text": "GDPR"},
      {"weight": 2, "text": "HIPAA"},
      {"weight": 3, "text": "PCI DSS"},
      {"weight": 4, "text": "CCPA"},
      {"weight": 5, "text": "FedRAMP"},
      {"weight": 6, "text": "COPPA"},
      {"weight": 7, "text": "ECPA"},
      {"weight": 8, "text": "FINRA"},
      {"weight": 9, "text": "Other (specify)"}
    ]
  },
  {
    "id": 14,
    "question": "List Operational SLAs",
    "description": "",
    "type": "MULTISELECT",
    "options": [
      {"weight": 1, "text": "Availability SLA"},
      {"weight": 2, "text": "Response Time SLA"},
      {"weight": 3, "text": "Incident Response SLA"},
      {"weight": 4, "text": "Resolution Time SLA"},
      {"weight": 5, "text": "Backup and Restore SLA"},
      {"weight": 6, "text": "Security Incident Response SLA"},
      {"weight": 7, "text": "Disaster Recovery SLA"},
      {"weight": 8, "text": "Vendor or Third-Party SLA"},
      {"weight": 9, "text": "Other (specify)"}
    ]
  },
  {
    "id": 15,
    "question": "List Regular Maintenance Window(s)",
    "description": "",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 16,
    "question": "List Blackout Periods (freeze periods)",
    "description": "",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 17,
    "question": "Storage Licensing Model",
    "description": "",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "Enterprise Licensing Agreements (ELA)"},
      {"weight": 2, "text": "Per Processor/Core Licensing"},
      {"weight": 3, "text": "Client Access License (CAL)"},
      {"weight": 4, "text": "Virtual Machine (VM) Licensing"},
      {"weight": 5, "text": "Container-Based Licensing"},
      {"weight": 6, "text": "Cluster or High Availability Licensing"},
      {"weight": 7, "text": "Subscription-Based Server"},
      {"weight": 8, "text": "Other (specify) Licensing"}
    ]
  },
  {
    "id": 18,
    "question": "Describe current reliability & performance (are there any special requirements)",
    "description": "",
    "type": "TEXT",
    "options": []
  },
  {
    "id": 19,
    "question": "List any future planned changes.",
    "description": "",
    "type": "TEXT",
    "options": []
  }
],
"Technical Questions": [
  {
    "id": 20,
    "question": "What are current Storage Infrastructure in used?",
    "description": "DAS Storage is directly attached to a server or a computing device, Low latency, simplicity.",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Direct-Attached Storage (DAS)"},
      {"weight": 2, "text": "Network Attached Storage (NAS)"},
      {"weight": 3, "text": "Storage Area Network (SAN)"},
      {"weight": 4, "text": "Hyperconverged Infrastructure (HCI)"},
      {"weight": 5, "text": "Software-Defined Storage (SDS)"},
      {"weight": 6, "text": "Cloud Storage"},
      {"weight": 7, "text": "More than one from above Options"}
    ],
    "other_option": {
      "text": "Other than above",
      "input_type": "TEXT"
    }
  },
  {
    "id": 21,
    "question": "Can you provide the specific models of the storage arrays currently in use?",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Dell EMC"},
      {"weight": 2, "text": "NetApp"},
      {"weight": 3, "text": "HPE"},
      {"weight": 4, "text": "IBM"},
      {"weight": 5, "text": "Hitachi"}
    ],
    "other_option": {
      "text": "Other than above",
      "input_type": "TEXT"
    }
  },
  {
    "id": 22,
    "question": "What is the span of the Storage AMC support?",
    "description": "",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "End of support"},
      {"weight": 2, "text": "No AMC Support"},
      {"weight": 3, "text": "Support till 2024 - 25"},
      {"weight": 4, "text": "Support till 2025 - 26"}
    ]
  },
  {
    "id": 23,
    "question": "What is the storage capacity in terms of data size measured in?",
    "description": "It is commonly used to quantify the capacity of smaller storage devices like USB drives, memory cards, and smartphone storage.",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "GB (1 GB to 1024 GB)"},
      {"weight": 2, "text": "TB (1 TB to 1024 TB)"},
      {"weight": 3, "text": "PB (1 PB to 1024 PB)"}
    ]
  },
  {
    "id": 24,
    "question": "Where does the workload originate from?",
    "description": "Applications and software generate data as they run and perform operations.",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Application"},
      {"weight": 2, "text": "Database"},
      {"weight": 3, "text": "Backup Data"},
      {"weight": 4, "text": "Logs"},
      {"weight": 5, "text": "User Input"},
      {"weight": 6, "text": "Any File Store"}
    ],
    "other_option": {
      "text": "Other than above",
      "input_type": "TEXT"
    }
  },
  {
    "id": 25,
    "question": "What types of data are present in the storage system?",
    "description": "",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Documents"},
      {"weight": 2, "text": "Images"},
      {"weight": 3, "text": "Videos"},
      {"weight": 4, "text": "Logs"},
      {"weight": 5, "text": "Databases"},
      {"weight": 6, "text": "Application"},
      {"weight": 7, "text": "Voice"}
    ],
    "other_option": {
      "text": "Other than above",
      "input_type": "TEXT"
    }
  },
  {
    "id": 26,
    "question": "Are there any specific pain points or challenges you are facing with the current storage architecture?",
    "description": "While the current architecture may provide functionality, it's crucial to be aware of potential security vulnerabilities.",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Security and Vulnerabilities"},
      {"weight": 2, "text": "Performance and Scalability"},
      {"weight": 3, "text": "Legacy / Obsolescence technology"},
      {"weight": 4, "text": "Operational Challenges"},
      {"weight": 5, "text": "Rapidely Growing File Share"},
      {"weight": 6, "text": "HA and DR requerment"}
    ],
    "other_option": {
      "text": "Other than above",
      "input_type": "TEXT"
    }
  },
  {
    "id": 27,
    "question": "What storage technologies are employed in your current storage arrays?",
    "description": "",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "RAID Configuration"},
      {"weight": 2, "text": "SSD"},
      {"weight": 3, "text": "SAS HDD"},
      {"weight": 4, "text": "NL SAS"},
      {"weight": 5, "text": "Hybrid Storage"},
      {"weight": 6, "text": "Software-Defined Storage (SDS)"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 28,
    "question": "Do we have any data classification/Labelling available on the files.",
    "description": "Files are labeled based on confidentiality levels, such as public, internal use, confidential, or restricted access.",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Confidentiality Levels"},
      {"weight": 2, "text": "Sensitivity Categories"},
      {"weight": 3, "text": "Regulatory Compliance"},
      {"weight": 4, "text": "User Access Levels"},
      {"weight": 5, "text": "Data Lifecycle Stages"},
      {"weight": 6, "text": "Custom Labels"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 29,
    "question": "What performance metrics are currently monitored for the storage infrastructure?",
    "description": "Tracking the time it takes for data to travel from source to destination.",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Latency"},
      {"weight": 2, "text": "IOPS"},
      {"weight": 3, "text": "Capacity Utilization"},
      {"weight": 4, "text": "Network Bandwidth"},
      {"weight": 5, "text": "Data Transfer Rates"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 30,
    "question": "Which connectivity protocols are used for accessing data from the storage arrays.",
    "description": "Fibre Channel is a high-speed, low-latency protocol commonly used for connecting servers to storage area networks (SANs).",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "FC - Fibre Channel"},
      {"weight": 2, "text": "iSCSI"},
      {"weight": 3, "text": "NFS"},
      {"weight": 4, "text": "NAS"},
      {"weight": 5, "text": "SMB"},
      {"weight": 6, "text": "SAS"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 31,
    "question": "Is there a tiered storage strategy in place, and if so, how is data classified across different storage tiers?",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Centralized Data"},
      {"weight": 2, "text": "Distributed data"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 32,
    "question": "What are the different categories or tiers of data used.",
    "description": "Hot data refers to the subset of data that is actively and frequently accessed or used by applications and users.",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Hot Data"},
      {"weight": 2, "text": "Cool Data"},
      {"weight": 3, "text": "Cold Data"},
      {"weight": 4, "text": "Archive data"},
      {"weight": 5, "text": "Backup Data"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 33,
    "question": "What are the criteria used for classifying data across different storage tiers?",
    "description": "We can create multiple Storage account basis on the type of access data frequency like - Daily access files will use the Hot Tier.",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Access Frequency"},
      {"weight": 2, "text": "Performance Requirements"},
      {"weight": 3, "text": "Data Age and Lifecycle"},
      {"weight": 4, "text": "Regulatory and Compliance Requirements"},
      {"weight": 5, "text": "Data Usage Patterns"},
      {"weight": 6, "text": "Budget and Cost Constraints"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 34,
    "question": "How is redundancy and high availability implemented in the current storage environment?",
    "description": "",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "RAID (Redundant Array of Independent Disks)"},
      {"weight": 2, "text": "Data Backup"},
      {"weight": 3, "text": "System Redundancy"},
      {"weight": 4, "text": "Failover Clustering"},
      {"weight": 5, "text": "Load Balancing"},
      {"weight": 6, "text": "Disaster Recovery Planning"},
      {"weight": 7, "text": "Business Requirement"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 35,
    "question": "Is there a replication mechanism in place for disaster recovery or data distribution?",
    "description": "",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Synchronous Replication"},
      {"weight": 2, "text": "Asynchronous Replication"},
      {"weight": 3, "text": "Snapshot-Based Replication"},
      {"weight": 4, "text": "Continuous Data Protection"},
      {"weight": 5, "text": "Geo-Replication"},
      {"weight": 6, "text": "Multi-Site Replication"},
      {"weight": 7, "text": "Failover and Failback"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 36,
    "question": "What is the data retention period for the stored information?",
    "description": "Data is retained for a brief period, typically for immediate or operational needs.",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "Short-Term Retention(0-3 Months)"},
      {"weight": 2, "text": "Medium-Term Retention(3-6 months)"},
      {"weight": 3, "text": "Long-Term Retention(more than 6 months)"},
      {"weight": 4, "text": "Customized Retention Periods"},
      {"weight": 5, "text": "No Formal Retention Policy"}
    ]
  },
  {
    "id": 37,
    "question": "What is the expected annual data growth rate for the storage infrastructure?",
    "description": "Minimal annual data growth.",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "0-5%"},
      {"weight": 2, "text": "6-10%"},
      {"weight": 3, "text": "11-15%"},
      {"weight": 4, "text": "16-20%"},
      {"weight": 5, "text": "21-25%"},
      {"weight": 6, "text": "26% and above"},
      {"weight": 7, "text": "Stable/No Significant Growth"}
    ]
  },
  {
    "id": 38,
    "question": "Is there any management interfaces or tools are used to administer and monitor the storage arrays, please select yes and provide more details",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Sure"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 39,
    "question": "How old are the existing storage arrays, and what is their expected lifecycle?",
    "description": "The storage arrays are relatively new, with an expected lifecycle of more than 5 years.",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "0-3 Years"},
      {"weight": 2, "text": "3-5 Years"},
      {"weight": 3, "text": "5-7 Years"},
      {"weight": 4, "text": "Unknown/Not Specified"}
    ]
  },
  {
    "id": 40,
    "question": "What is the current utilization percentage of the storage arrays' total capacity?",
    "description": "",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "5 to 10%"},
      {"weight": 2, "text": "10 to 30%"},
      {"weight": 3, "text": "30 to 60%"},
      {"weight": 4, "text": "60 to 80%"},
      {"weight": 5, "text": "80 to 100%"}
    ]
  },
  {
    "id": 41,
    "question": "What compliance and security features are available on the storage arrays.",
    "description": "implementing data encryption and access controls is crucial to safeguard sensitive data and restrict unauthorized access.",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Encryption"},
      {"weight": 2, "text": "Access Controls"},
      {"weight": 3, "text": "Authentication Mechanisms"},
      {"weight": 4, "text": "Auditing and Logging"},
      {"weight": 5, "text": "Secure Protocols"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 42,
    "question": "Are there integrations between the storage arrays and other systems or applications? please select yes and provide more details",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Sure"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 43,
    "question": "Have you encountered any capacity-related issues or constraints? please select yes and provide more details",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Sure"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 44,
    "question": "What is the acceptable downtime for the organization during the migration?",
    "description": "No acceptable downtime.",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "Zero Downtime"},
      {"weight": 2, "text": "Minimal Downtime (Minutes)"},
      {"weight": 3, "text": "Short Downtime (Hours)"},
      {"weight": 4, "text": "Moderate Downtime (Half a Day)"},
      {"weight": 5, "text": "Extended Downtime (Full Day)"},
      {"weight": 6, "text": "Weekend or Off-Peak Downtime"}
    ]
  },
  {
    "id": 45,
    "question": "Are there any storage performance bottlenecks? please select yes and provide more details",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not sure"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 46,
    "question": "Are there dependencies between different sets of data that need to be considered during migration?",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Sure"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 47,
    "question": "What security measures are currently in place for the existing storage environment?",
    "description": "Role-Based Access Control (RBAC): Is there RBAC implemented to ensure that users have appropriate access permissions based on their roles?",
    "type": "MULTISELECT",
    "options": [
      {"weight": 1, "text": "Access Controls"},
      {"weight": 2, "text": "Data Encryption"},
      {"weight": 3, "text": "Authentication Mechanisms"},
      {"weight": 4, "text": "Auditing and Monitoring"},
      {"weight": 5, "text": "Endpoint Security"},
      {"weight": 6, "text": "Network Security"},
      {"weight": 7, "text": "Physical Security"}
    ]
  },
  {
    "id": 48,
    "question": "How are user access and permissions managed in the current storage system?",
    "description": "Is the current storage system using RBAC to assign permissions based on users' roles within the organization?",
    "type": "MULTISELECT",
    "options": [
      {"weight": 1, "text": "Role-Based Access Control (RBAC)"},
      {"weight": 2, "text": "User Groups"},
      {"weight": 3, "text": "Individual User Permissions"},
      {"weight": 4, "text": "Access Control Lists (ACLs)"},
      {"weight": 5, "text": "Multi-Factor Authentication (MFA)"}
    ]
  },
  {
    "id": 49,
    "question": "What is the current backup strategy for data in the existing storage environment?",
    "description": "Perform backups on a daily basis to capture changes made during each day.",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "Daily Backups"},
      {"weight": 2, "text": "Weekly Backups"},
      {"weight": 3, "text": "Incremental Backups"},
      {"weight": 4, "text": "Full Backups"},
      {"weight": 5, "text": "Differential Backups"}
    ]
  },
  {
    "id": 50,
    "question": "What is the reason to migrate to Cloud Storage?",
    "description": "Vendor or AMC support is end and there will be no extending support.",
    "type": "MULTISELECT",
    "options": [
      {"weight": 1, "text": "End of Support"},
      {"weight": 2, "text": "Performance"},
      {"weight": 3, "text": "Scalability"},
      {"weight": 4, "text": "Hardware End of Life"},
      {"weight": 5, "text": "TCO of Storage"},
      {"weight": 6, "text": "HR/DR needs"},
      {"weight": 7, "text": "Easy to manage"},
      {"weight": 8, "text": "Easy to Access over WAN"},
      {"weight": 9, "text": "Security and Compliance needs"}
    ]
  },
  {
    "id": 51,
    "question": "Do we require new Cloud Account/Subscription for this Migration, please select yes and provide more details",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Sure"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 52,
    "question": "Does your organization currently have a Cloud Landing Zone in place? please select yes and provide more details",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Sure"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 53,
    "question": "What is the current on-premises network bandwidth allocated for the storage that is planned for migration?",
    "description": "",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": ">=10 Mbps"},
      {"weight": 2, "text": ">=50 Mbps"},
      {"weight": 3, "text": ">=100 Mbps"},
      {"weight": 4, "text": "<100 Mbps"}
    ]
  },
  {
    "id": 54,
    "question": "Considering the migration to an existing cloud account/subscription, can you confirm if there is established connectivity between our on-premises infrastructure and the designated cloud environment? please select yes and provide more details",
    "description": "",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ]
  },
  {
    "id": 55,
    "question": "If we have to migrate to existing cloud account/subcription than please share the Network bandwidth currently allocated between On-Premises and cloud",
    "description": "",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "50 Mbps"},
      {"weight": 2, "text": "100 Mbps"},
      {"weight": 3, "text": "200 Mbps"},
      {"weight": 4, "text": "500 Mbps"},
      {"weight": 5, "text": "1 Gbps"},
      {"weight": 6, "text": "<= 2 Gbps"},
      {"weight": 7, "text": "Not applicable"}
    ]
  },
  {
    "id": 56,
    "question": "Are there any specific industry regulations or compliance standards that the storage solution must adhere to?",
    "description": "",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "PCI"},
      {"weight": 2, "text": "HIPPA"},
      {"weight": 3, "text": "PII / PCI - DSS"}
    ]
  },
  {
    "id": 57,
    "question": "Are there any geographical considerations or restrictions regarding where your data can be stored?",
    "description": "GDPR may require data to be stored within the European Union.",
    "type": "MULTISELECT_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Regulatory Compliance"},
      {"weight": 2, "text": "Data Residency Requirements"},
      {"weight": 3, "text": "Industry-Specific Considerations"},
      {"weight": 4, "text": "Cross-Border Data Transfer"},
      {"weight": 5, "text": "Data Sensitivity Levels"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 58,
    "question": "Do you have multiple on-premises data centers in our infrastructure? please select yes and provide more details.",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 59,
    "question": "If you operate multiple on-premises data centers, is there established connectivity between these data centers? please select yes and provide more details",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 60,
    "question": "Can you confirm if we currently have an Identity Provider (IDP) in place as part of our cloud migration initiative?",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Not applicable"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Yes"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 61,
    "question": "Which cloud provider are you planning to use for storage?",
    "description": "Organizations typically choose a cloud provider based on various factors such as their specific requirements, budget, existing infrastructure, compliance needs, and the features offered by different cloud platforms.",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "AWS"},
      {"weight": 2, "text": "Azure"},
      {"weight": 3, "text": "GCP"},
      {"weight": 4, "text": "Not Decided"}
    ],
    "other_option": {
      "text": "Other than above option",
      "input_type": "TEXT"
    }
  },
  {
    "id": 62,
    "question": "Are there specific features or services from the cloud provider that are crucial for your storage needs? please select yes and provide more details.",
    "description": "",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 63,
    "question": "Have you estimated the costs associated with cloud storage, including data transfer and retrieval fees? If yes please provide more details.",
    "description": "This information is crucial for planning a better storage migration strategy, allowing us to consider cost implications and optimize the migration process accordingly.",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 64,
    "question": "Are there budget constraints or considerations that may impact the choice of cloud storage services? If yes please provide more details",
    "description": "With this information will guide us in planning the storage migration, ensuring alignment with budgetary constraints and making informed decisions on the choice of cloud storage services",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 65,
    "question": "What is the current on-premises Storage TCO?",
    "description": "If you moving to Cloud storage, we have the below benefits.",
    "type": "MCQ",
    "options": [
      {"weight": 1, "text": "<$10000"},
      {"weight": 2, "text": "$10000-$50000"},
      {"weight": 3, "text": "$50000-$100000"},
      {"weight": 4, "text": "More than $100000"}
    ]
  },
  {
    "id": 66,
    "question": "In TCO Cost have we considered network devices, Non-IT(AC, Infrastracture space etc), Servers, Software, IT-Staff, Security etc.",
    "description": "With this information, we can better understand or Analyze the cost breakdown for each component to understand the distribution of expenses within the TCO.",
    "type": "MCQ_WITH_OTHER",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "other_option": {
      "text": "",
      "input_type": "TEXT"
    }
  },
  {
    "id": 67,
    "question": "Currently are there specific metrics or key performance indicators (KPIs) to track, if yes please upload the document.",
    "description": "We recommend uploading the file for a better understanding of key performance indicators (KPIs)",
    "type": "MCQ_WITH_FILE",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "file_upload": True
  },
  {
    "id": 68,
    "question": "Do you have updated On premises resources inventory(Vcentre report-out, Physical Server etc) if yes please upload the document.",
    "description": "We recommend uploading the resource inventory for a more comprehensive discovery of the on-premise environment",
    "type": "MCQ_WITH_FILE",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "file_upload": True
  },
  {
    "id": 69,
    "question": "Do you currently have updated architecture documentation for the on-premises storage and network infrastructure? if yes please upload the document.",
    "description": "We recommend uploading the architecture documentation file for a better understanding of the on-premise architecture",
    "type": "MCQ_WITH_FILE",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "file_upload": True
  },
  {
    "id": 70,
    "question": "Do we have a storage utilization report available from the storage manager? If yes please upload the document.",
    "description": "We recommend uploading the storage utilization report to facilitate a more informed discussion on capacity planning",
    "type": "MCQ_WITH_FILE",
    "options": [
      {"weight": 1, "text": "Yes"},
      {"weight": 2, "text": "No"},
      {"weight": 3, "text": "Not Applicable"}
    ],
    "file_upload": True
  }
]

}
