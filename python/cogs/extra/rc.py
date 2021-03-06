"""This is a cog for a discord.py bot.
RC
"""

from discord.ext import commands
from discord import Member, TextChannel
from os import path
import asyncio
import json


class rc(commands.Cog, name='rc', command_attrs=dict(hidden=True)):
    def __init__(self, client):
        self.client = client
        with open(path.join(path.dirname(__file__), '../permissions.json')) as f:
            self.permitted_roles = json.load(f)[__name__.split('.')[-1]]
        self.rc_channel = None
        self.rc_user = None
        self.rc_target_channel = None
        self.rc_active = False

    async def cog_check(self, ctx):
        try:
            user_roles = [role.id for role in ctx.message.author.roles]
        except AttributeError:
            return False
        return any(role in self.permitted_roles for role in user_roles)

    # ----------------------------------------------
    # Cog Event listeners
    # ----------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return
        if msg.channel == self.rc_target_channel:
            await self.rc_channel.send(msg.author.name + ':  ' + msg.content)
        elif msg.channel == self.rc_channel:
            if not msg.author == self.rc_user:
                return
            if msg.content.startswith('felix'):
                return
            await self.rc_target_channel.send(msg.content)
        else:
            return

    # ----------------------------------------------
    # Cog Commands
    # ----------------------------------------------
    @commands.group(
        invoke_without_command=True,
        name='rc',
        brief='start rc',
        description='start rc',
        hidden=True,
    )
    @commands.guild_only()
    async def remote_control(self, ctx, target_channel: TextChannel = None):
        if self.rc_active:
            return
        if not target_channel:
            await ctx.send('Error: Please specify a channel!')
            return
        self.rc_target_channel = target_channel
        self.rc_user = ctx.author
        self.rc_channel = ctx.channel
        self.rc_active = True
        await ctx.send(f'Now remote controlling {target_channel.mention}')

    @remote_control.command(
        name='off',
        brief='stop rc',
        description='stop rc',
        hidden=True
    )
    @commands.guild_only()
    async def rc_off(self, ctx):
        if not self.rc_active:
            return
        if not ctx.author == self.rc_user:
            await ctx.send(f'{self.rc_user.name} is currently using rc!')
            return
        self.rc_target_channel = None
        self.rc_user = None
        self.rc_channel = None
        self.rc_active = False
        await ctx.send(f'Remote Control Stopped!')


def setup(client):
    """This is called when the cog is loaded via load_extension"""
    client.add_cog(rc(client))
