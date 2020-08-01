import typing

import discord
import psycopg2
from discord.ext import commands

from Smashcords2BlogBot import Smashcords2BlogBot
from cogs import is_mod
from database import categories


class Posts(commands.Cog):
    def __init__(self, bot):
        self.bot: Smashcords2BlogBot = bot
        # The following is a dictionary mapping the server ID to a tuple containing the currently edited embed
        # and the list of messages it references
        self.temp_posts: typing.Dict[int, typing.Tuple[discord.Embed, typing.List[discord.Message]]] = {}

    @commands.command(name='newpost', usage="",
                      brief="Initiates a new post",
                      aliases=['new'])
    async def create_embed(self, ctx: commands.Context):
        if not is_mod(self.bot.conn, ctx):
            await ctx.send("You're not a mod")
            return
        self.temp_posts[ctx.guild.id] = (discord.Embed(color=discord.Color.from_rgb(106, 252, 228)), [])
        await ctx.send("New post initiated\nSet up a **title**, the **content** and then **public** it to a category!")

    @commands.command(name='createcategory', usage="name",
                      brief="Creates a new category",
                      aliases=['newcategory', 'newcat', 'addcat', 'addcategory'])
    async def create_category(self, ctx: commands.Context, *args: str):
        if not is_mod(self.bot.conn, ctx):
            await ctx.send("You're not a mod")
            return
        arg: str = ' '.join(args)
        try:
            categories.add_category(self.bot.conn, ctx.guild.id, arg)
        except psycopg2.IntegrityError as err:
            await ctx.send("Error: {}".format(err))
            self.bot.conn.rollback()
            return
        await ctx.send("Category `{}` successfully created".format(arg))

    @commands.command(name='listcategories', usage="",
                      brief="Lists all categories",
                      aliases=['listcat', 'lc', 'categories'])
    async def list_categories(self, ctx: commands.Context):
        if not is_mod(self.bot.conn, ctx):
            await ctx.send("You're not a mod")
            return
        categories_list: list = categories.get_server_categories(self.bot.conn, ctx.guild.id)
        message: str = "Available categories:\n"
        for category in categories_list:
            message += "{}\n".format(category)
        await ctx.send(message)

    @commands.command(name='removecategory', usage="name",
                      brief="Removes a category",
                      aliases=['deletecategory', 'rmcat', 'yeetcat'])
    async def remove_category(self, ctx: commands.Context, *args: str):
        if not is_mod(self.bot.conn, ctx):
            await ctx.send("You're not a mod")
            return
        arg: str = ' '.join(args)
        categories_list: list = categories.get_server_categories(self.bot.conn, ctx.guild.id)
        if arg not in categories_list:
            await ctx.send("Category does not exist")
            return
        categories.remove_category(self.bot.conn, ctx.guild.id, arg)
        await ctx.send("Category `{}` successfully removed".format(arg))

    @commands.command(name='settitle', usage="name",
                      brief="Sets the title of the current post",
                      aliases=['title'])
    async def title(self, ctx: commands.Context, *args: str):
        if not is_mod(self.bot.conn, ctx):
            await ctx.send("You're not a mod")
            return
        self.temp_posts[ctx.guild.id][0].title = ' '.join(args)
        await ctx.send("Post edited", embed=self.temp_posts[ctx.guild.id][0])

    @title.error
    async def title_error(self, ctx: commands.Context, error: commands.CommandInvokeError):
        if isinstance(error.original, KeyError):
            await ctx.send("Please, create the post first using the `new` command")

    @commands.command(name='setcontent', usage="message IDs",
                      brief="Sets the content of the post",
                      descrition="Accepts multiple IDs at once, they need to be in order from top to bottom",
                      aliases=['content'])
    async def content(self, ctx: commands.Context, *args: str):
        if not is_mod(self.bot.conn, ctx):
            await ctx.send("You're not a mod")
            return
        current_tuple: typing.Tuple[discord.Embed, typing.List[discord.Message]] = self.temp_posts[ctx.guild.id]
        for messageID in args:
            try:
                current_tuple[1].append(await ctx.channel.fetch_message(int(messageID)))
            except Exception as e:
                await ctx.send("Error while adding the message with ID {}\n{}".format(messageID, e))
        embed_content = '\n'.join([str(message.jump_url) for message in self.temp_posts[ctx.guild.id][1]])
        current_tuple[0].clear_fields()
        current_tuple[0].add_field(name="content", value=embed_content)
        await ctx.send(embed=current_tuple[0])
        self.temp_posts[ctx.guild.id] = current_tuple  # not sure if needed since im not doing a deep copy

    @content.error
    async def content_error(self, ctx: commands.Context, error: commands.CommandInvokeError):
        if isinstance(error.original, KeyError):
            await ctx.send("Please, create the post first using the `new` command")
