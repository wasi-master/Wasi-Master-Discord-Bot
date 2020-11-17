import discord
import inspect
from discord.ext import commands
import json
import re

class Coding(commands.Cog):
    """Commands releated to Programming
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="regex")
    async def _regex(self, ctx, regex, text):
        """Matches text to the regex provided"""
        matches = re.findall(regex, text)
        if matches:
            messages = ()
            messages.append(f"**Regex:** ```{regex}```")
            for num, match in enumerate(matches, start=1):
                messages.append(f"__Match {num}__ ```{match}```")
            await ctx.send("\n".join(matches))
        else:
            await ctx.send("No match")


    @commands.command(name="json")
    async def _json(self, ctx, *, json_string):
        json_string = json_string.lstrip("```").rstrip("```").lstrip("json")
        try:
            js = json.loads(json_string)
        except:
            await ctx.send(embed=discord.Embed(title="Invalid JSON", description=discord.utils.escape_markdown(json_string), color=0xff0000))
        else:
            js_pretty = json.dumps(js, indent=4)
            await ctx.send(f"```json\n{js_pretty}```")


    @commands.command(
        name="pypi",
        description="Searches pypi for python packages",
        aliases=["pypl", "pip"],
    )
    async def pythonpackagingindex(self, ctx, package_name: str):

        url = f"https://pypi.org/pypi/{package_name}/json"
        async with self.bot.session.get(url) as response:
            if (
                "We looked everywhere but couldn't find this page"
                in await response.text()
            ):
                return await ctx.send("Project not found")
            else:
                fj = json.loads(await response.text())
        fj = fj["info"]
        if not len(fj["summary"]) == 0:
            embed = discord.Embed(
                title=fj["name"],
                description=fj["summary"].replace("![", "[").replace("]", ""),
                color=0x2F3136,
            )
        else:
            embed = discord.Embed(title=fj["name"], color=0x2F3136)
        if len(fj["author_email"]) == 0:
            email = "None"
        else:
            email = fj["author_email"]
        embed.add_field(name="Author", value=f"Name: {fj['author']}\nEmail: {email}")
        embed.add_field(name="Version", value=fj["version"])
        # embed.add_field(name="Summary", value=fj["summary"])
        hp = "Github Repo" if re.match(r"https:\/\/(www\.)?github\.com\/.{0,39}\/.{0,100}", fj["home_page"]) else "Home Page"
        embed.add_field(
            name="Links",
            value=f"[{hp}]({fj['home_page']})\n[Project Link]({fj['project_url']})\n[Release Link]({fj['release_url']})",
        )
        if fj["license"] is None or len(fj["license"]) < 3:
            license = "Not Specified"
        else:
            license = fj["license"].replace("{", "").replace("}", "").replace("'", "")
        embed.add_field(name="License", value=f"‌{license}")
        if not fj["requires_dist"] is None:
            if len(fj["requires_dist"]) > 15:
                embed.add_field(name="Dependencies", value=len(fj["requires_dist"]))
            elif not len(fj["requires_dist"]) == 0:
                embed.add_field(
                    name=f"Dependencies ({len(fj['requires_dist'])})",
                    value="\n".join([i.split(" ")[0] for i in fj["requires_dist"]]),
                )
        if not fj["requires_python"] is None:
            if len(fj["requires_python"]) > 2:
                embed.add_field(
                    name="<:python:596577462335307777> Python Version Required",
                    value=fj["requires_python"],
                )
        await ctx.send(embed=embed)


    @commands.command(
        name="npm",
        description="Searches npm for JavaScript packages",
    )
    async def nodepackagemanager(self, ctx, package_name: str):

        url = f"https://registry.npmjs.org/{package_name}"
        async with self.bot.session.get(url) as response:
            if (
                '{"error":"Not found"}'
                in await response.text()
            ):
                return await ctx.send("Project not found")
            else:
                fj = json.loads(await response.text())
        if not len(fj["description"]) == 0:
            embed = discord.Embed(
                title=fj["_id"],
                description=fj["description"].replace("![", "[").replace("]", ""),
                color=0x2F3136,
            )
        else:
            embed = discord.Embed(title=fj["_id"], color=0x2F3136)
        author = fj["author"]
        embed.add_field(name="Author", value=f"Name: [{author.get('name')}]({author.get('url', 'None')})\nEmail: {author.get('email')}", inline=False)
        latest_ver = sorted(fj["versions"])[-1]
        embed.add_field(name="Version", value=latest_ver)
        main = ""
        for num, maintainer in enumerate(fj["maintainers"], start=1):
            author = maintainer
            main += f"‌    **{num}.** Name: [{author.get('name')}]({author.get('url', 'None')})\n‌        Email: {author.get('email')}\n\n"
        embed.add_field(name="Maintainers:",  value=main, inline=False)
        links = []
        if fj.get("homepage"):
            links.append(f'[Home Page]({fj["homepage"]})')
        if fj.get("bugs"):
            links.append(f'[Bug Tracker]({fj["bugs"]["url"]})')
        github = fj["repository"]["url"][4:-4]
        links.append(f'[Github Repo]({github})')
        links.append(f"[Package Link]({'https://www.npmjs.com/package/'+fj['_id']})")
        embed.add_field(name="Links", value="\n".join(links))
        if fj.get("license"):
            embed.add_field(name="License", value=fj["license"])
        dependencies = list(fj["versions"][latest_ver]["dependencies"])
        if dependencies:
            if len(dependencies) > 15:
                embed.add_field(name="Dependencies", value=len(dependencies), inline=False)
            elif len(dependencies) > 7:
                embed.add_field(name="Dependencies", value=", ".join(dependencies))
            else:
                embed.add_field(name="Dependencies", value="\n".join(dependencies))
        await ctx.send(embed=embed)





    @commands.command()
    async def rtfs(self, ctx, search: commands.clean_content(escape_markdown=False)):
        """
        Gets the source for an object from the discord.py library
        """
        overhead = ""
        raw_search = search
        searches = []
        if "." in search:
            searches = search.split(".")
            search = searches[0]
            searches = searches[1:]
        get = getattr(discord, search, None)
        if get is None:
            get = getattr(commands, search, None)
            if get is None:
                get = getattr(discord.ext.tasks, search, None)
        if get is None:
            return await ctx.send(f"Nothing found under `{raw_search}`")
        if inspect.isclass(get) or searches:
            if searches:
                for i in searches:
                    last_get = get
                    get = getattr(get, i, None)
                    if get is None and last_get is None:
                        return await ctx.send(f"Nothing found under `{raw_search}`")
                    elif get is None:
                        overhead = f"Couldn't find `{i}` under `{last_get.__name__}`, showing source for `{last_get.__name__}`\n\n"
                        get = last_get
                        break
        if isinstance(get, property):
            get = get.fget

        lines, firstlineno = inspect.getsourcelines(get)
        try:
            module = get.__module__
            location = module.replace('.', '/') + '.py'
        except AttributeError:
            location = get.__name__.replace(".", "/") + ".py"

        ret = f"https://github.com/Rapptz/discord.py/blob/v{discord.__version__}"
        final = f"{overhead}[{location}]({ret}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1})"
        await ctx.send(embed=discord.Embed(description=final))

def setup(bot):
    bot.add_cog(Coding(bot))
