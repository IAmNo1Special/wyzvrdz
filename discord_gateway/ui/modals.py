"""Static and dynamic Discord modal UI components."""

from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import ui

from discord_gateway.cogs.shared import build_text_view

if TYPE_CHECKING:
    from discord_gateway.cogs.agent.agent import AgentCog

PARAGRAPH_STYLE_VALUE = 2


class SupportTicketModal(ui.Modal, title="Submit Support Ticket"):
    """A static modal for submitting support tickets via slash command."""

    _desc_text = ui.TextDisplay(
        "Please describe your issue and select an urgency level."
    )
    subject = ui.TextInput(
        label="Subject",
        placeholder="Short summary of your issue",
        required=True,
    )
    description = ui.TextInput(
        label="Description",
        style=discord.TextStyle.paragraph,
        placeholder="Please provide more details...",
        required=True,
    )

    # V2: Select must be wrapped in a Label + ActionRow inside a Modal
    _urgency_select = ui.Select(
        placeholder="Select urgency level",
        options=[
            discord.SelectOption(
                label="Low", value="Low", description="Not urgent"
            ),
            discord.SelectOption(
                label="Medium",
                value="Medium",
                description="Normal priority",
                default=True,
            ),
            discord.SelectOption(
                label="High",
                value="High",
                description="Requires immediate attention",
            ),
        ],
    )
    _urgency_label = ui.Label(text="Urgency", component=_urgency_select)

    def __init__(self, cog: AgentCog):
        """Initialize the modal with a cog reference.

        Args:
            cog: The AgentCog instance.
        """
        super().__init__()
        self.cog = cog
        self.add_item(self._desc_text)
        self.add_item(self._urgency_label)

    async def on_submit(self, interaction: discord.Interaction):
        """Processes the support ticket submission."""
        await interaction.response.defer(ephemeral=True)
        urgency_value = (
            self._urgency_select.values[0]
            if self._urgency_select.values
            else "Medium"
        )

        content = (
            "[System Note: User submitted a Support Ticket via slash command]\n"
            f"- Subject: {self.subject.value}\n"
            f"- Description: {self.description.value}\n"
            f"- Urgency: {urgency_value}"
        )
        await interaction.followup.send(
            view=build_text_view("Ticket submitted!"), ephemeral=True
        )
        await self.cog.process_agent_interaction(interaction, content)


class OnboardingModal(ui.Modal, title="User Onboarding"):
    """A static modal for user onboarding via slash command."""

    _desc_text = ui.TextDisplay(
        "Tell us about yourself so we can personalize your experience."
    )
    name = ui.TextInput(
        label="Preferred Name",
        placeholder="What should we call you?",
        required=True,
    )
    interests = ui.TextInput(
        label="Interests",
        style=discord.TextStyle.paragraph,
        placeholder="What are you interested in?",
        required=True,
    )
    experience = ui.TextInput(
        label="Experience Level",
        placeholder="Beginner, Intermediate, Expert",
        required=False,
    )

    def __init__(self, cog: AgentCog):
        """Initialize the modal with a cog reference.

        Args:
            cog: The AgentCog instance.
        """
        super().__init__()
        self.cog = cog
        self.add_item(self._desc_text)

    async def on_submit(self, interaction: discord.Interaction):
        """Processes the onboarding form submission."""
        await interaction.response.defer(ephemeral=True)
        content = (
            f"[System Note: User submitted Onboarding Form via slash command]\n"
            f"- Name: {self.name.value}\n"
            f"- Interests: {self.interests.value}\n"
            f"- Experience: {self.experience.value or 'N/A'}"
        )
        await interaction.followup.send(
            view=build_text_view("Onboarding complete!"), ephemeral=True
        )
        await self.cog.process_agent_interaction(interaction, content)


class DynamicModal(ui.Modal):
    """A dynamically generated modal based on agent-defined schema."""

    def __init__(
        self,
        cog: AgentCog,
        title: str,
        custom_id: str,
        fields: list,
    ):
        """Initialize the dynamic modal.

        Args:
            cog: The AgentCog instance.
            title: The modal title.
            custom_id: The modal's custom ID.
            fields: List of field definitions.
        """
        super().__init__(title=title, timeout=None)
        self.cog = cog
        self.custom_id_key = custom_id
        self.inputs = {}

        for field in fields:
            text_input = discord.ui.TextInput(
                label=field.get("label", "Field"),
                placeholder=field.get("placeholder", ""),
                style=(
                    discord.TextStyle.paragraph
                    if field.get("style") == PARAGRAPH_STYLE_VALUE
                    else discord.TextStyle.short
                ),
                required=field.get("required", True),
                custom_id=field.get("custom_id"),
            )
            self.add_item(text_input)
            self.inputs[field.get("custom_id")] = text_input

    async def on_submit(self, interaction: discord.Interaction):
        """Processes the dynamic modal submission and routes it to the agent."""
        await interaction.response.defer(ephemeral=True)
        results = [
            f"- {label}: {item.value}" for label, item in self.inputs.items()
        ]
        formatted_submission = (
            f"The user submitted the dynamic form '{self.title}':\n"
            + "\n".join(results)
        )
        await interaction.followup.send(
            view=build_text_view("Form submitted!"), ephemeral=True
        )
        await self.cog.process_agent_interaction(
            interaction, formatted_submission
        )
