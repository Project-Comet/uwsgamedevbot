import discord
from discord.ext import commands
import utilities as utils


class Roles:
	def __init__(self, bot):
		self.bot = bot
		self.restrictedRoles = bot.config["bot"]["restricted-roles"]

	@commands.command(pass_context=True)
	async def roles(self, ctx):
		"""Print a list of all server roles."""
		roleString = ""
		count = 0

		rolesDict = {}

		for role in ctx.message.author.server.roles:
			if role.name != "@everyone":
				rolesDict[role.name] = 0
		
		# For each server role, for each user's list of roles, add to a count if there is a user with that role
		for role in ctx.message.author.server.roles:
			if role.name != "@everyone":
				for user in ctx.message.author.server.members:
					for userRole in user.roles:
						if role == userRole:
							rolesDict[role.name] += 1

		# Convert dict to list so we can sort alphabetically
		rolesList = []
		for k, v in rolesDict.items():
			rolesString = "`"
			rolesString += k
			rolesString += "` "
			rolesString += str(v)
			rolesString += "\n"
			rolesList.append(rolesString)

		rolesList = sorted(rolesList)

		# Covnert list to string so we can display using line terminator \n
		rolesString = ""
		for x in rolesList:
			rolesString += x

		embed = discord.Embed(type="rich", colour=utils.generate_random_colour())
		embed.set_author(name="Use '!role Role Name' to add a role to your profile.")
		embed.add_field(name="Roles", value=rolesString)

		await self.bot.say(embed=embed)


	@commands.command(pass_context=True)
	async def role(self, ctx, *arg):
		"""Add or remove a role, e.g !role 1st Year to add or remove the role "1st Year".
		Must specify the role exactly, e.g "1st Year" and not "1st year".
		"""
		user = ctx.message.author
		roleToAdd = ""
		for x in arg:
			roleToAdd += str(x)
			roleToAdd += " "
		roleToAdd = roleToAdd[:-1]

		if roleToAdd not in self.restrictedRoles:
			role = None

			# compare role argument with server roles by checking their lower-case representations
			for tempRole in ctx.message.author.server.roles:
				if tempRole.name.lower() == roleToAdd.lower():
					print("MATCH! " + tempRole.name + " " + roleToAdd)
					role = tempRole
					break

			if role is None:
				return await self.bot.say("That role doesn't exist.")

			# we want to skip removing the specified role if we are adding one as we don't want to return/exit until we check if its a year role and deal with auto removals
			dontRemove = False

			if role not in user.roles:
				await self.bot.add_roles(user, role)
				await self.bot.say("{} role has been added to {}.".format(role, user.mention))
				dontRemove = True

			if role in user.roles and dontRemove == False:
				await self.bot.remove_roles(user, role)
				await self.bot.say("{} role has been removed from {}.".format(role, user.mention))

			# Auto remove old year role when new one added e.g if user has 2nd Year and adds 3rd Year, remove 2nd Year automatically
			years = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
			if role.name in years:
				userRoles = user.roles
				for r in userRoles:
					if r.name in years and r.name != role.name:
						await self.bot.remove_roles(user, r)
						await self.bot.say("{} role has been removed from {}.".format(r, user.mention))

		else:   
			await self.bot.say("This role requires manual approval from an admin.")

def setup(bot):
	bot.add_cog(Roles(bot))
	print("Roles module loaded.")