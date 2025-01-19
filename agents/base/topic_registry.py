from typing import Dict, List, Callable, Optional, Type
from agents.base.schemas import TopicSubscription
from agents.base.enums import AgentType, TaskType
from core.messaging.message import Message
from pydantic import Field

class TopicRegistry:
    """Central registry of all message topics and their mappings."""
    
    # Global topics that all agents should subscribe to
    GLOBAL_TOPICS = {
        "system.status": TopicSubscription(
            topic="system.status",
            task_type=TaskType.OPERATOR_SYSTEM_STATUS,
            description="System-wide status updates"
        ),
        "system.error": TopicSubscription(
            topic="system.error",
            task_type=TaskType.RESOLVER_ERROR_HANDLING,
            description="System error notifications"
        ),
        "agent.heartbeat": TopicSubscription(
            topic="agent.heartbeat",
            task_type=TaskType.AGENT_HEARTBEAT,
            description="Agent health monitoring"
        )
    }

    # Agent-specific topic subscriptions
    TOPIC_REGISTRY = {
        # Strategist Topics
        "strategist.vision": TopicSubscription(
            topic="strategist.vision",
            task_type=TaskType.STRATEGIST_VISION,
            description="Project vision creation and updates"
        ),
        "strategist.requirements": TopicSubscription(
            topic="strategist.requirements",
            task_type=TaskType.STRATEGIST_REQUIREMENTS,
            description="Project requirements management"
        ),
        "strategist.backlog": TopicSubscription(
            topic="strategist.backlog",
            task_type=TaskType.STRATEGIST_BACKLOG,
            description="Project backlog management"
        ),
        "strategist.roadmap": TopicSubscription(
            topic="strategist.roadmap",
            task_type=TaskType.STRATEGIST_ROADMAP,
            description="Project roadmap planning"
        ),
        "strategist.release": TopicSubscription(
            topic="strategist.release",
            task_type=TaskType.STRATEGIST_RELEASE_PLAN,
            description="Release planning"
        ),

        # Director Topics
        "director.project.create": TopicSubscription(
            topic="director.project.create",
            task_type=TaskType.DIRECTOR_PROJECT_CREATION,
            description="Project creation"
        ),
        "director.project.update": TopicSubscription(
            topic="director.project.update",
            task_type=TaskType.DIRECTOR_PROJECT_UPDATE,
            description="Project updates"
        ),
        "director.task.create": TopicSubscription(
            topic="director.task.create",
            task_type=TaskType.DIRECTOR_TASK_CREATION,
            description="Task creation"
        ),
        "director.task.assign": TopicSubscription(
            topic="director.task.assign",
            task_type=TaskType.DIRECTOR_TASK_ASSIGNMENT,
            description="Task assignment"
        ),

        # Developer Topics
        "developer.code.refactor": TopicSubscription(
            topic="developer.code.refactor",
            task_type=TaskType.DEVELOPER_REFACTOR,
            description="Code refactoring requests"
        ),
        "developer.code.optimize": TopicSubscription(
            topic="developer.code.optimize",
            task_type=TaskType.DEVELOPER_OPTIMIZE,
            description="Code optimization requests"
        ),

        # Custodian Topics
        "custodian.review.request": TopicSubscription(
            topic="custodian.review.request",
            task_type=TaskType.CUSTODIAN_CODE_REVIEW,
            description="Code review requests"
        ),

        # Guardian Topics
        "guardian.test.generate": TopicSubscription(
            topic="guardian.test.generate",
            task_type=TaskType.GUARDIAN_TEST_GENERATION,
            description="Test generation requests"
        ),
        "guardian.test.execute": TopicSubscription(
            topic="guardian.test.execute",
            task_type=TaskType.GUARDIAN_TEST_EXECUTION,
            description="Test execution requests"
        ),

        # Distributor Topics
        "distributor.deployment.create": TopicSubscription(
            topic="distributor.deployment.create",
            task_type=TaskType.DISTRIBUTOR_DEPLOYMENT_CREATION,
            description="Deployment creation"
        ),
        "distributor.deployment.execute": TopicSubscription(
            topic="distributor.deployment.execute",
            task_type=TaskType.DISTRIBUTOR_DEPLOYMENT_EXECUTION,
            description="Deployment execution"
        ),

        # Curator Topics
        "curator.docs.create": TopicSubscription(
            topic="curator.docs.create",
            task_type=TaskType.CURATOR_DOCUMENTATION_CREATION,
            description="Documentation creation"
        ),
        "curator.docs.update": TopicSubscription(
            topic="curator.docs.update",
            task_type=TaskType.CURATOR_DOCUMENTATION_UPDATE,
            description="Documentation updates"
        ),

        # Specialist Topics
        "specialist.research": TopicSubscription(
            topic="specialist.research",
            task_type=TaskType.SPECIALIST_RESEARCH,
            description="Research requests"
        ),
        "specialist.analyze": TopicSubscription(
            topic="specialist.analyze",
            task_type=TaskType.SPECIALIST_ANALYSIS,
            description="Analysis requests"
        ),

        # Designer Topics
        "designer.ui.create": TopicSubscription(
            topic="designer.ui.create",
            task_type=TaskType.DESIGNER_UI_CREATION,
            description="UI design creation"
        ),
        "designer.ux.create": TopicSubscription(
            topic="designer.ux.create",
            task_type=TaskType.DESIGNER_UX_CREATION,
            description="UX design creation"
        ),

        # Resolver Topics
        "resolver.debug": TopicSubscription(
            topic="resolver.debug",
            task_type=TaskType.UNKNOWN,  # Need to add specific debug task type
            description="Debug requests"
        ),

        # Operator Topics
        "operator.command": TopicSubscription(
            topic="operator.command",
            task_type=TaskType.OPERATOR_RUN_COMMAND,
            description="System command execution",
            context={"linux": {
                "run_command": {
                    "command": "{command}"
                },
            }}
        ),
        "operator.file.create": TopicSubscription(
            topic="operator.file.create",
            task_type=TaskType.OPERATOR_CREATE_FILE,
            description="File creation",
            context={"linux": {
                "create_file": {
                    "command": "touch {file_path}"
                }, 
                "create_directory": {
                    "command": "mkdir {directory_path}"
                },
            }}
        ),
        "operator.file.read": TopicSubscription(
            topic="operator.file.read",
            task_type=TaskType.OPERATOR_READ_FILE,
            description="File reading",
            context={"linux": {
                "read_file": {
                    "command": "cat {file_path}"
                },
            }}
        ),
        "operator.file.write": TopicSubscription(
            topic="operator.file.write",
            task_type=TaskType.OPERATOR_WRITE_FILE,
            description="File writing",
            context={"linux": {
                "write_file": {
                    "command": "echo {content} > {file_path}"
                },
            }}
        ),
        "operator.file.update": TopicSubscription(
            topic="operator.file.update",
            task_type=TaskType.OPERATOR_UPDATE_FILE,
            description="File updates",
            context={"linux": {
                "update_file": {
                    "command": "echo {content} > {file_path}"
                },
            }}
        ),
        "operator.file.delete": TopicSubscription(
            topic="operator.file.delete",
            task_type=TaskType.OPERATOR_DELETE_FILE,
            description="File deletion",
            context={"linux": {
                "delete_file": {
                    "command": "rm -f {file_path}"
                },
                "delete_directory": {
                    "command": "rm -rf {directory_path}"
                },
            }}
        ),
        "operator.file.copy": TopicSubscription(
            topic="operator.file.copy",
            task_type=TaskType.OPERATOR_COPY_FILE,
            description="File copying",
            context={"linux": {
                "copy_file": {
                    "command": "cp {source_path} {destination_path}"
                },
                "copy_directory": {
                    "command": "cp -r {source_path} {destination_path}"
                },
            }}
        ),
        "operator.file.move": TopicSubscription(
            topic="operator.file.move",
            task_type=TaskType.OPERATOR_MOVE_FILE,
            description="File moving",
            context={"linux": {
                "move_file": {
                    "command": "mv {source_path} {destination_path}"
                },
                "move_directory": {
                    "command": "mv -r {source_path} {destination_path}"
                },
            }}
        ),
        "operator.file.rename": TopicSubscription(
            topic="operator.file.rename",
            task_type=TaskType.OPERATOR_RENAME_FILE,
            description="File renaming",
            context={"linux": {
                "rename_file": {
                    "command": "mv {old_path} {new_path}"
                },
                "rename_directory": {
                    "command": "mv -r {old_path} {new_path}"
                },
            }}
        )
    }

    # Agent subscription mappings
    AGENT_SUBSCRIPTIONS = {
        AgentType.STRATEGIST: [
            "strategist.vision",
            "strategist.requirements",
            "strategist.backlog",
            "strategist.roadmap",
            "strategist.release"
        ],
        AgentType.DIRECTOR: [
            "director.project.create",
            "director.project.update",
            "director.task.create",
            "director.task.assign"
        ],
        AgentType.DEVELOPER: [
            "developer.code.generate",
            "developer.code.refactor",
            "developer.code.optimize"
        ],
        AgentType.CUSTODIAN: [
            "custodian.review.request"
        ],
        AgentType.GUARDIAN: [
            "guardian.test.generate",
            "guardian.test.execute"
        ],
        AgentType.DISTRIBUTOR: [
            "distributor.deployment.create",
            "distributor.deployment.execute"
        ],
        AgentType.CURATOR: [
            "curator.docs.create",
            "curator.docs.update"
        ],
        AgentType.SPECIALIST: [
            "specialist.research",
            "specialist.analyze"
        ],
        AgentType.DESIGNER: [
            "designer.ui.create",
            "designer.ux.create"
        ],
        AgentType.RESOLVER: [
            "resolver.debug"
        ],
        AgentType.OPERATOR: [
            "operator.command",
            "operator.file.create",
            "operator.file.update"
        ]
    }

    @classmethod
    def get_agent_topics(cls, agent_type: AgentType) -> List[str]:
        """Get all topics an agent should subscribe to."""
        return list(cls.GLOBAL_TOPICS.keys()) + cls.AGENT_SUBSCRIPTIONS.get(agent_type, [])

    @classmethod
    def get_subscription(cls, topic: str) -> Optional[TopicSubscription]:
        """Get subscription details for a topic."""
        return cls.GLOBAL_TOPICS.get(topic) or cls.TOPIC_REGISTRY.get(topic)

    @classmethod
    def get_task_type(cls, topic: str) -> Optional[TaskType]:
        """Get the task type associated with a topic."""
        subscription = cls.get_subscription(topic)
        return subscription.task_type if subscription else None

    @classmethod
    def validate_topic(cls, topic: str) -> bool:
        """Check if a topic is valid."""
        return topic in cls.GLOBAL_TOPICS or topic in cls.TOPIC_REGISTRY