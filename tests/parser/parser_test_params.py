import pytest

from pylox import nodes as pn
from pylox.token import Token, TokenType

TEST_PARSER_PARAMS = [
    pytest.param(
        "1;",
        [
            pn.ExprStmt(pn.LiteralExpr(value=1.0)),
        ],
        id="1;",
    ),
    pytest.param(
        "1 + 2;",
        [
            pn.ExprStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(1.0),
                    Token(TokenType.PLUS, "+", None, 1),
                    pn.LiteralExpr(2.0),
                ),
            )
        ],
        id="1 + 2;",
    ),
    pytest.param(
        """
        print 1;
        print 2;
        print 3;
        """,
        [
            pn.PrintStmt(pn.LiteralExpr(value=1.0)),
            pn.PrintStmt(pn.LiteralExpr(value=2.0)),
            pn.PrintStmt(pn.LiteralExpr(value=3.0)),
        ],
        id="multiple statements",
    ),
    pytest.param(
        """
        -2;
        !true;
        !false;
        !nil;
        -1 + 2;
        x;
        -x * y;
        x * -y;
        """,
        [
            pn.ExprStmt(
                pn.UnaryExpr(
                    Token(TokenType.MINUS, "-", None, 2),
                    pn.LiteralExpr(value=2.0),
                ),
            ),
            pn.ExprStmt(
                pn.UnaryExpr(
                    Token(TokenType.BANG, "!", None, 3),
                    pn.LiteralExpr(value=True),
                ),
            ),
            pn.ExprStmt(
                pn.UnaryExpr(
                    Token(TokenType.BANG, "!", None, 4),
                    pn.LiteralExpr(value=False),
                ),
            ),
            pn.ExprStmt(
                pn.UnaryExpr(
                    Token(TokenType.BANG, "!", None, 5),
                    pn.LiteralExpr(value=None),
                ),
            ),
            pn.ExprStmt(
                pn.BinaryExpr(
                    pn.UnaryExpr(
                        Token(TokenType.MINUS, "-", None, 6),
                        pn.LiteralExpr(value=1.0),
                    ),
                    Token(TokenType.PLUS, "+", None, 6),
                    pn.LiteralExpr(value=2.0),
                ),
            ),
            pn.ExprStmt(pn.VarExpr(Token(TokenType.IDENTIFIER, "x", None, 7))),
            pn.ExprStmt(
                pn.BinaryExpr(
                    pn.UnaryExpr(
                        Token(TokenType.MINUS, "-", None, 8),
                        pn.VarExpr(Token(TokenType.IDENTIFIER, "x", None, 8)),
                    ),
                    Token(TokenType.STAR, "*", None, 8),
                    pn.VarExpr(Token(TokenType.IDENTIFIER, "y", None, 8)),
                ),
            ),
            pn.ExprStmt(
                pn.BinaryExpr(
                    pn.VarExpr(Token(TokenType.IDENTIFIER, "x", None, 9)),
                    Token(TokenType.STAR, "*", None, 9),
                    pn.UnaryExpr(
                        Token(TokenType.MINUS, "-", None, 9),
                        pn.VarExpr(Token(TokenType.IDENTIFIER, "y", None, 9)),
                    ),
                ),
            ),
        ],
        id="Unary expressions",
    ),
    pytest.param(
        """
        1 + 2 * 3;
        (1 + 2) * 3;
        1 + (2 * 3);
        1 + 2 * 3 + 4;
        (1 + 2) * (3 + 4);
        """,
        [
            pn.ExprStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=1.0),
                    Token(TokenType.PLUS, "+", None, 2),
                    pn.BinaryExpr(
                        pn.LiteralExpr(value=2.0),
                        Token(TokenType.STAR, "*", None, 2),
                        pn.LiteralExpr(value=3.0),
                    ),
                ),
            ),
            pn.ExprStmt(
                pn.BinaryExpr(
                    pn.GroupingExpr(
                        pn.BinaryExpr(
                            pn.LiteralExpr(value=1.0),
                            Token(TokenType.PLUS, "+", None, 3),
                            pn.LiteralExpr(value=2.0),
                        )
                    ),
                    Token(TokenType.STAR, "*", None, 3),
                    pn.LiteralExpr(value=3.0),
                ),
            ),
            pn.ExprStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=1.0),
                    Token(TokenType.PLUS, "+", None, 4),
                    pn.GroupingExpr(
                        pn.BinaryExpr(
                            pn.LiteralExpr(value=2.0),
                            Token(TokenType.STAR, "*", None, 4),
                            pn.LiteralExpr(value=3.0),
                        )
                    ),
                ),
            ),
            pn.ExprStmt(
                pn.BinaryExpr(
                    pn.BinaryExpr(
                        pn.LiteralExpr(value=1.0),
                        Token(TokenType.PLUS, "+", None, 5),
                        pn.BinaryExpr(
                            pn.LiteralExpr(value=2.0),
                            Token(TokenType.STAR, "*", None, 5),
                            pn.LiteralExpr(value=3.0),
                        ),
                    ),
                    Token(TokenType.PLUS, "+", None, 5),
                    pn.LiteralExpr(value=4.0),
                ),
            ),
            pn.ExprStmt(
                pn.BinaryExpr(
                    pn.GroupingExpr(
                        pn.BinaryExpr(
                            pn.LiteralExpr(value=1.0),
                            Token(TokenType.PLUS, "+", None, 6),
                            pn.LiteralExpr(value=2.0),
                        )
                    ),
                    Token(TokenType.STAR, "*", None, 6),
                    pn.GroupingExpr(
                        pn.BinaryExpr(
                            pn.LiteralExpr(value=3.0),
                            Token(TokenType.PLUS, "+", None, 6),
                            pn.LiteralExpr(value=4.0),
                        )
                    ),
                ),
            ),
        ],
        id="grouping",
    ),
    pytest.param(
        """
        print 1;
        print 2.0;
        print "3";
        print true;
        print false;
        print nil;
        print 1 + 2;
        print x;
        """,
        [
            pn.PrintStmt(pn.LiteralExpr(value=1.0)),
            pn.PrintStmt(pn.LiteralExpr(value=2.0)),
            pn.PrintStmt(pn.LiteralExpr(value="3")),
            pn.PrintStmt(pn.LiteralExpr(value=True)),
            pn.PrintStmt(pn.LiteralExpr(value=False)),
            pn.PrintStmt(pn.LiteralExpr(value=None)),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=1.0),
                    Token(TokenType.PLUS, "+", None, 7),
                    pn.LiteralExpr(value=2.0),
                ),
            ),
            pn.PrintStmt(pn.VarExpr(Token(TokenType.IDENTIFIER, "x", None, 8))),
        ],
        id="multiple types",
    ),
    pytest.param(
        """
        print 1 + 2;
        print 3 - 4;
        print 5 * 6;
        print 7 / 8;
        print 9 == 10;
        print 11 != 12;
        print 13 < 14;
        print 15 <= 16;
        print 17 > 18;
        print 19 >= 20;
        print 21 and 22;
        print 23 or 24;
        """,
        [
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=1.0),
                    Token(TokenType.PLUS, "+", None, 2),
                    pn.LiteralExpr(value=2.0),
                ),
            ),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=3.0),
                    Token(TokenType.MINUS, "-", None, 3),
                    pn.LiteralExpr(value=4.0),
                ),
            ),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=5.0),
                    Token(TokenType.STAR, "*", None, 4),
                    pn.LiteralExpr(value=6.0),
                ),
            ),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=7.0),
                    Token(TokenType.SLASH, "/", None, 5),
                    pn.LiteralExpr(value=8.0),
                ),
            ),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=9.0),
                    Token(TokenType.EQUAL_EQUAL, "==", None, 6),
                    pn.LiteralExpr(value=10.0),
                ),
            ),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=11.0),
                    Token(TokenType.BANG_EQUAL, "!=", None, 7),
                    pn.LiteralExpr(value=12.0),
                ),
            ),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=13.0),
                    Token(TokenType.LESS, "<", None, 8),
                    pn.LiteralExpr(value=14.0),
                ),
            ),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=15.0),
                    Token(TokenType.LESS_EQUAL, "<=", None, 9),
                    pn.LiteralExpr(value=16.0),
                ),
            ),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=17.0),
                    Token(TokenType.GREATER, ">", None, 10),
                    pn.LiteralExpr(value=18.0),
                ),
            ),
            pn.PrintStmt(
                pn.BinaryExpr(
                    pn.LiteralExpr(value=19.0),
                    Token(TokenType.GREATER_EQUAL, ">=", None, 11),
                    pn.LiteralExpr(value=20.0),
                ),
            ),
            pn.PrintStmt(
                pn.LogicalExpr(
                    pn.LiteralExpr(value=21.0),
                    Token(TokenType.AND, "and", None, 12),
                    pn.LiteralExpr(value=22.0),
                ),
            ),
            pn.PrintStmt(
                pn.LogicalExpr(
                    pn.LiteralExpr(value=23.0),
                    Token(TokenType.OR, "or", None, 13),
                    pn.LiteralExpr(value=24.0),
                ),
            ),
        ],
        id="operations",
    ),
    pytest.param(
        """
        var a;
        a = 1;
        """,
        [
            pn.VarStmt(
                name=Token(TokenType.IDENTIFIER, "a", None, 1),
                initializer=None,
            ),
            pn.ExprStmt(
                pn.AssignExpr(
                    Token(TokenType.IDENTIFIER, "a", None, 2),
                    pn.LiteralExpr(value=1.0),
                ),
            ),
        ],
        id="var a = 1;",
    ),
    pytest.param(
        "var a = 1;",
        [
            pn.VarStmt(
                name=Token(TokenType.IDENTIFIER, "a", None, 1),
                initializer=pn.LiteralExpr(value=1.0),
            ),
        ],
        id="var a = 1;",
    ),
    pytest.param(
        "var a; var b = 2;",
        [
            pn.VarStmt(
                name=Token(TokenType.IDENTIFIER, "a", None, 1),
                initializer=None,
            ),
            pn.VarStmt(
                name=Token(TokenType.IDENTIFIER, "b", None, 1),
                initializer=pn.LiteralExpr(value=2.0),
            ),
        ],
        id="var a; var b = 2;",
    ),
    pytest.param(
        "print 1;",
        [pn.PrintStmt(pn.LiteralExpr(value=1.0))],
        id="print 1;",
    ),
    pytest.param(
        "{ print 1; }",
        [pn.BlockStmt([pn.PrintStmt(pn.LiteralExpr(value=1.0))])],
    ),
    pytest.param(
        "if (true) { print 1; }",
        [
            pn.IfStmt(
                pn.LiteralExpr(value=True),
                pn.BlockStmt([pn.PrintStmt(pn.LiteralExpr(value=1.0))]),
                None,
            )
        ],
        id="if: only then branch",
    ),
    pytest.param(
        "if (true) { print 1; } else { print 2; }",
        [
            pn.IfStmt(
                pn.LiteralExpr(value=True),
                pn.BlockStmt([pn.PrintStmt(pn.LiteralExpr(value=1.0))]),
                pn.BlockStmt([pn.PrintStmt(pn.LiteralExpr(value=2.0))]),
            )
        ],
        id="if else",
    ),
    pytest.param(
        "while (true) { print 1; }",
        [
            pn.WhileStmt(
                pn.LiteralExpr(value=True),
                pn.BlockStmt([pn.PrintStmt(pn.LiteralExpr(value=1.0))]),
            )
        ],
        id="while",
    ),
    pytest.param(
        "for (var i = 0; i < 10; i = i + 1) { print i; }",
        [
            pn.ForStmt(
                pn.VarStmt(
                    name=Token(TokenType.IDENTIFIER, "i", None, 1),
                    initializer=pn.LiteralExpr(value=0.0),
                ),
                pn.BinaryExpr(
                    pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1)),
                    Token(TokenType.LESS, "<", None, 1),
                    pn.LiteralExpr(value=10.0),
                ),
                pn.AssignExpr(
                    Token(TokenType.IDENTIFIER, "i", None, 1),
                    pn.BinaryExpr(
                        pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1)),
                        Token(TokenType.PLUS, "+", None, 1),
                        pn.LiteralExpr(value=1.0),
                    ),
                ),
                pn.BlockStmt(
                    [
                        pn.PrintStmt(
                            pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1))
                        )
                    ]
                ),
            )
        ],
        id="for complete",
    ),
    pytest.param(
        "for (; i < 10; i = i + 1) { print i; }",
        [
            pn.ForStmt(
                None,
                pn.BinaryExpr(
                    pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1)),
                    Token(TokenType.LESS, "<", None, 1),
                    pn.LiteralExpr(value=10.0),
                ),
                pn.AssignExpr(
                    Token(TokenType.IDENTIFIER, "i", None, 1),
                    pn.BinaryExpr(
                        pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1)),
                        Token(TokenType.PLUS, "+", None, 1),
                        pn.LiteralExpr(value=1.0),
                    ),
                ),
                pn.BlockStmt(
                    [
                        pn.PrintStmt(
                            pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1))
                        )
                    ]
                ),
            )
        ],
        id="for no init",
    ),
    pytest.param(
        "for (var i = 0; ; i = i + 1) { print i; }",
        [
            pn.ForStmt(
                pn.VarStmt(
                    name=Token(TokenType.IDENTIFIER, "i", None, 1),
                    initializer=pn.LiteralExpr(value=0.0),
                ),
                None,
                pn.AssignExpr(
                    Token(TokenType.IDENTIFIER, "i", None, 1),
                    pn.BinaryExpr(
                        pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1)),
                        Token(TokenType.PLUS, "+", None, 1),
                        pn.LiteralExpr(value=1.0),
                    ),
                ),
                pn.BlockStmt(
                    [
                        pn.PrintStmt(
                            pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1))
                        )
                    ]
                ),
            )
        ],
        id="for no cond",
    ),
    pytest.param(
        "for (var i = 0; ; ) { print i; }",
        [
            pn.ForStmt(
                pn.VarStmt(
                    name=Token(TokenType.IDENTIFIER, "i", None, 1),
                    initializer=pn.LiteralExpr(value=0.0),
                ),
                None,
                None,
                pn.BlockStmt(
                    [
                        pn.PrintStmt(
                            pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1))
                        )
                    ]
                ),
            )
        ],
        id="for no cond no incr",
    ),
    pytest.param(
        "for (; i < 10; ) { print i; }",
        [
            pn.ForStmt(
                None,
                pn.BinaryExpr(
                    pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1)),
                    Token(TokenType.LESS, "<", None, 1),
                    pn.LiteralExpr(value=10.0),
                ),
                None,
                pn.BlockStmt(
                    [
                        pn.PrintStmt(
                            pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1))
                        )
                    ]
                ),
            )
        ],
        id="for no init no incr",
    ),
    pytest.param(
        "for (var i = 0; i < 10; ) { print i; }",
        [
            pn.ForStmt(
                pn.VarStmt(
                    name=Token(TokenType.IDENTIFIER, "i", None, 1),
                    initializer=pn.LiteralExpr(value=0.0),
                ),
                pn.BinaryExpr(
                    pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1)),
                    Token(TokenType.LESS, "<", None, 1),
                    pn.LiteralExpr(value=10.0),
                ),
                None,
                pn.BlockStmt(
                    [
                        pn.PrintStmt(
                            pn.VarExpr(Token(TokenType.IDENTIFIER, "i", None, 1))
                        )
                    ]
                ),
            )
        ],
        id="for no incr",
    ),
    pytest.param(
        """
        fun hello() {
            print "Hello, world!";
        }
        """,
        [
            pn.FunStmt(
                name=Token(TokenType.IDENTIFIER, "hello", None, 2),
                params=[],
                body=pn.BlockStmt(
                    [pn.PrintStmt(pn.LiteralExpr(value="Hello, world!"))]
                ),
            )
        ],
        id="function: no params",
    ),
    pytest.param(
        """
        fun hello(name) {
            print "Hello, " + name + "!";
        }
        """,
        [
            pn.FunStmt(
                name=Token(TokenType.IDENTIFIER, "hello", None, 2),
                params=[Token(TokenType.IDENTIFIER, "name", None, 2)],
                body=pn.BlockStmt(
                    [
                        pn.PrintStmt(
                            pn.BinaryExpr(
                                pn.BinaryExpr(
                                    pn.LiteralExpr(value="Hello, "),
                                    Token(TokenType.PLUS, "+", None, 3),
                                    pn.VarExpr(
                                        Token(TokenType.IDENTIFIER, "name", None, 3)
                                    ),
                                ),
                                Token(TokenType.PLUS, "+", None, 3),
                                pn.LiteralExpr(value="!"),
                            )
                        )
                    ]
                ),
            )
        ],
        id="function: one param",
    ),
    pytest.param(
        """
        fun hello(name, greeting) {
            print greeting + ", " + name + "!";
        }
        """,
        [
            pn.FunStmt(
                name=Token(TokenType.IDENTIFIER, "hello", None, 2),
                params=[
                    Token(TokenType.IDENTIFIER, "name", None, 2),
                    Token(TokenType.IDENTIFIER, "greeting", None, 2),
                ],
                body=pn.BlockStmt(
                    [
                        pn.PrintStmt(
                            pn.BinaryExpr(
                                pn.BinaryExpr(
                                    pn.BinaryExpr(
                                        pn.VarExpr(
                                            Token(
                                                TokenType.IDENTIFIER,
                                                "greeting",
                                                None,
                                                3,
                                            )
                                        ),
                                        Token(TokenType.PLUS, "+", None, 3),
                                        pn.LiteralExpr(value=", "),
                                    ),
                                    Token(TokenType.PLUS, "+", None, 3),
                                    pn.VarExpr(
                                        Token(TokenType.IDENTIFIER, "name", None, 3)
                                    ),
                                ),
                                Token(TokenType.PLUS, "+", None, 3),
                                pn.LiteralExpr(value="!"),
                            )
                        )
                    ]
                ),
            )
        ],
        id="function: multiple params",
    ),
    pytest.param(
        """
        fun hello() {}
        """,
        [
            pn.FunStmt(
                name=Token(TokenType.IDENTIFIER, "hello", None, 2),
                params=[],
                body=pn.BlockStmt([]),
            )
        ],
        id="function: no body",
    ),
    pytest.param(
        """
        fun hello() {
            hello();
        }
        """,
        [
            pn.FunStmt(
                name=Token(TokenType.IDENTIFIER, "hello", None, 2),
                params=[],
                body=pn.BlockStmt(
                    [
                        pn.ExprStmt(
                            pn.CallExpr(
                                pn.VarExpr(
                                    Token(TokenType.IDENTIFIER, "hello", None, 3)
                                ),
                                [],
                            )
                        )
                    ]
                ),
            )
        ],
        id="function: infinite recursion",
    ),
    pytest.param(
        """
        fun fib(n) {
            if (n < 2) {
                return n;
            }
            return fib(n - 1) + fib(n - 2);
        }
        """,
        [
            pn.FunStmt(
                name=Token(TokenType.IDENTIFIER, "fib", None, 2),
                params=[Token(TokenType.IDENTIFIER, "n", None, 2)],
                body=pn.BlockStmt(
                    [
                        pn.IfStmt(
                            pn.BinaryExpr(
                                pn.VarExpr(Token(TokenType.IDENTIFIER, "n", None, 3)),
                                Token(TokenType.LESS, "<", None, 3),
                                pn.LiteralExpr(value=2.0),
                            ),
                            pn.BlockStmt(
                                [
                                    pn.ReturnStmt(
                                        Token(TokenType.RETURN, "return", None, 4),
                                        pn.VarExpr(
                                            Token(TokenType.IDENTIFIER, "n", None, 4)
                                        ),
                                    )
                                ]
                            ),
                            None,
                        ),
                        pn.ReturnStmt(
                            Token(TokenType.RETURN, "return", None, 7),
                            pn.BinaryExpr(
                                pn.CallExpr(
                                    pn.VarExpr(
                                        Token(TokenType.IDENTIFIER, "fib", None, 7)
                                    ),
                                    [
                                        pn.BinaryExpr(
                                            pn.VarExpr(
                                                Token(
                                                    TokenType.IDENTIFIER, "n", None, 7
                                                )
                                            ),
                                            Token(TokenType.MINUS, "-", None, 7),
                                            pn.LiteralExpr(value=1.0),
                                        )
                                    ],
                                ),
                                Token(TokenType.PLUS, "+", None, 7),
                                pn.CallExpr(
                                    pn.VarExpr(
                                        Token(TokenType.IDENTIFIER, "fib", None, 7)
                                    ),
                                    [
                                        pn.BinaryExpr(
                                            pn.VarExpr(
                                                Token(
                                                    TokenType.IDENTIFIER, "n", None, 7
                                                )
                                            ),
                                            Token(TokenType.MINUS, "-", None, 7),
                                            pn.LiteralExpr(value=2.0),
                                        )
                                    ],
                                ),
                            ),
                        ),
                    ]
                ),
            )
        ],
        id="function: recursive",
    ),
    pytest.param(
        """
        class Empty {}
        """,
        [
            pn.ClassStmt(
                name=Token(TokenType.IDENTIFIER, "Empty", None, 2),
                superclass=None,
                methods=[],
            )
        ],
        id="class: empty",
    ),
    pytest.param(
        """
        class SuperClass {}
        class SubClass < SuperClass {}
        """,
        [
            pn.ClassStmt(
                name=Token(TokenType.IDENTIFIER, "SuperClass", None, 2),
                superclass=None,
                methods=[],
            ),
            pn.ClassStmt(
                name=Token(TokenType.IDENTIFIER, "SubClass", None, 3),
                superclass=pn.VarExpr(
                    Token(TokenType.IDENTIFIER, "SuperClass", None, 3)
                ),
                methods=[],
            ),
        ],
        id="class: superclass",
    ),
    pytest.param(
        """
        class Breakfast {
            cook() {
                print "Cooking breakfast...";
            }
            serve(who) {
                print "Serving breakfast to " + who;
            }
        }
        """,
        [
            pn.ClassStmt(
                name=Token(TokenType.IDENTIFIER, "Breakfast", None, 2),
                superclass=None,
                methods=[
                    pn.FunStmt(
                        name=Token(TokenType.IDENTIFIER, "cook", None, 3),
                        params=[],
                        body=pn.BlockStmt(
                            [
                                pn.PrintStmt(
                                    expr=pn.LiteralExpr(value="Cooking breakfast...")
                                ),
                            ]
                        ),
                    ),
                    pn.FunStmt(
                        name=Token(TokenType.IDENTIFIER, "serve", None, 6),
                        params=[Token(TokenType.IDENTIFIER, "who", None, 6)],
                        body=pn.BlockStmt(
                            [
                                pn.PrintStmt(
                                    expr=pn.BinaryExpr(
                                        pn.LiteralExpr(value="Serving breakfast to "),
                                        Token(TokenType.PLUS, "+", None, 7),
                                        pn.VarExpr(
                                            Token(
                                                TokenType.IDENTIFIER,
                                                "who",
                                                None,
                                                7,
                                            )
                                        ),
                                    ),
                                )
                            ]
                        ),
                    ),
                ],
            )
        ],
        id="class: multiple methods",
    ),
    pytest.param(
        "a.b = 1;",
        [
            pn.ExprStmt(
                pn.SetExpr(
                    obj=pn.VarExpr(Token(TokenType.IDENTIFIER, "a", None, 1)),
                    name=Token(TokenType.IDENTIFIER, "b", None, 1),
                    value=pn.LiteralExpr(value=1.0),
                )
            )
        ],
        id="set expr",
    ),
    pytest.param(
        """
        fun foo() {
            var n = 2;
            if (n > 1) {
                print n;
            }
        }
        foo();
        """,
        [
            pn.FunStmt(
                name=Token(TokenType.IDENTIFIER, "foo", None, 2),
                params=[],
                body=pn.BlockStmt(
                    [
                        pn.VarStmt(
                            Token(TokenType.IDENTIFIER, "n", None, 3),
                            pn.LiteralExpr(value=2.0),
                        ),
                        pn.IfStmt(
                            pn.BinaryExpr(
                                pn.VarExpr(Token(TokenType.IDENTIFIER, "n", None, 4)),
                                Token(TokenType.GREATER, ">", None, 4),
                                pn.LiteralExpr(value=1.0),
                            ),
                            pn.BlockStmt(
                                [
                                    pn.PrintStmt(
                                        pn.VarExpr(
                                            Token(TokenType.IDENTIFIER, "n", None, 5)
                                        )
                                    )
                                ]
                            ),
                            None,
                        ),
                    ]
                ),
            ),
            pn.ExprStmt(
                pn.CallExpr(
                    pn.VarExpr(Token(TokenType.IDENTIFIER, "foo", None, 7)),
                    [],
                )
            ),
        ],
        id="function: if n>1",
    ),
    pytest.param(
        """
        if (true) {
            var n = 2;
            if (n > 1) {
                print n;
            }
        }
        """,
        [
            pn.IfStmt(
                pn.LiteralExpr(value=True),
                pn.BlockStmt(
                    [
                        pn.VarStmt(
                            Token(TokenType.IDENTIFIER, "n", None, 3),
                            pn.LiteralExpr(value=2.0),
                        ),
                        pn.IfStmt(
                            pn.BinaryExpr(
                                pn.VarExpr(Token(TokenType.IDENTIFIER, "n", None, 4)),
                                Token(TokenType.GREATER, ">", None, 4),
                                pn.LiteralExpr(value=1.0),
                            ),
                            pn.BlockStmt(
                                [
                                    pn.PrintStmt(
                                        pn.VarExpr(
                                            Token(TokenType.IDENTIFIER, "n", None, 5)
                                        )
                                    )
                                ]
                            ),
                            None,
                        ),
                    ]
                ),
                None,
            ),
        ],
        id="if:if:n>1",
    ),
]
