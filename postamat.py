import argparse
from datetime import datetime

import requests


class Postamat:
    IN_PLAN = 99
    WORKING = 100
    TEMP_DISABLED = 101
    DISABLED = 102
    STATUSES = {
        IN_PLAN: "Планируется установка",
        WORKING: "Станция работает",
        TEMP_DISABLED: "Станция временно отключена",
        DISABLED: "Станция отключена",
    }

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.type = kwargs.get('type')
        self.address = kwargs['address']
        self.address_struct = kwargs['address_struct']
        self.status_code = kwargs.get('status_code', 99)
        self.lat = kwargs.get('lat')
        self.lng = kwargs.get('lng')
        self.description = kwargs.get('description', '')
        self.is_automated = kwargs['is_automated']
        self.accept_payments = kwargs['accept_payments']
        self.accept_cash = kwargs['accept_cash']
        self.accept_card = kwargs['accept_card']
        # Следующая строка использует ключ, который не возвращает API teleport'а
        # self.bank_terminal = kwargs['bank_terminal']
        self.working_hours = kwargs['working_hours']

    @property
    def status(self):
        return self.STATUSES.get(self.status_code)

    @property
    def is_running_now(self) -> bool:
        """
        Возвращает True, если постамат сейчас работает.
        Время считается по UTC.
        """
        now = datetime.utcnow()
        weekday = now.weekday()
        time_now = datetime.strftime(now, '%H:%M')
        for day in self.working_hours:
            if day['dow'] == weekday:
                if day['time_open'] <= time_now <= day['time_close']:
                    return True
        return False


def _parse_args():
    parser = argparse.ArgumentParser(description='Get postamat statuses')
    parser.add_argument('pids', nargs='*', help='Arbitrary number of postamat ids')
    return parser.parse_args()


def main():
    args = _parse_args()
    for pid in args.pids:
        try:
            response = requests.get('https://api.tport.online/v2/public-stations/%d' % int(pid))
        except ValueError:
            print('Ошибка! Идентификатор постамата должен быть целым числом, а не "%s"' % pid)
            continue
        if response.status_code == 200:
            try:
                postamat = Postamat(**response.json())
            except KeyError as exc:
                print('Ошибка! Для постамата с id %s отсутствует обязательное поле: %s' % (pid, exc))
            else:
                print('Постамат с id %s в статусе: %s' % (pid, postamat.status))
        else:
            print('При запросе постамата с id %s возникла следующая ошибка: %s' % (pid, response.json().get('detail')))


if __name__ == '__main__':
    main()
