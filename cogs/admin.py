import discord
import os

from classes.utilities import load_config ,cogs_manager, reload_views, cogs_directory, root_directory

from discord.ext import commands

class Admin(commands.Cog, name="admin"):
	"""
		Admin commands.

		Require intents: 
			- message_content
		
		Require bot permission:
			- read_messages
			- send_messages
			- attach_files
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '⚙️'
		label = "Admin"
		description = "Show the list of admin commands."
		return emoji, label, description

	@commands.command(name="loadcog")
	@commands.bot_has_permissions(send_messages=True)
	@commands.is_owner()
	async def load_cog(self, ctx: commands.Context, cog: str):
		"""Load a cog."""
		await cogs_manager(self.bot, "load", [f"cogs.{cog}"])
		await ctx.send(f":point_right: Cog {cog} loaded!")

	@commands.command(name="unloadcog")
	@commands.bot_has_permissions(send_messages=True)
	@commands.is_owner()
	async def unload_cog(self, ctx: commands.Context, cog: str):
		"""Unload a cog."""
		await cogs_manager(self.bot, "unload", [f"cogs.{cog}"])
		await ctx.send(f":point_left: Cog {cog} unloaded!")

	@commands.command(name="reloadallcogs", aliases=["rell"])
	@commands.bot_has_permissions(send_messages=True)
	@commands.is_owner()
	async def reload_all_cogs(self, ctx: commands.Context):
		"""Reload all cogs."""
		cogs = [cog for cog in self.bot.extensions]
		await cogs_manager(self.bot, "reload", cogs)	

		await ctx.send(f":muscle: All cogs reloaded: `{len(cogs)}`!")

	@commands.command(name="reload", aliases=["rel"], require_var_positional=True)
	@commands.bot_has_permissions(send_messages=True)
	@commands.is_owner()
	async def reload_specified_cogs(self, ctx: commands.Context, *cogs: str):
		"""Reload specific cogs."""
		reload_cogs = [f"cogs.{cog}" for cog in cogs]
		await cogs_manager(self.bot, "reload", reload_cogs)

		await ctx.send(f":thumbsup: `{'` `'.join(cogs)}` reloaded!")

	@commands.command(name="reloadlatest", aliases=["rl"])
	@commands.bot_has_permissions(send_messages=True)
	@commands.is_owner()
	async def reload_latest_cogs(self, ctx: commands.Context, n_cogs: int = 1):
		"""Reload the latest edited n cogs."""
		def sort_cogs(cogs_last_edit: list[list]) -> list[list]:
			return sorted(cogs_last_edit, reverse = True, key = lambda x: x[1])
		
		cogs = []
		for file in os.listdir(cogs_directory):
			actual = os.path.splitext(file)
			if actual[1] == ".py":
				file_path = os.path.join(cogs_directory, file)
				latest_edit = os.path.getmtime(file_path)
				cogs.append([actual[0], latest_edit])

		sorted_cogs = sort_cogs(cogs)
		reload_cogs = [f"cogs.{cog[0]}" for cog in sorted_cogs[:n_cogs]]
		await cogs_manager(self.bot, "reload", reload_cogs)

		await ctx.send(f":point_down: `{'` `'.join(reload_cogs)}` reloaded!")
		
	@commands.command(name="reloadviews", aliases=["rv"])
	@commands.bot_has_permissions(send_messages=True)
	@commands.is_owner()
	async def reload_view(self, ctx: commands.Context):
		"""Reload each registered views."""
		infants = reload_views()
		succes_text = f"👌 All views reloaded ! | 🔄 __`{sum(1 for _ in infants)} view(s) reloaded`__ : "
		for infant in infants: 
			succes_text += f"`{infant.replace('views.', '')}` "
		await ctx.send(succes_text)

	@commands.command(name="reloadconfig", aliases=["rc"])
	@commands.bot_has_permissions(send_messages=True)
	@commands.is_owner()
	async def reload_config(self, ctx: commands.Context):
		"""Reload each json config file."""
		self.bot.config = load_config()
		await ctx.send(f":handshake: `{len(self.bot.config)}` config file(s) reloaded!")

	@commands.command(name="synctree", aliases=["st"])
	@commands.bot_has_permissions(send_messages=True)
	@commands.is_owner()
	async def sync_tree(self, ctx: commands.Context, guild_id: str = None):
		"""Sync application commands."""
		if guild_id:
			if guild_id == "guild" or guild_id == "~":
				guild_id = ctx.guild.id
			tree = await self.bot.tree.sync(guild=discord.Object(id=guild_id))
		else:
			tree = await self.bot.tree.sync()

		self.bot.logger.name = f"discord.cogs.admin.sync_tree"
		self.bot.logger.info(msg=f"{ctx.author} synced the tree({len(tree)}): {tree}")

		await ctx.send(f":pinched_fingers: `{len(tree)}` synced!")

	@commands.command(name="botlogs", aliases=["bl"])
	@commands.bot_has_permissions(send_messages=True, attach_files=True)
	@commands.is_owner()
	async def show_bot_logs(self, ctx: commands.Context):
		"""Upload the bot logs"""
		logs_file = os.path.join(root_directory, "discord.log")

		await ctx.send(file=discord.File(fp=logs_file, filename="bot.log"))

	@commands.command(name="changeprefix", aliases=["cp", "prefix"], require_var_positional=True)
	@commands.bot_has_permissions(send_messages=True)
	@commands.has_guild_permissions(administrator=True)
	@commands.guild_only()
	async def change_guild_prefix(self, ctx: commands.Context, new_prefix: str):
		"""Change the guild prefix."""
		try:
			table = self.bot.config["bot"]["prefix_table"]["table"]
			await self.bot.database.insert_onduplicate(table, {"guild_id": ctx.guild.id, "guild_prefix": new_prefix})

			self.bot.prefixes[ctx.guild.id] = new_prefix
			await ctx.send(f":warning: Prefix changed to `{new_prefix}`")
		except Exception as e:
			await ctx.send(f"Error: {e}")

	@commands.command(name="shutdown")
	@commands.bot_has_permissions(send_messages=True)
	@commands.is_owner()
	async def shutdown_structure(self, ctx: commands.Context):
		"""Shutdown the bot."""
		await ctx.send(f":wave: `{self.bot.user.name}` is shutting down...")

		await self.bot.close()



async def setup(bot):
	await bot.add_cog(Admin(bot))
