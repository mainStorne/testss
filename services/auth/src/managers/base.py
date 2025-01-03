from typing import Iterable, Any, Callable, List
from fastapi import HTTPException
from sqlalchemy import UnaryExpression, Select, Result
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import load_only, InstrumentedAttribute
from fastapi_sqlalchemy_toolkit import ModelManager
from fastapi_sqlalchemy_toolkit.model_manager import ModelDict, ModelT, CreateSchemaT, sqlalchemy_model_to_dict
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status


class BaseManager(ModelManager):

    async def create(
            self,
            session: AsyncSession,
            in_obj: CreateSchemaT | None = None,
            refresh_attribute_names: Iterable[str] | None = None,
            *,
            commit: bool = True,
            exc: Exception = HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad Request"),
            **attrs: Any,
    ) -> ModelT:
        """
        Создание экземпляра модели и сохранение в БД.
        Также выполняет валидацию на уровне БД.

        :param session: сессия SQLAlchemy

        :param in_obj: модель Pydantic для создания объекта

        :param refresh_attribute_names: названия полей, которые нужно обновить
        (может использоваться для подгрузки связанных полей)

        :param commit: нужно ли вызывать `session.commit()`, если используется
        подход commit as you go

        :param attrs: дополнительные значения полей создаваемого экземпляра
        (какие-то поля можно установить напрямую,
        например, пользователя запроса)

        :returns: созданный экземпляр модели
        """
        create_data = in_obj.model_dump() if in_obj else {}
        create_data.update(attrs)
        # Добавляем дефолтные значения полей для валидации уникальности
        for field, default in self.defaults.items():
            if field not in create_data:
                create_data[field] = default

        await self.run_db_validation(session, in_obj=create_data, exc=exc)
        db_obj = self.model(**create_data)
        session.add(db_obj)
        await self.save(session, commit=commit)
        await session.refresh(db_obj, attribute_names=refresh_attribute_names)
        return db_obj

    async def run_db_validation(
            self,
            session: AsyncSession,
            in_obj: ModelDict,
            exc: HTTPException,
            db_obj: ModelT | None = None,
    ) -> ModelDict:
        """
        Выполнить валидацию на соответствие ограничениям БД.
        """
        if db_obj:
            db_obj_dict = sqlalchemy_model_to_dict(db_obj)
            db_obj_dict.update(in_obj)
            in_obj = db_obj_dict
        if self.fk_name_to_model:
            await self.validate_fk_exists(session, in_obj, exc)
        if self.m2m_relationships:
            await self.handle_m2m_fields(session, in_obj, exc)
        await self.validate_unique_fields(session, in_obj, db_obj=db_obj, exc=exc)
        await self.validate_unique_constraints(session, in_obj, exc)
        return in_obj

    async def list(
            self,
            session: AsyncSession,
            order_by: InstrumentedAttribute | UnaryExpression | None = None,
            filter_expressions: dict[InstrumentedAttribute | Callable, Any] | None = None,
            nullable_filter_expressions: (
                    dict[InstrumentedAttribute | Callable, Any] | None
            ) = None,
            options: List[Any] | Any | None = None,
            where: Any | None = None,
            base_stmt: Select | None = None,
            limit: int | None = None,
            offset: int | None = None,
            *,
            unique: bool = False,
            **simple_filters: Any,
    ):
        """
        Получение списка объектов с фильтрами.
        Пропускает фильтры, значения которых None.

        :param session: сессия SQLAlchemy

        :param order_by: поле для сортировки

        :param filter_expressions: словарь, отображающий поля для фильтрации
        на их значения. Фильтрация по None не применяется. См. раздел "фильтрация"
        в документации.

        :param nullable_filter_expressions: словарь, отображающий поля для фильтрации
        на их значения. Фильтрация по None применятеся, если значение
        в fastapi_sqlalchemy_toolkit.NullableQuery. См. раздел "фильтрация"
        в документации.

        :param options: параметры для метода .options() загрузчика SQLAlchemy

        :param where: выражение, которое будет передано в метод .where() SQLAlchemy

        :param unique: определяет необходимость вызова метода .unique()
        у результата SQLAlchemy

        :param base_stmt: объект Select для SQL запроса. Если передан, то метод вернёт
        список Row, а не ModelT.
        Примечание: фильтрация и сортировка по связанным моделям скорее всего
        не будут работать вместе с этим параметром.

        :param limit: ограничение, передаётся в параметр limit запроса SQLAlchemy

        :param offset: смещение, передаётся в параметр offset запроса SQLAlchemy

        :param simple_filters: параметры для фильтрации по точному соответствию,
        аналогично методу .filter_by() SQLAlchemy

        :returns: список объектов или Row
        """
        if filter_expressions is None:
            filter_expressions = {}
        if nullable_filter_expressions is None:
            nullable_filter_expressions = {}
        self.remove_optional_filter_bys(simple_filters)
        self.handle_filter_expressions(filter_expressions)
        self.handle_nullable_filter_expressions(nullable_filter_expressions)
        filter_expressions = filter_expressions | nullable_filter_expressions

        stmt = self.assemble_stmt(
            base_stmt,
            order_by,
            options,
            where,
            limit=limit,
            offset=offset,
            **simple_filters,
        )
        stmt = self.get_joins(
            stmt,
            options=options,
            order_by=order_by,
            filter_expressions=filter_expressions,
        )

        for filter_expression, value in filter_expressions.items():
            if isinstance(filter_expression, InstrumentedAttribute):
                stmt = stmt.filter(filter_expression == value)
            else:
                stmt = stmt.filter(filter_expression(value))

        return await session.exec(stmt)

    async def validate_fk_exists(
            self, session: AsyncSession, in_obj: ModelDict, exc: Exception
    ) -> None:
        """
        Проверить, существуют ли связанные объекты с переданными для записи id.
        """

        for key in in_obj:
            if key in self.fk_name_to_model and in_obj[key] is not None:
                related_object_exists = await session.get(
                    self.fk_name_to_model[key],
                    in_obj[key],
                    options=[load_only(self.fk_name_to_model[key].id)],
                )
                if not related_object_exists:
                    raise exc

    async def validate_unique_constraints(
            self, session: AsyncSession, in_obj: ModelDict, exc: Exception
    ) -> None:
        """
        Проверить, не нарушаются ли UniqueConstraint модели.
        """
        for unique_constraint in self.unique_constraints:
            query = {}
            for field in unique_constraint:
                if in_obj[field] is not None:
                    query[field] = in_obj[field]
            object_exists = await self.exists(
                session, **query
            )
            if object_exists:
                raise exc

    async def validate_unique_fields(
            self,
            session: AsyncSession,
            in_obj: ModelDict,
            exc: Exception,
            db_obj: ModelT | None = None,
    ) -> None:
        """
        Проверить соблюдение уникальности полей.
        """
        for column in self.model.__table__.columns._all_columns:
            if (
                    column.unique
                    and column.name in in_obj
                    and in_obj[column.name] is not None
            ):
                if db_obj and getattr(db_obj, column.name) == in_obj[column.name]:
                    continue
                attrs_to_check = {column.name: in_obj[column.name]}
                object_exists = await self.exists(
                    session=session,
                    **attrs_to_check,

                )
                if object_exists:
                    raise exc

    async def handle_m2m_fields(self, session: AsyncSession, in_obj: ModelDict, exc: Exception) -> None:
        for field in in_obj:
            if field in self.m2m_relationships:
                related_model = self.m2m_relationships[field]
                related_objects = []
                for related_object_id in in_obj[field]:
                    related_object = await session.get(related_model, related_object_id)
                    if not related_object:
                        raise exc
                    related_objects.append(related_object)
                in_obj[field] = related_objects
