from datetime import datetime

from sqlmodel import Field, SQLModel


class RestrictedNetwork(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    source_virtual_address: str
    destination_virtual_address: str
    start_time: datetime
    end_time: datetime | None = None
    client_id: int | None = Field(default=None, foreign_key='client.id')

    def iptable_rules(self):
        return [
            f'-i tun0 -s {self.source_virtual_address} -d {self.destination_virtual_address} -j ACCEPT',
            f'-i tun0 -s {self.destination_virtual_address} -d {self.source_virtual_address} -j ACCEPT',
        ]
