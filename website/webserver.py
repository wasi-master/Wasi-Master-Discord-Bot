from discord.ext import ipc
from quart import Quart, render_template
from rich import traceback as rich_traceback

app = Quart(__name__)
rich_traceback.install()
ipc_client = ipc.Client(
    secret_key="WMBot"
)  # secret_key must be the same as your server


@app.route("/")
async def index():
    """Main Route"""
    # get the member count of server with ID 720217924350246913
    bot_commands = await ipc_client.request("get_commands")
    print(bot_commands)
    return await render_template(
        "index.html", commands=bot_commands
    )  # display member count


if __name__ == "__main__":
    app.run(debug=True)