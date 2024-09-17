from enum import Enum
from typing import List, Literal, Union

from pydantic import BaseModel
from sqlalchemy import text


class Command(str, Enum):
    # policies: https://www.postgresql.org/docs/current/sql-createpolicy.html
    all = "ALL"
    select = "SELECT"
    insert = "INSERT"
    update = "UPDATE"
    delete = "DELETE"


class Policy(BaseModel):
    definition: str
    expr: str
    cmd: Union[Command, List[Command]]

    def get_sql_policies(self, table_name: str, name_suffix: str = "0"):
        commands = [self.cmd] if isinstance(self.cmd, str) else self.cmd

        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print('definition', self.definition)
        print('expr', self.expr)
        print('commands', (commands[0].value))
        print('table_name', table_name)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")


        policy_lists = []
        for cmd in commands:
            cmd_value = cmd.value if isinstance(cmd, Command) else cmd
            policy_name = (
                f"{table_name}_{self.definition}" f"_{cmd_value}_policy_{name_suffix}".lower()
            )
            

            if cmd_value in ["ALL", "SELECT", "UPDATE", "DELETE"]:
                policy_lists.append(
                    text(
                        f"""
                        CREATE POLICY {policy_name} ON {table_name}
                        AS {self.definition}
                        FOR {cmd_value}
                        USING ({self.expr})
                        """
                    )
                )
            elif cmd in ["INSERT"]:
                policy_lists.append(
                    text(
                        f"""
                        CREATE POLICY {policy_name} ON {table_name}
                        AS {self.definition}
                        FOR {cmd_value}
                        WITH CHECK ({self.expr})
                        """
                    )
                )
            else:
                raise ValueError(f'Unknown policy command"{cmd_value}"')
        return policy_lists


class Permissive(Policy):
    definition: Literal["PERMISSIVE"] = "PERMISSIVE"


class Restrictive(Policy):
    definition: Literal["RESTRICTIVE"] = "RESTRICTIVE"
