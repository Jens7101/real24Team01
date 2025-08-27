from datetime import datetime, timedelta


class Sanduhr:
    def __init__(self) -> None:
        self.startZeit = datetime.now()

    def starten(self, dauerInMilliSekunden: int) -> None:
        self.startZeit = datetime.now()
        self.dauer = dauerInMilliSekunden

    def abgelaufen(self) -> bool:
        return datetime.now() >= (self.startZeit + timedelta(milliseconds=self.dauer))
