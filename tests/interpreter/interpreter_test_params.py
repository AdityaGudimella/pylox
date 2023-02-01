import pytest

INTERPRETER_SIDE_EFFECTS_PARAMS = [
    pytest.param("print 1;", ["1"], id="print"),
    pytest.param("print nil;", ["nil"], id="print: nil"),
    # Test unary operands
    pytest.param("print -1;", ["-1"], id="unary: negative"),
    pytest.param("print !true;", ["false"], id="unary: !true"),
    pytest.param("print !false;", ["true"], id="unary: !false"),
    # Test binary operands
    pytest.param("print 1 + 2;", ["3"], id="binary: add"),
    pytest.param("print 2 - 1;", ["1"], id="binary: sub"),
    pytest.param("print 2 * 1;", ["2"], id="binary: mul"),
    pytest.param("print 1 / 2;", ["0.5"], id="binary: div"),
    # Test precedence
    pytest.param("print 1 + 2 * 3;", ["7"], id="precedence"),
    pytest.param("print (1 + 2) * 3;", ["9"], id="precedence: group"),
    pytest.param("print (1 + 2) / (3 - 4);", ["-3"], id="precedence: group"),
    # Test string concatenation
    pytest.param('print "foo" + "bar";', ["foobar"], id="str: cat"),
    # Test string comparison
    pytest.param('print "foo" == "foo";', ["true"], id="str: true comp"),
    pytest.param('print "foo" != "foo";', ["false"], id="str: false comp"),
    pytest.param('print "foo" == "bar";', ["false"], id="str: diff false comp"),
    pytest.param('print "foo" != "bar";', ["true"], id="str: dif true comp"),
    # Test boolean comparison
    pytest.param("print true == true;", ["true"], id="bool: true comp"),
    pytest.param("print true != true;", ["false"], id="bool: false comp"),
    pytest.param("print true == false;", ["false"], id="bool: diff false comp"),
    pytest.param("print true != false;", ["true"], id="bool: diff true comp"),
    # Test comparison with nil
    pytest.param("print nil == nil;", ["true"], id="nil nil comp"),
    pytest.param("print nil != nil;", ["false"], id="nil nil false comp"),
    pytest.param("print nil == false;", ["false"], id="nil bool false comp"),
    pytest.param("print nil != false;", ["true"], id="nil bool comp"),
    # Test comparison with numbers
    pytest.param("print 1 == 1;", ["true"], id="num true comp"),
    pytest.param("print 1 != 1;", ["false"], id="num false comp"),
    pytest.param("print 1 == 2;", ["false"], id="num diff false comp"),
    pytest.param("print 1 != 2;", ["true"], id="num diff true comp"),
    # Test logical expressions
    pytest.param("print true or false;", ["true"], id="logical: true or false"),
    pytest.param("print true or true;", ["true"], id="logical: true or true"),
    pytest.param("print false or false;", ["false"], id="logical: false or false"),
    pytest.param("print false or true;", ["true"], id="logical: false or true"),
    pytest.param("print 0 or 1;", ["0"], id="logical: 0 or 1"),
    pytest.param("print nil or 1;", ["1"], id="logical: 0 or 1"),
    pytest.param("print true and false;", ["false"], id="logical: true and false"),
    pytest.param("print true and true;", ["true"], id="logical: true and true"),
    pytest.param("print false and false;", ["false"], id="logical: false and false"),
    pytest.param("print false and true;", ["false"], id="logical: false and true"),
    pytest.param("print nil and 1;", ["nil"], id="logical: 0 and 1"),
    # Test block
    pytest.param("{ print 1; }", ["1"], id="block: print"),
    # Test if statement
    pytest.param("if (true) print 1;", ["1"], id="if: true"),
    pytest.param("if (false) print 1;", [], id="if: false"),
    pytest.param("if (false) print 1; else {print 0;}", ["0"], id="if: false"),
    # Test builtins
    pytest.param("""clock();""", [], id="builtin: clock"),
    # Test variables
    pytest.param(
        "var a = 1; print a;",
        ["1"],
        id="var: a=1",
    ),
    pytest.param(
        "var a; print a;",
        ["nil"],
        id="var: no initializer",
    ),
    pytest.param(
        """
        var a;
        var b = 1;
        print a;
        print b;
        """,
        ["nil", "1"],
        id="var: multiple",
    ),
    # Test if condition
    pytest.param(
        """
        if (true) {
            var n = 2;
            if (n > 1) {
                print n;
            }
        }
        """,
        ["2"],
        id="if:if: n>1",
    ),
    pytest.param(
        """
        var n = 2;
        if (n > 1) {
            print n;
        }
        """,
        ["2"],
        id="if: n>1",
    ),
    # Test for loop
    pytest.param(
        """
        for (var i = 0; i < 3; i = i + 1) {
            print i;
        }
        """,
        ["0", "1", "2"],
        id="for: i=0, i<3, i=i+1",
    ),
    pytest.param(
        """
        // Calculate the 21st Fibonacci number.
        var a = 0;
        var temp;
        var fib_no = 0;

        for (var b = 1; a < 10000; b = temp + b) {
            temp = a;
            a = b;
            fib_no = fib_no + 1;
            if (fib_no == 21) { print a; }
        }
        """,
        ["10946"],
        id="for: fib_no=21",
    ),
    # Test while loop
    pytest.param(
        """
        var i = 0;
        while (i < 3) {
            print i;
            i = i + 1;
        }
        """,
        ["0", "1", "2"],
        id="while: i=0, i<3, i=i+1",
    ),
    # Test function
    pytest.param(
        """
        fun foo() {
            print "hello world";
        }
        """,
        [],
        id="function: def no args",
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
        ["2"],
        id="function: if n>1",
    ),
    pytest.param(
        """
        fun greet(name) {
            print "hello " + name;
        }
        greet("world");
        """,
        ["hello world"],
        id="function: def one arg",
    ),
    pytest.param(
        """
        fun greet(greeting, name) {
            print greeting + name;
        }
        greet("hello ", "world");
        """,
        ["hello world"],
        id="function: def two args",
    ),
    pytest.param(
        """
        fun add(a, b) {
            return a + b;
        }
        print add(1, 2);
        """,
        ["3"],
        id="function: with return",
    ),
    pytest.param(
        """
        fun fib(n) {
            if (n < 2) {
                return n;
            }
            return fib(n - 1) + fib(n - 2);
        }
        print fib(1);
        """,
        ["1"],
        id="fun: fib_no=1",
    ),
    pytest.param(
        """
        fun fib(n) {
            if (n < 2) {
                return n;
            }
            return fib(n - 1) + fib(n - 2);
        }
        print fib(21);
        """,
        ["10946"],
        id="fun: fib_no=21",
    ),
    # Scope
    pytest.param(
        """
        var a = "global a";
        var b = "global b";
        var c = "global c";
        {
            var a = "outer a";
            var b = "outer b";
            {
                var a = "inner a";
                print a;
                print b;
                print c;
            }
            print a;
            print b;
            print c;
        }
        print a;
        print b;
        print c;
        """,
        [
            "inner a",
            "outer b",
            "global c",
            "outer a",
            "outer b",
            "global c",
            "global a",
            "global b",
            "global c",
        ],
        id="scope",
    ),
    # Closures
    pytest.param(
        """
        fun  makeCounter() {
            var i = 0;
            fun count() {
                i = i + 1;
                print i;
            }

            return count;
        }

        var counter = makeCounter();
        counter();
        counter();
        """,
        ["1", "2"],
        id="closure",
    ),
    # Test classes
    pytest.param("""class Empty{}""", [], id="class: empty"),
]
