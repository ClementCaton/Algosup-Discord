from datetime import datetime, date
import aiomysql
import asyncio

class DataSQL():
    def __init__(self, host:str = "127.0.0.1", port:int = 3306, loop:asyncio.AbstractEventLoop = None) -> None:
        self.loop, self.host, self.port = loop, host, port

    async def auth(self, user:str="root", password:str='', database:str="mysql", autocommit:bool = True) -> None:
        self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit = user, password, database, autocommit
        self.connector = await aiomysql.connect(
            host=self.host, 
            port=self.port, 
            user=user, 
            password=password, 
            db=database, 
            loop=self.loop, 
            autocommit=autocommit
        )

    async def query(self, query:str) -> tuple:
        async with self.connector.cursor() as cursor:
            try:
                await cursor.execute(query)
                response = await cursor.fetchall()
                return response

            except aiomysql.OperationalError as e:
                if e.args[0] == 2013: #Lost connection to SQL server during query
                    await self.auth(self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit)
                    return await self.query(query)
                return e            

            except Exception as e:
                return e
    
    async def select(self, table:str, target:str, condition:str = '', order:str = '') -> query:
        query = "SELECT "+ target +" FROM `"+ table +"`"
        if condition: query += " WHERE "+ condition
        if order: query += " ORDER BY "+ order
        return await self.query(query + ';')

    async def count(self, table:str, what:str, condition:str = '') -> select:
        return await self.select(table, "COUNT("+what+")", condition)

    async def lookup(self, table:str, target:str, what:str, which:str) -> select:
        return await self.select(table, target, what+" REGEXP '"+which+"'")

    async def insert(self, table:str, args:dict) -> query:
        query, variables, values, lenght = f"INSERT INTO `{table}` (", '', '', len(args)
        for i, items in enumerate(args.items()):
            variable, value = items[0], items[1]
            
            variables += "`"+ str(variable) +"`, " if i+1 < lenght else "`"+ str(variable) +"`"

            if isinstance(value, (str)): value = f"'{value}'"
            elif isinstance(value, (date)): value = f"'{value.strftime('%Y-%m-%d')}'"
            elif isinstance(value, (datetime)): value = f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
            values += f"{value}, " if i+1 < lenght else f"{value}"    

        query += f"{variables} ) VALUES ({values});"	 

        return await self.query(query)

    async def update(self, table:str, variable:str, value:any, condition:str) -> query:
        if isinstance(value, (str)): value = "'"+value+"'"
        query = "UPDATE "+ table +" SET `"+ variable +"` = "+ str(value)
        if condition: query += " WHERE "+ condition
        return await self.query(query + ';')

    def close(self) -> None:
        self.connector.close()