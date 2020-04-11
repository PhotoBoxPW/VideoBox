# -*- coding: utf-8 -*-

# videobox helpcmd
# Provides a new custom help command with some pretty formatting

'''HelpCmd File'''

import discord
from discord.ext import commands
import itertools

class TaciHelpCommand(commands.MinimalHelpCommand):
    def __init__(self, **options):

        # Main Stuff
        super().__init__(**options)
        self.command_attrs['help'] = "Find more assistance on this bot."
        self.subcommands_heading = "Subcommands"
        self.no_category = "Miscellaneous"

    def get_opening_note(self):
        """Provides the header for all help commands."""

        # Prerequisites
        bot = self.context.bot

        # __**name v0.0**__ - _description_
        return f"__**{bot.user.name} v{bot.config['version']}**__ - _AAAA_"

    def get_ending_note(self):
        """Provides the footer for all help commands."""

        # Prerequisites
        command_name = self.invoked_with
        bot = self.context.bot

        end_note = (
            "_For more info, see "
            # `prefix!command [category/command/subcommand]`
            f"`{self.clean_prefix}{command_name} [category/command/subcommand]`._"
        )

        return end_note

    def get_command_signature(self, command):
        """Gets the syntax string for a command."""

        # **`prefix!command [parameters]`**
        params = ""
        if command.signature:
            params = f" {command.signature}"

        return f"**`{self.clean_prefix}{command.qualified_name}{params}`**"

    def add_aliases_formatting(self, aliases):
        """Adds a listing of aliases to a command help."""

        # _Aliases: `alias1`, `alias2`, `alias3`_
        self.paginator.add_line(
            f"_{self.aliases_heading} {','.join(f'`{a}`' for a in aliases)}_"
        )

    def add_command_formatting(self, command):
        """Creates the help for the main command in a command help."""

        # Usually unused
        if command.description:
            self.paginator.add_line(command.description, empty=True)

        # **`prefix!command [parameters]`**
        signature = self.get_command_signature(command)

        # _Aliases: `alias1`, `alias2`, `alias3`_
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)

        # Anything from the help, which is usually from the command's docstring
        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    def add_subcommand_formatting(self, command):
        """Adds the entry for each subcommand under a cog or group."""

        # `command` - description OR `command`
        if command.short_doc:
            line = f"`{command.qualified_name}` - {command.short_doc}"
        else:
            line = f"`{command.qualified_name}`"
        self.paginator.add_line(line)
    
    def get_bot_prefixes(self):
        prefixes = [
            f"<@{self.context.bot.user.id}>"
        ]

        for prefix in self.context.bot.config['prefixes']:
            if prefix.endswith(' '):
                continue
            prefixes.append(f"`{prefix}`")

        return prefixes
            
    async def send_bot_help(self, mapping):
        """Sends the entire help for the bot."""

        embed = discord.Embed(
            description=(
                f"**VideoBox** by Snazzah\n\n"
                f"**Prefixes:** {', '.join(self.get_bot_prefixes())}\n"
                f"`{self.clean_prefix}{self.invoked_with} [category/command/subcommand]` for more info"
            )
        )

        ctx = self.context
        bot = ctx.bot
        main_cmds = []
        other_cmds = {}

        no_category = f"\u200b{self.no_category}"
        def get_category(command, *, no_category=no_category):
            cog = command.cog
            if cog is not None:
                return f"{cog.emoji}  {cog.qualified_name}" if cog.emoji else cog.qualified_name
            else:
                return no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        # Splits Bot List and Core commands out of the others
        for category, commands in to_iterate:
            embed.add_field(name=f"**{category}**", value=", ".join(f"`{c.name}`" for c in commands))

        if self.context.bot.config.get('color'):
            embed.color = self.context.bot.config.get('color')

        await self.context.send(embed=embed)

    async def send_cog_help(self, cog):
        """Sends the help for a cog."""

        embed = discord.Embed(
            title=f"{cog.emoji}  **{cog.qualified_name}**" if cog.emoji else f"{cog.qualified_name}"
        )

        if cog.description:
            embed.description = cog.description.strip()

        # Lists all commands in the cog
        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        if filtered:
            embed.add_field(
                name="**Commands**",
                value=", ".join(f"`{c.name}`" for c in filtered)
            )

        if self.context.bot.config.get('color'):
            embed.color = self.context.bot.config.get('color')

        await self.context.send(embed=embed)

    async def send_group_help(self, group):      
        """Sends the help for a command group."""

        # Adds the header if there
        note = self.get_opening_note()
        if note:
            self.paginator.add_line(note, empty=True)
            # New Line

        # Adds the formatting for the main group command 
        self.add_command_formatting(group)

        # Adds any subcommands
        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        if filtered:
            # **Subcommands** (or subcommands_heading)
            self.paginator.add_line(f"**{self.subcommands_heading}**")
            # Adds each subcommand entry
            for command in filtered:
                self.add_subcommand_formatting(command)

        # Adds the footer if there 
        note = self.get_ending_note()
        if note:
            self.paginator.add_line()  # New Line
            self.paginator.add_line(note)

        # Sends the completed help output
        await self.send_pages()

    async def send_command_help(self, command):
        """Sends the help for a single command."""

        params = ""
        if command.signature:
            params = f" {command.signature}"

        embed = discord.Embed(
            title=f"{self.clean_prefix}{command.qualified_name}"
        )

        if command.description:
            embed.description = command.description.strip()
        if command.help:
            embed.description = command.help.strip()
        if command.signature:
            embed.add_field(
                name="Usage",
                value=f"{self.clean_prefix}{command.qualified_name} `{command.signature}`"
            )
        if command.aliases:
            embed.add_field(
                name="Aliases",
                value=f"{','.join(f'`{self.clean_prefix}{a}`' for a in command.aliases)}"
            )
        if self.context.bot.config.get('color'):
            embed.color = self.context.bot.config.get('color')
        
        await self.context.send(embed=embed)

def setup(bot):
    """Lets helpcmd be added and reloaded as an extension."""
    pass