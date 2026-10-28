"""
Report Agent Service
Implements simulation report generation using the ReACT pattern with Zep graph memory.

Features:
1. Generates reports based on simulation requirements and Zep knowledge graph
2. Plans report outline first, then generates section by section
3. Employs multi-turn ReACT thought and action loop per section
4. Supports conversational chat with autonomous retrieval tool invocation
"""

import os
import json
import time
import re
from collections import defaultdict
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..config import Config
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from ..utils.locale import get_language_instruction, t
from .zep_tools import (
    ZepToolsService, 
    SearchResult, 
    InsightForgeResult, 
    PanoramaResult,
    InterviewResult
)

logger = get_logger('lokantra.report_agent')


class ReportLogger:
    """
    Report Agent Detailed Action Logger
    
    Generates an agent_log.jsonl file inside the report directory, logging every action in detail.
    Each line is a complete JSON object containing timestamp, action type, detailed payload, etc.
    """
    
    def __init__(self, report_id: str):
        """
        Initialize logger.
        
        Args:
            report_id: Report ID used to locate the log file path
        """
        self.report_id = report_id
        self.log_file_path = os.path.join(
            Config.UPLOAD_FOLDER, 'reports', report_id, 'agent_log.jsonl'
        )
        self.start_time = datetime.now()
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure directory for log file exists"""
        log_dir = os.path.dirname(self.log_file_path)
        os.makedirs(log_dir, exist_ok=True)
    
    def _get_elapsed_time(self) -> float:
        """Get elapsed time from start in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def log(
        self, 
        action: str, 
        stage: str,
        details: Dict[str, Any],
        section_title: str = None,
        section_index: int = None
    ):
        """
        Log an action record.
        
        Args:
            action: Action type, e.g. 'start', 'tool_call', 'llm_response', 'section_complete', etc.
            stage: Current stage, e.g. 'planning', 'generating', 'completed'
            details: Detailed dictionary payload (untruncated)
            section_title: Current section title (optional)
            section_index: Current section index (optional)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(self._get_elapsed_time(), 2),
            "report_id": self.report_id,
            "action": action,
            "stage": stage,
            "section_title": section_title,
            "section_index": section_index,
            "details": details
        }
        
        # Append to JSONL file
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def log_start(self, simulation_id: str, graph_id: str, simulation_requirement: str):
        """Log report generation start"""
        self.log(
            action="report_start",
            stage="pending",
            details={
                "simulation_id": simulation_id,
                "graph_id": graph_id,
                "simulation_requirement": simulation_requirement,
                "message": t('report.taskStarted')
            }
        )
    
    def log_planning_start(self):
        """Log outline planning start"""
        self.log(
            action="planning_start",
            stage="planning",
            details={"message": t('report.planningStart')}
        )
    
    def log_planning_context(self, context: Dict[str, Any]):
        """Log context information retrieved during planning"""
        self.log(
            action="planning_context",
            stage="planning",
            details={
                "message": t('report.fetchSimContext'),
                "context": context
            }
        )
    
    def log_planning_complete(self, outline_dict: Dict[str, Any]):
        """Log outline planning completion"""
        self.log(
            action="planning_complete",
            stage="planning",
            details={
                "message": t('report.planningComplete'),
                "outline": outline_dict
            }
        )
    
    def log_section_start(self, section_title: str, section_index: int):
        """Log section generation start"""
        self.log(
            action="section_start",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={"message": t('report.sectionStart', title=section_title)}
        )
    
    def log_react_thought(self, section_title: str, section_index: int, iteration: int, thought: str):
        """Log ReACT thought process"""
        self.log(
            action="react_thought",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "thought": thought,
                "message": t('report.reactThought', iteration=iteration)
            }
        )
    
    def log_tool_call(
        self, 
        section_title: str, 
        section_index: int,
        tool_name: str, 
        parameters: Dict[str, Any],
        iteration: int
    ):
        """Log tool call"""
        self.log(
            action="tool_call",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "tool_name": tool_name,
                "parameters": parameters,
                "message": t('report.toolCall', toolName=tool_name)
            }
        )
    
    def log_tool_result(
        self,
        section_title: str,
        section_index: int,
        tool_name: str,
        result: str,
        iteration: int
    ):
        """Log tool call result (complete content, untruncated)"""
        self.log(
            action="tool_result",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "tool_name": tool_name,
                "result": result,  # Full result, untruncated
                "result_length": len(result),
                "message": t('report.toolResult', toolName=tool_name)
            }
        )
    
    def log_llm_response(
        self,
        section_title: str,
        section_index: int,
        response: str,
        iteration: int,
        has_tool_calls: bool,
        has_final_answer: bool
    ):
        """Log LLM response (complete content, untruncated)"""
        self.log(
            action="llm_response",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "response": response,  # Full response, untruncated
                "response_length": len(response),
                "has_tool_calls": has_tool_calls,
                "has_final_answer": has_final_answer,
                "message": t('report.llmResponse', hasToolCalls=has_tool_calls, hasFinalAnswer=has_final_answer)
            }
        )
    
    def log_section_content(
        self,
        section_title: str,
        section_index: int,
        content: str,
        tool_calls_count: int
    ):
        """Log section content generation complete (content only, not entire section finished)"""
        self.log(
            action="section_content",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "content": content,  # Full content, untruncated
                "content_length": len(content),
                "tool_calls_count": tool_calls_count,
                "message": t('report.sectionContentDone', title=section_title)
            }
        )
    
    def log_section_full_complete(
        self,
        section_title: str,
        section_index: int,
        full_content: str
    ):
        """
        Log section generation complete

        The frontend monitors this event to determine when a section is finished and retrieve full content.
        """
        self.log(
            action="section_complete",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "content": full_content,
                "content_length": len(full_content),
                "message": t('report.sectionComplete', title=section_title)
            }
        )
    
    def log_report_complete(self, total_sections: int, total_time_seconds: float):
        """Log report generation complete"""
        self.log(
            action="report_complete",
            stage="completed",
            details={
                "total_sections": total_sections,
                "total_time_seconds": round(total_time_seconds, 2),
                "message": t('report.reportComplete')
            }
        )
    
    def log_error(self, error_message: str, stage: str, section_title: str = None):
        """Log error"""
        self.log(
            action="error",
            stage=stage,
            section_title=section_title,
            section_index=None,
            details={
                "error": error_message,
                "message": t('report.errorOccurred', error=error_message)
            }
        )


class ReportConsoleLogger:
    """
    Report Agent Console Logger
    
    Writes console-style logs (INFO, WARNING, etc.) into console_log.txt inside the report folder.
    These logs represent plaintext console output distinct from structured agent_log.jsonl records.
    """
    
    def __init__(self, report_id: str):
        """
        Initialize console logger.
        
        Args:
            report_id: Report ID used to locate the log file path
        """
        self.report_id = report_id
        self.log_file_path = os.path.join(
            Config.UPLOAD_FOLDER, 'reports', report_id, 'console_log.txt'
        )
        self._ensure_log_file()
        self._file_handler = None
        self._setup_file_handler()
    
    def _ensure_log_file(self):
        """Ensure directory for log file exists"""
        log_dir = os.path.dirname(self.log_file_path)
        os.makedirs(log_dir, exist_ok=True)
    
    def _setup_file_handler(self):
        """Setup file handler to duplicate logs to file"""
        import logging
        
        # Create file handler
        self._file_handler = logging.FileHandler(
            self.log_file_path,
            mode='a',
            encoding='utf-8'
        )
        self._file_handler.setLevel(logging.INFO)
        
        # Use clean console formatting
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        self._file_handler.setFormatter(formatter)
        
        # Add to report_agent loggers
        loggers_to_attach = [
            'lokantra.report_agent',
            'lokantra.zep_tools',
        ]
        
        for logger_name in loggers_to_attach:
            target_logger = logging.getLogger(logger_name)
            # Avoid duplicate handlers
            if self._file_handler not in target_logger.handlers:
                target_logger.addHandler(self._file_handler)
    
    def close(self):
        """Close file handler and remove from loggers"""
        import logging
        
        if self._file_handler:
            loggers_to_detach = [
                'lokantra.report_agent',
                'lokantra.zep_tools',
            ]
            
            for logger_name in loggers_to_detach:
                target_logger = logging.getLogger(logger_name)
                if self._file_handler in target_logger.handlers:
                    target_logger.removeHandler(self._file_handler)
            
            self._file_handler.close()
            self._file_handler = None
    
    def __del__(self):
        """Ensure file handler is closed on destruction"""
        self.close()


class ReportStatus(str, Enum):
    """Report status"""
    PENDING = "pending"
    PLANNING = "planning"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ReportSection:
    """Report section"""
    title: str
    content: str = ""
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content,
            "description": self.description
        }

    def to_markdown(self, level: int = 2) -> str:
        """Convert to Markdown format"""
        md = f"{'#' * level} {self.title}\n\n"
        if self.content:
            md += f"{self.content}\n\n"
        return md


@dataclass
class ReportOutline:
    """Report outline"""
    title: str
    summary: str
    sections: List[ReportSection]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "sections": [s.to_dict() for s in self.sections]
        }
    
    def to_markdown(self) -> str:
        """Convert to Markdown format"""
        md = f"# {self.title}\n\n"
        md += f"> {self.summary}\n\n"
        for section in self.sections:
            md += section.to_markdown()
        return md


@dataclass
class Report:
    """Complete report"""
    report_id: str
    simulation_id: str
    graph_id: str
    simulation_requirement: str
    status: ReportStatus
    outline: Optional[ReportOutline] = None
    markdown_content: str = ""
    created_at: str = ""
    completed_at: str = ""
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "simulation_id": self.simulation_id,
            "graph_id": self.graph_id,
            "simulation_requirement": self.simulation_requirement,
            "status": self.status.value,
            "outline": self.outline.to_dict() if self.outline else None,
            "markdown_content": self.markdown_content,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error": self.error
        }


# ═══════════════════════════════════════════════════════════════
# Prompt template constants
# ═══════════════════════════════════════════════════════════════

# ── Tool Descriptions ──

TOOL_DESC_INSIGHT_FORGE = """\
[Deep Insight Retrieval - Powerful Multi-Dimensional Search]
Our core retrieval function designed for deep analysis:
1. Automatically decomposes your query into multiple sub-questions
2. Retrieves information across dimensions from the simulation graph
3. Integrates semantic search, entity analysis, and relationship chain tracing
4. Returns comprehensive and in-depth evidence

