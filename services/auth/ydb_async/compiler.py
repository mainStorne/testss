from sqlalchemy.sql.compiler import FromLinter, COLLECT_CARTESIAN_PRODUCTS, WARN_LINTING
from ydb_sqlalchemy.sqlalchemy import YqlDDLCompiler as _YqlDDLCompiler, YqlCompiler as _YqlCompiler


class YqlCompiler(_YqlCompiler):

    def _compose_select_body(
        self,
        text,
        select,
        compile_state,
        inner_columns,
        froms,
        byfrom,
        toplevel,
        kwargs,
    ):
        text += ", ".join(inner_columns)

        if self.linting & COLLECT_CARTESIAN_PRODUCTS:
            from_linter = FromLinter({}, set())
            warn_linting = self.linting & WARN_LINTING
            if toplevel:
                self.from_linter = from_linter
        else:
            from_linter = None
            warn_linting = False

        # adjust the whitespace for no inner columns, part of #9440,
        # so that a no-col SELECT comes out as "SELECT WHERE..." or
        # "SELECT FROM ...".
        # while it would be better to have built the SELECT starting string
        # without trailing whitespace first, then add whitespace only if inner
        # cols were present, this breaks compatibility with various custom
        # compilation schemes that are currently being tested.
        if not inner_columns:
            text = text.rstrip()

        if froms:
            text += " \nFROM "

            if select._hints:
                text += ", ".join(
                    [
                        f._compiler_dispatch(
                            self,
                            asfrom=True,
                            fromhints=byfrom,
                            from_linter=from_linter,
                            **kwargs,
                        )
                        for f in froms
                    ]
                )
            else:
                text += " \nCROSS JOIN ".join(
                    [
                        f._compiler_dispatch(
                            self,
                            asfrom=True,
                            from_linter=from_linter,
                            **kwargs,
                        )
                        for f in froms
                    ]
                )
        else:
            text += self.default_from()

        if select._where_criteria:
            t = self._generate_delimited_and_list(
                select._where_criteria, from_linter=from_linter, **kwargs
            )
            if t:
                text += " \nWHERE " + t

        if warn_linting:
            assert from_linter is not None
            from_linter.warn()

        if select._group_by_clauses:
            text += self.group_by_clause(select, **kwargs)

        if select._having_criteria:
            t = self._generate_delimited_and_list(
                select._having_criteria, **kwargs
            )
            if t:
                text += " \nHAVING " + t

        if select._order_by_clauses:
            text += self.order_by_clause(select, **kwargs)

        if select._has_row_limiting_clause:
            text += self._row_limit_clause(select, **kwargs)

        if select._for_update_arg is not None:
            text += self.for_update_clause(select, **kwargs)

        return text



class YqlDDLCompiler(_YqlDDLCompiler):

    def create_table_constraints(
            self, table, _include_foreign_key_constraints=None, **kw
    ):
        # Copy from parent but removed FK constraints
        # On some DB order is significant: visit PK first, then the
        # other constraints (engine.ReflectionTest.testbasic failed on FB2)
        constraints = []
        if table.primary_key:
            constraints.append(table.primary_key)

        return ", \n\t".join(
            p
            for p in (
                self.process(constraint)
                for constraint in constraints
                if (constraint._should_create_for_compiler(self))
                   and (
                           not self.dialect.supports_alter
                           or not getattr(constraint, "use_alter", False)
                   )
            )
            if p is not None
        )
