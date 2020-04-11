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
        embed = discord.Embed(
            title=f"{self.clean_prefix}{group.qualified_name}"
        )

        if group.description:
            embed.description = group.description.strip()
        if group.help:
            embed.description = group.help.strip()
        if group.signature:
            embed.add_field(
                name="Usage",
                value=f"{self.clean_prefix}{group.qualified_name} `{group.signature}`"
            )
        if group.aliases:
            embed.add_field(
                name="Aliases",
                value=f"{', '.join(f'`{self.clean_prefix}{a}`' for a in group.aliases)}"
            )

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        if filtered:
            def get_subc_line(subcommand):
                result = f"`{self.clean_prefix}{group.qualified_name} {subcommand.name}"
                if subcommand.signature:
                    result += f" {subcommand.signature}"
                desc = "`"
                if subcommand.description:
                    desc = f"` - {subcommand.description}"
                elif subcommand.help:
                    desc = f"` - {subcommand.help}"
                return result + desc

            embed.add_field(
                name="**Subcommands**",
                value="\n".join(get_subc_line(c) for c in filtered),
                inline=False
            )
        if self.context.bot.config.get('color'):
            embed.color = self.context.bot.config.get('color')
        
        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        """Sends the help for a single command."""
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
                value=f"{', '.join(f'`{self.clean_prefix}{a}`' for a in command.aliases)}"
            )
        if self.context.bot.config.get('color'):
            embed.color = self.context.bot.config.get('color')
        
        await self.context.send(embed=embed)

def setup(bot):
    """Lets helpcmd be added and reloaded as an extension."""
    pass