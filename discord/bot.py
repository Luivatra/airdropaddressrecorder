from discord.ext import commands
from discord.user import User
from discord.guild import Guild, Member, Role
from discord import Intents
from dislash import slash_commands
from dislash.interactions import *
import os
import psycopg2
import requests
from cardano_verify import verify_address
import logging

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

intents = Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!",intents=intents)
slash = slash_commands.SlashClient(client)

@slash.command(
    name="register-ergo",
    description="Register your address for the airdrop.",
    options=[Option("address","Your ergo wallet address",OptionType.STRING,required=True)]
    )
async def registerErgo(interaction: SlashInteraction, address: str):
    # ------------- get user & guild ------------------
    guild: Guild = interaction.guild
    member: Member = interaction.author
    user: User = interaction.author

    # ------------- get wallet info based on address ---------------
    r = requests.get(f'{os.environ.get("ERGO_NODE")}/utils/address/{address}')
    res = r.json()

    # -------------- if wallet is valid save it in the DB ------------------
    if res['isValid']:
        with psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT"),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
            ) as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO discord_wallets 
                (guild_id,user_id,user_name,guild_join_date,wallet_address) 
                VALUES 
                (%s,%s,%s,%s,%s)
                ON CONFLICT ON CONSTRAINT "discord_wallets_GUILD_ID_USER_ID"
                DO UPDATE SET
                (user_name, wallet_address, wallet_update_ts)
                = (EXCLUDED.user_name, EXCLUDED.wallet_address, CURRENT_TIMESTAMP)""",(
                    guild.id,
                    user.id,
                    member.display_name,
                    member.joined_at,
                    address
                    ))
                conn.commit()
                # this seems redundant 
                # ---------------------------
                # cur.execute("""
                # SELECT count(*) from discord_wallets
                # where guild_id = '%s' and wallet_registration_ts <= (select wallet_registration_ts from discord_wallets where user_id = '%s' and guild_id = '%s')
                # """,(guild.id,user.id,guild.id))
                # count = cur.fetchone()[0]
                # ---------------------------
                extra = f"🦾 We'll keep this on hand for any future airdrops and events!😇"
                # if guild.id == 876475955701501962:
                    
                    # this seems redundant
                    # ---------------------------------------
                    # cur.execute("""
                    # SELECT count(*) from discord_users
                    # where guild_id = '%s' and join_date <= (select join_date from discord_users where user_id = '%s' and guild_id = '%s')
                    # """,(guild.id,user.id,guild.id))
                    # ogcount = cur.fetchone()[0]

                    # if ogcount > 0 and ogcount <= 1500:
                    #     extra = f"You were Discord member number {ogcount}, congratulations and thank you for being one of the first 1,500 Discord members to join our community. 😇 You are now successfully registered and will receive your airdrop soon!🥳🎉"
                    # ----------------------------------------
                    
                    # ---------- OG badge is no longer available -----------
                    # for r in guild.roles:
                    #     role: Role = r
                    #     if role.name == "OG":
                    #         await member.add_roles(role)
                    #  ---------------------------------------
                await interaction.reply(f"CONGRATULATIONS! 🎊 You successfully registered your Ergo Wallet address. {extra}")
    else:
        await interaction.reply("ERROR! Please re-enter a valid Ergo wallet address.")

# @slash.command(
#     name="register-cardano",
#     description="Register your address to get LISO badge.",
#     options=[Option("address","Your Cardano wallet address",OptionType.STRING,required=True)]
#     )
# async def registerCardano(interaction: SlashInteraction, address: str):
#     # ------------- get user & guild ------------------
#     guild: Guild = interaction.guild
#     member: Member = interaction.author
#     user: User = interaction.author

