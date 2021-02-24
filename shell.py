from basic import run

while True:
    result, err = run("<stdin>", input("kripp >> "))

    if err:
        print(err.as_string())
    else:
        print(result)