[Use Cases]
- In-depth thematic analysis
- Multi-faceted event understanding
- Gathering robust source evidence to support report sections

[Returns]
- Original relevant facts (directly citable)
- Core entity insights
- Relationship chain analyses"""

TOOL_DESC_PANORAMA_SEARCH = """\
[Panorama Search - Broad Overview]
Used to capture the full landscape of simulation results, especially evolutionary dynamics:
1. Retrieves all relevant nodes and relationships
2. Distinguishes active facts from historical/expired facts
3. Helps trace opinion and behavior evolution over time

[Use Cases]
- Understanding full event development trajectories
- Comparing opinion shifts across simulation stages
- Comprehensive entity and relation mapping

[Returns]
- Active facts (latest simulation results)
- Historical / expired facts (evolution records)
- All involved entities"""

TOOL_DESC_QUICK_SEARCH = """\
[Quick Search - Fast Semantic Retrieval]
Lightweight, fast retrieval tool for direct queries.

[Use Cases]
- Rapid lookup of specific facts
- Verifying individual data points
- Simple information checks

[Returns]
- List of most relevant facts matching query"""

TOOL_DESC_INTERVIEW_AGENTS = """\
[In-Depth Interview - Live Agent Interview (Dual Platform)]
Calls OASIS interview APIs to interview live running simulated agents!
Obtains authentic first-person responses from simulated agents across Twitter and Reddit simultaneously.

Process:
1. Inspects agent profile personas
2. Selects most relevant agent roles (e.g. Students, Media, Officials, etc.)
3. Generates targeted interview questions
4. Executes batch interview API calls across both platforms
5. Synthesizes findings for multi-perspective qualitative insights

[Use Cases]
- Investigating varied stakeholder stances
- Gathering contrasting community sentiments
- Incorporating direct interviewee transcripts into report sections

[Returns]
- Persona metadata of interviewees
- Responses across platforms
- Citable direct quotes
- Interview summary and perspective comparison

[Important] Requires an active running simulation environment."""

# ── Outline Planning Prompt ──

PLAN_SYSTEM_PROMPT = """\
You are an expert author of Future Forecast Reports, possessing an omniscient perspective over the simulated world—observing the behaviors, statements, and interactions of every agent.

[Core Concept]
We built a simulated world and injected specific simulation requirements as variables. The evolutionary outcome of the simulated world represents a forecast of possible future realities. You are observing a preview of the future.

[Your Mission]
Draft a Future Forecast Report addressing:
1. Under our configured scenario, what unfolded in the future?
2. How did varied agent cohorts react and act?
3. What key future trends, emergent dynamics, and risks did this simulation reveal?

[Report Orientation]
- Based on simulation forecast: reveals "what happens if this scenario occurs"
- Focus on forecast outcomes: event trajectories, collective reactions, emergent phenomena, latent risks
- Simulated agent actions predict real-world collective human behaviors
- NOT a retrospective analysis of current real-world status
- NOT a superficial sentiment summary

[Section Count Constraints]
- Minimum 2 sections, maximum 5 sections
- No sub-sections; each section is written as cohesive complete prose
- Keep concise and focused on core forecast discoveries
- Design the section outline based on the simulation findings

Output the report outline in JSON format:
```json
{
    "title": "Report Title",
    "summary": "Report summary (one-sentence overview of core forecast findings)",
    "sections": [
        {
            "title": "Section Title",
            "description": "Description of section content and scope"
        }
    ]
}
```
Note: The sections array MUST contain between 2 and 5 elements!"""

PLAN_USER_PROMPT_TEMPLATE = """\
[Forecast Scenario Setup]
Injected simulation condition / requirement: {simulation_requirement}

[Simulation Scale]
- Participating entities: {total_nodes}
- Relationships generated: {total_edges}
- Entity type distribution: {entity_types}
- Active agents: {total_entities}

[Sample Forecast Facts from Simulation]
{sample_facts}

Review this future rehearsal with an omniscient perspective:
1. Under these conditions, what future state emerged?
2. How did diverse groups and agents respond and behave?
3. What critical future trends and risks were uncovered?

Design the most fitting report structure based on these forecast outcomes.

[Reminder] Report sections: minimum 2, maximum 5, concise and tightly focused on core discoveries."""

# ── Section Generation Prompt ──

SECTION_SYSTEM_PROMPT_TEMPLATE = """\
You are an expert author of Future Forecast Reports, currently writing a chapter of the report.

Report Title: {report_title}
Report Summary: {report_summary}
Forecast Scenario (Simulation Condition): {simulation_requirement}

Current Section: {section_title}
Section Description: {section_description}

[Core Philosophy]
The simulated world is a preview of the future. By injecting specific conditions,
the actions and interactions of agents predict real-world future collective behavior.

Your objectives:
- Reveal what unfolds in the future under the configured conditions
- Forecast how diverse stakeholder cohorts (agents) respond and act
- Identify emerging trends, latent risks, and strategic opportunities

- Do NOT write a retrospective analysis of the present status
- Focus exclusively on "what the future will hold"—the simulation results are the predicted future

[Crucial Rules - Mandatory]

1. [Must Use Retrieval Tools to Inspect the Simulated World]
- Observe the future preview from an omniscient stance
- All claims must originate from simulated world events and agent actions
- Do not rely on ungrounded personal knowledge
- Call tools at least 3 times (up to 5 times) per section

2. [Must Cite Direct Agent Quotes and Actions]
- Agent statements and behaviors predict future community behaviors
- Embed quotes in standard blockquote format, e.g.:
  > "Cohort perspective: verbatim statement..."
- Direct quotes serve as core empirical evidence for the forecast

3. [Language Consistency]
- The entire report must be written in English
- Translate any foreign-language source materials into clear, natural English before citing
- Preserve original meaning faithfully in both prose and blockquotes (>)

4. [Faithful Presentation]
- Accurately reflect the simulation findings
- Do not fabricate events absent from the simulation
- If information on an angle is limited, state that transparently

5. [Zero Fabrication]
- Do NOT fabricate usernames, citations, statistics, or interactions
- Do NOT output <tool_result> blocks—tool results are provided strictly by the environment
- Cite only entities, quotes, and metrics returned by tool observations

[Formatting Guidelines - Crucial]