#     # -------------- if wallet is valid save it in the DB ------------------
#     # Important !!!!!!!
#     # Add blockfrost_project_id
#     if verify_address(address, os.environ.get('blockfrost_project_id')):
#         with psycopg2.connect(
#             host=os.environ.get("POSTGRES_HOST"),
#             port=os.environ.get("POSTGRES_PORT"),
#             database=os.environ.get('POSTGRES_DB'),
#             user=os.environ.get('POSTGRES_USER'),
#             password=os.environ.get('POSTGRES_PASSWORD')
#             ) as conn:
#             # Important !!!!
#             # Create discord_cardano_wallets table that uses schema of discord_wallets tabel used for ERGO
#             with conn.cursor() as cur:
#                 cur.execute("""INSERT INTO discord_cardano_wallets 
#                 (guild_id,user_id,user_name,guild_join_date,wallet_address) 
#                 VALUES 
#                 (%s,%s,%s,%s,%s)
#                 ON CONFLICT ON CONSTRAINT "discord_cardano_wallets_GUILD_ID_USER_ID"
#                 DO UPDATE SET
#                 (user_name, wallet_address, wallet_update_ts)
#                 = (EXCLUDED.user_name, EXCLUDED.wallet_address, CURRENT_TIMESTAMP)""",(
#                     guild.id,
#                     user.id,
#                     member.display_name,
#                     member.joined_at,
#                     address
#                     ))
#                 conn.commit()
#                 extra = f"🦾 We'll keep this on hand for any future airdrops and events!😇"
#                 if guild.id == 876475955701501962:
#                     for r in guild.roles:
#                         role: Role = r
#                         if role.name == "LISO":
#                             await member.add_roles(role)
#                 await interaction.reply(f"CONGRATULATIONS! 🎊 You successfully registered your Cardano Wallet address. {extra}")
#     else:
#         await interaction.reply("ERROR! Please re-enter a valid Cardano wallet address that is delegated to one of the NETA pools.")

async def getMemberNumber(guild_id, user_id):
    try:
        with psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT"),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
            ) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT guild_id,user_id,display_name,join_date, ROW_NUMBER() OVER(ORDER BY join_date) 
                    FROM discord_users 
                    WHERE guild_id = '%s' AND user_id = '%s'""",(
                        guild_id,
                        user_id
                        ))
                res = cur.fetchone()
                if res is not None:
                    return res[4]
                else:
                    return -1
    except Exception as e:
        logging.error(e)

async def insertMember(guild_id, user_id, joined_at, display_name):
    try:
        with psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT"),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
            ) as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO discord_users
                    (guild_id,user_id,display_name,join_date)
                    VALUES
                    (%s,%s,%s,%s)""",(
                        guild_id,
                        user_id,
                        joined_at,
                        display_name
                        ))
                conn.commit()
    except Exception as e:
        logging.error(e)
            

@client.event
async def on_ready():
    try:
        logging.info("on_ready")
        for guild in client.guilds:
            if guild.id == int(os.environ.get("GUILD_ID")):
                logging.info("Found the right guild")
                for member in guild.members:
                    logging.info(f"Found member {member.display_name}")
                    if not member.bot:
                        logging.info("not a bot")
                        if member.top_role >= guild.get_role(int(os.environ.get("ROLE_ID"))):
                            logging.info("Has the correct role")
                            if await getMemberNumber(guild.id, member.id) == -1:
                                logging.info("not in db yet")
                                await insertMember(guild.id,member.id,member.joined_at,member.display_name.replace(","," "))
    except Exception as e:
        logging.error(e)

@client.event
async def on_member_update(old: Member, member: Member):
    try:
        logging.info(f"on_member_update: {member.display_name}")
        if old.top_role < member.guild.get_role(int(os.environ.get("ROLE_ID"))):
            logging.info("Got the right role")
            if await getMemberNumber(member.guild.id, member.id) == -1:
                logging.info("not in db yet")
                await insertMember(member.guild.id, member.id, member.joined_at, member.display_name)
    except Exception as e:
        logging.error(e)
                    


client.run(os.environ.get("DISCORD_KEY"))