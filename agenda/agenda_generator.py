"""
Meeting Agenda Generator
Generates formatted meeting agendas using Claude AI based on Items and Projects.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from config.logging_config import get_logger
from services.claude_service import ClaudeService
from services.notion_service import NotionService
from models.notion_schemas import NotionMeeting, NotionItem, NotionProject, NotionQueryFilter, NotionQuerySort

logger = get_logger(__name__)


# Introduction template (stored in code as requested)
MEETING_INTRODUCTION = """INTRODUCTION

Hello and welcome to the meeting for Lambeth Cyclists - we are the Lambeth branch of the charity London Cycling Campaign. Whether you are a member of LCC or not, you are more than welcome to join and give your thoughts. We are interested in basically anyone who wants to make conditions in Lambeth better for cyclists of all ages.

We try to be studiously apolitical, but part of our role is often as a consultee on TfL or Lambeth Council road or infrastructure plans. We also organise social rides when we can, and we support the central London Cycling Campaign as we can.
"""


class AgendaGenerator:
    """Generates meeting agendas with Claude AI."""

    def __init__(self):
        """Initialize the agenda generator."""
        self.notion = NotionService()
        self.claude = ClaudeService()

    def generate_agenda(self, meeting: NotionMeeting) -> Tuple[str, List[str], List[str]]:
        """
        Generate a formatted agenda for a meeting.

        Args:
            meeting: The meeting to generate an agenda for

        Returns:
            Tuple of (agenda_text, item_ids, project_ids)
        """
        logger.info(f"Generating agenda for meeting: {meeting.meeting_title}")

        try:
            # Get the previous meeting to determine "since last meeting"
            previous_meeting = self._get_previous_meeting(meeting.meeting_date)

            # Gather relevant items and projects
            new_items = self._get_new_items(previous_meeting)
            deadline_items = self._get_items_with_approaching_deadlines(days=30)
            active_projects = self._get_active_projects()

            logger.info(
                f"Found {len(new_items)} new items, {len(deadline_items)} deadline items, "
                f"{len(active_projects)} active projects"
            )

            # Generate the formatted agenda
            agenda_text = self._format_agenda(
                meeting=meeting,
                new_items=new_items,
                deadline_items=deadline_items,
                active_projects=active_projects
            )

            # Get discussion prompts from Claude
            discussion_prompts = self._generate_discussion_prompts(
                new_items=new_items,
                deadline_items=deadline_items,
                active_projects=active_projects
            )

            # Add discussion prompts to agenda
            final_agenda = agenda_text + "\n\n" + discussion_prompts

            # Collect IDs for relations
            item_ids = list(set([item.notion_id for item in new_items + deadline_items]))
            project_ids = [project.notion_id for project in active_projects]

            logger.info(f"Generated agenda: {len(final_agenda)} characters")

            return final_agenda, item_ids, project_ids

        except Exception as e:
            logger.error(f"Error generating agenda: {e}", exc_info=True)
            raise

    def _get_previous_meeting(self, current_meeting_date: datetime) -> NotionMeeting | None:
        """Get the most recent meeting before the current one."""
        try:
            filters = [
                NotionQueryFilter(
                    property_name="Meeting Date",
                    property_type="date",
                    condition="before",
                    value=current_meeting_date.isoformat()
                )
            ]
            sorts = [NotionQuerySort(property_name="Meeting Date", direction="descending")]

            meetings = self.notion.query_meetings(filters=filters, sorts=sorts, limit=1)

            if meetings:
                logger.debug(f"Found previous meeting: {meetings[0].meeting_title}")
                return meetings[0]
            else:
                logger.debug("No previous meetings found")
                return None

        except Exception as e:
            logger.warning(f"Error finding previous meeting: {e}")
            return None

    def _get_new_items(self, previous_meeting: NotionMeeting | None) -> List[NotionItem]:
        """Get items created since the last meeting."""
        if not previous_meeting:
            # No previous meeting - get items from last 60 days
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)
        else:
            cutoff_date = previous_meeting.meeting_date

        try:
            filters = [
                NotionQueryFilter(
                    property_name="Date Received",
                    property_type="date",
                    condition="on_or_after",
                    value=cutoff_date.isoformat()
                )
            ]
            sorts = [NotionQuerySort(property_name="Date Received", direction="descending")]

            items = self.notion.query_items(filters=filters, sorts=sorts, limit=50)
            logger.debug(f"Found {len(items)} items since last meeting")
            return items

        except Exception as e:
            logger.error(f"Error querying new items: {e}", exc_info=True)
            return []

    def _get_items_with_approaching_deadlines(self, days: int = 30) -> List[NotionItem]:
        """Get items with deadlines in the next N days."""
        try:
            deadline_date = datetime.now(timezone.utc) + timedelta(days=days)

            filters = [
                NotionQueryFilter(
                    property_name="Consultation Deadline",
                    property_type="date",
                    condition="on_or_before",
                    value=deadline_date.isoformat()
                ),
                NotionQueryFilter(
                    property_name="Consultation Deadline",
                    property_type="date",
                    condition="on_or_after",
                    value=datetime.now(timezone.utc).isoformat()
                )
            ]
            sorts = [NotionQuerySort(property_name="Consultation Deadline", direction="ascending")]

            items = self.notion.query_items(filters=filters, sorts=sorts, limit=20)
            logger.debug(f"Found {len(items)} items with approaching deadlines")
            return items

        except Exception as e:
            logger.error(f"Error querying deadline items: {e}", exc_info=True)
            return []

    def _get_active_projects(self) -> List[NotionProject]:
        """Get currently active projects."""
        try:
            filters = [
                NotionQueryFilter(
                    property_name="Status",
                    property_type="select",
                    condition="equals",
                    value="active"
                )
            ]
            sorts = [NotionQuerySort(property_name="Priority", direction="descending")]

            projects = self.notion.query_projects(filters=filters, sorts=sorts, limit=10)
            logger.debug(f"Found {len(projects)} active projects")
            return projects

        except Exception as e:
            logger.error(f"Error querying active projects: {e}", exc_info=True)
            return []

    def _format_agenda(
        self,
        meeting: NotionMeeting,
        new_items: List[NotionItem],
        deadline_items: List[NotionItem],
        active_projects: List[NotionProject]
    ) -> str:
        """Format the agenda as markdown."""
        lines = []

        # Header
        lines.append(f"# {meeting.meeting_title}")
        lines.append(f"**Date:** {meeting.meeting_date.strftime('%A, %d %B %Y at %H:%M')}")

        if meeting.meeting_format:
            lines.append(f"**Format:** {meeting.meeting_format}")
        if meeting.location:
            lines.append(f"**Location:** {meeting.location}")
        if meeting.zoom_link:
            lines.append(f"**Zoom Link:** {meeting.zoom_link}")

        lines.append("\n---\n")

        # Introduction
        lines.append(MEETING_INTRODUCTION)
        lines.append("\n---\n")

        # Infrastructure & Consultations
        lines.append("## INFRASTRUCTURE & CONSULTATIONS\n")

        if new_items:
            lines.append("### New Items Since Last Meeting:\n")
            for item in new_items[:10]:  # Limit to 10 most recent
                deadline_str = ""
                if item.consultation_deadline:
                    deadline_str = f" (Deadline: {item.consultation_deadline.strftime('%d %b %Y')})"

                location_str = ""
                if item.locations:
                    location_str = f" - {', '.join(item.locations[:2])}"

                lines.append(f"- **{item.title}**{location_str}{deadline_str}")
                if item.summary:
                    lines.append(f"  {item.summary[:200]}")
                lines.append("")
        else:
            lines.append("_No new items since last meeting_\n")

        if deadline_items:
            lines.append("### Approaching Deadlines (Next 30 Days):\n")
            for item in deadline_items:
                deadline_str = item.consultation_deadline.strftime('%d %b %Y') if item.consultation_deadline else "TBD"
                lines.append(f"- **{item.title}** - Deadline: {deadline_str}")
                lines.append("")
        else:
            lines.append("_No approaching deadlines_\n")

        lines.append("\n---\n")

        # Current Campaigns & Projects
        lines.append("## CURRENT CAMPAIGNS & PROJECTS\n")

        if active_projects:
            for project in active_projects:
                lines.append(f"### {project.title}\n")
                if project.summary:
                    lines.append(f"{project.summary}\n")
                if project.current_status:
                    lines.append(f"**Status:** {project.current_status}\n")
                lines.append("")
        else:
            lines.append("_No active projects_\n")

        lines.append("\n---\n")

        # Recruitment & Volunteers
        lines.append("## RECRUITMENT & VOLUNTEERS\n")
        lines.append("- Committee members needed")
        lines.append("- Recent interest from Google Groups members")
        lines.append("- Outreach opportunities\n")

        lines.append("\n---\n")

        # Any Other Business
        lines.append("## ANY OTHER BUSINESS\n")
        lines.append("_To be added during the meeting_\n")

        return "\n".join(lines)

    def _generate_discussion_prompts(
        self,
        new_items: List[NotionItem],
        deadline_items: List[NotionItem],
        active_projects: List[NotionProject]
    ) -> str:
        """Use Claude to generate discussion prompts and questions."""
        try:
            # Build context for Claude
            context_parts = []

            if new_items:
                context_parts.append("NEW ITEMS:")
                for item in new_items[:5]:  # Top 5
                    context_parts.append(f"- {item.title}")
                    if item.summary:
                        context_parts.append(f"  Summary: {item.summary[:200]}")
                    if item.ai_key_points:
                        context_parts.append(f"  Key points: {', '.join(item.ai_key_points[:3])}")

            if deadline_items:
                context_parts.append("\nUPCOMING DEADLINES:")
                for item in deadline_items[:3]:
                    deadline_str = item.consultation_deadline.strftime('%d %b %Y') if item.consultation_deadline else "TBD"
                    context_parts.append(f"- {item.title} (Deadline: {deadline_str})")

            if active_projects:
                context_parts.append("\nACTIVE PROJECTS:")
                for project in active_projects[:3]:
                    context_parts.append(f"- {project.title}")
                    if project.summary:
                        context_parts.append(f"  {project.summary[:150]}")

            context = "\n".join(context_parts)

            prompt = f"""You are helping generate discussion prompts for a Lambeth Cyclists committee meeting.

Based on the items and projects below, generate:
1. Key discussion questions for the group
2. Specific actions that could be taken
3. Points that need decisions

Keep it concise and action-oriented. Focus on what the committee can do to advocate for better cycling conditions in Lambeth.

{context}

Generate 3-5 discussion prompts in markdown format."""

            # Call Claude
            message = self.claude.client.messages.create(
                model=self.claude.model,
                max_tokens=800,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text

            return f"## DISCUSSION PROMPTS (AI-Generated)\n\n{response_text}"

        except Exception as e:
            logger.warning(f"Could not generate discussion prompts: {e}")
            return "## DISCUSSION PROMPTS\n\n_Discussion prompts will be added during the meeting_"
