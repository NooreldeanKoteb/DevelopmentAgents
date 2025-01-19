from datetime import datetime
from enum import Enum, auto
from pydantic import Field
from core.schemas.base import TimestampedSchema, MetadataSchema
from typing import List, Dict, Optional

class AgentMode(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    DEBUG = "debug"
    MAINTENANCE = "maintenance"
    LEARNING = "learning"

class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPING = "stopping"
    SHUTTING_DOWN = "shutting_down"
    RESTARTING = "restarting"
    RECOVERING = "recovering"
    PAUSED = "paused"
    INITIALIZING = "initializing"

class AgentType(str, Enum):
    # CTO = "cto" #chief technology officer

    STRATEGIST = "strategist" # previous Product Owner
    DIRECTOR = "director" # previous Project Manager
    OPERATOR = "operator" # previous System Agent
    DEVELOPER = "developer" # previous Code Agent
    CUSTODIAN = "custodian" # previous Reviewer Agent
    GUARDIAN = "guardian" # previous QA Agent
    DISTRIBUTOR = "distributor" # previous Deployment Agent
    CURATOR = "curator" # previous Documentation Agent
    SPECIALIST = "specialist" # previous Knowledge Agent
    DESIGNER = "designer" # previous UI/UX Agent
    RESOLVER = "resolver" # previous Debug Agent
    
    # Future Agents
    SECURITY_AGENT = "security_agent"
    PERFORMANCE_AGENT = "performance_agent"
    SCALABILITY_AGENT = "scalability_agent"
    COST_OPTIMIZATION_AGENT = "cost_optimization_agent"
    ETHICS_AGENT = "ethics_agent"
    ACCESSIBILITY_AGENT = "accessibility_agent"
    LOCALIZATION_AGENT = "localization_agent"



    # # Extreme Future Agents
    # CEO = "ceo" #chief executive officer
    
    # CMO = "cmo" #chief marketing officer
    # MARKETING = "marketing"
    # SALES = "sales"
    # CUSTOMER_RELATIONS = "customer_relations"
    # CUSTOMER_SUCCESS = "customer_success"
    # CUSTOMER_SUPPORT = "customer_support"
    # CUSTOMER_EXPERIENCE = "customer_experience"
    # DATA_ANALYTICS = "data_analytics"
    
    # CSO = "cso" #chief security officer
    # SECURITY = "security"
    # PRIVACY = "privacy"
    # DATA_PROTECTION = "data_protection"
    # DATA_SECURITY = "data_security"
    # DATA_INTEGRITY = "data_integrity"
    

    # CFO = "cfo" #chief financial officer
    # FINANCE = "finance"
    # ACCOUNTING = "accounting"
    # BUDGETING = "budgeting"
    # FINANCIAL_PLANNING = "financial_planning"
    # INVESTMENT = "investment"
    # INVENTORY = "inventory"
    # INVOICING = "invoicing"
    # PAYROLL = "payroll"
    # TAXES = "taxes"

    # COO = "coo" #chief operating officer
    # OPERATIONS = "operations"
    # LOGISTICS = "logistics"
    # SUPPLY_CHAIN = "supply_chain"


class TaskType(Enum):
    # Strategist Tasks
    STRATEGIST_VISION = "strategist_vision"
    STRATEGIST_REQUIREMENTS = "strategist_requirements"
    STRATEGIST_BACKLOG = "strategist_backlog"
    STRATEGIST_ROADMAP = "strategist_roadmap"
    STRATEGIST_RELEASE_PLAN = "strategist_release_plan"
    STRATEGIST_PLAN = "strategist_plan"
    STRATEGIST_REVIEW = "strategist_review"
    
    # Director Tasks
    DIRECTOR_PROJECT_CREATION = "director_project_creation"
    DIRECTOR_PROJECT_UPDATE = "director_project_update"
    DIRECTOR_PROJECT_DELETION = "director_project_deletion"
    DIRECTOR_PROJECT_STATUS = "director_project_status"
    DIRECTOR_PROJECT_SCHEDULE = "director_project_schedule"

    DIRECTOR_PROJECT_PHASE_CREATION = "director_project_phase_creation"
    DIRECTOR_PROJECT_PHASE_UPDATE = "director_project_phase_update"
    DIRECTOR_PROJECT_PHASE_DELETION = "director_project_phase_deletion"
    
    DIRECTOR_PROJECT_INITIAL_SETUP = "director_project_initial_setup" # commands for operator to setup project
    
    DIRECTOR_TASK_CREATION = "director_task_creation"
    DIRECTOR_TASK_ASSIGNMENT = "director_task_assignment"
    DIRECTOR_TASK_UPDATE = "director_task_update"
    DIRECTOR_TASK_DELETION = "director_task_deletion"
    DIRECTOR_TASK_COMPLETION = "director_task_completion" # command sent to director when agent completes task
    
    DIRECTOR_AGENT_REQUEST = "director_project_agent_request"
    DIRECTOR_PROJECT_REVIEW = "director_project_review"

    #Operator Tasks
    OPERATOR_RUN_COMMAND = "operator_run_command"
    OPERATOR_CREATE_FILE = "operator_create_file"
    OPERATOR_DELETE_FILE = "operator_delete_file"
    OPERATOR_UPDATE_FILE = "operator_update_file"
    OPERATOR_READ_FILE = "operator_read_file"
    OPERATOR_WRITE_FILE = "operator_write_file"
    OPERATOR_RESTART = "operator_restart"
    OPERATOR_UPGRADE = "operator_upgrade"
    OPERATOR_DOWNLOAD_FILE = "operator_download_file"
    OPERATOR_UPLOAD_FILE = "operator_upload_file"
    OPERATOR_COPY_FILE = "operator_copy_file"
    OPERATOR_MOVE_FILE = "operator_move_file"
    OPERATOR_RENAME_FILE = "operator_rename_file"
    OPERATOR_DELETE_DIRECTORY = "operator_delete_directory"
    OPERATOR_CREATE_DIRECTORY = "operator_create_directory"
    OPERATOR_LIST_FILES = "operator_list_files"
    OPERATOR_LIST_DIRECTORIES = "operator_list_directories"
    OPERATOR_CHANGE_DIRECTORY = "operator_change_directory"
    OPERATOR_CHANGE_PERMISSIONS = "operator_change_permissions"
    OPERATOR_CHECK_FILE_EXISTS = "operator_check_file_exists"
    OPERATOR_CHECK_DIRECTORY_EXISTS = "operator_check_directory_exists"
    OPERATOR_SYSTEM_STATUS = "operator_system_status"
    
    # Version Control and installation
    OPERATOR_SETUP_VERSION_CONTROL = "operator_setup_version_control"
    OPERATOR_COMMIT_CHANGES = "operator_commit_changes"
    OPERATOR_PUSH_CHANGES = "operator_push_changes"
    OPERATOR_PULL_CHANGES = "operator_pull_changes"
    OPERATOR_MERGE_BRANCHES = "operator_merge_branches"
    OPERATOR_CREATE_BRANCH = "operator_create_branch"
    OPERATOR_DELETE_BRANCH = "operator_delete_branch"
    OPERATOR_LIST_BRANCHES = "operator_list_branches"
    OPERATOR_CHECKOUT_BRANCH = "operator_checkout_branch"
    OPERATOR_CLONE_REPOSITORY = "operator_clone_repository"
    
    OPERATOR_INSTALL_DEPENDENCIES = "operator_install_dependencies"
    OPERATOR_UPDATE_DEPENDENCIES = "operator_update_dependencies"
    OPERATOR_UNINSTALL_DEPENDENCIES = "operator_uninstall_dependencies"
    OPERATOR_CHECK_DEPENDENCIES = "operator_check_dependencies"
    OPERATOR_LIST_DEPENDENCIES = "operator_list_dependencies"
    


    # Developer Tasks
    DEVELOPER_CREATE_STRUCTURE = "developer_create_structure"
    DEVELOPER_GENERATE_BOILERPLATE = "developer_generate_boilerplate"
    DEVELOPER_GENERATE_TODO = "developer_generate_todo"
    DEVELOPER_GENERATE_CODE = "developer_generate_code"
    DEVELOPER_HANDLE_ERRORS = "developer_handle_errors"
    DEVELOPER_GENERATE_COMMENTS = "developer_generate_comments"
    DEVELOPER_SUBMIT_CODE = "developer_submit_code"
    DEVELOPER_REFACTOR = "developer_refactor"
    DEVELOPER_OPTIMIZE = "developer_optimize"

    # Custodian Tasks  
    CUSTODIAN_CODE_REVIEW = "custodian_code_review"

    # Guardian Tasks
    GUARDIAN_TEST_GENERATION = "guardian_test_generation"
    GUARDIAN_TEST_EXECUTION = "guardian_test_execution"

    # Distributor Tasks
    DISTRIBUTOR_DEPLOYMENT_CREATION = "distributor_deployment_creation"
    DISTRIBUTOR_DEPLOYMENT_REVIEW = "distributor_deployment_review"
    DISTRIBUTOR_DEPLOYMENT_UPDATE = "distributor_deployment_update"
    DISTRIBUTOR_DEPLOYMENT_EXECUTION = "distributor_deployment_execution"

    # Curator Tasks
    CURATOR_DOCUMENTATION_CREATION = "curator_documentation_creation"
    CURATOR_DOCUMENTATION_REVIEW = "curator_documentation_review"
    CURATOR_DOCUMENTATION_UPDATE = "curator_documentation_update"

    # Specialist Tasks
    SPECIALIST_RESEARCH = "specialist_research"
    SPECIALIST_RESPONSE = "specialist_response"
    SPECIALIST_STORAGE = "specialist_storage"
    SPECIALIST_RETRIEVAL = "specialist_retrieval"
    SPECIALIST_ANALYSIS = "specialist_analysis"
    SPECIALIST_SECURITY = "specialist_security"
    SPECIALIST_OPTIMIZATION = "specialist_optimization"
    SPECIALIST_REFACTORING = "specialist_refactoring"

    # Designer Tasks
    DESIGNER_UI_CREATION = "designer_ui_creation"
    DESIGNER_UX_CREATION = "designer_ux_creation"
    DESIGNER_UI_REVIEW = "designer_ui_review"
    DESIGNER_UX_REVIEW = "designer_ux_review"
    DESIGNER_UI_UPDATE = "designer_ui_update"
    DESIGNER_UX_UPDATE = "designer_ux_update"

    # Resolver Tasks
    RESOLVER_DEBUG = "resolver_debug"
    RESOLVER_ERROR_HANDLING = "resolver_error_handling"


    # Global Topics
    AGENT_HEARTBEAT = "agent_heartbeat"
    AGENT_STATUS = "agent_status"
    AGENT_ASK_QUESTION = "agent_ask_question"
    AGENT_ANSWER_QUESTION = "agent_answer_question"
    UNKNOWN = "unknown"
