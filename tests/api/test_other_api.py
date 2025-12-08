# Modul_4\Cinescope\tests\api\test_other_api.py
import pytest
from sqlalchemy.orm import Session

from db_models.payments import AccountTransactionTemplate
from utils.data_generator import DataGenerator


def test_accounts_transaction_template(db_session: Session):
    # ====================================================================== Подготовка к тесту
    # Создаем новые записи в базе данных (чтоб точно быть уверенными что в базе присутствуют данные для тестирования)

    biba = AccountTransactionTemplate(user=f"Biba_{DataGenerator.generate_random_int(10)}", balance=1000)
    boba = AccountTransactionTemplate(user=f"Boba_{DataGenerator.generate_random_int(10)}", balance=500)

    # Добавляем записи в сессию
    db_session.add_all([biba, boba])
    # Фиксируем изменения в базе данных
    db_session.commit()
    biba_initial_balance = biba.balance
    boba_initial_balance = boba.balance

    def transfer_money(session, from_account, to_account, amount):
        # пример функции выполняющей транзакцию
        # представим что она написана на стороне тестируемого сервиса
        # и вызывая метод transfer_money, мы какбудтобы делем запрос в api_manager.movies_api.transfer_money
        """
        Переводит деньги с одного счета на другой.
        :param session: Сессия SQLAlchemy.
        :param from_account_id: ID счета, с которого списываются деньги.
        :param to_account_id: ID счета, на который зачисляются деньги.
        :param amount: Сумма перевода.
        """
        # Получаем счета
        from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
        to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()



        # Проверяем, что на счете достаточно средств
        if from_account.balance < amount:
            raise ValueError("Недостаточно средств на счете")
        # Выполняем перевод
        from_account.balance -= amount
        to_account.balance += amount

        # Сохраняем изменения
        session.commit()

    # ====================================================================== Тест
    # Проверяем начальные балансы
    assert biba.balance == 1000
    assert boba.balance == 500

    try:
        # Выполняем перевод 200 единиц от stan к bob
        transfer_money(db_session, from_account=biba.user, to_account=boba.user, amount=1200)

        # Проверяем, что балансы изменились
        assert biba.balance == 800
        assert boba.balance == 700

    except Exception as e:
        # Если произошла ошибка, откатываем транзакцию
        db_session.rollback()  # откат всех введеных нами изменений

        biba_after_rollback = db_session.query(AccountTransactionTemplate).filter_by(user=biba.user).one()
        boba_after_rollback = db_session.query(AccountTransactionTemplate).filter_by(user=boba.user).one()

        assert biba_after_rollback.balance == biba_initial_balance
        assert boba_after_rollback.balance == boba_initial_balance

    finally:
        # Удаляем данные для тестирования из базы
        db_session.delete(biba)
        db_session.delete(boba)
        # Фиксируем изменения в базе данных
        db_session.commit()