"""Agent cog for modals, agent routing, slash commands, and messages."""

import json
import logging
import traceback
import uuid

import discord
from discord import ui
from discord.ext import commands
from google.genai import types

from agents.agent import runner
from agents.configs import WYZVRD_SETTINGS
from agents.sub_agents.discord_mgmt_agent.tools import DiscordAPIClient
from discord_gateway.cogs.shared import (
    ADK_CONFIRMATION_FUNC,
    build_text_view,
    with_typing_indicator,
)
from discord_gateway.state import TraceData, get_state
from discord_gateway.ui.modals import (
    DynamicModal,
    OnboardingModal,
    SupportTicketModal,
)

USER_ID = WYZVRD_SETTINGS.user_id

logger = logging.getLogger("discord_bot")

# Constants
MAX_V2_TEXT_LENGTH = 4000  # Components V2 supports up to 4000 chars
MAX_STANDARD_MESSAGE_LENGTH = 2000  # Standard messages still limited to 2000
THOUGHT_TRUNCATE_LENGTH = 1900
BUTTON_COMPONENT_TYPE = 2
SELECT_COMPONENT_TYPE = 3


class AgentCog(commands.Cog):
    """Handles agent interaction routing and Discord UI."""

    def __init__(self, bot: commands.Bot):
        """Initialize the AgentCog.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot
        self.discord = DiscordAPIClient()  # Owns API client instance

    @with_typing_indicator
    async def process_agent_interaction(  # noqa: PLR0912, PLR0915
        self,
        interaction: discord.Interaction,
        content: str | types.Content,
        invocation_id: str | None = None,
    ):
        """Route interaction data back to the ADK agent with live UI updates.

        Shows typing indicator while processing. Automatically handles
        rate limits, errors, and provides trace viewing via buttons.

        Args:
            interaction: The Discord interaction object.
            content: The formatted string content or Content object to send.
            invocation_id: Optional ID to resume an existing conversation turn.
        """
        session_id = f"discord_{USER_ID}"
        channel = interaction.channel

        async with get_state().get_session_lock(session_id):
            # 1. Send initial Status layout
            interaction_ui: ui.LayoutView = ui.LayoutView()
            title_text: ui.TextDisplay = ui.TextDisplay(self.bot.user.name)
            body_text: ui.TextDisplay = ui.TextDisplay(
                f"🔄 {self.bot.user.name} is working..."
            )

            status_container: ui.Container = ui.Container(
                title_text, body_text, accent_color=discord.Color.blue()
            )
            interaction_ui.add_item(status_container)
            status_msg: discord.Message = await channel.send(
                view=interaction_ui
            )

            try:
                session_obj = await runner.session_service.get_session(
                    app_name=WYZVRD_SETTINGS.name,
                    user_id=USER_ID,
                    session_id=session_id,
                )
                if not session_obj:
                    await runner.session_service.create_session(
                        app_name=WYZVRD_SETTINGS.name,
                        user_id=USER_ID,
                        session_id=session_id,
                        state={},
                    )

                # Map inputs to ADK Content
                if isinstance(content, str):
                    guild_context = (
                        f", Guild ID: {interaction.guild.id}"
                        if interaction.guild
                        else ""
                    )
                    discord_context = (
                        "\n\n[System Note: This is an Interaction Response "
                        f"from Discord. Channel ID: {interaction.channel.id}"
                        f"{guild_context}.]"
                    )
                    user_content = types.Content(
                        role="user",
                        parts=[types.Part(text=content + discord_context)],
                    )
                else:
                    user_content = content

                full_text = ""
                current_thought = ""
                current_invocation_id = invocation_id

                # --- TRACE UI State ---
                tools_used = []
                non_fatal_errors = []

                async for event in runner.run_async(
                    user_id=USER_ID,
                    session_id=session_id,
                    invocation_id=current_invocation_id,
                    new_message=user_content,
                ):
                    update_needed = False

                    # Store invocation ID for potential resumption
                    if event.invocation_id:
                        current_invocation_id = event.invocation_id

                    # A. Handle Errors
                    if event.error_message:
                        # Treat API/Validation errors as fatal for the loop,
                        if event.error_code in [
                            "INVALID_ARGUMENT",
                            "PERMISSION_DENIED",
                            "UNKNOWN_ERROR",
                        ]:
                            title_text.content = "Error Occurred"
                            body_text.content = (
                                f"**Code:** {event.error_code}\n"
                                f"**Detail:** {event.error_message}"
                            )
                            await status_msg.edit(view=interaction_ui)
                            return
                        else:
                            non_fatal_errors.append(
                                f"**{event.error_code}**: {event.error_message}"
                            )

                    # B. Handle Thoughts and Text
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.thought:
                                current_thought += part.thought
                                update_needed = True
                            if part.text and not event.partial:
                                full_text += part.text
                                title_text.content = self.bot.user.name
                                body_text.content = full_text
                                update_needed = True

                    # C. Handle Tool Calls
                    tool_calls: list[types.FunctionCall] = (
                        event.get_function_calls()
                    )
                    if tool_calls:
                        tools_str: str = ""
                        for tc in tool_calls:
                            if tc.name not in tools_used:
                                tools_used.append(tc.name)

                            tools_str += (
                                f"🛠️ **Tools:** `{tc.name}({tc.args})`\n"
                            )
                            body_text.content = tools_str
                            update_needed = True

                    # D. Handle Confirmations (NEW)
                    if event.actions.requested_tool_confirmations:
                        title_text.content = "⚖️ Confirmation Required"
                        body_text.content = (
                            "A tool requires your approval to proceed."
                        )
                        await status_msg.edit(view=interaction_ui)

                        for (
                            call_id,
                            conf,
                        ) in event.actions.requested_tool_confirmations.items():
                            # Encode ids into custom_id
                            approve_id = (
                                f"tool_conf:approve:{call_id}:"
                                f"{current_invocation_id}"
                            )
                            decline_id = (
                                f"tool_conf:decline:{call_id}:"
                                f"{current_invocation_id}"
                            )

                            # 1. Add text elements to the status container
                            hint = conf.hint or (
                                "The assistant wants to use a protected tool."
                            )
                            conf_text = ui.TextDisplay(
                                content=f"**Approval Requested**\n{hint}"
                            )
                            status_container.add_item(conf_text)

                            if conf.payload:
                                status_container.add_item(
                                    ui.TextDisplay(
                                        f"```json\n{json.dumps(conf.payload, indent=2)}\n```"  # noqa: E501
                                    )
                                )
                                print(f"Payload: {conf.payload}")

                            approve_btn = ui.Button(
                                label="Approve",
                                style=discord.ButtonStyle.success,
                                custom_id=approve_id,
                            )
                            decline_btn = ui.Button(
                                label="Decline",
                                style=discord.ButtonStyle.danger,
                                custom_id=decline_id,
                            )

                            # Create ActionRow and add to top-level view
                            action_row = ui.ActionRow(approve_btn, decline_btn)
                            status_container.add_item(action_row)

                            await status_msg.edit(view=interaction_ui)
                        # Stop processing; resumes on click
                        return

                    # E. Update UI if something changed
                    if update_needed:
                        try:
                            await status_msg.edit(view=interaction_ui)
                        except Exception:  # noqa: S110
                            pass

                # 2. Finalize UI (Trace Registry)
                trace_id = str(uuid.uuid4())
                get_state().store_trace(
                    trace_id,
                    TraceData(
                        thoughts=current_thought,
                        tools=tools_used,
                        errors=non_fatal_errors,
                    ),
                )

                status_container.accent_color = (
                    discord.Color.green()
                    if not non_fatal_errors
                    else discord.Color.orange()
                )

                # Build View with Trace Buttons
                if current_thought:
                    interaction_ui.add_item(ui.Separator())
                    thoughts_section_title = ui.TextDisplay("Thoughts")
                    thoughts_section_button = ui.Button(
                        label="View",
                        style=discord.ButtonStyle.secondary,
                        custom_id=f"trace_view:thoughts:{trace_id}",
                    )
                    thoughts_section = ui.Section(
                        thoughts_section_title,
                        accessory=thoughts_section_button,
                    )
                    interaction_ui.add_item(thoughts_section)
                if tools_used:
                    interaction_ui.add_item(ui.Separator())
                    tools_section_title = ui.TextDisplay("Tools")
                    tool_section_button = ui.Button(
                        label="View",
                        style=discord.ButtonStyle.primary,
                        custom_id=f"trace_view:tools:{trace_id}",
                    )
                    tools_section = ui.Section(
                        tools_section_title, accessory=tool_section_button
                    )
                    interaction_ui.add_item(tools_section)
                if non_fatal_errors:
                    interaction_ui.add_item(ui.Separator())
                    errors_section_title = ui.TextDisplay("Errors")
                    errors_section_button = ui.Button(
                        label="View",
                        style=discord.ButtonStyle.danger,
                        custom_id=f"trace_view:errors:{trace_id}",
                    )
                    errors_section = ui.Section(
                        errors_section_title, accessory=errors_section_button
                    )
                    interaction_ui.add_item(errors_section)

                # Update status message with final response
                if full_text:
                    if len(full_text) <= MAX_V2_TEXT_LENGTH:
                        title_text.content = self.bot.user.name
                        body_text.content = full_text
                    else:
                        # If too long for embed,
                        # show truncated in embed and send full as messages
                        title_text.content = (
                            f"{self.bot.user.name} (Continued below)"
                        )
                        body_text.content = (
                            full_text[:MAX_V2_TEXT_LENGTH] + "..."
                        )
                        for i in range(
                            0, len(full_text), MAX_STANDARD_MESSAGE_LENGTH
                        ):
                            await channel.send(
                                view=build_text_view(
                                    full_text[
                                        i : i + MAX_STANDARD_MESSAGE_LENGTH
                                    ]
                                )
                            )

                # Final UI update to show trace buttons and response
                await status_msg.edit(view=interaction_ui)

            except Exception as e:
                body_text.content = "💥 Critical Failure"
                status_container.accent_color = discord.Color.dark_red()
                body_text.content = f"An unexpected error occurred: `{str(e)}`"
                await status_msg.edit(view=interaction_ui)
                traceback.print_exc()

    # --- Slash Commands ---

    @commands.Cog.listener()
    async def on_interaction(  # noqa: PLR0912, PLR0915
        self, interaction: discord.Interaction
    ):
        """Main interaction handler for components like buttons and menus."""
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id", "")

            # 1. Handle Turn Trace Viewing (Ephemeral)
            if custom_id.startswith("trace_view:"):
                parts = custom_id.split(":")
                trace_type = parts[1]  # thoughts, tools, errors
                trace_id = parts[2]

                trace_data = get_state().get_trace(trace_id)
                if not trace_data:
                    await interaction.response.send_message(
                        view=build_text_view(
                            "Sorry, this trace data has expired from memory."
                        ),
                        ephemeral=True,
                    )
                    return

                if trace_type == "thoughts":
                    # truncated for safety
                    thoughts = trace_data["thoughts"][:THOUGHT_TRUNCATE_LENGTH]
                    content = f"**Agent Thoughts:**\n```md\n{thoughts}\n```"
                elif trace_type == "tools":
                    tools_str = "\n- ".join(trace_data["tools"])
                    content = f"**Tools Executed:**\n- {tools_str}"
                elif trace_type == "errors":
                    errs_str = "\n- ".join(trace_data["errors"])
                    content = f"**Non-Fatal Errors:**\n- {errs_str}"
                else:
                    content = "Invalid trace type."

                await interaction.response.send_message(
                    view=build_text_view(content), ephemeral=True
                )
                return

            # 2. Handle Tool Confirmations (Approve/Decline)
            if custom_id.startswith("tool_conf:"):
                parts = custom_id.split(":")
                choice = parts[1]  # "approve" or "decline"
                call_id = parts[2]
                inv_id = parts[3]

                is_confirmed: bool = choice == "approve"

                # Construct ADK FunctionResponse for confirmation
                func_response = types.FunctionResponse(
                    name=ADK_CONFIRMATION_FUNC,
                    id=call_id,
                    response={"confirmed": is_confirmed, "payload": {}},
                )
                # Content part with the function response
                content = types.Content(
                    role="user",
                    parts=[types.Part(function_response=func_response)],
                )

                # FIX 3: It's good practice to delete the confirmation message
                # to prevent the user from clicking the buttons again.
                try:
                    await interaction.message.delete()
                except Exception:  # noqa: S110
                    pass

                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(
                    view=build_text_view(
                        f"Action {'Approved' if is_confirmed else 'Declined'}."
                    ),
                    ephemeral=True,
                )

                # Resume the agent with the confirmation
                await self.process_agent_interaction(
                    interaction, content, invocation_id=inv_id
                )
                return

            # 2. Handle Modal Triggers
            if custom_id.startswith("modal_trigger:"):
                modal_key = custom_id.replace("modal_trigger:", "")
                modal_data = self.discord.get_modal_schema(modal_key)

                if modal_data:
                    await interaction.response.send_modal(
                        DynamicModal(
                            cog=self,
                            title=modal_data["title"],
                            custom_id=modal_key,
                            fields=modal_data["fields"],
                        )
                    )
                    return
                else:
                    await interaction.response.send_message(
                        view=build_text_view("Form expired."),
                        ephemeral=True,
                    )
                    return

            # 3. Handle standard Button/Select clicks
            component_type = interaction.data.get("component_type")
            if component_type == BUTTON_COMPONENT_TYPE:
                msg = (
                    f"The user clicked the button with custom_id: '{custom_id}'"
                )
            elif component_type == SELECT_COMPONENT_TYPE:
                values = interaction.data.get("values", [])
                msg = (
                    f"The user selected values {values} from menu '{custom_id}'"
                )
            else:
                msg = f"Interaction received: {custom_id}"

            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(
                view=build_text_view("Received!"), ephemeral=True
            )
            await self.process_agent_interaction(interaction, msg)

    async def cog_load(self):
        """Called when cog is loaded. Initialize Discord API client."""
        await self.discord.connect()
        logger.info("AgentCog loaded and Discord API client connected.")

    async def cog_unload(self):
        """Called when cog is unloaded. Cleanup Discord API client."""
        await self.discord.close()
        logger.info("AgentCog unloaded and Discord API client closed.")

    @commands.Cog.listener()
    async def on_ready(self):
        """Agent-specific startup tasks."""
        logger.info("AgentCog ready.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Main message handler for standard DMs and mentions."""
        if message.author == self.bot.user:
            return

        # Prevent double-processing
        state = get_state()
        if state.is_message_processed(message.id):
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = self.bot.user.mentioned_in(message)

        if is_dm or is_mentioned:
            state.mark_message_processed(message.id)

            content = message.content
            if is_mentioned:
                content = (
                    content.replace(f"<@!{self.bot.user.id}>", "")
                    .replace(f"<@{self.bot.user.id}>", "")
                    .strip()
                )

            if not content:
                return

            # Simulate interaction for the helper
            class MockInteraction:
                def __init__(self, msg):
                    self.user = msg.author
                    self.guild = msg.guild
                    self.channel = msg.channel

            try:
                await self.process_agent_interaction(
                    MockInteraction(message), content
                )
            except Exception as e:
                logger.error(
                    "Unhandled error in on_message: %s",
                    e,
                    exc_info=True,
                )
                await message.channel.send(
                    view=build_text_view(
                        f"An unexpected error occurred: `{e}`",
                        accent_color=discord.Color.red(),
                    )
                )

        await self.bot.process_commands(message)


# --- Slash Commands (registered via app_command on the cog) ---


async def support_ticket_callback(interaction: discord.Interaction):
    """Slash command to trigger the support ticket modal."""
    cog: AgentCog = interaction.client.get_cog("AgentCog")
    await interaction.response.send_modal(SupportTicketModal(cog))


async def onboarding_callback(interaction: discord.Interaction):
    """Slash command to trigger the onboarding modal."""
    cog: AgentCog = interaction.client.get_cog("AgentCog")
    await interaction.response.send_modal(OnboardingModal(cog))


async def setup(bot: commands.Bot):
    """Set up the AgentCog.

    Args:
        bot: The Discord bot instance.
    """
    try:
        cog = AgentCog(bot)

        # Register slash commands on the cog's tree
        bot.tree.command(
            name="supportticket", description="Open a new support ticket"
        )(support_ticket_callback)
        bot.tree.command(
            name="onboarding", description="Fill out your onboarding profile"
        )(onboarding_callback)

        await bot.add_cog(cog)
    except Exception as e:
        print(f'ERROR in AgentCog "setup" function: {e}')