[One Section = Atomic Content Unit]
- Each section is an atomic building block of the report
- Do NOT include any Markdown headers (#, ##, ###, ####, etc.) inside the section
- Do NOT place the section title at the top
- The system automatically prepends the section header; output only body prose
- Use **bold text**, paragraph breaks, blockquotes, and lists to structure content

[Correct Example]
This section examines communication dynamics during the incident. Analyzing simulation traces reveals...

**Initial Catalyst Phase**
Early discourse concentrated on primary communication channels:
> "Primary channels accounted for 68% of initial narrative volume..."
This demonstrates rapid early information diffusion.

**Emotional Amplification Phase**
Secondary platforms amplified societal resonance:
- Heightened visual salience
- Elevated emotional contagion

[Incorrect Example]
## Executive Summary       <-- WRONG! Never add headers
### 1. Initial Phase       <-- WRONG! Never use ###
This section analyzes...

[Available Tools] (Invoke 3-5 times per section)
{tools_description}

[Tool Usage Recommendations - Mix Different Tools]
- insight_forge: Deep multi-dimensional analysis, query decomposition, and relationship chains
- panorama_search: Wide overview, timeline evolution, active vs historical facts
- quick_search: Fast verification of specific data points
- interview_agents: Interviews active simulated agents for authentic first-person perspectives

[Workflow]
In each response, perform exactly ONE of the following (never both):

Option A - Call a Tool:
State your Thought, then invoke a tool in this format:
<tool_call>
{{"name": "tool_name", "parameters": {{"param_name": "param_value"}}}}
</tool_call>
The system executes the tool and returns observations. Never write mock tool results.

Option B - Output Final Answer:
Once sufficient evidence is collected, prefix your complete section content with "Final Answer:".

Strictly Prohibited:
- Outputting both a tool call and Final Answer in the same response
- Fabricating tool observations
- Calling more than one tool per response

[Section Content Standards]
1. Grounded strictly in simulation data retrieved via tools
2. Richly cited with source statements
3. Clean Markdown without headers:
   - Use **bold text** for topic emphasis (instead of sub-headers)
   - Use lists (- or 1. 2. 3.) for itemized takeaways
   - Separate paragraphs with blank lines
   - Strictly NO #, ##, ###, #### header tags
4. Blockquotes must be isolated paragraphs with blank lines before and after
5. Ensure logical coherence with prior sections
6. Avoid redundancy by reviewing completed sections below
7. Remember: NO Markdown headers! Use **bold** instead."""

SECTION_USER_PROMPT_TEMPLATE = """\
Completed section contents (review carefully to avoid redundancy):
{previous_sections_content}

---

[Current Task] Write Section: {section_title}
Section Description: {section_description}

[Key Reminders]
1. Review completed sections above to avoid duplicating points!
2. Invoke tools first to retrieve simulation evidence before drafting
3. Diversify tool usage across different retrieval modalities
4. Ground all narrative strictly in tool results

[Formatting Constraints]
- Do NOT write any Markdown headers (#, ##, ###, ####)
- Do NOT write "{section_title}" at the beginning
- Section headers are prepended automatically by the system
- Write pure body content using **bold** for subsection highlights

Begin now:
1. Thought: What simulation evidence is required for this section?
2. Action: Call a retrieval tool to inspect the simulation world
3. After sufficient evidence is gathered, output Final Answer (pure body prose without headers)."""

# ── ReACT Loop Message Templates ──

REACT_OBSERVATION_TEMPLATE = """\
Observation (Retrieval Result):

=== Tool {tool_name} Returned ===
{result}
==============================

Tools invoked: {tool_calls_count}/{max_tool_calls} (Used: {used_tools_str}){unused_hint}
- If evidence is sufficient: output section content starting with "Final Answer:" (citing retrieved facts)
- If more evidence is needed: call another tool to continue retrieval"""

REACT_INSUFFICIENT_TOOLS_MSG = (
    "[Notice] You have only invoked tools {tool_calls_count} time(s); at least {min_tool_calls} calls are required. "
    "Please call a tool to retrieve more simulation data before providing Final Answer.{unused_hint}"
)

REACT_INSUFFICIENT_TOOLS_MSG_ALT = (
    "Currently only {tool_calls_count} tool call(s) made; at least {min_tool_calls} required. "
    "Please call tools to retrieve simulation data.{unused_hint}"
)

REACT_TOOL_LIMIT_MSG = (
    "Tool invocation limit reached ({tool_calls_count}/{max_tool_calls}). "
    'Please output the section content immediately starting with "Final Answer:" based on retrieved evidence.'
)

REACT_UNUSED_TOOLS_HINT = "\n💡 You have not used: {unused_list}. We recommend trying different tools for multi-angle insights."

REACT_FORCE_FINAL_MSG = "Tool invocation limit reached. Please output Final Answer: directly and generate the section content."

CHAT_SYSTEM_PROMPT_TEMPLATE = """\
You are a concise, high-efficiency simulation forecast assistant.

[Background]
Simulation condition: {simulation_requirement}

[Generated Analysis Report]
{report_content}

[Rules]
1. Prioritize answering based on the report content above
2. Answer questions directly without lengthy preambles
3. Only invoke retrieval tools when report content is insufficient
4. Keep answers concise, clear, and structured

[Available Tools] (Use only when necessary, at most 1-2 calls)
{tools_description}

[Tool Call Format]
<tool_call>
{{"name": "tool_name", "parameters": {{"param_name": "param_value"}}}}
</tool_call>

[Response Style]
- Concise and direct
- Quote critical statements using > blockquote format
- State conclusions first, followed by explanations"""

CHAT_OBSERVATION_SUFFIX = "\n\nPlease answer the question concisely."


# ═══════════════════════════════════════════════════════════════
# ReportAgent Main Class
# ═══════════════════════════════════════════════════════════════


class ReportAgent:
    """
    Report Agent - Simulation Report Generation Agent

    Adopts ReACT (Reasoning + Acting) pattern:
    1. Planning stage: Analyzes simulation requirements and designs report outline
    2. Generation stage: Generates content section by section, calling retrieval tools
    3. Reflection stage: Validates content completeness and fidelity
    """
    
    # Maximum tool calls per section
    MAX_TOOL_CALLS_PER_SECTION = 5
    
    # Maximum reflection iterations
    MAX_REFLECTION_ROUNDS = 3
    
    # Maximum tool calls in chat mode
    MAX_TOOL_CALLS_PER_CHAT = 2
    
    def __init__(
        self, 
        graph_id: str,
        simulation_id: str,
        simulation_requirement: str,
        llm_client: Optional[LLMClient] = None,
        zep_tools: Optional[ZepToolsService] = None
    ):
        """
        Initialize Report Agent
        
        Args:
            graph_id: Graph ID
            simulation_id: Simulation ID
            simulation_requirement: Simulation requirement description
            llm_client: LLM client (optional)
            zep_tools: Zep retrieval tools service (optional)
        """
        self.graph_id = graph_id
        self.simulation_id = simulation_id
        self.simulation_requirement = simulation_requirement
        
        self.llm = llm_client or LLMClient()
        self.zep_tools = zep_tools or ZepToolsService()
        
        # Tool definitions
        self.tools = self._define_tools()
        
        # Action logger (initialized in generate_report)
        self.report_logger: Optional[ReportLogger] = None
        # Console logger (initialized in generate_report)
        self.console_logger: Optional[ReportConsoleLogger] = None
        
        logger.info(t('report.agentInitDone', graphId=graph_id, simulationId=simulation_id))
    
    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """Define available tools"""
        return {
            "insight_forge": {
                "name": "insight_forge",
                "description": TOOL_DESC_INSIGHT_FORGE,
                "parameters": {
                    "query": "The question or topic you want to analyze in depth",
                    "report_context": "Current section context (optional, helps generate targeted sub-questions)"
                }
            },
            "panorama_search": {
                "name": "panorama_search",
                "description": TOOL_DESC_PANORAMA_SEARCH,
                "parameters": {
                    "query": "Search query used for relevance ranking",
                    "include_expired": "Whether to include expired/historical content (default True)"
                }
            },
            "quick_search": {
                "name": "quick_search",
                "description": TOOL_DESC_QUICK_SEARCH,
                "parameters": {
                    "query": "Search query string",
                    "limit": "Number of results to return (optional, default 10)"
                }
            },
            "interview_agents": {
                "name": "interview_agents",
                "description": TOOL_DESC_INTERVIEW_AGENTS,
                "parameters": {
                    "interview_topic": "Interview topic or requirement description",
                    "max_agents": "Maximum number of agents to interview (optional, default 5, max 10)"
                }
            }
        }
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any], report_context: str = "") -> str:
        """
        Execute tool invocation
        
        Args:
            tool_name: Tool name
            parameters: Tool parameters
            report_context: Report context (used by InsightForge)
            
        Returns:
            Tool execution result (text format)
        """
        logger.info(t('report.executingTool', toolName=tool_name, params=parameters))
        
        try:
            if tool_name == "insight_forge":
                query = parameters.get("query", "")
                ctx = parameters.get("report_context", "") or report_context
                result = self.zep_tools.insight_forge(
                    graph_id=self.graph_id,
                    query=query,
                    simulation_requirement=self.simulation_requirement,
                    report_context=ctx
                )
                return result.to_text()
            
            elif tool_name == "panorama_search":
                # Broad search - comprehensive overview
                query = parameters.get("query", "")
                include_expired = parameters.get("include_expired", True)
                if isinstance(include_expired, str):
                    include_expired = include_expired.lower() in ['true', '1', 'yes']
                result = self.zep_tools.panorama_search(
                    graph_id=self.graph_id,
                    query=query,
                    include_expired=include_expired
                )
                return result.to_text()
            
            elif tool_name == "quick_search":
                # Fast search - rapid retrieval
                query = parameters.get("query", "")
                limit = parameters.get("limit", 10)
                if isinstance(limit, str):
                    limit = int(limit)
                result = self.zep_tools.quick_search(
                    graph_id=self.graph_id,
                    query=query,
                    limit=limit
                )
                return result.to_text()
            
            elif tool_name == "interview_agents":
                # In-depth interview - calls OASIS interview API for real agent responses (dual-platform)
                interview_topic = parameters.get("interview_topic", parameters.get("query", ""))
                max_agents = parameters.get("max_agents", 5)
                if isinstance(max_agents, str):
                    max_agents = int(max_agents)
                max_agents = min(max_agents, 10)
                result = self.zep_tools.interview_agents(
                    simulation_id=self.simulation_id,
                    interview_requirement=interview_topic,
                    simulation_requirement=self.simulation_requirement,
                    max_agents=max_agents
                )
                return result.to_text()
            
            # ========== Backward compatible legacy tools (redirected internally) ==========
            
            elif tool_name == "search_graph":
                # Redirect to quick_search
                logger.info(t('report.redirectToQuickSearch'))
                return self._execute_tool("quick_search", parameters, report_context)
            
            elif tool_name == "get_graph_statistics":
                result = self.zep_tools.get_graph_statistics(self.graph_id)
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_entity_summary":
                entity_name = parameters.get("entity_name", "")
                result = self.zep_tools.get_entity_summary(
                    graph_id=self.graph_id,
                    entity_name=entity_name
                )
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_simulation_context":
                # Redirect to insight_forge
                logger.info(t('report.redirectToInsightForge'))
                query = parameters.get("query", self.simulation_requirement)
                return self._execute_tool("insight_forge", {"query": query}, report_context)
            
            elif tool_name == "get_entities_by_type":
                entity_type = parameters.get("entity_type", "")
                nodes = self.zep_tools.get_entities_by_type(
                    graph_id=self.graph_id,
                    entity_type=entity_type
                )
                result = [n.to_dict() for n in nodes]
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            else:
                return f"Unknown tool: {tool_name}. Please use one of: insight_forge, panorama_search, quick_search, interview_agents"
                
        except Exception as e:
            logger.error(t('report.toolExecFailed', toolName=tool_name, error=str(e)))
            return f"Tool execution failed: {str(e)}"
    
    # Valid tool names set, used for fallback bare-JSON parsing validation
    VALID_TOOL_NAMES = {"insight_forge", "panorama_search", "quick_search", "interview_agents"}

    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse tool calls from LLM response

        Supported formats (by priority):
        1. <tool_call>{"name": "tool_name", "parameters": {...}}</tool_call>
        2. Bare JSON (response or single line is a tool call JSON)
        """
        tool_calls = []

        # Format 1: XML-style tags (standard format)
        xml_pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'
        for match in re.finditer(xml_pattern, response, re.DOTALL):
            try:
                call_data = json.loads(match.group(1))
                tool_calls.append(call_data)
            except json.JSONDecodeError:
                pass

        if tool_calls:
            return tool_calls

        # Format 2: Fallback - LLM output bare JSON without <tool_call> tags
        # Only attempted when Format 1 produces no matches
        stripped = response.strip()
        if stripped.startswith('{') and stripped.endswith('}'):
            try:
                call_data = json.loads(stripped)
                if self._is_valid_tool_call(call_data):
                    tool_calls.append(call_data)
                    return tool_calls
            except json.JSONDecodeError:
                pass

        # Response may contain thoughts + bare JSON; extract trailing JSON object
        json_pattern = r'(\{"(?:name|tool)"\s*:.*?\})\s*$'
        match = re.search(json_pattern, stripped, re.DOTALL)
        if match:
            try:
                call_data = json.loads(match.group(1))
                if self._is_valid_tool_call(call_data):
                    tool_calls.append(call_data)
            except json.JSONDecodeError:
                pass

        return tool_calls

    def _is_valid_tool_call(self, data: dict) -> bool:
        """Validate whether parsed JSON is a valid tool call"""
        # Supports both name/parameters and tool/params key conventions
        tool_name = data.get("name") or data.get("tool")
        if tool_name and tool_name in self.VALID_TOOL_NAMES:
            # Standardize keys to name / parameters
            if "tool" in data:
                data["name"] = data.pop("tool")
            if "params" in data and "parameters" not in data:
                data["parameters"] = data.pop("params")
            return True
        return False
    
    @staticmethod
    def _safe_format(template: str, **kwargs: Any) -> str:
        """Render a prompt template without crashing on missing placeholders."""
        safe_kwargs = defaultdict(str, kwargs)
        return template.format_map(safe_kwargs)

    def _get_tools_description(self) -> str:
        """Generate tool description text"""
        desc_parts = ["Available Tools:"]
        for name, tool in self.tools.items():
            params_desc = ", ".join([f"{k}: {v}" for k, v in tool["parameters"].items()])
            desc_parts.append(f"- {name}: {tool['description']}")
            if params_desc:
                desc_parts.append(f"  Parameters: {params_desc}")
        return "\n".join(desc_parts)

    @staticmethod
    def _strip_fake_tool_results(response: str) -> str:
        """Strip any <tool_result> blocks the LLM fabricated in its response.

        When the LLM generates a <tool_call> block and then continues to generate
        a <tool_result> block in the same response, we must strip the fake result
        before appending to message history. The real tool result will be injected
        separately by the system.
        """
        tag_pattern = re.compile(r'</?tool_result\b[^>]*>', flags=re.IGNORECASE)
        parts = []
        cursor = 0
        depth = 0

        for match in tag_pattern.finditer(response):
            if depth == 0:
                parts.append(response[cursor:match.start()])

            if match.group(0).lstrip().startswith('</'):
                depth = max(0, depth - 1)
            else:
                depth += 1
            cursor = match.end()

        if depth == 0:
            parts.append(response[cursor:])

        cleaned = ''.join(parts)
        # Treat a malformed opening tag without a closing `>` as unsafe too.
        cleaned = re.sub(r'<tool_result\b.*$', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned.strip()

    def plan_outline(
        self, 
        progress_callback: Optional[Callable] = None
    ) -> ReportOutline:
        """
        Plan report outline
        
        Uses LLM to analyze simulation requirements and design report outline
        
        Args:
            progress_callback: Progress callback function
            
        Returns:
            ReportOutline: Report outline
        """
        logger.info(t('report.startPlanningOutline'))
        
        if progress_callback:
            progress_callback("planning", 0, t('progress.analyzingRequirements'))
        
        # First retrieve simulation context
        context = self.zep_tools.get_simulation_context(
            graph_id=self.graph_id,
            simulation_requirement=self.simulation_requirement
        )
        
        if progress_callback:
            progress_callback("planning", 30, t('progress.generatingOutline'))
        
        system_prompt = f"{PLAN_SYSTEM_PROMPT}\n\n{get_language_instruction()}"
        sample_facts = json.dumps(context.get('related_facts', [])[:10], ensure_ascii=False, indent=2)
        user_prompt = ReportAgent._safe_format(
            PLAN_USER_PROMPT_TEMPLATE,
            simulation_requirement=self.simulation_requirement,
            total_nodes=context.get('graph_statistics', {}).get('total_nodes', 0),
            total_edges=context.get('graph_statistics', {}).get('total_edges', 0),
            entity_types=list(context.get('graph_statistics', {}).get('entity_types', {}).keys()),
            total_entities=context.get('total_entities', 0),
            sample_facts=sample_facts,
        )

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            if progress_callback:
                progress_callback("planning", 80, t('progress.parsingOutline'))
            
            # Parse outline
            sections = []
            for section_data in response.get("sections", []):
                sections.append(ReportSection(
                    title=section_data.get("title", ""),
                    content="",
                    description=section_data.get("description", "")
                ))
            
            outline = ReportOutline(
                title=response.get("title", "Simulation Analysis Report"),
                summary=response.get("summary", ""),
                sections=sections
            )
            
            if progress_callback:
                progress_callback("planning", 100, t('progress.outlinePlanComplete'))
            
            logger.info(t('report.outlinePlanDone', count=len(sections)))
            return outline
            
        except Exception as e:
            logger.error(t('report.outlinePlanFailed', error=str(e)))
            # Fallback default outline (3 sections)
            return ReportOutline(
                title="Future Forecast Report",
                summary="Future trends and risk analysis based on simulation forecast",
                sections=[
                    ReportSection(title="Scenario Setup & Core Forecast Findings"),
                    ReportSection(title="Cohort Behavioral Forecast Analysis"),
                    ReportSection(title="Trends Outlook & Risk Assessment")
                ]
            )
    
    def _generate_section_react(
        self, 
        section: ReportSection,
        outline: ReportOutline,
        previous_sections: List[str],
        progress_callback: Optional[Callable] = None,
        section_index: int = 0
    ) -> str:
        """
        Generate single section content using ReACT pattern
        
        ReACT Loop:
        1. Thought - Analyze what information is needed
        2. Action - Invoke tools to retrieve data
        3. Observation - Analyze tool results
        4. Repeat until sufficient evidence gathered or limit reached
        5. Final Answer - Generate section content
        
        Args:
            section: Target section to generate
            outline: Full outline
            previous_sections: Previous sections content (for continuity)
            progress_callback: Progress callback
            section_index: Section index (for logging)
            
        Returns:
            Section content (Markdown format)
        """
        logger.info(t('report.reactGenerateSection', title=section.title))
        
        # Log section start
        if self.report_logger:
            self.report_logger.log_section_start(section.title, section_index)
        
        section_description = getattr(section, "description", "") or ""
        system_prompt = ReportAgent._safe_format(
            SECTION_SYSTEM_PROMPT_TEMPLATE,
            report_title=outline.title,
            report_summary=outline.summary,
            simulation_requirement=self.simulation_requirement,
            section_title=section.title,
            section_description=section_description,
            tools_description=self._get_tools_description(),
        )
        system_prompt = f"{system_prompt}\n\n{get_language_instruction()}"

        # Build user prompt - up to 4000 chars per completed section
        if previous_sections:
            previous_parts = []
            for sec in previous_sections:
                # Up to 4000 chars per section
                truncated = sec[:4000] + "..." if len(sec) > 4000 else sec
                previous_parts.append(truncated)
            previous_content = "\n\n---\n\n".join(previous_parts)
        else:
            previous_content = "(This is the first section)"

        user_prompt = ReportAgent._safe_format(
            SECTION_USER_PROMPT_TEMPLATE,
            previous_sections_content=previous_content,
            section_title=section.title,
            section_description=section_description,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # ReACT Loop
        tool_calls_count = 0
        max_iterations = 5  # Max iterations
        min_tool_calls = 3  # Min tool calls required
        conflict_retries = 0  # Consecutive conflict count
        used_tools = set()  # Track invoked tool names
        all_tools = {"insight_forge", "panorama_search", "quick_search", "interview_agents"}

        # Section context for InsightForge sub-queries
        report_context = f"Section Title: {section.title}\nSimulation Requirement: {self.simulation_requirement}"
        
        for iteration in range(max_iterations):
            if progress_callback:
                progress_callback(
                    "generating", 
                    int((iteration / max_iterations) * 100),
                    t('progress.deepSearchAndWrite', current=tool_calls_count, max=self.MAX_TOOL_CALLS_PER_SECTION)
                )
            
            # Call LLM
            response = self.llm.chat(
                messages=messages,
                temperature=0.5,
                max_tokens=4096
            )

            # Check if LLM response is None (API error or empty)
            if response is None:
                logger.warning(t('report.sectionIterNone', title=section.title, iteration=iteration + 1))
                # If iterations remain, append message and retry
                if iteration < max_iterations - 1:
                    messages.append({"role": "assistant", "content": "(Empty response)"})
                    messages.append({"role": "user", "content": "Please continue generating content."})
                    continue
                # Exit loop on final iteration if still None
                break

            logger.debug(f"LLM response: {response[:200]}...")

            # Parse once and reuse
            tool_calls = self._parse_tool_calls(response)
            has_tool_calls = bool(tool_calls)
            has_final_answer = "Final Answer:" in response

            # ── Conflict handling: LLM output both tool call and Final Answer ──
            if has_tool_calls and has_final_answer:
                conflict_retries += 1
                logger.warning(
                    t('report.sectionConflict', title=section.title, iteration=iteration+1, conflictCount=conflict_retries)
                )

                if conflict_retries <= 2:
                    # First two attempts: discard and ask LLM to re-respond cleanly
                    cleaned_response = ReportAgent._strip_fake_tool_results(response)
                    messages.append({"role": "assistant", "content": cleaned_response})
                    messages.append({
                        "role": "user",
                        "content": (
                            "[Format Error] You included both a tool call and Final Answer in the same response, which is not permitted.\n"
                            "Each response must perform only ONE action:\n"
                            "- Call a tool (output a single <tool_call> block without Final Answer)\n"
                            "- Output final content (starting with 'Final Answer:' without <tool_call>)\n"
                            "Please re-respond performing only one of these actions."
                        ),
                    })
                    continue
                else:
                    # Third attempt: fallback truncate to first tool call and execute
                    logger.warning(
                        t('report.sectionConflictDowngrade', title=section.title, conflictCount=conflict_retries)
                    )
                    first_tool_end = response.find('</tool_call>')
                    if first_tool_end != -1:
                        response = response[:first_tool_end + len('</tool_call>')]
                        tool_calls = self._parse_tool_calls(response)
                        has_tool_calls = bool(tool_calls)
                    has_final_answer = False
                    conflict_retries = 0

            # Log LLM response
            if self.report_logger:
                self.report_logger.log_llm_response(
                    section_title=section.title,
                    section_index=section_index,
                    response=response,
                    iteration=iteration + 1,
                    has_tool_calls=has_tool_calls,
                    has_final_answer=has_final_answer
                )

            # ── Case 1: LLM output Final Answer ──
            if has_final_answer:
                cleaned_response = ReportAgent._strip_fake_tool_results(response)
                # Insufficient tool calls, reject and prompt to continue retrieval
                if tool_calls_count < min_tool_calls:
                    messages.append({"role": "assistant", "content": cleaned_response})
                    unused_tools = all_tools - used_tools
                    unused_hint = f" (Unused tools recommended: {', '.join(unused_tools)})" if unused_tools else ""
                    messages.append({
                        "role": "user",
                        "content": ReportAgent._safe_format(
                            REACT_INSUFFICIENT_TOOLS_MSG,
                            tool_calls_count=tool_calls_count,
                            min_tool_calls=min_tool_calls,
                            unused_hint=unused_hint,
                        ),
                    })
                    continue

                # Normal completion
                final_answer = cleaned_response.split("Final Answer:")[-1].strip()
                logger.info(t('report.sectionGenDone', title=section.title, count=tool_calls_count))

                if self.report_logger:
                    self.report_logger.log_section_content(
                        section_title=section.title,
                        section_index=section_index,
                        content=final_answer,
                        tool_calls_count=tool_calls_count
                    )
                return final_answer

            # ── Case 2: LLM attempted tool call ──
            if has_tool_calls:
                # Tool budget exhausted -> instruct to output Final Answer
                if tool_calls_count >= self.MAX_TOOL_CALLS_PER_SECTION:
                    cleaned_response = ReportAgent._strip_fake_tool_results(response)
                    messages.append({"role": "assistant", "content": cleaned_response})
                    messages.append({
                        "role": "user",
                        "content": ReportAgent._safe_format(
                            REACT_TOOL_LIMIT_MSG,
                            tool_calls_count=tool_calls_count,
                            max_tool_calls=self.MAX_TOOL_CALLS_PER_SECTION,
                        ),
                    })
                    continue

                # Execute only first tool call
                call = tool_calls[0]
                if len(tool_calls) > 1:
                    logger.info(t('report.multiToolOnlyFirst', total=len(tool_calls), toolName=call['name']))

                if self.report_logger:
                    self.report_logger.log_tool_call(
                        section_title=section.title,
                        section_index=section_index,
                        tool_name=call["name"],
                        parameters=call.get("parameters", {}),
                        iteration=iteration + 1
                    )

                result = self._execute_tool(
                    call["name"],
                    call.get("parameters", {}),
                    report_context=report_context
                )

                if self.report_logger:
                    self.report_logger.log_tool_result(
                        section_title=section.title,
                        section_index=section_index,
                        tool_name=call["name"],
                        result=result,
                        iteration=iteration + 1
                    )

                tool_calls_count += 1
                used_tools.add(call['name'])

                # Build unused tools hint
                unused_tools = all_tools - used_tools
                unused_hint = ""
                if unused_tools and tool_calls_count < self.MAX_TOOL_CALLS_PER_SECTION:
                    unused_hint = ReportAgent._safe_format(REACT_UNUSED_TOOLS_HINT, unused_list="、".join(unused_tools))

                cleaned_response = ReportAgent._strip_fake_tool_results(response)
                messages.append({"role": "assistant", "content": cleaned_response})
                messages.append({
                    "role": "user",
                    "content": ReportAgent._safe_format(
                        REACT_OBSERVATION_TEMPLATE,
                        tool_name=call["name"],
                        result=result,
                        tool_calls_count=tool_calls_count,
                        max_tool_calls=self.MAX_TOOL_CALLS_PER_SECTION,
                        used_tools_str=", ".join(used_tools),
                        unused_hint=unused_hint,
                    ),
                })
                continue

            # ── Case 3: Neither tool call nor Final Answer present ──
            cleaned_response = ReportAgent._strip_fake_tool_results(response)
            messages.append({"role": "assistant", "content": cleaned_response})

            if tool_calls_count < min_tool_calls:
                # Tool calls insufficient, recommend unused tools
                unused_tools = all_tools - used_tools
                unused_hint = f" (Unused tools recommended: {', '.join(unused_tools)})" if unused_tools else ""

                messages.append({
                    "role": "user",
                    "content": ReportAgent._safe_format(
                        REACT_INSUFFICIENT_TOOLS_MSG_ALT,
                        tool_calls_count=tool_calls_count,
                        min_tool_calls=min_tool_calls,
                        unused_hint=unused_hint,
                    ),
                })
                continue

            # Tool calls sufficient, LLM output body content without Final Answer prefix
            # Accept body content directly as final answer
            logger.info(t('report.sectionNoPrefix', title=section.title, count=tool_calls_count))
            final_answer = cleaned_response

            if self.report_logger:
                self.report_logger.log_section_content(
                    section_title=section.title,
                    section_index=section_index,
                    content=final_answer,
                    tool_calls_count=tool_calls_count
                )
            return final_answer
        
        # Max iterations reached, force finalize content
        logger.info(t('report.sectionMaxIter', title=section.title))
        messages.append({"role": "user", "content": REACT_FORCE_FINAL_MSG})
        
        response = self.llm.chat(
            messages=messages,
            temperature=0.5,
            max_tokens=4096
        )

        # Check if force finalize response is None
        if response is None:
            logger.error(t('report.sectionForceFailed', title=section.title))
            final_answer = t('report.sectionGenFailedContent')
        elif "Final Answer:" in response:
            final_answer = response.split("Final Answer:")[-1].strip()
        else:
            final_answer = response
        
        # Log section content generation complete
        if self.report_logger:
            self.report_logger.log_section_content(
                section_title=section.title,
                section_index=section_index,
                content=final_answer,
                tool_calls_count=tool_calls_count
            )
        
        return final_answer
    
    def generate_report(
        self, 
        progress_callback: Optional[Callable[[str, int, str], None]] = None,
        report_id: Optional[str] = None
    ) -> Report:
        """
        Generate complete report with real-time section-by-section streaming
        
        Saves each section immediately to disk upon completion without waiting for full report.
        File structure:
        reports/{report_id}/
            meta.json       - Report metadata
            outline.json    - Report outline
            progress.json   - Generation progress
            section_01.md   - Section 1
            section_02.md   - Section 2
            ...
            full_report.md  - Assembled complete report
        
        Args:
            progress_callback: Progress callback function (stage, progress, message)
            report_id: Report ID (optional, auto-generated if omitted)
            
        Returns:
            Report: Complete report object
        """
        import uuid
        
        # Auto-generate report_id if not supplied
        if not report_id:
            report_id = f"report_{uuid.uuid4().hex[:12]}"
        start_time = datetime.now()
        
        report = Report(
            report_id=report_id,
            simulation_id=self.simulation_id,
            graph_id=self.graph_id,
            simulation_requirement=self.simulation_requirement,
            status=ReportStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        # Completed section titles list (for progress tracking)
        completed_section_titles = []
        
        try:
            # Initialize report folder and persist initial state
            ReportManager._ensure_report_folder(report_id)
            
            # Initialize structured action logger (agent_log.jsonl)
            self.report_logger = ReportLogger(report_id)
            self.report_logger.log_start(
                simulation_id=self.simulation_id,
                graph_id=self.graph_id,
                simulation_requirement=self.simulation_requirement
            )
            
            # Initialize console logger (console_log.txt)
            self.console_logger = ReportConsoleLogger(report_id)
            
            ReportManager.update_progress(
                report_id, "pending", 0, t('progress.initReport'),
                completed_sections=[]
            )
            ReportManager.save_report(report)
            
            # Stage 1: Plan outline
            report.status = ReportStatus.PLANNING
            ReportManager.update_progress(
                report_id, "planning", 5, t('progress.startPlanningOutline'),
                completed_sections=[]
            )
            
            # Log planning start
            self.report_logger.log_planning_start()
            
            if progress_callback:
                progress_callback("planning", 0, t('progress.startPlanningOutline'))
            
            outline = self.plan_outline(
                progress_callback=lambda stage, prog, msg: 
                    progress_callback(stage, prog // 5, msg) if progress_callback else None
            )
            report.outline = outline
            
            # Log planning complete
            self.report_logger.log_planning_complete(outline.to_dict())
            
            # Save outline to disk
            ReportManager.save_outline(report_id, outline)
            ReportManager.update_progress(
                report_id, "planning", 15, t('progress.outlineDone', count=len(outline.sections)),
                completed_sections=[]
            )
            ReportManager.save_report(report)
            
            logger.info(t('report.outlineSavedToFile', reportId=report_id))
            
            # Stage 2: Generate section by section (streaming save)
            report.status = ReportStatus.GENERATING
            
            total_sections = len(outline.sections)
            generated_sections = []  # Store contents for context
            
            for i, section in enumerate(outline.sections):
                section_num = i + 1
                base_progress = 20 + int((i / total_sections) * 70)
                
                # Update progress
                ReportManager.update_progress(
                    report_id, "generating", base_progress,
                    t('progress.generatingSection', title=section.title, current=section_num, total=total_sections),
                    current_section=section.title,
                    completed_sections=completed_section_titles
                )

                if progress_callback:
                    progress_callback(
                        "generating",
                        base_progress,
                        t('progress.generatingSection', title=section.title, current=section_num, total=total_sections)
                    )
                
                # Generate section content
                section_content = self._generate_section_react(
                    section=section,
                    outline=outline,
                    previous_sections=generated_sections,
                    progress_callback=lambda stage, prog, msg:
                        progress_callback(
                            stage, 
                            base_progress + int(prog * 0.7 / total_sections),
                            msg
                        ) if progress_callback else None,
                    section_index=section_num
                )
                
                section.content = section_content
                generated_sections.append(f"## {section.title}\n\n{section_content}")

                # Save section
                ReportManager.save_section(report_id, section_num, section)
                completed_section_titles.append(section.title)

                # Log section complete
                full_section_content = f"## {section.title}\n\n{section_content}"

                if self.report_logger:
                    self.report_logger.log_section_full_complete(
                        section_title=section.title,
                        section_index=section_num,
                        full_content=full_section_content.strip()
                    )

                logger.info(t('report.sectionSaved', reportId=report_id, sectionNum=f"{section_num:02d}"))
                
                # Update progress
                ReportManager.update_progress(
                    report_id, "generating", 
                    base_progress + int(70 / total_sections),
                    t('progress.sectionDone', title=section.title),
                    current_section=None,
                    completed_sections=completed_section_titles
                )
            
            # Stage 3: Assemble full report
            if progress_callback:
                progress_callback("generating", 95, t('progress.assemblingReport'))
            
            ReportManager.update_progress(
                report_id, "generating", 95, t('progress.assemblingReport'),
                completed_sections=completed_section_titles
            )
            
            # Assemble full report via ReportManager
            report.markdown_content = ReportManager.assemble_full_report(report_id, outline)
            report.status = ReportStatus.COMPLETED
            report.completed_at = datetime.now().isoformat()
            
            # Calculate total elapsed time
            total_time_seconds = (datetime.now() - start_time).total_seconds()
            
            # Log report complete
            if self.report_logger:
                self.report_logger.log_report_complete(
                    total_sections=total_sections,
                    total_time_seconds=total_time_seconds
                )
            
            # Save final report
            ReportManager.save_report(report)
            ReportManager.update_progress(
                report_id, "completed", 100, t('progress.reportComplete'),
                completed_sections=completed_section_titles
            )
            
            if progress_callback:
                progress_callback("completed", 100, t('progress.reportComplete'))
            
            logger.info(t('report.reportGenDone', reportId=report_id))
            
            # Close console logger
            if self.console_logger:
                self.console_logger.close()
                self.console_logger = None
            
            return report
            
        except Exception as e:
            logger.error(t('report.reportGenFailed', error=str(e)))
            report.status = ReportStatus.FAILED
            report.error = str(e)
            
            # Log error event
            if self.report_logger:
                self.report_logger.log_error(str(e), "failed")
            
            # Save failed state
            try:
                ReportManager.save_report(report)
                ReportManager.update_progress(
                    report_id, "failed", -1, t('progress.reportFailed', error=str(e)),
                    completed_sections=completed_section_titles
                )
            except Exception:
                pass  # Ignore failure saving error
            
            # Close console logger
            if self.console_logger:
                self.console_logger.close()
                self.console_logger = None
            
            return report
    
    def chat(
        self, 
        message: str,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Chat with Report Agent.
        
        Agent autonomously queries retrieval tools to answer user questions.
        
        Args:
            message: User message
            chat_history: Chat history
            
        Returns:
            {
                "response": "Agent response",
                "tool_calls": [List of invoked tools],
                "sources": [Information sources]
            }
        """
        logger.info(t('report.agentChat', message=message[:50]))
        
        chat_history = chat_history or []
        
        # Retrieve generated report content
        report_content = ""
        try:
            report = ReportManager.get_report_by_simulation(self.simulation_id)
            if report and report.markdown_content:
                # Truncate report content to prevent context overflow
                report_content = report.markdown_content[:15000]
                if len(report.markdown_content) > 15000:
                    report_content += "\n\n... [Report content truncated] ..."
        except Exception as e:
            logger.warning(t('report.fetchReportFailed', error=e))
        
        system_prompt = ReportAgent._safe_format(
            CHAT_SYSTEM_PROMPT_TEMPLATE,
            simulation_requirement=self.simulation_requirement,
            report_content=report_content if report_content else "(No report available)",
            tools_description=self._get_tools_description(),
        )
        system_prompt = f"{system_prompt}\n\n{get_language_instruction()}"

        # Construct messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Append chat history
        for h in chat_history[-10:]:  # Limit history window
            messages.append(h)
        
        # Append user message
        messages.append({
            "role": "user", 
            "content": message
        })
        
        # ReACT Loop (simplified)
        tool_calls_made = []
        max_iterations = 2  # Limit iterations
        
        for iteration in range(max_iterations):
            response = self.llm.chat(
                messages=messages,
                temperature=0.5
            )
            
            # Parse tool calls
            tool_calls = self._parse_tool_calls(response)
            
            if not tool_calls:
                # No tool calls, return response directly
                clean_response = re.sub(r'<tool_call>.*?</tool_call>', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\[TOOL_CALL\].*?\)', '', clean_response)
                clean_response = ReportAgent._strip_fake_tool_results(clean_response)
                
                return {
                    "response": clean_response.strip(),
                    "tool_calls": tool_calls_made,
                    "sources": [tc.get("parameters", {}).get("query", "") for tc in tool_calls_made]
                }
            
            # Execute tool invocation (constrained count)
            tool_results = []
            for call in tool_calls[:1]:  # Max 1 tool call per turn
                if len(tool_calls_made) >= self.MAX_TOOL_CALLS_PER_CHAT:
                    break
                result = self._execute_tool(call["name"], call.get("parameters", {}))
                tool_results.append({
                    "tool": call["name"],
                    "result": result[:1500]  # Truncate result length
                })
                tool_calls_made.append(call)
            
            # Append results to messages
            cleaned_response = ReportAgent._strip_fake_tool_results(response)
            messages.append({"role": "assistant", "content": cleaned_response})
            observation = "\n".join([f"[{r['tool']} Result]\n{r['result']}" for r in tool_results])
            messages.append({
                "role": "user",
                "content": observation + CHAT_OBSERVATION_SUFFIX
            })
        
        # Max iterations reached, retrieve final response
        final_response = self.llm.chat(
            messages=messages,
            temperature=0.5
        )
        
        # Clean response
        clean_response = re.sub(r'<tool_call>.*?</tool_call>', '', final_response, flags=re.DOTALL)
        clean_response = re.sub(r'\[TOOL_CALL\].*?\)', '', clean_response)
        clean_response = ReportAgent._strip_fake_tool_results(clean_response)
        
        return {
            "response": clean_response.strip(),
            "tool_calls": tool_calls_made,
            "sources": [tc.get("parameters", {}).get("query", "") for tc in tool_calls_made]
        }


class ReportManager:
    """
    Report Manager
    
    Manages report persistence and retrieval.
    
    File structure (section-by-section streaming):
    reports/
      {report_id}/
        meta.json          - Report metadata and status
        outline.json       - Report outline
        progress.json      - Generation progress
        section_01.md      - Section 1
        section_02.md      - Section 2
        ...
        full_report.md     - Assembled complete report
    """
    
    # Report storage directory
    REPORTS_DIR = os.path.join(Config.UPLOAD_FOLDER, 'reports')
    
    @classmethod
    def _ensure_reports_dir(cls):
        """Ensure report root directory exists"""
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
    
    @classmethod
    def _get_report_folder(cls, report_id: str) -> str:
        """Get report folder path"""
        return os.path.join(cls.REPORTS_DIR, report_id)
    
    @classmethod
    def _ensure_report_folder(cls, report_id: str) -> str:
        """Ensure report directory exists and return path"""
        folder = cls._get_report_folder(report_id)
        os.makedirs(folder, exist_ok=True)
        return folder
    
    @classmethod
    def _get_report_path(cls, report_id: str) -> str:
        """Get report metadata file path"""
        return os.path.join(cls._get_report_folder(report_id), "meta.json")
    
    @classmethod
    def _get_report_markdown_path(cls, report_id: str) -> str:
        """Get full report Markdown file path"""
        return os.path.join(cls._get_report_folder(report_id), "full_report.md")
    
    @classmethod
    def _get_outline_path(cls, report_id: str) -> str:
        """Get outline file path"""
        return os.path.join(cls._get_report_folder(report_id), "outline.json")
    
    @classmethod
    def _get_progress_path(cls, report_id: str) -> str:
        """Get progress file path"""
        return os.path.join(cls._get_report_folder(report_id), "progress.json")
    
    @classmethod
    def _get_section_path(cls, report_id: str, section_index: int) -> str:
        """Get section Markdown file path"""
        return os.path.join(cls._get_report_folder(report_id), f"section_{section_index:02d}.md")
    
    @classmethod
    def _get_agent_log_path(cls, report_id: str) -> str:
        """Get agent log file path"""
        return os.path.join(cls._get_report_folder(report_id), "agent_log.jsonl")
    
    @classmethod
    def _get_console_log_path(cls, report_id: str) -> str:
        """Get console log file path"""
        return os.path.join(cls._get_report_folder(report_id), "console_log.txt")
    
    @classmethod
    def get_console_log(cls, report_id: str, from_line: int = 0) -> Dict[str, Any]:
        """
        Retrieve console log content.
        
        Contains raw console output (INFO, WARNING, etc.) distinct from structured agent_log.jsonl.
        
        Args:
            report_id: Report ID
            from_line: Line offset to read from (0 for entire file)
            
        Returns:
            {
                "logs": [List of log lines],
                "total_lines": Total line count,
                "from_line": Starting line offset,
                "has_more": Whether more logs remain
            }
        """
        log_path = cls._get_console_log_path(report_id)
        
        if not os.path.exists(log_path):
            return {
                "logs": [],
                "total_lines": 0,
                "from_line": 0,
                "has_more": False
            }
        
        logs = []
        total_lines = 0
        
        with open(log_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                total_lines = i + 1
                if i >= from_line:
                    # Retain log lines without trailing newlines
                    logs.append(line.rstrip('\n\r'))
        
        return {
            "logs": logs,
            "total_lines": total_lines,
            "from_line": from_line,
            "has_more": False  # Reached end of file
        }
    
    @classmethod
    def get_console_log_stream(cls, report_id: str) -> List[str]:
        """
        Retrieve complete console logs (all at once)
        
        Args:
            report_id: Report ID
            
        Returns:
            List of log lines
        """
        result = cls.get_console_log(report_id, from_line=0)
        return result["logs"]
    
    @classmethod
    def get_agent_log(cls, report_id: str, from_line: int = 0) -> Dict[str, Any]:
        """
        Retrieve Agent log content
        
        Args:
            report_id: Report ID
            from_line: Line offset to read from (0 for entire file)
            
        Returns:
            {
                "logs": [List of log entries],
                "total_lines": Total line count,
                "from_line": Starting line offset,
                "has_more": Whether more logs remain
            }
        """
        log_path = cls._get_agent_log_path(report_id)
        
        if not os.path.exists(log_path):
            return {
                "logs": [],
                "total_lines": 0,
                "from_line": 0,
                "has_more": False
            }
        
        logs = []
        total_lines = 0
        
        with open(log_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                total_lines = i + 1
                if i >= from_line:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        # Skip unparseable lines
                        continue
        
        return {
            "logs": logs,
            "total_lines": total_lines,
            "from_line": from_line,
            "has_more": False  # Reached end of file
        }
    
    @classmethod
    def get_agent_log_stream(cls, report_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve complete Agent logs (all at once)
        
        Args:
            report_id: Report ID
            
        Returns:
            List of log entries
        """
        result = cls.get_agent_log(report_id, from_line=0)
        return result["logs"]
    
    @classmethod
    def save_outline(cls, report_id: str, outline: ReportOutline) -> None:
        """
        Save report outline.
        
        Invoked immediately after planning stage completes.
        """
        cls._ensure_report_folder(report_id)
        
        with open(cls._get_outline_path(report_id), 'w', encoding='utf-8') as f:
            json.dump(outline.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.info(t('report.outlineSaved', reportId=report_id))
    
    @classmethod
    def save_section(
        cls,
        report_id: str,
        section_index: int,
        section: ReportSection
    ) -> str:
        """
        Save single section

        Invoked immediately upon section generation to support incremental streaming.

        Args:
            report_id: Report ID
            section_index: Section index (1-based)
            section: Section object

        Returns:
            Saved file path
        """
        cls._ensure_report_folder(report_id)

        # Build section Markdown content - strip redundant titles
        cleaned_content = cls._clean_section_content(section.content, section.title)
        md_content = f"## {section.title}\n\n"
        if cleaned_content:
            md_content += f"{cleaned_content}\n\n"

        # Save file
        file_suffix = f"section_{section_index:02d}.md"
        file_path = os.path.join(cls._get_report_folder(report_id), file_suffix)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        logger.info(t('report.sectionFileSaved', reportId=report_id, fileSuffix=file_suffix))
        return file_path
    
    @classmethod
    def _clean_section_content(cls, content: str, section_title: str) -> str:
        """
        Clean section content.
        
        1. Strips redundant Markdown headers matching section title at start
        2. Converts all sub-headers (###, etc.) to bold prose
        
        Args:
            content: Raw content
            section_title: Section title
            
        Returns:
            Cleaned content
        """
        import re
        
        if not content:
            return content
        
        content = content.strip()
        lines = content.split('\n')
        cleaned_lines = []
        skip_next_empty = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check if line is a Markdown header
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            
            if heading_match:
                level = len(heading_match.group(1))
                title_text = heading_match.group(2).strip()
                
                # Check if header duplicates section title (skip if within first 5 lines)
                if i < 5:
                    if title_text == section_title or title_text.replace(' ', '') == section_title.replace(' ', ''):
                        skip_next_empty = True
                        continue
                
                # Convert all header levels (#, ##, ###, ####, etc.) to bold text
                # Section headers are added automatically by system; body contains no headers
                cleaned_lines.append(f"**{title_text}**")
                cleaned_lines.append("")  # Add blank line
                continue
            
            # Skip empty line immediately following a stripped header
            if skip_next_empty and stripped == '':
                skip_next_empty = False
                continue
            
            skip_next_empty = False
            cleaned_lines.append(line)
        
        # Remove leading empty lines
        while cleaned_lines and cleaned_lines[0].strip() == '':
            cleaned_lines.pop(0)
        
        # Remove leading horizontal rules
        while cleaned_lines and cleaned_lines[0].strip() in ['---', '***', '___']:
            cleaned_lines.pop(0)
            # Remove blank lines following horizontal rules
            while cleaned_lines and cleaned_lines[0].strip() == '':
                cleaned_lines.pop(0)
        
        return '\n'.join(cleaned_lines)
    
    @classmethod
    def update_progress(
        cls, 
        report_id: str, 
        status: str, 
        progress: int, 
        message: str,
        current_section: str = None,
        completed_sections: List[str] = None
    ) -> None:
        """
        Update report generation progress.
        
        Frontend polls progress.json for real-time generation metrics.
        """
        cls._ensure_report_folder(report_id)
        
        progress_data = {
            "status": status,
            "progress": progress,
            "message": message,
            "current_section": current_section,
            "completed_sections": completed_sections or [],
            "updated_at": datetime.now().isoformat()
        }
        
        with open(cls._get_progress_path(report_id), 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def get_progress(cls, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report generation progress"""
        path = cls._get_progress_path(report_id)
        
        if not os.path.exists(path):
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def get_generated_sections(cls, report_id: str) -> List[Dict[str, Any]]:
        """
        Get list of generated sections.
        
        Returns metadata for all persisted section files.
        """
        folder = cls._get_report_folder(report_id)
        
        if not os.path.exists(folder):
            return []
        
        sections = []
        for filename in sorted(os.listdir(folder)):
            if filename.startswith('section_') and filename.endswith('.md'):
                file_path = os.path.join(folder, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse section index from filename
                parts = filename.replace('.md', '').split('_')
                section_index = int(parts[1])

                sections.append({
                    "filename": filename,
                    "section_index": section_index,
                    "content": content
                })

        return sections
    
    @classmethod
    def assemble_full_report(cls, report_id: str, outline: ReportOutline) -> str:
        """
        Assemble full report.
        
        Concatenates saved section files into complete report with title cleanup.
        """
        folder = cls._get_report_folder(report_id)
        
        # Build report header
        md_content = f"# {outline.title}\n\n"
        md_content += f"> {outline.summary}\n\n"
        md_content += f"---\n\n"
        
        # Sequentially read all section files
        sections = cls.get_generated_sections(report_id)
        for section_info in sections:
            md_content += section_info["content"]
        
        # Post-processing: clean header hierarchy throughout report
        md_content = cls._post_process_report(md_content, outline)
        
        # Save full report
        full_path = cls._get_report_markdown_path(report_id)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(t('report.fullReportAssembled', reportId=report_id))
        return md_content
    
    @classmethod
    def _post_process_report(cls, content: str, outline: ReportOutline) -> str:
        """
        Post-process report content.
        
        1. Removes redundant headers
        2. Retains main report header (#) and section headers (##); converts others to bold
        3. Cleans extraneous blank lines and horizontal rules
        
        Args:
            content: Raw report content
            outline: Report outline
            
        Returns:
            Processed content
        """
        import re
        
        lines = content.split('\n')
        processed_lines = []
        prev_was_heading = False
        
        # Collect all section titles from outline
        section_titles = set()
        for section in outline.sections:
            section_titles.add(section.title)
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Check if line is a header
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                # Check if header is duplicated within 5 lines
                is_duplicate = False
                for j in range(max(0, len(processed_lines) - 5), len(processed_lines)):
                    prev_line = processed_lines[j].strip()
                    prev_match = re.match(r'^(#{1,6})\s+(.+)$', prev_line)
                    if prev_match:
                        prev_title = prev_match.group(2).strip()
                        if prev_title == title:
                            is_duplicate = True
                            break
                
                if is_duplicate:
                    # Skip duplicate header and following blank line
                    i += 1
                    while i < len(lines) and lines[i].strip() == '':
                        i += 1
                    continue
                
                # Header hierarchy normalization:
                # - # (level=1) Main report title only
                # - ## (level=2) Section titles
                # - ### and lower (level>=3) Converted to bold prose
                
                if level == 1:
                    if title == outline.title:
                        # Retain main report title
                        processed_lines.append(line)
                        prev_was_heading = True
                    elif title in section_titles:
                        # Section title erroneously used #, fix to ##
                        processed_lines.append(f"## {title}")
                        prev_was_heading = True
                    else:
                        # Convert other level 1 headers to bold
                        processed_lines.append(f"**{title}**")
                        processed_lines.append("")
                        prev_was_heading = False
                elif level == 2:
                    if title in section_titles or title == outline.title:
                        # Retain section title
                        processed_lines.append(line)
                        prev_was_heading = True
                    else:
                        # Convert non-section level 2 headers to bold
                        processed_lines.append(f"**{title}**")
                        processed_lines.append("")
                        prev_was_heading = False
                else:
                    # Convert level 3+ headers to bold prose
                    processed_lines.append(f"**{title}**")
                    processed_lines.append("")
                    prev_was_heading = False
                
                i += 1
                continue
            
            elif stripped == '---' and prev_was_heading:
                # Skip horizontal rule immediately after header
                i += 1
                continue
            
            elif stripped == '' and prev_was_heading:
                # Retain single blank line after header
                if processed_lines and processed_lines[-1].strip() != '':
                    processed_lines.append(line)
                prev_was_heading = False
            
            else:
                processed_lines.append(line)
                prev_was_heading = False
            
            i += 1
        
        # Clean consecutive blank lines (retain max 2)
        result_lines = []
        empty_count = 0
        for line in processed_lines:
            if line.strip() == '':
                empty_count += 1
                if empty_count <= 2:
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    @classmethod
    def save_report(cls, report: Report) -> None:
        """Save report metadata and full report"""
        cls._ensure_report_folder(report.report_id)
        
        # Save metadata JSON
        with open(cls._get_report_path(report.report_id), 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Save outline
        if report.outline:
            cls.save_outline(report.report_id, report.outline)
        
        # Save complete Markdown report
        if report.markdown_content:
            with open(cls._get_report_markdown_path(report.report_id), 'w', encoding='utf-8') as f:
                f.write(report.markdown_content)
        
        logger.info(t('report.reportSaved', reportId=report.report_id))
    
    @classmethod
    def get_report(cls, report_id: str) -> Optional[Report]:
        """Get report"""
        path = cls._get_report_path(report_id)
        
        if not os.path.exists(path):
            # Backward compatibility: check files stored directly under reports directory
            old_path = os.path.join(cls.REPORTS_DIR, f"{report_id}.json")
            if os.path.exists(old_path):
                path = old_path
            else:
                return None
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruct Report object
        outline = None
        if data.get('outline'):
            outline_data = data['outline']
            sections = []
            for s in outline_data.get('sections', []):
                sections.append(ReportSection(
                    title=s['title'],
                    content=s.get('content', ''),
                    description=s.get('description', '')
                ))
            outline = ReportOutline(
                title=outline_data['title'],
                summary=outline_data['summary'],
                sections=sections
            )
        
        # If markdown_content is empty, read from full_report.md
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            full_report_path = cls._get_report_markdown_path(report_id)
            if os.path.exists(full_report_path):
                with open(full_report_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
        
        return Report(
            report_id=data['report_id'],
            simulation_id=data['simulation_id'],
            graph_id=data['graph_id'],
            simulation_requirement=data['simulation_requirement'],
            status=ReportStatus(data['status']),
            outline=outline,
            markdown_content=markdown_content,
            created_at=data.get('created_at', ''),
            completed_at=data.get('completed_at', ''),
            error=data.get('error')
        )
    
    @classmethod
    def get_report_by_simulation(cls, simulation_id: str) -> Optional[Report]:
        """Get report by simulation ID"""
        cls._ensure_reports_dir()
        
        for item in os.listdir(cls.REPORTS_DIR):
            item_path = os.path.join(cls.REPORTS_DIR, item)
            # Directory format
            if os.path.isdir(item_path):
                report = cls.get_report(item)
                if report and report.simulation_id == simulation_id:
                    return report
            # Legacy format: JSON file
            elif item.endswith('.json'):
                report_id = item[:-5]
                report = cls.get_report(report_id)
                if report and report.simulation_id == simulation_id:
                    return report
        
        return None
    
    @classmethod
    def list_reports(cls, simulation_id: Optional[str] = None, limit: int = 50) -> List[Report]:
        """List reports"""
        cls._ensure_reports_dir()
        
        reports = []
        for item in os.listdir(cls.REPORTS_DIR):
            item_path = os.path.join(cls.REPORTS_DIR, item)
            # Directory format
            if os.path.isdir(item_path):
                report = cls.get_report(item)
                if report:
                    if simulation_id is None or report.simulation_id == simulation_id:
                        reports.append(report)
            # Legacy format: JSON file
            elif item.endswith('.json'):
                report_id = item[:-5]
                report = cls.get_report(report_id)
                if report:
                    if simulation_id is None or report.simulation_id == simulation_id:
                        reports.append(report)
        
        # Sort by creation time descending
        reports.sort(key=lambda r: r.created_at, reverse=True)
        
        return reports[:limit]
    
    @classmethod
    def delete_report(cls, report_id: str) -> bool:
        """Delete report directory"""
        import shutil
        
        folder_path = cls._get_report_folder(report_id)
        
        # Directory format: delete entire folder
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
            logger.info(t('report.reportFolderDeleted', reportId=report_id))
            return True
        
        # Legacy format: delete individual file
        deleted = False
        old_json_path = os.path.join(cls.REPORTS_DIR, f"{report_id}.json")
        old_md_path = os.path.join(cls.REPORTS_DIR, f"{report_id}.md")
        
        if os.path.exists(old_json_path):
            os.remove(old_json_path)
            deleted = True
        if os.path.exists(old_md_path):
            os.remove(old_md_path)
            deleted = True
        
        return deleted
