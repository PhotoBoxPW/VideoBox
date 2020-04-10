# -*- coding: utf-8 -*-

# tacibot rethink util
# Provides utils for dealing with rethinkdb inside a bot.

'''Online File'''

import discord
import rethinkdb
from typing import List


class ReUtils():
    """Provides RethinkDB utilities for bots."""

    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn
        self.re = bot.re
        self.rdb = bot.rdb
        self.rtables = bot.rtables

    async def ensure_tables(self, *wanted_tables: str) -> List[str]:
        """Ensures that a table or tables is in the database for use."""

        # Prerequisites
        created_tables = []
        exist_tables = await self.re.db(self.rdb).table_list().run(self.conn)
        
        # Create Any Not Existing Tables
        for t in wanted_tables:
            if t not in exist_tables:
                await self.re.table_create(t).run(self.conn)
                created_tables.append(t)
                self.rtables.append(t)

        # Return any created tables
        return created_tables

    async def ensure_entry(self, table: str, sample_entry: dict) -> bool:
        """Ensures there is a sample entry in a table."""

        # Prerequisites
        # Filters by seeing if row matches sample entry
        # If nothing is found, returns true
        not_exists = await self.re \
            .table(table) \
            .filter(self.re.row == sample_entry) \
            .isEmpty() \
            .run(self.conn)

        # Sees if exists, creates if not
        if not_exists:
            await self.re.table(table) \
                .insert(sample_entry) \
                .run(self.conn)
            return True
        else:
            return False

    async def ensure_index(self, table: str, index: str) -> bool:
        """Ensures there is a certain index on a table."""
        
        # Prerequisuites
        exists = await self.re \
            .table(table) \
            .index_list() \
            .contains(index) \
            .run(self.conn)

        if exists:
            return False
        else:
            # Creates Index
            await self.re.table(table) \
                .index_create(index) \
                .run(self.conn)
            # Waits for creation
            await self.re.table(table) \
                .index_wait(index) \
                .run(self.conn)
            return True


def setup(bot):
    if bot.rdb:
        bot.reutils = ReUtils(bot)
    else:
        pass
